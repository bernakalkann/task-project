from rest_framework import viewsets, filters, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .models import User, Task, Comment
from .serializers import UserSerializer, TaskSerializer, CommentSerializer
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