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
from django.db import transaction
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import Tournament, TournamentParticipant, GameSession, TournamentMatch
import random

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

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import uuid
import random
import threading

# A global dictionary to hold multiple tournaments in memory.
tournaments = {}

# A lock to protect reads/writes to the 'tournaments' dictionary
tournament_lock = threading.RLock()

class CreateTournamentView(APIView):
    """
    POST /api/tournament/create/
    Creates a new in-memory tournament and returns its ID.
    """
    def post(self, request):
        with tournament_lock:
            tournament_id = str(uuid.uuid4())
            tournaments[tournament_id] = {
                "participants": [],
                "matches": [],            # List of matches: { player1, player2, winner }
                "is_started": False,
                "lock": threading.RLock() # Each tournament can also have its own lock
            }
        return Response({"status": "tournament_created", "tournament_id": tournament_id}, status=status.HTTP_201_CREATED)

class RegisterAliasView(APIView):
    """
    POST /api/tournament/<tournament_id>/register/
    Body: { "alias": "PlayerAlias" }
    Registers an alias (i.e., player's name) in the tournament.
    """
    def post(self, request, tournament_id):
        alias = request.data.get("alias")
        if not alias:
            return Response({"error": "Alias is required."}, status=status.HTTP_400_BAD_REQUEST)

        with tournament_lock:
            tournament = tournaments.get(tournament_id)
            if not tournament:
                return Response({"error": "Tournament not found."}, status=status.HTTP_404_NOT_FOUND)

            with tournament["lock"]:
                if tournament["is_started"]:
                    return Response({"error": "Tournament already started."}, status=status.HTTP_400_BAD_REQUEST)

                if alias in tournament["participants"]:
                    return Response({"error": "Alias already taken."}, status=status.HTTP_400_BAD_REQUEST)

                tournament["participants"].append(alias)

        return Response({"status": "registered", "alias": alias})

class StartTournamentView(APIView):
    """
    POST /api/tournament/<tournament_id>/start/
    Generates the full match tree, including placeholders for future rounds.
    """
    def post(self, request, tournament_id):
        with tournament_lock:
            tournament = tournaments.get(tournament_id)
            if not tournament:
                return Response({"error": "Tournament not found."}, status=status.HTTP_404_NOT_FOUND)

            with tournament["lock"]:
                if tournament["is_started"]:
                    return Response({"error": "Tournament already started."}, status=status.HTTP_400_BAD_REQUEST)

                participants = tournament["participants"]
                if len(participants) < 2:
                    return Response({"error": "At least 2 participants are required to start."}, status=status.HTTP_400_BAD_REQUEST)

                # Shuffle participants for randomness
                random.shuffle(participants)

                # Generate the full match tree
                match_tree = self.generate_match_tree(participants)
                tournament["matches"] = match_tree
                tournament["is_started"] = True

                return Response({
                    "status": "tournament_started",
                    "matches": match_tree
                })

    def generate_match_tree(self, participants):
        """
        Recursively generates the match tree with placeholders (TBD).
        Each match is represented as:
        { "round": X, "match_number": Y, "player1": "Alias1", "player2": "Alias2", "winner": None }
        """
        rounds = []
        current_round = self.create_round(participants, round_number=1)
        rounds.append(current_round)

        while len(current_round) > 1:
            winners = ["TBD"] * len(current_round)  # Placeholder for winners
            next_round = self.create_round(winners, round_number=len(rounds) + 1)
            rounds.append(next_round)
            current_round = next_round

        return [match for round_matches in rounds for match in round_matches]

    def create_round(self, players, round_number):
        """
        Creates a single round of matches.
        """
        matches = []
        for i in range(0, len(players), 2):
            player1 = players[i]
            player2 = players[i + 1] if i + 1 < len(players) else None
            matches.append({
                "round": round_number,
                "match_number": (i // 2) + 1,
                "player1": player1,
                "player2": player2,
                "winner": None
            })
        return matches


    def generate_match_tree(self, participants):
        """
        Recursively generates the match tree with placeholders (TBD).
        Each match is represented as:
        { "round": X, "match_number": Y, "player1": "Alias1", "player2": "Alias2", "winner": None }
        """
        rounds = []
        current_round = self.create_round(participants, round_number=1)
        rounds.append(current_round)

        while len(current_round) > 1:
            winners = ["TBD"] * len(current_round)  # Placeholder for winners
            next_round = self.create_round(winners, round_number=len(rounds) + 1)
            rounds.append(next_round)
            current_round = next_round

        return [match for round_matches in rounds for match in round_matches]

    def create_round(self, players, round_number):
        """
        Creates a single round of matches.
        """
        matches = []
        for i in range(0, len(players), 2):
            player1 = players[i]
            player2 = players[i + 1] if i + 1 < len(players) else None
            matches.append({
                "round": round_number,
                "match_number": (i // 2) + 1,
                "player1": player1,
                "player2": player2,
                "winner": None
            })
        return matches

class SaveMatchResultView(APIView):
    """
    POST /api/tournament/<tournament_id>/match/<match_index>/save_result/
    Body: { "winner_alias": "PlayerAlias", "score_player1": 10, "score_player2": 8 }
    Saves the result of one match and progresses the tournament.
    """
    def post(self, request, tournament_id, match_index):
        winner_alias = request.data.get("winner_alias")
        score_player1 = request.data.get("score_player1")
        score_player2 = request.data.get("score_player2")

        if not winner_alias:
            return Response({"error": "winner_alias is required."}, status=status.HTTP_400_BAD_REQUEST)
        if score_player1 is None or score_player2 is None:
            return Response({"error": "Scores for both players are required."}, status=status.HTTP_400_BAD_REQUEST)

        with tournament_lock:
            tournament = tournaments.get(tournament_id)
            if not tournament:
                return Response({"error": "Tournament not found."}, status=status.HTTP_404_NOT_FOUND)

            with tournament["lock"]:
                try:
                    match_index = int(match_index)
                except ValueError:
                    return Response({"error": "Invalid match index."}, status=status.HTTP_400_BAD_REQUEST)

                if match_index < 0 or match_index >= len(tournament["matches"]):
                    return Response({"error": "Match index out of range."}, status=status.HTTP_404_NOT_FOUND)

                match = tournament["matches"][match_index]
                if match["winner"] is not None:
                    return Response({"error": "Match winner already set."}, status=status.HTTP_400_BAD_REQUEST)

                # Validate the winner is actually one of the players
                if winner_alias not in (match["player1"], match["player2"]):
                    return Response({"error": "Winner alias does not match players."}, status=status.HTTP_400_BAD_REQUEST)

                # Save the winner and scores
                match["winner"] = winner_alias
                match["score_player1"] = score_player1
                match["score_player2"] = score_player2

                # Propagate the winner to the next round
                self.propagate_winner(tournament["matches"], match)

                return Response({
                    "status": "result_saved",
                    "match": match,
                    "matches": tournament["matches"]
                })

    def propagate_winner(self, matches, completed_match):
        """
        Updates the next round match with the winner of the completed match.
        """
        print(f"Propagating winner of Match {completed_match['match_number']} (Round {completed_match['round']})")
        next_round_number = completed_match['round'] + 1
        next_match_number = (completed_match['match_number'] + 1) // 2

        for match in matches:
            if match["round"] == next_round_number and match["match_number"] == next_match_number:
                if match["player1"] == "TBD":
                    match["player1"] = completed_match["winner"]
                elif match["player2"] == "TBD":
                    match["player2"] = completed_match["winner"]
                break
        print("Updated matches:", matches)
