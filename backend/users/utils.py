from django.contrib.auth.tokens import default_token_generator
from game.models import MatchHistory
from django.db.models import Sum, Q, F
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def generate_verification_token(user):
    return default_token_generator.make_token(user)


def calculate_streak(user):
    """
    Calculates the longest win streak, longest loss streak, and the current streak.
    Returns the longest win streak, longest loss streak, and current streak value
    (positive for win streak, negative for loss streak, 0 if no streak).
    """
    # Get all matches (both wins and losses for the user)
    matches = MatchHistory.objects.filter(Q(player1=user) | Q(player2=user)).order_by('created_at')

    longest_win_streak = 0
    longest_loss_streak = 0
    current_streak = 0

    for match in matches:
        user_score = match.player1_score if match.player1 == user else match.player2_score
        opponent_score = match.player2_score if match.player1 == user else match.player1_score

        if user_score > opponent_score:  # Win
            current_streak = current_streak + 1 if current_streak > 0 else 1
            longest_win_streak = max(longest_win_streak, current_streak)
        elif user_score < opponent_score:  # Loss
            current_streak = current_streak - 1 if current_streak < 0 else -1
            longest_loss_streak = min(longest_loss_streak, current_streak)

    return longest_win_streak, abs(longest_loss_streak), current_streak


def get_user_stats(user):
    # Total Games
    total_games = MatchHistory.objects.filter(Q(player1=user) | Q(player2=user)).count()

    # Games Won
    games_won = MatchHistory.objects.filter(
        Q(player1=user, player1_score__gt=F('player2_score')) |
        Q(player2=user, player2_score__gt=F('player1_score'))
    ).count()

    # Games Lost
    games_lost = total_games - games_won

    # Points Scored
    points_scored = MatchHistory.objects.filter(player1=user).aggregate(
        total=Sum('player1_score')
    )['total'] or 0
    points_scored += MatchHistory.objects.filter(player2=user).aggregate(
        total=Sum('player2_score')
    )['total'] or 0

    # Points Conceded
    points_conceded = MatchHistory.objects.filter(player1=user).aggregate(
        total=Sum('player2_score')
    )['total'] or 0
    points_conceded += MatchHistory.objects.filter(player2=user).aggregate(
        total=Sum('player1_score')
    )['total'] or 0

    # Win Ratio %
    win_ratio = (games_won / total_games * 100) if total_games else 0

    # Points Ratio %
    points_ratio = (points_scored / (points_scored + points_conceded) * 100) if points_conceded else 100

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
    html_message = render_to_string('email_verification_template.html', {
        'code': code,
        'user': user
    })

    email = EmailMultiAlternatives(
        subject="ft_transendance 2FA Code",
        body="This is the link for your 2FA",
        from_email=settings.DEFAULT_FROM_MAIL,
        to=[user.email],
    )
    email.attach_alternative(html_message, "text/html")
    email.send()