from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import TranscendenceUser

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'display_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match"})
        if len(attrs['username']) < 3:
            raise serializers.ValidationError("Username must be atleast 3 characters long.")
        if len(attrs['username']) > 15:
            raise serializers.ValidationError("Username can't be more than 15 characters long.")
    
        if len(attrs['display_name']) < 3:
            raise serializers.ValidationError("Display Name must be atleast 3 characters long.")
        if len(attrs['display_name']) > 15:
            raise serializers.ValidationError("Display Name can't be more than 15 characters long.")

        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("This email is already associated with another account.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'display_name', 'bio', 'avatar', 'created_at')
        read_only_fields = ('id', 'username', 'email', 'created_at')

    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Username must be atleast 3 characters long.")
        if len(value) > 15:
            raise serializers.ValidationError("Username can't be more than 15 characters long.")
        return value
    
    def validate_display_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Display Name must be atleast 3 characters long.")
    
        if len(value) > 15:
            raise serializers.ValidationError("Display Name can't be more than 15 characters long.")
        return value

    def validate_bio(self, value):
        if len(value) > 150:
            raise serializers.ValidationError("Bio can't be more than 150 characters long.")
        return value
    
    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("This email is already associated with another account.")
        return value
    
    def validate_avatar(self, value):
        max_size = 2 * 1024 * 1024  #2MB
        if value.size > max_size:
            raise serializers.ValidationError("Avatar image size cannot exceed 2MB.")
        if not value.content_type.startswith("image/"):
            raise serializers.ValidationError("Uploaded file must be an image.")
        return value
    
    def to_representation(self, instance):
        representaion = super().to_representation(instance)
        request = self.context.get('request')
        representaion.pop('created_at')
        representaion.pop('id')
        if request.user != instance:
            representaion.pop('email')
        return representaion

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get("username")

        try:
            user = User.objects.get(username=username) if username else None
        except:
            user = None
        if user and not user.is_verified:
            raise serializers.DjangoValidationError("Your account is not verified. Please check your email for verification instructions.")

        data = super().validate(attrs)
        
        data.update(
            {
                'username': self.user.username,
                'display_name': self.user.display_name,
            }
        )

        return data