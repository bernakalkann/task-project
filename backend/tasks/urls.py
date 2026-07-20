from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, CommentViewSet, NotificationViewSet, UserViewSet, CustomObtainAuthToken

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'comments', CommentViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', CustomObtainAuthToken.as_view(), name='api_token_auth'),
]