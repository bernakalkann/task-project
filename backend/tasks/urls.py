from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TaskViewSet, CommentViewSet, NotificationViewSet, UserViewSet, 
    CustomObtainAuthToken, VerifyOTPView, ForgotPasswordView, ResetPasswordView, 
    ProfileView, AttachmentViewSet, RequestLogViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'comments', CommentViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'attachments', AttachmentViewSet)
router.register(r'logs', RequestLogViewSet, basename='request-log')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', ProfileView.as_view(), name='user-profile'),
    path('login/', CustomObtainAuthToken.as_view(), name='api_token_auth'),
    path('login/verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
]