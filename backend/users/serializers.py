from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import TranscendenceUser, FriendRequest, FeedUpdate
from game.models import MatchHistory
from django.conf import settings
from urllib.parse import urlparse
from django.utils.timezone import now

User = get_user_model()

# Serializer for user registration
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])  # Password with validation
    password2 = serializers.CharField(write_only=True, required=True)  # Confirm password field

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'display_name')

    # Custom validation for passwords, username, display name, and email uniqueness
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match"})
        if len(attrs['username']) < settings.FORM_SETTINGS['username_length_min']:
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        if len(attrs['username']) > settings.FORM_SETTINGS['username_length_max']:
            raise serializers.ValidationError("Username can't be more than 15 characters long.")
    
        if len(attrs['display_name']) < settings.FORM_SETTINGS['displayname_length_min']:
            raise serializers.ValidationError("Display Name must be at least 3 characters long.")
        if len(attrs['display_name']) > settings.FORM_SETTINGS['displayname_length_max']:
            raise serializers.ValidationError("Display Name can't be more than 15 characters long.")

        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("This email is already associated with another account.")
        return attrs
    
    # Create a new user using the validated data
    def create(self, validated_data):
        validated_data.pop('password2')  # Remove the confirm password field
        user = User.objects.create_user(**validated_data)
        return user
from rest_framework import serializers
from urllib.parse import urlparse

class UserProfileSerializer(serializers.ModelSerializer):
    editable = serializers.SerializerMethodField()
    avatar = serializers.ImageField(required=False)  # Allow file uploads

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'display_name',
            'bio',
            'avatar',  # Include avatar for both read and write
            'created_at',
            'two_factor_enabled',
            "is_online",
            "editable"
        )
        read_only_fields = ('id', 'username', 'email', 'created_at', "is_online", "editable")

    def get_editable(self, obj):
        request = self.context.get('request')
        return request.user == obj

    # Return the full URL of the avatar
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Generate the full avatar URL
        if instance.avatar:
            avatar_url = instance.avatar.url if hasattr(instance.avatar, 'url') else instance.avatar
            representation['avatar'] = f"http://localhost:8080{avatar_url}"
        else:
            representation['avatar'] = "./assets/default_avatar.png"  # Default avatar URL

        # Hide the email field if the user is not viewing their own profile
        request = self.context.get('request')
        if request.user != instance:
            representation.pop('email', None)

        return representation

    # Validate the avatar field
    def validate_avatar(self, value):
        max_size = 2 * 1024 * 1024  # 2MB
        if value.size > max_size:
            raise serializers.ValidationError("Avatar image size cannot exceed 2MB.")
        if not value.content_type.startswith("image/"):
            raise serializers.ValidationError("Uploaded file must be an image.")
        return value

    # Other validations
    def validate_username(self, value):
        if len(value) < settings.FORM_SETTINGS['username_length_min']:
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        if len(value) > settings.FORM_SETTINGS['username_length_max']:
            raise serializers.ValidationError("Username can't be more than 15 characters long.")
        return value
    
    def validate_display_name(self, value):
        if len(value) < settings.FORM_SETTINGS['displayname_length_min']:
            raise serializers.ValidationError("Display Name must be at least 3 characters long.")
        if len(value) > settings.FORM_SETTINGS['displayname_length_max']:
            raise serializers.ValidationError("Display Name can't be more than 15 characters long.")
        return value

    def validate_bio(self, value):
        if len(value) > settings.FORM_SETTINGS['bio_length_max']:
            raise serializers.ValidationError("Bio can't be more than 150 characters long.")
        return value

    def validate_email(self, value):
        user = self.context.get('request').user
        if User.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("This email is already associated with another account.")
        return value


# Custom serializer for JWT token generation
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get("username")

        # Ensure user is verified
        try:
            user = User.objects.get(username=username) if username else None
            if not user:
                user = User.objects.get(email=username) if username else None
        except:
            user = None
        if user and not user.is_verified:
            raise serializers.DjangoValidationError("Your account is not verified. Please check your email for verification instructions.")

        # Generate token and add extra user data
        data = super().validate(attrs)
        data.update(
            {
                'username': self.user.username,
                'display_name': self.user.display_name,
            }
        )
        return data

# Serializer for friend request management
class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'created_at', 'accepted']
        read_only_fields = ['id', 'created_at', 'accepted']

