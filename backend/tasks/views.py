import secrets
import logging
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password, check_password
from django.db import transaction
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from rest_framework import viewsets, filters, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.throttling import ScopedRateThrottle

from .models import User, Task, Comment, Notification, UserProfile, Attachment, RequestLog
from .serializers import (
    UserSerializer, TaskSerializer, CommentSerializer, NotificationSerializer, 
    UserProfileSerializer, AttachmentSerializer, RequestLogSerializer
)
from .permissions import IsCommentOwnerOrAdmin
from .validators import validate_password_policy
from .crypto_utils import encrypt_data
from .telegram import send_telegram_otp

logger = logging.getLogger(__name__)

# Sadece adminlerin kullanıcı yönetimi yapabilmesi için özel izin sınıfı
class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

# Admin CRUD işlemleri
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']

# Görevler üzerinde CRUD işlemleri
from .models import User, Task, Comment, Notification, UserProfile, Attachment, RequestLog, Sprint
from .serializers import (
    UserSerializer, TaskSerializer, CommentSerializer, NotificationSerializer, 
    UserProfileSerializer, AttachmentSerializer, RequestLogSerializer, SprintSerializer
)

class SprintViewSet(viewsets.ModelViewSet):
    queryset = Sprint.objects.all().order_by('-created_at')
    serializer_class = SprintSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def start_sprint(self, request, pk=None):
        sprint = self.get_object()
        # Diğer aktif sprintleri tamamlandı yapıp bunu aktif yapalım
        Sprint.objects.filter(status='active').update(status='future')
        sprint.status = 'active'
        sprint.save()
        return Response(SprintSerializer(sprint).data)

    @action(detail=True, methods=['post'])
    def complete_sprint(self, request, pk=None):
        sprint = self.get_object()
        sprint.status = 'completed'
        sprint.save()
        # Tamamlanmamış görevleri Backlog'a (sprint=None) aktar
        sprint.tasks.exclude(state='done').update(sprint=None)
        return Response(SprintSerializer(sprint).data)

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Task.objects.none()
            
        if self.request.user.is_staff:
            queryset = Task.objects.all()
        else:
            queryset = Task.objects.filter(assignee=self.request.user)

        # Sprint filtreleme
        sprint_param = self.request.query_params.get('sprint')
        if sprint_param:
            if sprint_param in ['null', 'backlog']:
                queryset = queryset.filter(sprint__isnull=True)
            else:
                queryset = queryset.filter(sprint_id=sprint_param)

        active_sprint = self.request.query_params.get('active_sprint')
        if active_sprint == 'true':
            queryset = queryset.filter(sprint__status='active')

        return queryset

    def _broadcast_task_event(self, task_id=None, action='task_updated'):
        try:
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    'tasks_channel_group',
                    {
                        'type': 'task_event',
                        'action': action,
                        'task_id': task_id
                    }
                )
        except Exception as e:
            logger.error(f"WebSocket broadcast hatası: {e}")

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            task = serializer.save(creator=self.request.user)
        else:
            task = serializer.save(creator=self.request.user, assignee=self.request.user)
        self._broadcast_task_event(task.id, 'task_updated')

    def perform_update(self, serializer):
        task = serializer.save()
        self._broadcast_task_event(task.id, 'task_updated')

    def perform_destroy(self, instance):
        task_id = instance.id
        instance.delete()
        self._broadcast_task_event(task_id, 'task_updated')

    # Özet endpoint'i (Şifreli yanıt döner)
    @action(detail=False, methods=['get'])
    def summary(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "girdiğiniz bilgiler hatalı"}, status=403)
            
        if request.user.is_staff:
            tasks = Task.objects.all()
        else:
            tasks = Task.objects.filter(assignee=request.user)
        
        data = {choice[0]: tasks.filter(state=choice[0]).count() for choice in Task.STATE_CHOICES}
        # BE -> FE Şifreli Gönderim
        return Response(encrypt_data(data))

    # Excel (CSV) olarak dışa aktar
    @action(detail=False, methods=['get'])
    def export_excel(self, request):
        import csv
        from django.http import HttpResponse

        tasks = self.get_queryset()

        response = HttpResponse(content_type='text/csv')
        response.write(u'\ufeff'.encode('utf8'))
        response['Content-Disposition'] = 'attachment; filename="gorevler.csv"'

        writer = csv.writer(response)
        writer.writerow(['Başlık', 'Durum', 'Oluşturan', 'Atanan Kişi'])

        for task in tasks:
            writer.writerow([
                task.title,
                task.state.upper(),
                task.creator.username if task.creator else '',
                task.assignee.username if task.assignee else ''
            ])

        return response

