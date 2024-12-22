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
    game_mode = models.CharField(max_length=50, default="local")  # Game mode: local/online/tournament

    def __str__(self):
        return f"GameSession {self.session_id} between {self.player1} and {self.player2}"


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

    match_duration = models.FloatField(default=0, help_text="Duration of the match in seconds")
    total_ball_hits = models.PositiveIntegerField(default=0)  # Number of ball hits in the match
    avg_ball_speed = models.FloatField(null=True, blank=True)  # Average ball speed
    max_ball_speed = models.FloatField(null=True, blank=True)  # Maximum ball speed
    longest_rally = models.PositiveIntegerField(default=0)  # Maximum number of consecutive hits without scoring
    reaction_time_player1 = models.FloatField(null=True, blank=True)  # Avg reaction time for player1
    reaction_time_player2 = models.FloatField(null=True, blank=True)  # Avg reaction time for player2
    victory_margin = models.PositiveIntegerField(null=True, blank=True)  # Margin of victory (score difference)

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

class Tournament(models.Model):
    name = models.CharField(max_length=100, default="Pong Tournament")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_started = models.BooleanField(default=False)
    winner = models.CharField(max_length=100, null=True, blank=True)  # Alias of the winner

    def __str__(self):
        return f"Tournament {self.name}"


class TournamentParticipant(models.Model):
    tournament = models.ForeignKey(
        Tournament, related_name="participants", on_delete=models.CASCADE
    )
    alias = models.CharField(max_length=50, unique=True)  # Alias must be unique
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )  # Optional link to a user

    def __str__(self):
        return f"{self.alias} in {self.tournament.name}"


class TournamentMatch(models.Model):
    tournament = models.ForeignKey(
        Tournament, related_name="matches", on_delete=models.CASCADE
    )
    game_session = models.OneToOneField(
        "GameSession", on_delete=models.CASCADE, related_name="tournament_match"
    )
    round_number = models.PositiveIntegerField()  # Round in the tournament (e.g., 1 for semi-finals)
    match_number = models.PositiveIntegerField()  # Match order within the round
    player1_alias = models.CharField(max_length=50)
    player2_alias = models.CharField(max_length=50)
    winner_alias = models.CharField(max_length=50, null=True, blank=True)  # Alias of the match winner

    def __str__(self):
        return f"Match {self.match_number} (Round {self.round_number}) of {self.tournament.name}"