# Serializer for accepting a friend request
class AcceptFriendRequestSerializer(serializers.Serializer):
    friend_request_id = serializers.IntegerField()

    # Ensure the friend request exists and isn't already accepted
    def validate_friend_request_id(self, value):
        try:
            friend_request = FriendRequest.objects.get(id=value)
            if friend_request.accepted:
                raise serializers.ValidationError("Friend request already accepted.")
        except FriendRequest.DoesNotExist:
            raise serializers.ValidationError("Friend request does not exist.")
        return friend_request

# Serializer for deleting a friend request
class DeleteFriendRequestSerializer(serializers.Serializer):
    friend_request_id = serializers.IntegerField()

    # Ensure the friend request exists and has been accepted
    def validate_friend_request_id(self, value):
        try:
            friend_request = FriendRequest.objects.get(id=value)
            if not friend_request.accepted:
                raise serializers.ValidationError("Friend request not accepted.")
        except FriendRequest.DoesNotExist:
            raise serializers.ValidationError("Friend request does not exist.")
        return friend_request

# Serializer for listing friends
class GetFriendsSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = FriendRequest
        fields = ['id', 'display_name', 'username', 'avatar', 'created_at']

    # Get the friend's display name
    def get_display_name(self, obj):
        request_user = self.context['request'].user
        friend_user = obj.receiver if obj.sender == request_user else obj.sender
        return friend_user.display_name

    # Get the friend's username
    def get_username(self, obj):
        request_user = self.context['request'].user
        friend_user = obj.receiver if obj.sender == request_user else obj.sender
        return friend_user.username

    # Get the friend's avatar URL
    def get_avatar(self, obj):
        request_user = self.context['request'].user
        friend_user = obj.receiver if obj.sender == request_user else obj.sender
        return friend_user.avatar.url if friend_user.avatar else "./assets/default_avatar.png"


class FeedUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedUpdate
        fields = ['sender_username', 'sender_displayname', 'info', 'created_at']

class UserStatsSerializer(serializers.Serializer):
    total_games = serializers.IntegerField()
    games_won = serializers.IntegerField()
    games_lost = serializers.IntegerField()
    points_scored = serializers.IntegerField()
    points_conceded = serializers.IntegerField()
    win_ratio = serializers.FloatField()
    points_ratio = serializers.FloatField()
    longest_win_streak = serializers.IntegerField()
    longest_loss_streak = serializers.IntegerField()
    longest_current_streak = serializers.IntegerField()

class MatchHistorySerializer(serializers.ModelSerializer):
    game_session_id = serializers.CharField(source='game_session.session_id')  # Adjusted field to fit `game_session`
    result = serializers.SerializerMethodField()  # Computes the result dynamically
    opponent = serializers.SerializerMethodField()  # Computes the opponent dynamically
    opponent_avatar = serializers.SerializerMethodField()  # Adds the avatar of the opponent

    class Meta:
        model = MatchHistory
        fields = [
            'game_session_id',
            'opponent',
            'opponent_avatar',
            'result',
            'player1_score',
            'player2_score',
            'forfeit',
            'created_at',
        ]

    def get_result(self, obj):
        request_user = self.context['request'].user
        if obj.game_session.player1 == request_user:
            return "Win" if obj.player1_score > obj.player2_score else "Loss"
        elif obj.game_session.player2 == request_user:
            return "Win" if obj.player2_score > obj.player1_score else "Loss"
        else:
            return "Not a participant"

    def get_opponent(self, obj):
        request_user = self.context['request'].user
        if obj.game_session.player1 == request_user:
            return obj.game_session.player2.username if obj.game_session.player2 else "Unknown"
        elif obj.game_session.player2 == request_user:
            return obj.game_session.player1.username if obj.game_session.player1 else "Unknown"
        else:
            return "Not a participant"

    def get_opponent_avatar(self, obj):
        request_user = self.context['request'].user
        if obj.game_session.player1 == request_user:
            return obj.game_session.player2.avatar.url if obj.game_session.player2 and obj.game_session.player2.avatar else None
        elif obj.game_session.player2 == request_user:
            return obj.game_session.player1.avatar.url if obj.game_session.player1 and obj.game_session.player1.avatar else None
        else:
            return None


class Verify2FACodeSerializer(serializers.Serializer):
    code = serializers.IntegerField()
    email = serializers.EmailField()

    def validate(self, data):
        email = data['email']
        code = data['code']

        try:
            user = TranscendenceUser.objects.get(email=email)
        except TranscendenceUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        if not user.two_factor_enabled:
            raise serializers.ValidationError("Two-factor authentication is not enabled.")

        if user.two_factor_code != code:
            raise serializers.ValidationError("Invalid 2FA code.")

        if user.code_expiry < now():
            raise serializers.ValidationError("2FA code has expired.")

        return user
