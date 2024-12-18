from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from .models import User
from celery import shared_task
from datetime import timedelta
from .tasks import send_message_to_friends

# Update User status on logged in
@receiver(user_logged_in)
def set_user_online(sender, user, request, **kwargs):
    user.is_online = True
    user.last_activity = timezone.now()
    send_message_to_friends(user, {'type': 'feed', 'sender_username': user.username, 'sender_displayname': user.display_name, 'info': 'Is now online'}, save=False)
    user.save()

# Update User status on logged out
@receiver(user_logged_out)
def set_user_offline(sender, user, request, **kwargs):
    user.is_online = False
    send_message_to_friends(user, {'type': 'feed', 'sender_username': user.username, 'sender_displayname': user.display_name, 'info': 'Is now offline'}, save=False)
    user.save()

