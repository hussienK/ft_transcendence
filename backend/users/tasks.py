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
