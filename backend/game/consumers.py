import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .game_state import GameState

# Dictionary to store game loops and game states for each game
game_loops = {}
game_states = {}
input_queues = {}

class PongGameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['room_name']
        self.game_group_name = f"game_{self.game_id}"

        # Add the WebSocket connection to the group
        await self.channel_layer.group_add(
            self.game_group_name,
            self.channel_name
        )

        # Accept the connection
        await self.accept()

        # Initialize game state, input queue, and game loop if they don't exist
        if self.game_id not in game_states:
            game_states[self.game_id] = GameState(self.game_id)
            input_queues[self.game_id] = asyncio.Queue()
            game_loops[self.game_id] = asyncio.create_task(self.game_loop(game_states[self.game_id], input_queues[self.game_id]))
        
        # Attach the existing game state to this consumer instance
        self.game_state = game_states[self.game_id]

    async def disconnect(self, close_code):
        # Remove the WebSocket connection from the group
        await self.channel_layer.group_discard(
            self.game_group_name,
            self.channel_name
        )

        # Clean up game state, input queue, and loop if no more players are connected
        if not self.channel_layer.groups[self.game_group_name]:
            if self.game_id in game_loops:
                game_loops[self.game_id].cancel()
                del game_loops[self.game_id]
            if self.game_id in game_states:
                del game_states[self.game_id]
            if self.game_id in input_queues:
                del input_queues[self.game_id]

    async def receive(self, text_data):
        data = json.loads(text_data)
        player = data["player"]  # "player1" or "player2"
        direction = data["direction"]  # "up" or "down"

        if direction not in ['up', 'down']:
            return
        
        # Add the input to the queue for the game loop to process
        await input_queues[self.game_id].put((player, direction))

    async def send_game_state(self, event):
        # Send the updated game state to the WebSocket client
        await self.send(text_data=json.dumps(event["game_state"]))

    async def game_loop(self, game_state, input_queue):
        game_state.game_is_active = True
        while game_state.game_is_active:
            # Process all inputs in the queue
            while not input_queue.empty():
                player, direction = await input_queue.get()
                game_state.update_paddle(player, direction)

            # Update ball position
            game_state.update_ball_position()

            # Broadcast the updated game state to all players
            await self.channel_layer.group_send(
                self.game_group_name,
                {
                    "type": "send_game_state",
                    "game_state": game_state.to_dict(),
                }
            )

            # Run the loop at 60 FPS
            await asyncio.sleep(1 / 60)

        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'game_over',
                'winner': 'player1' if game_state.score1 >= game_state.winning_score else 'player2'
            }
        )

class MatchmakingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        # Create a private group for the user
        self.user_group_name = f"user_{self.user.username}"
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the private group when the user disconnects
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    async def send_match_found(self, event):
        # Send the match details to the user
        match_data = event["data"]
        await self.send(text_data=json.dumps(match_data))
