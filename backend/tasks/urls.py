from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, CommentViewSet, NotificationViewSet, UserViewSet, CustomObtainAuthToken, ProfileView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'comments', CommentViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', ProfileView.as_view(), name='user-profile'),
    path('login/', CustomObtainAuthToken.as_view(), name='api_token_auth'),
]