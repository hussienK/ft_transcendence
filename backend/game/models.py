# models.py

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class GameSession(models.Model):
    session_id = models.CharField(max_length=100, unique=True, default='default_session_id')
    player1 = models.ForeignKey(User, related_name='player1_sessions', on_delete=models.CASCADE)
    player2 = models.ForeignKey(User, related_name='player2_sessions', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"GameSession {self.session_id} between {self.player1} and {self.player2}"
