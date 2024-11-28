from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import TranscendenceUser, FriendRequest, FeedUpdate
from django.conf import settings

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

# Serializer for user profile updates
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'display_name', 'bio', 'avatar', 'created_at', "is_online")
        read_only_fields = ('id', 'username', 'email', 'created_at', "is_online")

    # Validate username length
    def validate_username(self, value):
        if len(value) < settings.FORM_SETTINGS['username_length_min']:
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        if len(value) > settings.FORM_SETTINGS['username_length_max']:
            raise serializers.ValidationError("Username can't be more than 15 characters long.")
        return value
    
    # Validate display name length
    def validate_display_name(self, value):
        if len(value) < settings.FORM_SETTINGS['displayname_length_min']:
            raise serializers.ValidationError("Display Name must be at least 3 characters long.")
        if len(value) > settings.FORM_SETTINGS['displayname_length_max']:
            raise serializers.ValidationError("Display Name can't be more than 15 characters long.")
        return value

    # Validate bio length
    def validate_bio(self, value):
        if len(value) > settings.FORM_SETTINGS['bio_length_max']:
            raise serializers.ValidationError("Bio can't be more than 150 characters long.")
        return value

    # Ensure email is unique
    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("This email is already associated with another account.")
        return value

    # Validate avatar size and type
    def validate_avatar(self, value):
        max_size = 2 * 1024 * 1024  # 2MB
        if value.size > max_size:
            raise serializers.ValidationError("Avatar image size cannot exceed 2MB.")
        if not value.content_type.startswith("image/"):
            raise serializers.ValidationError("Uploaded file must be an image.")
        return value
    
    # Customize the representation of user profile data
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        representation.pop('created_at')  # Remove creation date
        representation.pop('id')  # Remove ID
        if request.user != instance:  # Hide email for other users
            representation.pop('email')
        return representation

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
        return friend_user.avatar.url if friend_user.avatar else None


class FeedUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedUpdate
        fields = ['sender_username', 'sender_displayname', 'info', 'created_at']
