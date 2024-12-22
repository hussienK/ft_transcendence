import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from urllib.parse import parse_qs
import time
from asyncio import Lock

from .game_state import GameState

class PongGameConsumer(AsyncWebsocketConsumer):
    game_states = {}
    game_state_lock = Lock()

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'game_{self.room_name}'
        self.user = self.scope["user"]
        self.countdown_in_progress = False

        query_params = parse_qs(self.scope['query_string'].decode('utf-8'))
        try:
            is_local = query_params.get('is_local', ['false'])[0].lower() == 'true'
            self.is_local = is_local
        except:
            self.is_local = False

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Initialize or retrieve GameState
        if self.room_name not in self.game_states:
            self.game_states[self.room_name] = GameState(
                game_id=self.room_name,
                channel_layer=self.channel_layer,
                group_name=self.room_group_name
            )

        self.game_state = self.game_states[self.room_name]

        if not self.is_local:
            self.game_state.players_ready += 1

            if not self.game_state.player1:
                self.game_state.player1 = self.user
                self.player = 'player1'
            elif not self.game_state.player2:
                self.game_state.player2 = self.user
                self.player = 'player2'
            else:
                await self.close()
                return

            # When both players are ready, start a countdown in the background
            if self.game_state.players_ready >= 2 and not self.game_state.game_is_active:
                asyncio.create_task(self.start_countdown())
        else:
            self.game_state.player1 = "player1"
            self.game_state.player2 = "player2"
            self.game_state.is_local = True
            asyncio.create_task(self.start_countdown_local())


        await self.accept()

    async def start_countdown_local(self):
        self.countdown_in_progress = True
        try:
            for i in range(3, 0, -1):
                if not self.countdown_in_progress:  # Check if countdown was interrupted
                    break
                await self.broadcast_special_state(phase="countdown", countdown=i)
                await asyncio.sleep(1)
        finally:
            self.countdown_in_progress = False
            self.game_state.start_game()

    async def start_countdown(self):
        self.countdown_in_progress = True
        try:
            for i in range(3, 0, -1):
                if not self.countdown_in_progress:  # Check if countdown was interrupted
                    break
                await self.broadcast_special_state(phase="countdown", countdown=i)
                await asyncio.sleep(1)
        finally:
            self.countdown_in_progress = False
            if self.game_state.players_ready >= 2:  # Only start the game if two players are still present
                self.game_state.start_game()


    async def broadcast_special_state(self, phase=None, countdown=None):
        # Broadcast a special state (like countdown) to all clients
        state = self.game_state.to_dict()
        # Add extra info for the countdown or phase
        if phase:
            state['phase'] = phase
        if countdown is not None:
            state['countdown'] = countdown
        state['timestamp'] = time.time()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_game_state',
                'game_state': state
            }
        )

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        if not self.is_local:
            # Decrement the players ready count
            self.game_state.players_ready -= 1

            winner = None
            loser = None

            # Identify the disconnecting user and the remaining user
            if self.user == self.game_state.player1:
                self.game_state.player1 = None
                winner = self.game_state.player2  # Remaining player
                self.game_state.winner = winner
                loser = self.user
            elif self.user == self.game_state.player2:
                self.game_state.player2 = None
                winner = self.game_state.player1  # Remaining player
                self.game_state.winner = winner
                loser = self.user

            # If less than 2 players are left, stop the game
            if self.game_state.players_ready < 2:
                if self.countdown_in_progress:  # Countdown is running
                    self.countdown_in_progress = False  # Stop the countdown
                self.game_state.stop_game()

                # Set the winner if there is one remaining player
                if winner:
                    await self.game_state.handle_game_end(winner, loser, True)

    async def receive(self, text_data):
        data = json.loads(text_data)
        player = data.get('player')
        direction = data.get('direction')

        if player and direction:
            self.game_state.update_paddle(player, direction)

    async def send_game_state(self):
        # Add timestamp and possibly phase info
        state = self.game_state.to_dict()
        state['timestamp'] = time.time()
        if not self.game_state.game_is_active and not self.countdown_in_progress:
            state['phase'] = 'ended' if self.game_state.winner else 'waiting'
        await self.send(text_data=json.dumps(state))

    async def game_loop_broadcast(self):
        while self.game_state.game_is_active:
            state = self.game_state.to_dict()
            state['timestamp'] = time.time()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast_game_state',
                    'game_state': state
                }
            )
            await asyncio.sleep(0.016)  # ~60 times per second

    async def broadcast_game_state(self, event):
        # Add timestamp if not already there
        game_state = event['game_state']
        if 'timestamp' not in game_state:
            game_state['timestamp'] = time.time()
        await self.send(text_data=json.dumps(game_state))


class UpdatesConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            print("Connection rejected: unauthenticated user.")
            return

        self.user_group_name = f"user_{self.user.username}"

        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        await self.accept()

        print(f"WebSocket connection established for user {self.user.username}.")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
        print(f"WebSocket connection closed for user {self.user.username}.")

    async def receive(self, text_data):
        print(f"Received message from user {self.user.username}: {text_data}")

    async def send_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    async def send_match_found(self, event):
        try:
            match_data = event["data"]
            await self.send(text_data=json.dumps(match_data))
            print(f"Sent match found data to {self.user.username}: {match_data}")
        except Exception as e:
            print(f"Error sending match found to {self.user.username}: {e}")
