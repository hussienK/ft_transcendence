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
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
import json

# In-memory matchmaking queue
matchmaking_queue = []
# Lock for thread-safe operations on matchmaking_queue
matchmaking_lock = asyncio.Lock()

class JoinQueueView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Check if the user is already in the queue
        if user in matchmaking_queue:
            print(f"User {user.username} attempted to join the queue but is already in it.")
            return Response({'status': 'already_in_queue'}, status=status.HTTP_200_OK)

        matchmaking_queue.append(user)
        print(f"User {user.username} joined the matchmaking queue.")

        # Check if there are at least two players to start a game
        if len(matchmaking_queue) >= 2:
            player1 = matchmaking_queue.pop(0)
            player2 = matchmaking_queue.pop(0)
            session_id = str(uuid.uuid4())
            
            # Create a new game session
            try:
                game_session = GameSession.objects.create(
                    session_id=session_id,
                    player1=player1,
                    player2=player2
                )
                print(f"Game session {session_id} created for {player1.username} and {player2.username}")
            except Exception as e:
                print(f"Error creating game session: {e}")
                # Re-add players to the queue in case of failure
                matchmaking_queue.insert(0, player2)
                matchmaking_queue.insert(0, player1)
                return Response({'status': 'error_creating_session'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Prepare match data
            channel_layer = get_channel_layer()
            game_ws_url = f"/ws/game/{session_id}/"
            match_data_player1 = {
                'type': 'match_found',
                'session_id': session_id,
                'player': 'player1',
                'opponent': player2.username,
                'game_ws_url': game_ws_url,
            }
            match_data_player2 = {
                'type': 'match_found',
                'session_id': session_id,
                'player': 'player2',
                'opponent': player1.username,
                'game_ws_url': game_ws_url,
            }

            # Notify Player 1
            async_to_sync(channel_layer.group_send)(
                f"user_{player1.username}",
                {
                    "type": "send_match_found",
                    "data": match_data_player1,
                }
            )

            # Notify Player 2
            async_to_sync(channel_layer.group_send)(
                f"user_{player2.username}",
                {
                    "type": "send_match_found",
                    "data": match_data_player2,
                }
            )

            return Response({
                'status': 'match_found'
            }, status=status.HTTP_200_OK)

        return Response(
            {'status': 'awaiting_match'},
            status=status.HTTP_200_OK
        )

class JoinLocalGame(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Check if the user is already in the queue
        if user in matchmaking_queue:
            print(f"User {user.username} attempted to join the queue but is already in Online Queue.")
            return Response({'status': 'already_in_queue'}, status=status.HTTP_200_OK)
        
        session_id = str(uuid.uuid4())
        channel_layer = get_channel_layer()
        game_ws_url = f"/ws/game/{session_id}/"
        match_data = {
            'type': 'match_found_local',
            'session_id': session_id,
            'game_ws_url': game_ws_url,
        }

        async_to_sync(channel_layer.group_send)(
            f"user_{user.username}",
            {
                "type": "send_match_found",
                "data": match_data,
            }
        )

        return Response(
            {'status': 'starting_match'},
            status=status.HTTP_200_OK
        )

class LeaveQueueView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Check if the user is already in the queue
        if user not in matchmaking_queue:
            print(f"User {user.username} Not in queue")
            return Response({'status': 'not_in_queue'}, status=status.HTTP_200_OK)

        matchmaking_queue.remove(user)
        print(f"User {user.username} joined the matchmaking queue.")

        return Response(
            {'status': 'left_queue'},
            status=status.HTTP_200_OK
        )

