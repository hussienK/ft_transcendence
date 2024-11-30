from django.contrib.auth.tokens import default_token_generator
from game.models import MatchHistory
from django.db.models import Sum, Q

def generate_verification_token(user):
    return default_token_generator.make_token(user)

def calculate_streak(user, won=True):
    """
    Calculates the longest win or loss streak for a user.
    """
    if won:
        matches = MatchHistory.objects.filter(winner=user).order_by('created_at')
    else:
        matches = MatchHistory.objects.filter(loser=user).order_by('created_at')

    longest_streak = 0
    current_streak = 0
    last_match_date = None

    for match in matches:
        if last_match_date and (match.created_at - last_match_date).days > 1:
            # Streak breaks if matches are not consecutive
            longest_streak = max(longest_streak, current_streak)
            current_streak = 0

        current_streak += 1
        last_match_date = match.created_at

    longest_streak = max(longest_streak, current_streak)
    return longest_streak


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
    points_ratio = (points_scored / points_conceded * 100) if points_conceded else 0

    # Longest Win Streak
    longest_win_streak = calculate_streak(user, won=True)

    # Longest Loss Streak
    longest_loss_streak = calculate_streak(user, won=False)

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
    }