from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect
from django.urls import reverse
from .models import GameSession
import uuid
from rest_framework import status

# In-memory matchmaking queue
matchmaking_queue = []

class JoinQueueView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		user = request.user

		# Check if the user is already in the queue
		if user in matchmaking_queue:
			matchmaking_queue.remove(user)
			return Response({'status': 'already_in_queue'}, status=status.HTTP_200_OK)
		
		matchmaking_queue.append(user)
		print(f"User {user.usernme} joined the matchmaking queue.")

		if len(matchmaking_queue) >= 2:
			player1 = matchmaking_queue.pop(0)
			player2 = matchmaking_queue.pop(0)
			session_id = str(uuid.uuid4())
			game_session = GameSession.objects.create(
				session_id=session_id,
				player1=player1,
				player2=player2
			)
			print(f"Gamesession {session_id} created successfully for users {player1.username} and {player2.username}")

			player = 'player1' if user == player1 else 'player2'
			return Response({
				'status': 'match_found',
				'session_id': session_id,
				'player': player
			})