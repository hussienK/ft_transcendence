from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect
from django.urls import reverse
from .models import GameSession
import uuid
from rest_framework import status
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

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
        print(matchmaking_queue)
        print(f"User {user.username} joined the matchmaking queue.")

        if len(matchmaking_queue) >= 2:
            player1 = matchmaking_queue.pop(0)
            player2 = matchmaking_queue.pop(0)
            session_id = str(uuid.uuid4())
            game_session = GameSession.objects.create(
                session_id=session_id,
                player1=player1,
                player2=player2
            )
            print(f"Game session {session_id} created for {player1.username} and {player2.username}")

            # Notify both players
            channel_layer = get_channel_layer()
            match_data = {
                'status': 'match_found',
                'session_id': session_id,
                'player1': player1.username,
                'player2': player2.username,
                'role': 'player1' if user == player1 else 'player2',
                'game_ws_url': f"/ws/game/{session_id}/",
            }

            # Notify Player 1
            async_to_sync(channel_layer.group_send)(
                f"user_{player1.username}",
                {
                    "type": "send_match_found",
                    "data": match_data,
                }
            )

            # Notify Player 2
            async_to_sync(channel_layer.group_send)(
                f"user_{player2.username}",
                {
                    "type": "send_match_found",
                    "data": match_data,
                }
            )

            return Response({
                'status': 'match_found',
                'session_id': session_id,
                'player': 'player1' if user == player1 else 'player2',
            }, status=status.HTTP_200_OK)

        return Response(
            {'status': 'awaiting match'},
            status=status.HTTP_200_OK
        )