# Yorumlar
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentOwnerOrAdmin]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# 1. Aşama: Giriş yapma ve OTP gönderme
class CustomObtainAuthToken(APIView):
    """
    1. Aşama Login: Kullanıcı adı ve parolayı doğrular.
    - Kriptografik olarak güvenli 6 haneli OTP üretir (secrets modülü).
    - OTP veritabanında make_password() ile hash'li saklanır.
    - IP/Kullanıcı başına rate limiting uygulanır.
    """
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'otp_request'

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            return Response({'detail': 'Girdiğiniz bilgiler hatalı.'}, status=status.HTTP_400_BAD_REQUEST)

        # Kriptografik olarak güvenli 6 haneli OTP üret
        otp = f"{secrets.randbelow(900000) + 100000:06d}"
        
        # OTP'yi veritabanında hash'li sakla ve sayacı sıfırla
        user.otp_code = make_password(otp)
        user.otp_created_at = timezone.now()
        user.otp_attempt_count = 0
        user.save()

        # E-posta & Telegram gönderme akışı
        email = user.email or 'user@example.com'
        try:
            send_mail(
                subject='Giriş Doğrulama Kodu (OTP)',
                message=f'Sayın {user.username},\n\nSisteme giriş yapmak için OTP kodunuz: {otp}\nBu kod 5 dakika geçerlidir.',
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@taskproject.com'),
                recipient_list=[email],
                fail_silently=True
            )
            send_telegram_otp(otp, user)
        except Exception as e:
            logger.error(f"OTP maili/telegram gönderilemedi: {e}")

        # Maskelenmiş e-posta hazırlığı
        email_parts = email.split('@') if '@' in email else [email, '']
        masked_email = f"{email_parts[0][:2]}***@{email_parts[1]}" if len(email_parts[0]) > 2 else email

        return Response({
            'otp_required': True,
            'user_id': user.id,
            'email': masked_email,
            'message': 'OTP doğrulama kodu e-posta adresinize gönderildi.'
        })

# 2. Aşama: OTP Doğrulama ve Token Alma
class VerifyOTPView(APIView):
    """
    2. Aşama Login: OTP Doğrulama ve DRF Token teslimi.
    - Race condition önlemek için transaction.atomic() ve select_for_update() kullanır.
    - OTP kontrolü check_password() ile güvenli biçimde yapılır.
    - Hatalı, eksik veya süresi dolmuş isteklerde tek tip hata mesajı döndürülür.
    - 5 hatalı denemede OTP otomatik olarak iptal edilir.
    """
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'otp_verify'

    def _clear_otp(self, user):
        user.otp_code = None
        user.otp_created_at = None
        user.otp_attempt_count = 0
        user.save()

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        otp_code = request.data.get('otp_code')
        generic_error = Response({'detail': 'Girdiğiniz bilgiler hatalı.'}, status=status.HTTP_400_BAD_REQUEST)

        if not user_id or not otp_code:
            return generic_error

        try:
            with transaction.atomic():
                user = User.objects.select_for_update().get(pk=user_id)

                # 1. OTP veya oluşturulma tarihi yoksa
                if not user.otp_code or not user.otp_created_at:
                    self._clear_otp(user)
                    return generic_error

                # 2. 5 Dakikalık zaman aşımı kontrolü
                if timezone.now() - user.otp_created_at > timedelta(minutes=5):
                    self._clear_otp(user)
                    return generic_error

                # 3. Maksimum deneme sayısı aşılmışsa
                if (user.otp_attempt_count or 0) >= 5:
                    self._clear_otp(user)
                    return generic_error

                # 4. Hash doğrulaması (check_password)
                if not check_password(str(otp_code).strip(), user.otp_code):
                    user.otp_attempt_count = (user.otp_attempt_count or 0) + 1
                    if user.otp_attempt_count >= 5:
                        self._clear_otp(user)
                    else:
                        user.save(update_fields=['otp_attempt_count'])
                    return generic_error

                # OTP Doğrulandı: OTP alanlarını temizle ve token teslim et
                self._clear_otp(user)
                token, created = Token.objects.get_or_create(user=user)

                return Response({
                    'token': token.key,
                    'user_id': user.pk,
                    'username': user.username,
                    'email': user.email,
                    'is_staff': user.is_staff
                })
        except User.DoesNotExist:
            return generic_error

