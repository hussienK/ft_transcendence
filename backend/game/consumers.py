import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .game_state import GameState
from urllib.parse import parse_qs

# Dictionary to store game loops and game states for each game
game_loops = {}
input_queues = {}
class PongGameConsumer(AsyncWebsocketConsumer):
    game_states = {}

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'game_{self.room_name}'
        self.user = self.scope["user"]

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
            if self.game_state.players_ready >= 2 and not self.game_state.game_is_active:
                self.game_state.start_game()
        else:
            self.game_state.player1= "player1"
            self.game_state.player2= "player2"
            self.game_state.is_local = True
            self.game_state.start_game()

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        if not self.is_local:
            self.game_state.players_ready -= 1

            if self.user == self.game_state.player1:
                self.game_state.player1 = None
                winner = self.game_state.player2
                loser = self.user
            elif self.user == self.game_state.player2:
                self.game_state.player2 = None
                winner = self.game_state.player1
                loser = self.user
            else:
                winner = None
                loser = None

            if self.game_state.players_ready < 2:
                self.game_state.stop_game()
                # Set the winner if there is one
                if winner and loser:
                    await self.game_state.handle_game_end(winner, loser, True)

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        player = data.get('player')
        direction = data.get('direction')

        if player and direction:
            # Update paddle position
            self.game_state.update_paddle(player, direction)

    # Send game state to WebSocket
    async def send_game_state(self):
        game_state_dict = self.game_state.to_dict()
        await self.send(text_data=json.dumps(game_state_dict))

    # Periodically send game state updates to all clients
    async def game_loop_broadcast(self):
        while self.game_state.game_is_active:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast_game_state',
                    'game_state': self.game_state.to_dict()
                }
            )
            await asyncio.sleep(0.016)  # ~60 times per second

    # Handler for broadcasting game state
    async def broadcast_game_state(self, event):
        game_state = event['game_state']
        await self.send(text_data=json.dumps(game_state))


class UpdatesConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # Authenticate the user
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            print("Connection rejected: unauthenticated user.")
            return

        self.user_group_name = f"user_{self.user.username}"

        # Add the user to their group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        await self.accept()

        print(f"WebSocket connection established for user {self.user.username}.")

    async def disconnect(self, close_code):
        # Remove the user from their group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
        print(f"WebSocket connection closed for user {self.user.username}.")

    async def receive(self, text_data):
        # Handle messages from the client if needed
        print(f"Received message from user {self.user.username}: {text_data}")

    async def send_update(self, event):
        # Send data to the client
        await self.send(text_data=json.dumps(event["data"]))

    async def send_match_found(self, event):
        try:
            match_data = event["data"]
            await self.send(text_data=json.dumps(match_data))
            print(f"Sent match found data to {self.user.username}: {match_data}")
        except Exception as e:
            print(f"Error sending match found to {self.user.username}: {e}")