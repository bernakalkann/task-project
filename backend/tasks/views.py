from rest_framework import viewsets, filters, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .models import User, Task, Comment, Notification, UserProfile
from .serializers import UserSerializer, TaskSerializer, CommentSerializer, NotificationSerializer, UserProfileSerializer
from .permissions import IsCommentOwnerOrAdmin

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
    
    # İZİN AYARI: İsteklerin token ile gelmesi şart
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Eğer kullanıcı giriş yapmadıysa (hata durumu), boş liste dön
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

    # Özet endpoint'i
    @action(detail=False, methods=['get'])
    def summary(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Giriş yapmalısınız"}, status=403)
            
        if request.user.is_staff:
            tasks = Task.objects.all()
        else:
            tasks = Task.objects.filter(assignee=request.user)
        
        data = {
            'todo': tasks.filter(state='to do').count(),
            'in_progress': tasks.filter(state='in progress').count(),
            'done': tasks.filter(state='done').count(),
        }
        return Response(data)

    # Excel (CSV) olarak dışa aktar
    @action(detail=False, methods=['get'])
    def export_excel(self, request):
        import csv
        from django.http import HttpResponse

        # Giriş yapmış kullanıcının görmeye yetkili olduğu görevleri çek
        tasks = self.get_queryset()

        response = HttpResponse(content_type='text/csv')
        # Türkçe karakter uyumluluğu için UTF-8 BOM ekliyoruz
        response.write(u'\ufeff'.encode('utf8'))
        response['Content-Disposition'] = 'attachment; filename="gorevler.csv"'

        writer = csv.writer(response)
        # Sütun başlıkları
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

class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff
        })
    


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Sadece giriş yapmış kullanıcının bildirimlerini getir
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'ok'})

from rest_framework.views import APIView

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)

    def patch(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def put(self, request):
        return self.patch(request)