import random
from faker import Faker
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User as DjangoUser  # For password handling
from game.models import GameSession, MatchHistory
from users.models import FeedUpdate, FriendRequest

User = get_user_model()

class Command(BaseCommand):
	help = 'Generate random users, friendships, game sessions, and stats for testing'

	def handle(self, *args, **kwargs):
		fake = Faker()
		num_users = 10  # You can change this to the number of users you want to generate
		min_friends = 1
		max_friends = 5
		max_wins = 50
		max_losses = 50

		# Step 1: Create users
		users = []
		for _ in range(num_users):
			username = fake.user_name()
			email = fake.email()
			display_name = fake.first_name()
			bio = fake.text(max_nb_chars=200)
			is_verified = True
			two_factor_enabled = False
			last_activity = timezone.now()
			created_at = timezone.now()

			# Create and save the user
			user = User.objects.create(
				username=username,
				email=email,
				display_name=display_name,
				bio=bio,
				is_verified=is_verified,
				two_factor_enabled=two_factor_enabled,
				last_activity=last_activity,
				created_at=created_at
			)

			# Assign a random password
			password = "Hk@12345"  # Create a random password
			user.set_password(password)  # Set the password after hashing it
			user.save()  # Save the user with the hashed password

			users.append(user)

			# Optionally, print the generated user details for reference
			self.stdout.write(f"Created user: {user.username}, Email: {user.email}, Wins: {user.wins}, Losses: {user.losses}, Password: {password}")

		# Step 3: Create random friendships
		self.create_random_friendships(users)

		# Step 4: Create random game sessions and match history
		self.create_random_game_sessions_and_history(users)

	def create_random_friendships(self, users):
			# Randomly create friend requests between users
			for user in users:
				num_friends = random.randint(1, 5)  # Each user will have 1 to 5 friends
				potential_friends = [u for u in users if u != user]

				for _ in range(num_friends):
					friend = random.choice(potential_friends)
					potential_friends.remove(friend)  # Ensure no duplicate friend requests

					# Create a friend request
					friend_request = FriendRequest.objects.create(sender=user, receiver=friend)

					# Randomly decide if the request is accepted or declined
					if random.choice([True, False]):
						friend_request.accept()  # Accept the friend request, making them friends
						self.stdout.write(f"Friendship accepted between {user.username} and {friend.username}")

	def create_random_game_sessions_and_history(self, users):
		# Randomly create game sessions and match history for users
		for _ in range(random.randint(5, 10)):  # Create between 5 and 10 game sessions
			# Randomly select players for the game session
			player1, player2 = random.sample(users, 2)  # Select 2 random users

			# Create GameSession
			game_session = GameSession.objects.create(
				player1=player1,
				player2=player2,
				session_id=f"session_{random.randint(1000, 9999)}",  # Random session ID
				is_active=True
			)

			# Randomly generate scores
			player1_score = random.randint(0, 10)
			player2_score = random.randint(0, 10)

			# Determine winner and loser based on scores
			if player1_score > player2_score:
				winner = player1
				loser = player2
			elif player2_score > player1_score:
				winner = player2
				loser = player1
			else:
				# In case of a tie, assign randomly
				winner, loser = random.sample([player1, player2], 2)

			# Create MatchHistory
			match_history = MatchHistory.objects.create(
				game_session=game_session,
				winner=winner,
				loser=loser,
				player1_score=player1_score,
				player2_score=player2_score,
				points_scored_by_winner=max(player1_score, player2_score),
				points_conceded_by_loser=min(player1_score, player2_score)
			)

			self.stdout.write(f"Created game session: {game_session.session_id} with winner {winner.username} and loser {loser.username}")
