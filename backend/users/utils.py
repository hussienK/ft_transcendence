from django.contrib.auth.tokens import default_token_generator
from game.models import MatchHistory
from django.db.models import Sum, Q

def generate_verification_token(user):
    return default_token_generator.make_token(user)

def calculate_streak(user):
    """
    Calculates the longest win streak, longest loss streak, and the current streak.
    Returns the longest win streak, longest loss streak, and current streak value
    (positive for win streak, negative for loss streak, 0 if no streak).
    """
    # Get all matches (both wins and losses for the user)
    matches = MatchHistory.objects.filter(Q(winner=user) | Q(loser=user)).order_by('created_at')

    longest_win_streak = 0
    longest_loss_streak = 0
    current_streak = 0  # Can be positive for wins, negative for losses
    longest_current_streak = 0  # Tracks the ongoing streak with its sign (positive/negative)

    for match in matches:

        if match.winner == user:  # If the user won
            current_streak += 1  # Increment streak for wins
        elif match.loser == user:  # If the user lost
            current_streak -= 1  # Decrement streak for losses

        # Track the longest streaks
        longest_win_streak = max(longest_win_streak, current_streak) if current_streak > 0 else longest_win_streak
        longest_loss_streak = min(longest_loss_streak, current_streak) if current_streak < 0 else longest_loss_streak
        longest_current_streak = current_streak  # Ongoing streak value (positive/negative)


    # Final check after loop to account for the streak at the end
    if current_streak > 0:
        longest_win_streak = max(longest_win_streak, current_streak)
    elif current_streak < 0:
        longest_loss_streak = min(longest_loss_streak, current_streak)

    return longest_win_streak, longest_loss_streak, longest_current_streak



def get_user_stats(user):
    # Total Games
    total_games = MatchHistory.objects.filter(
        Q(winner=user) | Q(loser=user)
    ).count()

    # Games Won
    games_won = MatchHistory.objects.filter(winner=user).count()

    # Games Lost
    games_lost = MatchHistory.objects.filter(loser=user).count()

    # Points Scored
    points_scored = MatchHistory.objects.filter(winner=user).aggregate(
        total=Sum('points_scored_by_winner')
    )['total'] or 0

    # Points Conceded
    points_conceded = MatchHistory.objects.filter(loser=user).aggregate(
        total=Sum('points_conceded_by_loser')
    )['total'] or 0

    # Win Ratio %
    win_ratio = (games_won / total_games * 100) if total_games else 0

    # Points Ratio %
    points_ratio = (points_scored / (points_scored + points_conceded) * 100) if points_conceded else 0

    # Longest Win Streak and Longest Current Streak
    longest_win_streak, longest_loss_streak, longest_current_streak = calculate_streak(user)

    return {
        'total_games': total_games,
        'games_won': games_won,
        'games_lost': games_lost,
        'points_scored': points_scored,
        'points_conceded': points_conceded,
        'win_ratio': win_ratio,
        'points_ratio': points_ratio,
        'longest_win_streak': longest_win_streak,
        'longest_loss_streak': longest_loss_streak,
        'longest_current_streak': longest_current_streak,
    }

from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
import random
from ft_transcendance import settings

def send_2fa_email(user):
    # Generate a random 6-digit code
    code = random.randint(100000, 999999)
    
    # Save the code and expiry to the user model
    user.two_factor_code = code
    user.code_expiry = now() + timedelta(minutes=10)  # Code valid for 10 minutes
    user.save()

    # Send the email
    send_mail(
        subject="Verify Your Email",
        message=f"This is your 2FA code {code}",
        from_email=settings.DEFAULT_FROM_MAIL,
        recipient_list=[user.email],
    )