from rest_framework import status, generics, permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer, UserProfileSerializer
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomTokenObtainPairSerializer, FriendRequestSerializer, AcceptFriendRequestSerializer, DeleteFriendRequestSerializer, GetFriendsSerializer
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from .permissions import IsVerified
from datetime import timedelta
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django_otp.plugins.otp_totp.models import TOTPDevice
from .models import TranscendenceUser, FriendRequest
from django.db.models import Q

User = get_user_model()

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        existing_user = User.objects.filter(email=email, is_verified=False).first()

        if existing_user:
            expiration_period = timedelta(days=3)
            if existing_user.date_joined + expiration_period < timezone.now():
                existing_user.delete()

        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            user.save()

            token = default_token_generator.make_token(user)
            verification_url = request.build_absolute_uri(
                reverse('email-verify', args=[user.pk, token])
            )

            send_mail(
                subject="Verify Your Email",
                message=f"Please Click The link to verify your email: {verification_url}",
                from_email=settings.DEFAULT_FROM_MAIL,
                recipient_list=[user.email],
            )

            return Response({"detail": "Registration successful. Please check your email to verify your account."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsVerified]

    def get_object(self):
        username = self.kwargs.get('username')

        if username:
            try:
                return User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"Details": "User Not Found."}, status=status.HTTP_404_NOT_FOUND)
            
        return self.request.user

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance != request.user:
            return Response({"Details": "You do not have permission to edit this profile."}, status=status.HTTP_401_UNAUTHORIZED)
        
        return super().update(request, *args, **kwargs)
    

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.two_factor_enabled:
                request.session['temp_user_id'] = user.id
                return Response({"detail": "2FA required"}, status=status.HTTP_202_ACCEPTED)
            
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            })
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
class UserDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user

        user.delete()
        return Response({"detail": "Your account has been deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uid, token):
        user = get_object_or_404(User, pk=uid)

        if default_token_generator.check_token(user, token):
            user.is_verified = True
            user.is_active = True
            user.save()
            return render(request, 'email_verify_success.html', status=status.HTTP_200_OK)
        else:
            return render(request, 'email_verify_invalid_token.html', status=status.HTTP_400_BAD_REQUEST)
        
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get('identifier')
        try:
            user = User.objects.filter(email=identifier).first() or User.objects.filter(username=identifier).first()

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            reset_url = request.build_absolute_uri(
                reverse('password-reset-confirm', args=[uid, token])
            )
            send_mail(
                subject="Password Reset Request",
                message=f"Please click the link to reset your password : {reset_url}",
                from_email=settings.DEFAULT_FROM_MAIL,
                recipient_list=[user.email],
            )

            return Response({"detail": "Password reset email has been sent."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "Password reset email has been sent."}, status=status.HTTP_200_OK)
        


User = get_user_model()

class PasswordResetConfirmView(APIView):
    class PasswordResetConfirmSerializer(serializers.Serializer):
        new_password = serializers.CharField(write_only=True)
        confirm_password = serializers.CharField(write_only=True)

        def validate(self, data):
            if data['new_password'] != data['confirm_password']:
                raise serializers.ValidationError("Passwords do not match.")
            
            try:
                validate_password(data['new_password'])
            except ValidationError as e:
                raise serializers.ValidationError({"new_password": e.messages})
            return data

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            if not default_token_generator.check_token(user, token):
                return render(request, 'password_reset_invalid_token.html', status=status.HTTP_400_BAD_REQUEST)
            
            return render(request, 'password_reset_confirm.html', context={'uidb64': uidb64, 'token': token})
        
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return render(request, 'password_reset_error.html', status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if not default_token_generator.check_token(user, token):
                return render(request, 'password_reset_invalid_token.html', status=status.HTTP_400_BAD_REQUEST)

            serializer = self.PasswordResetConfirmSerializer(data=request.data)
            if serializer.is_valid():
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return render(request, 'password_reset_success.html', status=status.HTTP_200_OK)
            
            return render(request, 'password_reset_confirm.html', context={'errors': serializer.errors, 'uidb64': uidb64, 'token': token}, status=status.HTTP_400_BAD_REQUEST)
        
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return render(request, 'password_reset_error.html', status=status.HTTP_400_BAD_REQUEST)


class TwoFactorSetupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.two_factor_enabled:
            return Response({"error": "Already 2FA Enabled"}, status=status.HTTP_400_BAD_REQUEST)
        device, created = TOTPDevice.objects.get_or_create(user=user, confirmed=False)

        qr_code_url = device.config_url

        return Response({"qr_code_url": qr_code_url}, status=status.HTTP_200_OK)
    
class TwoFactorVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        otp_code = request.data.get("otp_code")

        if not username:
             return Response({"error": "No username found in request"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(username=username)
            device = TOTPDevice.objects.get(user=user, confirmed=True)

            if device.verify_token(otp_code):
                refresh = RefreshToken.for_user(user)

                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid OTP code"}, status=status.HTTP_400_BAD_REQUEST)
        except (TranscendenceUser.DoesNotExist, TOTPDevice.DoesNotExist) as e:
            print(e)
            return Response({"error": "Invalid user or no 2FA setup found"}, status=status.HTTP_404_NOT_FOUND)

class TwoFactorVerifySetupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        otp_code = request.data.get("otp_code")

        try:
            device = TOTPDevice.objects.get(user=user, confirmed=False)

            if device.verify_token(otp_code):
                device.confirmed = True
                device.save()
                user.two_factor_enabled = True  
                user.save()

                return Response({"status": "2FA setup confirmed successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid OTP code for setup"}, status=status.HTTP_400_BAD_REQUEST)
        except TOTPDevice.DoesNotExist:
            return Response({"error": "No unconfirmed 2FA device found"}, status=status.HTTP_404_NOT_FOUND)


class TwoFactorDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        try:
            device = TOTPDevice.objects.get(user=user, confirmed=True)
            device.delete()
            user.two_factor_enabled = False
            user.save()
            return Response({"status": "2FA disabled successfully"}, status=status.HTTP_200_OK)
        except TOTPDevice.DoesNotExist:
            return Response({"error": "No 2FA device found"}, status=status.HTTP_404_NOT_FOUND)

# Friend Requests
class SendFriendRequestView(generics.CreateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        receiver_username=request.data.get("receiver")
        if not receiver_username:
            return Response({"error": "receiver Username is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        receiver = get_object_or_404(User, username=receiver_username)

        if FriendRequest.objects.filter(sender=request.user, receiver=receiver).exists() or \
           FriendRequest.objects.filter(sender=receiver, receiver=request.user).exists():
            return Response({"error": "A friend request already exists between you and this user."},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.user == receiver:
            return Response({"error": "You cannot send a friend request to yourself."},
                            status=status.HTTP_400_BAD_REQUEST)

        friend_request = FriendRequest.objects.create(sender=request.user, receiver=receiver)
        serializer = self.get_serializer(friend_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class AcceptFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AcceptFriendRequestSerializer(data=request.data)
        if serializer.is_valid():
            friend_request = serializer.validated_data['friend_request_id']

            if friend_request.receiver != request.user:
                return Response({"error": "You can only accept requests sent to you."}, status=status.HTTP_403_FORBIDDEN)
            
            friend_request.accept()
            return Response({"status": "Friend request accepted"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class DeclineFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AcceptFriendRequestSerializer(data=request.data)
        if serializer.is_valid():
            friend_request = serializer.validated_data['friend_request_id']

            if friend_request.receiver != request.user:
                return Response({"error": "You can only decline requests sent to you."}, status=status.HTTP_403_FORBIDDEN)
            
            friend_request.delete()

            return Response({"status": "Friend request decline"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CancelFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AcceptFriendRequestSerializer(data=request.data)
        if serializer.is_valid():
            friend_request = serializer.validated_data['friend_request_id']

            # print(friend_request.sender + '|')
            # print(request.user.username + "|")
            if friend_request.sender != request.user:
                return Response({"error": "You can only Cancel friend requests you sent."}, status=status.HTTP_403_FORBIDDEN)
            
            friend_request.delete()
            
            return Response({"status": "Friend request cancelled"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteFriendshipView(APIView):
    """
    Deletes a friendship between the authenticated user and another user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        serializer = DeleteFriendRequestSerializer(data=request.data)
        if serializer.is_valid():
            # Get the friend user by username
            friend_request = serializer.validated_data['friend_request_id']


            if not friend_request:
                return Response({"error": "Friendship does not exist."}, status=status.HTTP_404_NOT_FOUND)

            # Delete the friendship
            friend_request.delete()

            return Response({"status": "Friendship successfully deleted."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class GetFriends(generics.ListAPIView):
    serializer_class = GetFriendsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return FriendRequest.objects.filter(
        (Q(sender=user) & Q(accepted=True)) | (Q(receiver=user) & Q(accepted=True)))
    

class GetSentFriendRequests(generics.ListAPIView):
    serializer_class = GetFriendsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return  (FriendRequest.objects.filter(accepted=False, sender=user))
    
class GetReceivedFriendRequests(generics.ListAPIView):
    serializer_class = GetFriendsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return  FriendRequest.objects.filter(accepted=False, receiver=user)