# Şifremi Unuttum (6 Haneli OTP Kod Üretimi)
class ForgotPasswordView(APIView):
    """
    Şifremi Unuttum Endpoint'i.
    - User Enumeration engellemek için e-posta sistemde kayıtlı olmasa bile aynı başarılı yanıtı döner.
    - secrets.randbelow() ile 6 haneli OTP üretir ve make_password() ile hash'ler.
    """
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'otp_request'

    def post(self, request):
        email = request.data.get('email')
        success_response = Response({
            'message': 'Şifre sıfırlama kodu e-posta adresinize gönderildi.'
        })

        if not email:
            return Response({'detail': 'Girdiğiniz bilgiler hatalı.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if user:
            reset_code = f"{secrets.randbelow(900000) + 100000:06d}"
            user.otp_code = make_password(reset_code)
            user.otp_created_at = timezone.now()
            user.otp_attempt_count = 0
            user.save()

            try:
                send_mail(
                    subject='Şifre Sıfırlama Kodu',
                    message=f'Merhaba {user.username},\n\nŞifrenizi güncellemek için doğrulama kodunuz: {reset_code}\nBu kod 5 dakika geçerlidir.',
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@taskproject.com'),
                    recipient_list=[user.email],
                    fail_silently=True
                )
                send_telegram_otp(reset_code, user)
            except Exception as e:
                logger.error(f"Şifre sıfırlama maili/telegram gönderilemedi: {e}")

        return success_response

# Şifre Sıfırlama (OTP Hash Kontrolü ve Yeni Parola Atama)
class ResetPasswordView(APIView):
    """
    Şifre Sıfırlama Endpoint'i.
    - E-posta, reset_code ve new_password doğrulaması yapar.
    - Race condition engellemek için select_for_update() kullanır.
    - set_password() ile yeni parolayı hash'ler.
    """
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'otp_verify'

    def _clear_otp(self, user):
        user.otp_code = None
        user.otp_created_at = None
        user.otp_attempt_count = 0
        user.save(update_fields=['otp_code', 'otp_created_at', 'otp_attempt_count'])

    def post(self, request):
        email = request.data.get('email')
        reset_code = request.data.get('reset_code')
        new_password = request.data.get('new_password')
        generic_error = Response({'detail': 'Girdiğiniz bilgiler hatalı.'}, status=status.HTTP_400_BAD_REQUEST)

        if not email or not reset_code or not new_password:
            return generic_error

        user = User.objects.filter(email=email).first()
        if not user:
            return generic_error

        try:
            with transaction.atomic():
                user = User.objects.select_for_update().get(pk=user.pk)

                if not user.otp_code or not user.otp_created_at:
                    self._clear_otp(user)
                    return generic_error

                if timezone.now() - user.otp_created_at > timedelta(minutes=5):
                    self._clear_otp(user)
                    return generic_error

                if (user.otp_attempt_count or 0) >= 5:
                    self._clear_otp(user)
                    return generic_error

                if not check_password(str(reset_code).strip(), user.otp_code):
                    user.otp_attempt_count = (user.otp_attempt_count or 0) + 1
                    if user.otp_attempt_count >= 5:
                        self._clear_otp(user)
                    else:
                        user.save(update_fields=['otp_attempt_count'])
                    return generic_error

                try:
                    validate_password_policy(new_password)
                except Exception as e:
                    detail_msg = str(e.detail[0] if isinstance(e.detail, list) else e.detail)
                    return Response({'detail': detail_msg}, status=status.HTTP_400_BAD_REQUEST)

                user.set_password(new_password)
                user.otp_code = None
                user.otp_created_at = None
                user.otp_attempt_count = 0
                user.save()

                return Response({'message': 'Şifreniz başarıyla güncellendi. Yeni şifrenizle giriş yapabilirsiniz.'})
        except User.DoesNotExist:
            return generic_error

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'ok'})

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'ok'})

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, context={'request': request})
        # BE -> FE Şifreli Gönderim
        return Response(encrypt_data(serializer.data))

    def patch(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def put(self, request):
        return self.patch(request)

class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]

# Sadece Admin'in görebileceği HTTP Request Logs ViewSet
class RequestLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RequestLog.objects.all()
    serializer_class = RequestLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'ip_address', 'endpoint', 'method', 'status_code', 'user_agent']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # İsteğe bağlı URL parametre filtreleri (method, status_code)
        method_param = request.query_params.get('method')
        if method_param:
            queryset = queryset.filter(method__iexact=method_param)

        status_param = request.query_params.get('status_code')
        if status_param and status_param.isdigit():
            queryset = queryset.filter(status_code=int(status_param))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(encrypt_data(serializer.data))

        serializer = self.get_serializer(queryset, many=True)
        # BE -> FE Şifreli Gönderim
        return Response(encrypt_data(serializer.data))