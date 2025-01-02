from django.contrib.auth.tokens import default_token_generator
from game.models import MatchHistory
from django.db.models import Sum, Q, F, Avg, Max, Min
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
    matches = MatchHistory.objects.filter(Q(player1=user) | Q(player2=user))
    total_games = matches.count()

    # Games Won
    games_won = sum(1 for match in matches if match.winner == user)

    # Games Lost
    games_lost = total_games - games_won

    # Points Scored
    points_scored = (
        MatchHistory.objects.filter(player1=user).aggregate(total=Sum('player1_score'))['total'] or 0
    ) + (
        MatchHistory.objects.filter(player2=user).aggregate(total=Sum('player2_score'))['total'] or 0
    )

    # Points Conceded
    points_conceded = (
        MatchHistory.objects.filter(player1=user).aggregate(total=Sum('player2_score'))['total'] or 0
    ) + (
        MatchHistory.objects.filter(player2=user).aggregate(total=Sum('player1_score'))['total'] or 0
    )

    # Win Ratio %
    win_ratio = (games_won / total_games * 100) if total_games else 0

    # Points Ratio %
    points_ratio = (points_scored / (points_scored + points_conceded) * 100) if points_conceded else 100

    # Longest Win Streak and Longest Current Streak
    longest_win_streak, longest_loss_streak, longest_current_streak = calculate_streak(user)

    # Match Durations
    total_duration = matches.aggregate(total=Sum('match_duration'))['total']
    avg_duration = matches.aggregate(avg=Avg('match_duration'))['avg']
    max_duration = matches.aggregate(max=Max('match_duration'))['max']
    min_duration = matches.aggregate(min=Min('match_duration'))['min']

    # Ball Hits
    total_ball_hits = matches.aggregate(total=Sum('total_ball_hits'))['total'] or 0

    # Longest Rally
    longest_rally = matches.aggregate(max_rally=Max('longest_rally'))['max_rally']

    # Average Ball Speed
    avg_ball_speed = matches.aggregate(avg_speed=Avg('avg_ball_speed'))['avg_speed']

    # Maximum Ball Speed
    max_ball_speed = matches.aggregate(max_speed=Max('max_ball_speed'))['max_speed']

    # Reaction Time
    reaction_time_player1 = matches.filter(player1=user).aggregate(avg=Avg('reaction_time_player1'))['avg'] or 0
    reaction_time_player2 = matches.filter(player2=user).aggregate(avg=Avg('reaction_time_player2'))['avg'] or 0
    avg_reaction_time = (reaction_time_player1 + reaction_time_player2) / 2 if total_games > 0 else 0

    # Victory Margin
    victory_margins = [
        match.victory_margin for match in matches if match.winner == user and match.victory_margin is not None
    ]
    avg_victory_margin = sum(victory_margins) / len(victory_margins) if victory_margins else 0
    
    max_victory_margin = max(victory_margins) if victory_margins else 0
    min_victory_margin = min(victory_margins) if victory_margins else 0

    hits_miss_ratio = (total_ball_hits / (total_ball_hits + points_conceded) * 100) if points_conceded and total_ball_hits else 0

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
        'total_duration': total_duration,
        'avg_duration': avg_duration,
        'min_duration': min_duration,
        'max_duration': max_duration,
        'total_ball_hits': total_ball_hits,
        'hits_miss_ratio': hits_miss_ratio,
        'longest_rally': longest_rally,
        'avg_ball_speed': avg_ball_speed,
        'max_ball_speed': max_ball_speed,
        'avg_reaction_time': avg_reaction_time,
        'avg_victory_margin': avg_victory_margin,
        'max_victory_margin': max_victory_margin,
        'min_victory_margin': min_victory_margin,
    }

