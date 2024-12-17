from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.timezone import now

# The Basic user model for our website
class TranscendenceUser(AbstractUser):
    display_name = models.CharField(max_length=30, unique=True)
    avatar = models.ImageField(upload_to='avatars/', default=None)
    bio = models.TextField(blank=True)
    is_online = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    last_activity = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    two_factor_code = models.IntegerField(null=True, blank=True)
    code_expiry = models.DateTimeField(null=True, blank=True)

    #an auto property with some details

    def update_activity(self):
        self.is_online = True
        self.last_activity = timezone.now()
        self.save()

User = get_user_model()

# A mode for friend requests
class FriendRequest(models.Model):
    sender = models.ForeignKey(User, related_name="sent_friend_requests", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_friend_requests", on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    accepted = models.BooleanField(default=False)

    def accept(self):
        self.accepted = True
        self.save()
        self.sender.friends.add(self.receiver)
        self.receiver.friends.add(self.sender)

    def decline(self):
        self.delete()

User.add_to_class('friends', models.ManyToManyField('self', symmetrical=True, blank=True))


class FeedUpdate(models.Model):
    user = models.TextField()
    sender_username = models.TextField()
    sender_displayname = models.TextField()
    info = models.TextField()
    created_at = models.DateTimeField(default=now)

    class Meta:
        ordering = ['created_at']  # Latest updates first
