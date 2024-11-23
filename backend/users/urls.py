from django.urls import path
from .views import (
    UserRegistrationView, UserProfileView, LoginView, LogoutView, UserDeleteView,
    VerifyEmailView, PasswordResetConfirmView, PasswordResetRequestView,
    SendFriendRequestView, AcceptFriendRequestView, DeclineFriendRequestView,
    GetFriends, CancelFriendRequestView, DeleteFriendshipView, GetFriendsOnline,
    GetSentFriendRequests, GetReceivedFriendRequests, TokenVerifyView
)
from rest_framework_simplejwt.views import TokenRefreshView

# Define URL patterns for the application
urlpatterns = [
    # User registration, profile, and authentication
    path('register/', UserRegistrationView.as_view(), name='user-register'),  # Register a new user
    path('profile/<str:username>/', UserProfileView.as_view(), name='user-profile-detail'),  # View user profile by username
    path('profile/', UserProfileView.as_view(), name='user-profile'),  # View/update own profile
    path('signin/', LoginView.as_view(), name='token_obtain_pair'),  # User login (JWT)
    path('delete/', UserDeleteView.as_view(), name='user_delete'),  # Delete user account
    path('logout/', LogoutView.as_view(), name='logout'),  # Logout user

    # JWT token operations
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh JWT token
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),  # Verify JWT token

    # Email verification
    path('verify-email/<int:uid>/<str:token>/', VerifyEmailView.as_view(), name='email-verify'),  # Email verification link

    # Password reset
    path('password-reset/', PasswordResetRequestView.as_view(), name="password-reset"),  # Request password reset
    path('password-reset-confirm/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(), name="password-reset-confirm"),  # Confirm password reset

    # Friend request operations
    path('friend-request/send/', SendFriendRequestView.as_view(), name='send_friend_request'),  # Send a friend request
    path('friend-request/accept/', AcceptFriendRequestView.as_view(), name='accept_friend_request'),  # Accept a friend request
    path('friend-request/decline/', DeclineFriendRequestView.as_view(), name='decline_friend_request'),  # Decline a friend request
    path('friend-request/cancel/', CancelFriendRequestView.as_view(), name='cancel_friend_request'),  # Cancel a sent friend request
    path('friends/unfriend/', DeleteFriendshipView.as_view(), name='delete_friendship'),  # Remove a friend

    # Friends list and friend request lists
    path('friends/', GetFriends.as_view(), name='friends_list'),  # List all friends
    path('friends/online/', GetFriendsOnline.as_view(), name='friends_list_online'),  # List all online friends
    path('friend-request/sent/', GetSentFriendRequests.as_view(), name='sent_friendship_list'),  # List sent friend requests
    path('friend-request/received/', GetReceivedFriendRequests.as_view(), name='received_friendship_list'),  # List received friend requests
]
