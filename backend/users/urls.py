from django.urls import path
from .views import UserRegistrationView, UserProfileView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('profile/<str:username>/', UserProfileView.as_view(), name='user-profile-detail'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]
