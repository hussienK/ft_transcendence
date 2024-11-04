from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.
class TranscendenceUser(AbstractUser):
    display_name = models.CharField(max_length=30, unique=True)
    avatar = models.ImageField(upload_to='avatars', default='avatars/default.jpg')
    bio = models.TextField(blank=True)
    is_online = models.BooleanField(default=False)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    two_factor_enabled = models.BooleanField(default=False)
    last_activity = models.DateTimeField(default=timezone.now)

    @property
    def win_loss_ratio(self):
        if self.losses == 0:
            return float(self.wins)
        return self.wins / self.losses
    
    def update_activity(self):
        self.is_online = True
        self.last_activity = timezone.now()
        self.save()