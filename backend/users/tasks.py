from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from .models import User
from celery import shared_task
from datetime import timedelta
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.timezone import now

# The task that marks the user offline if they've been inactive for a ceretain time, called by celery
@shared_task
def mark_users_offline():
    timeout = timezone.now() - timedelta(minutes=1)
    User.objects.filter(last_activity__lt=timeout, is_online=True).update(is_online=False)

# A custom middleware to update user's online status on any activity with their token in it, Has a timer to make sure we aren't innefcient with db requests.
class UpdateLastActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_authenticator = JWTAuthentication()

    def __call__(self, request):
        try:
            user, token = self.jwt_authenticator.authenticate(request)
            if user:
                time_threshold = timezone.now() - timedelta(seconds=30)
                if user.last_activity is None or user.last_activity < time_threshold:
                    user.last_activity = now()
                    user.is_online = True
                    user.save()
        except:
            user = None
        response = self.get_response(request)
        return response


from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.functional import SimpleLazyObject

class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        request.user = SimpleLazyObject(lambda: self.get_user_from_jwt(request))
        return self.get_response(request)

    def get_user_from_jwt(self, request):
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            jwt_auth = JWTAuthentication()
            try:
                validated_token = jwt_auth.get_validated_token(token)
                return jwt_auth.get_user(validated_token)
            except Exception as e:
                print(f"JWT authentication failed: {e}")
                return None
        return None  # If no valid token is found


    
from rest_framework.authentication import BaseAuthentication
from django.contrib.auth.models import AnonymousUser

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        token = request.headers.get("Authorization")
        if not token:
            return None  # Return None when no token is found

        # Call `get_user_from_jwt` with the full request
        user = self.get_user_from_jwt(request)
        if user:
            return user, token  # Return a tuple if user is authenticated

        return None  # Return None if authentication fails

    def get_user_from_jwt(self, request):
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            jwt_auth = JWTAuthentication()
            try:
                validated_token = jwt_auth.get_validated_token(token)
                return jwt_auth.get_user(validated_token)
            except Exception as e:
                print(f"JWT authentication failed: {e}")
        return None  # If no valid token is found


class DebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the body has been accessed
        if hasattr(request, '_body'):
            print(f"DebugMiddleware: Request body already accessed in {type(self).__name__}")
        else:
            print(f"DebugMiddleware: Request body not accessed yet in {type(self).__name__}")

        response = self.get_response(request)

        # After processing the request
        if hasattr(request, '_body'):
            print(f"DebugMiddleware: Request body was accessed by {type(self).__name__}")

        return response