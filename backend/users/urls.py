from django.urls import path
from .views import UserRegistrationView, UserProfileView, CustomTokenObtainPairView, LogoutView, VerifyEmailView, PasswordResetConfirmView, PasswordResetRequestView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('profile/<str:username>/', UserProfileView.as_view(), name='user-profile-detail'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('signin/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify-email/<int:uid>/<str:token>/', VerifyEmailView.as_view(), name='email-verify'),
    path('password-reset/', PasswordResetRequestView.as_view(), name="password-reset"),
    path('password-reset-confirm/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(), name="password-reset-confirm")
]
