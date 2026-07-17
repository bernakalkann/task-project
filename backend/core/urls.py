from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tasks.views import UserViewSet, TaskViewSet, CommentViewSet 
from rest_framework.authtoken.views import obtain_auth_token # <--- Bunu ekle

# Router otomatik olarak GET, POST, PUT, DELETE URL'lerini oluşturur
router = DefaultRouter()

# /api/users/ URL'lerini UserViewSet'e bağla
router.register(r'users', UserViewSet)
# /api/tasks/ URL'lerini TaskViewSet'e bağla
router.register(r'tasks', TaskViewSet, basename='task')
# /api/comments/ URL'lerini CommentViewSet'e bağla
router.register(r'comments', CommentViewSet)

urlpatterns = [
    # Django admin paneline giriş
    path('admin/', admin.site.urls),
    # Tüm API endpointlerini /api/ önekiyle dahil et
    path('api/', include(router.urls)),
    path('api/login/', obtain_auth_token),
    # DRF'in kendi giriş/çıkış sayfası (geliştirme aşamasında çok işe yarar)
    path('api-auth/', include('rest_framework.urls')),
]