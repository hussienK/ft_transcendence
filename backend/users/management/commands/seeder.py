import random
from faker import Faker
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from game.models import GameSession, MatchHistory
from users.models import FriendRequest

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate random users, friendships, game sessions, and stats for testing'

    def handle(self, *args, **kwargs):
        fake = Faker()
        num_users = 10  # Number of users to generate

        # Step 1: Create users
        users = self.create_users(fake, num_users)

        # Step 2: Create random friendships
        self.create_random_friendships(users)

        # Step 3: Create random game sessions and match history
        self.create_random_game_sessions_and_history(users)

    def create_users(self, fake, num_users):
        users = []
        for _ in range(num_users):
            username = fake.user_name()
            email = fake.email()
            display_name = fake.first_name()
            bio = fake.text(max_nb_chars=200)
            avatar = None  # Default avatar (you can set a specific path if required)
            is_verified = True
            two_factor_enabled = False
            last_activity = timezone.now()
            created_at = timezone.now()
            two_factor_code = random.randint(100000, 999999) if two_factor_enabled else None
            code_expiry = timezone.now() + timezone.timedelta(minutes=5) if two_factor_enabled else None

            # Create and save the user
            user = User.objects.create(
                username=username,
                email=email,
                display_name=display_name,
                bio=bio,
                avatar=avatar,
                is_verified=is_verified,
                two_factor_enabled=two_factor_enabled,
                last_activity=last_activity,
                created_at=created_at,
                two_factor_code=two_factor_code,
                code_expiry=code_expiry
            )

            # Assign a random password
            password = "Hk@12345"  # Random password
            user.set_password(password)
            user.save()

            users.append(user)

            self.stdout.write(f"Created user: {user.username}, Display Name: {user.display_name}, "
                              f"Email: {user.email}, Two-Factor: {user.two_factor_enabled}, "
                              f"Password: {password}")

        return users

    def create_random_friendships(self, users):
        for user in users:
            num_friends = random.randint(1, 5)  # Each user will have 1 to 5 friends
            potential_friends = [u for u in users if u != user]

            for _ in range(num_friends):
                if not potential_friends:
                    break

                friend = random.choice(potential_friends)
                potential_friends.remove(friend)  # Avoid duplicate friend requests

                # Create a friend request
                friend_request = FriendRequest.objects.create(sender=user, receiver=friend)

                # Randomly decide if the request is accepted
                if random.choice([True, False]):
                    friend_request.accept()
                    self.stdout.write(f"Friendship accepted between {user.username} and {friend.username}")

    def create_random_game_sessions_and_history(self, users):
        for _ in range(random.randint(5, 10)):  # Create between 5 and 10 game sessions
            player1, player2 = random.sample(users, 2)  # Select 2 random users

            # Create GameSession
            game_session = GameSession.objects.create(
                player1=player1,
                player2=player2,
                session_id=f"session_{random.randint(1000, 9999)}",  # Random session ID
                is_active=False,  # Game session is inactive after completion
                game_mode=random.choice(["local", "online", "tournament"])  # Random game mode
            )

            # Generate random match data
            player1_score = random.randint(0, 5)
            player2_score = random.randint(0, 5)
            total_ball_hits = random.randint(10, 100)
            avg_ball_speed = round(random.uniform(5.0, 20.0), 2)  # Average ball speed
            max_ball_speed = round(random.uniform(avg_ball_speed, avg_ball_speed + 10.0), 2)
            longest_rally = random.randint(5, 30)
            reaction_time_player1 = round(random.uniform(0.2, 1.0), 2)
            reaction_time_player2 = round(random.uniform(0.2, 1.0), 2)
            victory_margin = abs(player1_score - player2_score)
            match_duration = round(random.uniform(300, 1800), 2)  # Duration in seconds
            forfeit = random.choice([True, False])

            # Create MatchHistory
            match_history = MatchHistory.objects.create(
                game_session=game_session,
                player1=player1,
                player2=player2,
                player1_score=player1_score,
                player2_score=player2_score,
                match_duration=match_duration,
                total_ball_hits=total_ball_hits,
                avg_ball_speed=avg_ball_speed,
                max_ball_speed=max_ball_speed,
                longest_rally=longest_rally,
                reaction_time_player1=reaction_time_player1,
                reaction_time_player2=reaction_time_player2,
                victory_margin=victory_margin,
                forfeit=forfeit
            )

            # Log match results
            if player1_score > player2_score:
                winner, loser = player1, player2
            elif player2_score > player1_score:
                winner, loser = player2, player1
            else:
                winner, loser = None, None  # Tie game

            if winner and loser:
                self.stdout.write(
                    f"Game session {game_session.session_id}: Winner {winner.username} ({player1_score}) "
                    f"vs Loser {loser.username} ({player2_score})"
                )
            else:
                self.stdout.write(f"Game session {game_session.session_id} resulted in a tie")

            # Log additional statistics
            self.stdout.write(
                f"Stats: Duration {match_duration}s, Ball Hits {total_ball_hits}, "
                f"Avg Speed {avg_ball_speed} m/s, Max Speed {max_ball_speed} m/s, "
                f"Longest Rally {longest_rally}, "
                f"Reaction Times P1 {reaction_time_player1}s, P2 {reaction_time_player2}s, "
                f"Victory Margin {victory_margin}"
            )
