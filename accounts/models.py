from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Create your models here.
class TranscendenceUser(AbstractUser):
    #most basic info
    email = models.EmailField(unique=True)

    #details
    display_name = models.CharField(max_length=30, unique=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg')
    bio = models.TextField(blank=True, null=True)

    #socials
    # friends = models.ManyToManyField('self', through='Friendship', symmetrical=False, related_name='friend_set')
    is_online = models.BooleanField(default=False)

    #history
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    # match_history = models.ManyToManyField('Match', blank=True)

    #secuirity
    two_factor_enabled = models.BooleanField(default=False)
    last_activity = models.DateTimeField(default=timezone.now)

    #for representaion
    def __str__(self):
        return self.username
    
    @property
    def win_loss_ratio(self):
        if self.losses == 0:
            return self.wins
        return self.wins / (self.wins + self.losses)
    
    def update_online_status(self, is_online):
        self.is_online = is_online
        self.last_activity = timezone.now()
        self.save()