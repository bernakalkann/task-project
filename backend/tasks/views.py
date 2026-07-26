import random
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from rest_framework import viewsets, filters, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from .models import User, Task, Comment, Notification, UserProfile, Attachment, RequestLog
from .serializers import (
    UserSerializer, TaskSerializer, CommentSerializer, NotificationSerializer, 
    UserProfileSerializer, AttachmentSerializer, RequestLogSerializer
)
from .permissions import IsCommentOwnerOrAdmin
from .validators import validate_password_policy
from .crypto_utils import encrypt_data

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
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Task.objects.none()
            
        if self.request.user.is_staff:
            return Task.objects.all()
        return Task.objects.filter(assignee=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            serializer.save(creator=self.request.user)
        else:
            serializer.save(creator=self.request.user, assignee=self.request.user)

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
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            # Şart: kullanıcı adı veya parolada tek tip hata mesajı
            return Response({'detail': 'girdiğiniz bilgiler hatalı'}, status=status.HTTP_400_BAD_REQUEST)

        # 6 haneli OTP üret
        otp = f"{random.randint(100000, 999999)}"
        user.otp_code = otp
        user.otp_created_at = timezone.now()
        user.save()

        # E-posta gönderme akışı (Terminal print + Django email backend)
        email = user.email or 'user@example.com'
        try:
            send_mail(
                subject='Giriş Doğrulama Kodu (OTP)',
                message=f'Sayın {user.username},\n\nSisteme giriş yapmak için OTP kodunuz: {otp}\nBu kod 5 dakika geçerlidir.',
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@taskproject.com'),
                recipient_list=[email],
                fail_silently=True
            )
        except Exception:
            pass
        
        # Terminale de print at
        print(f"\n==========================================")
        print(f"[OTP MAIL SENT] User: {user.username} | Email: {email} | OTP Code: {otp}")
        print(f"==========================================\n")

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
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        otp_code = request.data.get('otp_code')

        if not user_id or not otp_code:
            return Response({'detail': 'girdiğiniz bilgiler hatalı'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'girdiğiniz bilgiler hatalı'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.otp_code or user.otp_code != str(otp_code).strip():
            return Response({'detail': 'girdiğiniz bilgiler hatalı'}, status=status.HTTP_400_BAD_REQUEST)

        # 5 Dakika Süre Kontrolü
        if user.otp_created_at and (timezone.now() - user.otp_created_at > timedelta(minutes=5)):
            user.otp_code = None
            user.save()
            return Response({'detail': 'girdiğiniz bilgiler hatalı'}, status=status.HTTP_400_BAD_REQUEST)

        # OTP başarılı, sıfırla ve token üret
        user.otp_code = None
        user.save()

        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff
        })

# Şifremi Unuttum (6 Haneli Kod Gönderme - Yöntem 2)
class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'detail': 'E-posta adresi zorunludur.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if user:
            reset_code = f"{random.randint(100000, 999999)}"
            user.otp_code = reset_code
            user.otp_created_at = timezone.now()
            user.save()

            try:
                send_mail(
                    subject='Şifre Sıfırlama Kodu',
                    message=f'Merhaba {user.username},\n\nŞifrenizi güncellemek için doğrulama kodunuz: {reset_code}\nBu kod 5 dakika geçerlidir.',
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@taskproject.com'),
                    recipient_list=[user.email],
                    fail_silently=True
                )
            except Exception:
                pass

            print("\n" + "🔑 "*15)
            print(f"  🔐 [ŞİFRE SIFIRLAMA KODU / RESET CODE]")
            print(f"  Kullanıcı : {user.username}")
            print(f"  E-Posta   : {user.email}")
            print(f"  =====================================")
            print(f"  GİRİLECEK 6 HANELİ KOD: ===>  {reset_code}  <===")
            print("🔑 "*15 + "\n")

        return Response({
            'message': 'Şifre sıfırlama kodu e-posta adresinize gönderildi.',
            'email': email
        })

# Şifre Sıfırlama (6 Haneli Kod ve Yeni Şifre İle Sıfırlama - Yöntem 2)
class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        reset_code = request.data.get('reset_code')
        new_password = request.data.get('new_password')

        if not email or not reset_code or not new_password:
            return Response({'detail': 'E-posta, doğrulama kodu ve yeni şifre zorunludur.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user or not user.otp_code or user.otp_code != str(reset_code).strip():
            return Response({'detail': 'Doğrulama kodu hatalı veya geçersiz.'}, status=status.HTTP_400_BAD_REQUEST)

        # 5 Dakika Geçerlilik Kontrolü
        if user.otp_created_at and (timezone.now() - user.otp_created_at > timedelta(minutes=5)):
            user.otp_code = None
            user.save()
            return Response({'detail': 'Doğrulama kodunun süresi dolmuş.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password_policy(new_password)
        except Exception as e:
            return Response({'detail': str(e.detail[0] if isinstance(e.detail, list) else e.detail)}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.otp_code = None
        user.save()

        return Response({'message': 'Şifreniz başarıyla güncellendi. Yeni şifrenizle giriş yapabilirsiniz.'})

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