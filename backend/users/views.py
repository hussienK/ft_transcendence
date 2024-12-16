from rest_framework import status, generics, permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer, UserProfileSerializer
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserStatsSerializer, FriendRequestSerializer, AcceptFriendRequestSerializer, DeleteFriendRequestSerializer, GetFriendsSerializer, FeedUpdateSerializer, MatchHistorySerializer
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
from .models import TranscendenceUser, FriendRequest, FeedUpdate
from game.models import MatchHistory
from django.db.models import Q
import re
from django.core.validators import validate_email
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .permissions import IsVerified
from rest_framework_simplejwt.tokens import AccessToken
from django.core.exceptions import ValidationError
from .tasks import send_update_to_user_sync
from .utils import get_user_stats
from rest_framework.parsers import MultiPartParser, FormParser

User = get_user_model()

### Token Verification View ###
class TokenVerifyView(APIView):
    '''Called by Frontend to verify if a Token is available or no'''
    permission_classes = [permissions.IsAuthenticated, IsVerified]

    def post(self, request):
        return Response({"detail": "Success!"}, status=status.HTTP_200_OK)

### User Registration View ###
class UserRegistrationView(APIView):
    '''Lets User Register to Website'''
    permission_classes = [AllowAny]

    def post(self, request):
        #Matches with email
        email = request.data.get("email")
        existing_user = User.objects.filter(email=email, is_verified=False).first()

        #if a user with email exists and isn't verified yet for a certain time, it delete the old account or asks user to verify
        if existing_user:
            expiration_period = timedelta(days=3)
            if existing_user.date_joined + expiration_period < timezone.now():
                existing_user.delete()
            else:
                return Response({"error": "Please Verify This Email First"}, status=status.HTTP_401_UNAUTHORIZED)

        #password regex enforces secuirity measures
        password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%?&_-])[A-Za-z\d@$!%?&_-]{8,}$'
        
        if not re.match(password_regex, request.data.get("password")):
            return Response({"error": "Password does not meet complexity requirements."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        # Validates the Data
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            user.save()

            # Generate Verify Email and sends the email
            token = default_token_generator.make_token(user)
            verification_url = f"{request.scheme}://{request.get_host().split(':')[0]}:8443{reverse('email-verify', args=[user.pk, token])}"
            # only if in development
            print("Email Verify Link: ", {verification_url})
            send_mail(
                subject="Verify Your Email",
                message=f"Please Click The link to verify your email: {verification_url}",
                from_email=settings.DEFAULT_FROM_MAIL,
                recipient_list=[user.email],
            )
            return Response({"detail": "Registration successful. Please check your email to verify your account."}, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors[next(iter(serializer.errors))]}, status=status.HTTP_400_BAD_REQUEST)

### User Profile View ###
class UserProfileView(generics.RetrieveUpdateAPIView):
    '''Allows users to view profiles or update theirs'''
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsVerified]
    parser_classes = [MultiPartParser, FormParser]

    # returns the object based on username or the current user if no username
    def get_object(self):
        username = self.kwargs.get('username')

        if username:
            # Let `get_object_or_404` handle non-existent users
            return get_object_or_404(User, username=username)

        # Default to the current user if no username is provided
        return self.request.user


    # updates a user
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance != request.user:
            return Response(
                {"detail": "You do not have permission to edit this profile."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Debug the incoming data
        print(f"Incoming data: {request.data}")

        try:
            # Perform the update using the serializer
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)  # Trigger validation errors if present

            # Debug the validated data
            print(f"Validated data: {serializer.validated_data}")

            # Save the updated instance
            self.perform_update(serializer)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            print(f"EXCEPTION: {e}")  # Corrected exception printing
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Unexpected Error: {e}")
            return Response({"error": f"{e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
### A view For Logging IN ###
class LoginView(APIView):
    skip_otp_verification = True

    '''Let's users login to our website'''
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        #get the credentials
        identifier = request.data.get('username')
        password = request.data.get('password')

        #enforce regex on password
        try:
            password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%?&_-])[A-Za-z\d@$!%?&_-]{8,}$'
            
            if not re.match(password_regex, password):
                return Response({"error": "Password does not meet complexity requirements."}, 
                                status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"error": "Invalid Credentials"}, 
                        status=status.HTTP_401_UNAUTHORIZED)

        user_instance = None

        # tries to get user either through their name or email
        try:
            validate_email(identifier)
            is_email = True
        except ValidationError:
            is_email = False

        if is_email:
            try:
                user_instance = User.objects.get(email=identifier)
                username = user_instance.username
            except User.DoesNotExist:
                return Response({"error": "Invalid Credentials"}, 
                                status=status.HTTP_401_UNAUTHORIZED)
        else:
            username = identifier
            try:
                user_instance = User.objects.get(username=identifier)
            except User.DoesNotExist:
                return Response({"error": "Invalid Credentials"}, 
                                status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(request, username=username, password=password)
        
        # if there is a user redirects to 2FA response instead of loggin in
        if user is not None:
            if user.two_factor_enabled:
                request.session['temp_user_id'] = user.id
                return Response({"detail": "2FA required"}, status=status.HTTP_202_ACCEPTED)
            
            # creates the tokens and returns them
            user_logged_in.send(sender=user.__class__, request=request, user=user)
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "userInfo": {
                    "username": user_instance.username,
                    "email": user_instance.email,
                    "display_name": user_instance.display_name                   
                }
            })
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """Logs the user out by blacklisting their Refresh Token."""
    def post(self, request):
        try:
            # Safely access the 'refresh' token in the request data
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'error': 'Refresh token is missing.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            # Signal user logout
            user_logged_out.send(sender=request.user.__class__, request=request, user=request.user)
            
            return Response(status=status.HTTP_205_RESET_CONTENT)
        
        except KeyError as e:
            return Response({'error': f'Missing key: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Return the exception message as a string
            return Response({'error': e.error[next(iter(e.error))]}, status=status.HTTP_400_BAD_REQUEST)
        

### User Delete View ###
class UserDeleteView(APIView):
    '''Delete's a users account'''
    permission_classes = [permissions.IsAuthenticated, IsVerified]

    def delete(self, request):
        user = request.user

        user.delete()
        return Response({"detail": "Your account has been deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

### Email Verify View ###
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
        
### Password Reset View ###
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
            print("Password Reset Link: ", {reset_url})
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


# Friend Requests
class SendFriendRequestView(generics.CreateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsVerified]

    def post(self, request):
        auth_header = request.headers.get('Authorization')  # Preferred way
        # Alternatively (case-insensitive headers)
        # auth_header = request.META.get('HTTP_AUTHORIZATION')

        receiver_username=request.data.get("receiver")
        if not receiver_username:
            return Response({"error": "receiver Username is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            receiver = get_object_or_404(User, username=receiver_username)
        except:
            return Response({"error": "User Not Found."},
                            status=status.HTTP_404_NOT_FOUND)

        if FriendRequest.objects.filter(sender=request.user, receiver=receiver).exists() or \
           FriendRequest.objects.filter(sender=receiver, receiver=request.user).exists():
            return Response({"error": "A friend request already exists between you and this user."},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.user == receiver:
            return Response({"error": "You cannot send a friend request to yourself."},
                            status=status.HTTP_400_BAD_REQUEST)

        friend_request = FriendRequest.objects.create(sender=request.user, receiver=receiver)
        serializer = self.get_serializer(friend_request)
        send_update_to_user_sync(receiver_username, {"type": "feed", "sender_username": request.user.username, "sender_displayname": request.user.display_name, "info": "Sent you a friend request"})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class AcceptFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsVerified]

    def post(self, request):
        serializer = AcceptFriendRequestSerializer(data=request.data)
        if serializer.is_valid():
            friend_request = serializer.validated_data['friend_request_id']

            if friend_request.receiver != request.user:
                return Response({"error": "You can only accept requests sent to you."}, status=status.HTTP_403_FORBIDDEN)
            
            friend_request.accept()

            # Fetch the updated list of received friend requests
            received_requests = FriendRequest.objects.filter(
                accepted=False, receiver=request.user
            )
            response_serializer = GetFriendsSerializer(
                received_requests, many=True, context={"request": request}
            )
            send_update_to_user_sync(friend_request.sender, {"type": "feed", "sender_username": friend_request.receiver.username, "sender_displayname": friend_request.receiver.display_name, "info": "Accepted your friend request"})
            return Response({"status": "Friend request accepted", "friends": response_serializer.data}, status=status.HTTP_200_OK)
        return Response({'error': serializer.errors[next(iter(serializer.errors))]}, status=status.HTTP_400_BAD_REQUEST)

    
class DeclineFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsVerified]

    def post(self, request):
        serializer = AcceptFriendRequestSerializer(data=request.data)
        if serializer.is_valid():
            friend_request = serializer.validated_data['friend_request_id']

            if friend_request.receiver != request.user:
                return Response({"error": "You can only decline requests sent to you."}, status=status.HTTP_403_FORBIDDEN)
            
            friend_request.delete()


            # Fetch the updated list of received friend requests
            received_requests = FriendRequest.objects.filter(
                accepted=False, receiver=request.user
            )
            response_serializer = GetFriendsSerializer(
                received_requests, many=True, context={"request": request}
            )
            send_update_to_user_sync(friend_request.sender, {"type": "feed", "sender_username": friend_request.receiver.username, "sender_displayname": friend_request.receiver.display_name, "info": "Declined your friend request"})
            return Response({"status": "Friend request decline", "friends": response_serializer.data}, status=status.HTTP_200_OK)

        return Response({'error': serializer.errors[next(iter(serializer.errors))]}, status=status.HTTP_400_BAD_REQUEST)
    
class CancelFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsVerified]

    def post(self, request):
        serializer = AcceptFriendRequestSerializer(data=request.data)
        if serializer.is_valid():
            friend_request = serializer.validated_data['friend_request_id']

            if friend_request.sender != request.user:
                return Response({"error": "You can only Cancel friend requests you sent."}, status=status.HTTP_403_FORBIDDEN)
            
            friend_request.delete()
            
            # Fetch the updated list of received friend requests
            sent_requests = FriendRequest.objects.filter(
                accepted=False, sender=request.user
            )
            response_serializer = GetFriendsSerializer(
                sent_requests, many=True, context={"request": request}
            )
            send_update_to_user_sync(friend_request.receiver, {"type": "feed", "sender_username": friend_request.sender.username, "sender_displayname": friend_request.sender.display_name, "info": "Canceled their friend request to you"})
            return Response({"status": "Friend request cancelled", "friends": response_serializer.data}, status=status.HTTP_200_OK)

        return Response({'error': serializer.errors[next(iter(serializer.errors))]}, status=status.HTTP_400_BAD_REQUEST)

class DeleteFriendshipView(APIView):
    """
    Deletes a friendship between the authenticated user and another user.
    """
    permission_classes = [permissions.IsAuthenticated, IsVerified]

    def post(self, request):
        serializer = DeleteFriendRequestSerializer(data=request.data)
        if serializer.is_valid():
            # Get the friend user by username
            friend_request = serializer.validated_data['friend_request_id']


            if not friend_request:
                return Response({"error": "Friendship does not exist."}, status=status.HTTP_404_NOT_FOUND)

            # Delete the friendship
            friend_request.delete()

            # Fetch the updated list of received friend requests
            friends = FriendRequest.objects.filter(
                (Q(sender=request.user) & Q(accepted=True)) | (Q(receiver=request.user) & Q(accepted=True))
            )
            response_serializer = GetFriendsSerializer(
                friends, many=True, context={"request": request}
            )
            if (friend_request.sender == request.user):
                send_update_to_user_sync(friend_request.receiver, {"type": "feed", "sender_username": friend_request.sender.username, "sender_displayname": friend_request.sender.display_name, "info": "Unfriended you"})
            else:
                send_update_to_user_sync(friend_request.sender, {"type": "feed", "sender_username": friend_request.receiver.username, "sender_displayname": friend_request.receiver.display_name, "info": "Unfriended you"})
            return Response({"status": "Friendship successfully deleted.", "friends": response_serializer.data}, status=status.HTTP_200_OK)
        return Response({'error': serializer.errors[next(iter(serializer.errors))]}, status=status.HTTP_400_BAD_REQUEST)
    

class GetFriends(generics.ListAPIView):
    serializer_class = GetFriendsSerializer
    permission_classes = [permissions.IsAuthenticated, IsVerified]

    def get_queryset(self):
        user = self.request.user
        return FriendRequest.objects.filter(
        (Q(sender=user) & Q(accepted=True)) | (Q(receiver=user) & Q(accepted=True)))
    
class GetFriendsOnline(generics.ListAPIView):
    serializer_class = GetFriendsSerializer
    permission_classes = [permissions.IsAuthenticated, IsVerified]

    def get_queryset(self):
        user = self.request.user
        return FriendRequest.objects.filter(
        (Q(sender=user) & Q(accepted=True)) | (Q(receiver=user) & Q(accepted=True)))
    

class GetSentFriendRequests(generics.ListAPIView):
    serializer_class = GetFriendsSerializer
    permission_classes = [permissions.IsAuthenticated, IsVerified]

    def get_queryset(self):
        user = self.request.user
        return  (FriendRequest.objects.filter(accepted=False, sender=user))
    
class GetReceivedFriendRequests(generics.ListAPIView):
    serializer_class = GetFriendsSerializer
    permission_classes = [permissions.IsAuthenticated, IsVerified]

    def get_queryset(self):
        user = self.request.user
        return  FriendRequest.objects.filter(accepted=False, receiver=user)
    
class FeedUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsVerified]

    def get(self, request):
        user = request.user
        updates = FeedUpdate.objects.filter(user=user.username).order_by('created_at')[:10]
        serializer = FeedUpdateSerializer(updates, many=True)
        return Response(serializer.data)
    
class UserStatsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsVerified]

    def get(self, request, *args, **kwargs):
        username = self.kwargs.get('username', None)
        
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"detail": "User Not Found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user
        
        stats = get_user_stats(user)

        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)

    
class UserMatchHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        username = self.kwargs.get('username', None)

        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"detail": "User Not Found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user

        match_history = MatchHistory.objects.filter(
            game_session__player1=user
        ) | MatchHistory.objects.filter(
            game_session__player2=user
        )

        serializer = MatchHistorySerializer(match_history, many=True, context={'request': request})
        return Response(serializer.data)

class UserRankView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Ensure the user is authenticated

    def get_player_rank(self, user):
        all_users = User.objects.all()

        # Collect stats for all players
        results = []
        for player in all_users:
            stats = get_user_stats(player)
            total_games = stats['total_games']
            games_won = stats['games_won']
            points_scored = stats['points_scored']
            points_conceded = stats['points_conceded']

            # Calculate win ratio and points scored ratio
            win_ratio = (games_won / total_games * 100) if total_games > 0 else 0
            points_ratio = (
                (points_scored / (points_scored + points_conceded) * 100)
                if (points_scored + points_conceded) > 0
                else 0
            )

            obj = {
                'player': player.username,
                'player_id': player.id,
                'total_games': total_games,
                'games_won': games_won,
                'games_lost': stats['games_lost'],
                'points_scored': points_scored,
                'points_conceded': points_conceded,
                'win_ratio': win_ratio,
                'points_ratio': points_ratio,
            }
            results.append(obj)

        # Rank players based on points_scored, then win_ratio, then points_ratio
        ranked_results = sorted(
            results,
            key=lambda x: (x['points_scored'], x['win_ratio'], x['points_ratio'], -x['player_id']),
            reverse=True,  # Higher values should come first
        )

        # Determine rank of the current user
        rank = next(
            (index + 1 for index, obj in enumerate(ranked_results) if obj['player'] == user.username),
            None,
        )

        return {
            'rank': rank,
            'total_players': len(ranked_results),
        }

    def get(self, request):
        # Get the rank for the authenticated user
        user = request.user
        rank_info = self.get_player_rank(user)
        link = None
        if user.avatar:
            link = f"http://localhost:8080/{user.avatar.url}" 
        else:
            link = './assets/default_avatar.png'            
        return Response({
            'user': user.username,
            'avatar': link,
            'rank': rank_info['rank'],
            'total_players': rank_info['total_players'],
        })
