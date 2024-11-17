from django.urls import path
from .views import UserRegistrationView, UserProfileView, LoginView, LogoutView, UserDeleteView, VerifyEmailView, PasswordResetConfirmView, PasswordResetRequestView, TwoFactorSetupView, TwoFactorVerifyView, TwoFactorVerifySetupView, TwoFactorDeleteView, SendFriendRequestView, AcceptFriendRequestView, DeclineFriendRequestView, GetFriends, CancelFriendRequestView, DeleteFriendshipView, GetSentFriendRequests, GetReceivedFriendRequests
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('profile/<str:username>/', UserProfileView.as_view(), name='user-profile-detail'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('signin/', LoginView.as_view(), name='token_obtain_pair'),
    path('delete/', UserDeleteView.as_view(), name='user_delete'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify-email/<int:uid>/<str:token>/', VerifyEmailView.as_view(), name='email-verify'),
    path('password-reset/', PasswordResetRequestView.as_view(), name="password-reset"),
    path('password-reset-confirm/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path('tfa/setup/', TwoFactorSetupView.as_view(), name="2fa_setup"),
    path('tfa/verify/', TwoFactorVerifyView.as_view(), name="2fa_verify"),
    path('tfa/verify-setup/', TwoFactorVerifySetupView.as_view(), name="2fa_verify_setup"),
    path('tfa/delete/', TwoFactorDeleteView.as_view(), name="2fa_delete"),

    path('friend-request/send/', SendFriendRequestView.as_view(), name='send_friend_request'),
    path('friend-request/accept/', AcceptFriendRequestView.as_view(), name='accept_friend_request'),
    path('friend-request/decline/', DeclineFriendRequestView.as_view(), name='decline_friend_request'),
    path('friend-request/cancel/', CancelFriendRequestView.as_view(), name='cancel_friend_request'),
    path('friend-request/delete/', DeleteFriendshipView.as_view(), name='delete_friendship'),
    path('friends/', GetFriends.as_view(), name='friends_list'),
    path('friend-request/sent/', GetSentFriendRequests.as_view(), name='sent_friendship_list'),
    path('friend-request/received/', GetReceivedFriendRequests.as_view(), name='received_friendship_list'),
]
