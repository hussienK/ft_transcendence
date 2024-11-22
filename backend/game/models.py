from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class GameSession(models.Model):
	player1 = models.ForeignKey(User, related_name='games_as_player1', on_delete=models.CASCADE)
	player2 = models.ForeignKey(User, related_name='games_as_player2', on_delete=models.CASCADE, null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

