# models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class GameSession(models.Model):
    session_id = models.CharField(max_length=100, unique=True, default='default_session_id')
    player1 = models.ForeignKey(User, related_name='player1_sessions', on_delete=models.CASCADE)
    player2 = models.ForeignKey(User, related_name='player2_sessions', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"GameSession {self.session_id} between {self.player1} and {self.player2}"

from django.db import models
from django.contrib.auth.models import User

class MatchHistory(models.Model):
    game_session = models.OneToOneField(
        "GameSession",
        on_delete=models.CASCADE,
        related_name="match_history"
    )
    player1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="player1_match_history",
        on_delete=models.CASCADE
    )
    player2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="player2_match_history",
        on_delete=models.CASCADE
    )
    player1_score = models.PositiveIntegerField(default=0)
    player2_score = models.PositiveIntegerField(default=0)
    forfeit = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def winner(self):
        if self.player1_score > self.player2_score:
            return self.player1
        elif self.player2_score > self.player1_score:
            return self.player2
        else:
            return None

    @property
    def loser(self):
        if self.winner == self.player1:
            return self.player2
        elif self.winner == self.player2:
            return self.player1
        else:
            return None

    def __str__(self):
        return f"MatchHistory for GameSession {self.game_session.session_id} ({self.player1} vs {self.player2})"