def get_user_stats_for_visualization(user):
    # Original stats calculation
    stats = get_user_stats(user)

    rally_data = MatchHistory.objects.filter(Q(player1=user) | Q(player2=user)).values(
            'longest_rally', 'avg_ball_speed'
        )

    longest_rallies = [match['longest_rally'] for match in rally_data if match['longest_rally'] is not None]
    avg_ball_speeds = [match['avg_ball_speed'] for match in rally_data if match['avg_ball_speed'] is not None]

    match_history = MatchHistory.objects.filter(Q(player1=user) | Q(player2=user)).order_by('-created_at')
    recent_margins = [match.victory_margin for match in match_history[:10] if match.victory_margin is not None]  # Last 10 games
    all_margins = [match.victory_margin for match in match_history if match.victory_margin is not None]

    # Prepare data for visualizations
    visualization_data = {
        # Data for the bar chart: Games won vs. games lost
        'bar_chart': {
            'x': ['Games Won', 'Games Lost'],
            'y': [stats['games_won'], stats['games_lost']],
            'type': 'bar',
            'name': 'Games Performance',
            'marker': {
                'color': ['#4caf50', '#ff0000']  # Green for won, red for lost
            },
        },
        # Data for the gauge chart: Win ratio
        'gauge_chart': {
            'value': stats['win_ratio'],
            'title': {'text': 'Win Ratio (%)'},
            'type': 'indicator',
            'mode': 'gauge+number',
            'gauge': {
                'axis': {'range': [0, 100]},
                'bar': {'color': 'green'},
                'steps': [
                    {'range': [0, 50], 'color': 'red'},
                    {'range': [50, 100], 'color': 'green'}
                ],
            },
        },
        # Data for the pie chart: Points scored vs. points conceded
        'pie_chart': {
            'labels': ['Points Scored', 'Points Conceded'],
            'values': [stats['points_scored'], stats['points_conceded']],
            'type': 'pie',
            'name': 'Points Breakdown',
            'marker': {
                'colors': ['#4caf50', '#ff0000']  # Green for scored, red for conceded
            },
        },
        'streaks': {
            'labels': ['Win Streak', 'Lose Streak', 'Current Streak'],
            'values': [stats['longest_win_streak'], -stats['longest_loss_streak'], stats['longest_current_streak']],
        },
        'reaction_time_gauge': {
            'value': stats['avg_reaction_time'],
            'title': {'text': 'Average Reaction Time (ms)'},
            'type': 'indicator',
            'mode': 'gauge+number',
            'gauge': {
                'axis': {'range': [0, 500]},  # 0 to 500 ms
                'bar': {'color': 'blue'},  # Needle color
                'steps': [
                    {'range': [0, 100], 'color': 'green'},  # Excellent
                    {'range': [100, 200], 'color': 'yellow'},  # Good
                    {'range': [200, 300], 'color': 'orange'},  # Average
                    {'range': [300, 500], 'color': 'red'},  # Poor
                ],
            },
        },
        # Other visualizations...
        'rally_bar_chart': {
            'x': ['Total Ball Hits', 'Longest Rally'],
            'y': [stats['total_ball_hits'], stats['longest_rally']],
            'type': 'bar',
            'name': 'Ball Handling Stats',
            'marker': {
                'color': ['#2196f3', '#ff9800'],  # Blue for hits, orange for rally
            },
        },
        'rally_bubble_chart': {
            'x': longest_rallies,
            'y': avg_ball_speeds,
            'size': [r / 10 for r in longest_rallies],  # Scale bubble size by rally length
            'text': [f'Rally: {r}, Speed: {s} km/h' for r, s in zip(longest_rallies, avg_ball_speeds)],
            'type': 'scatter',
            'mode': 'markers',
            'marker': {
                'size': [r / 10 for r in longest_rallies],  # Bubble size
                'color': '#4caf50',  # Green bubbles
                'opacity': 0.6,
            },
        },
         'victory_box_plot': {
            'min': stats['min_victory_margin'],
            'avg': stats['avg_victory_margin'],
            'max': stats['max_victory_margin'],
            'all_margins': all_margins,  # Data for Box Plot
        },
    }
    
    # Include original stats for any additional use
    return {
        'stats': stats,
        'visualization_data': visualization_data
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

def get_match_stats(match_id):
    try:
        match = MatchHistory.objects.get(id=match_id)

        stats = {
            "session_id": match.game_session.session_id,
            "player1": match.player1.username,
            "player2": match.player2.username,
            "player1_score": match.player1_score,
            "player2_score": match.player2_score,
            "winner": match.winner.username if match.winner else "Draw",
            "loser": match.loser.username if match.loser else "Draw",
            "match_duration": match.match_duration,
            "total_ball_hits": match.total_ball_hits,
            "avg_ball_speed": match.avg_ball_speed,
            "max_ball_speed": match.max_ball_speed,
            "longest_rally": match.longest_rally,
            "reaction_time_player1": match.reaction_time_player1,
            "reaction_time_player2": match.reaction_time_player2,
            "victory_margin": match.victory_margin or abs(match.player1_score - match.player2_score),
            "forfeit": match.forfeit,
        }

        return stats

    except MatchHistory.DoesNotExist:
        return {"error": "Match not found"}
