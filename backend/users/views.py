from rest_framework import status, generics, permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer, UserProfileSerializer
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomTokenObtainPairSerializer
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
    
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
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
        
from django.shortcuts import render
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth.password_validation import validate_password

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
            except DjangoValidationError as e:
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
