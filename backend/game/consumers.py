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
        try:
            await self.channel_layer.group_add(
                self.game_group_name,
                self.channel_name
            )
            await self.accept()
            print(f"User connected to game group {self.game_group_name}.")
        except Exception as e:
            print(f"Error adding user to game group {self.game_group_name}: {e}")
            await self.close()
            return

        # Initialize game state, input queue, and game loop if they don't exist
        if self.game_id not in game_states:
            game_states[self.game_id] = GameState(self.game_id)
            input_queues[self.game_id] = asyncio.Queue()
            game_loops[self.game_id] = asyncio.create_task(
                self.game_loop(game_states[self.game_id], input_queues[self.game_id])
            )
            print(f"Initialized game state and loop for game {self.game_id}.")

        # Attach the existing game state to this consumer instance
        self.game_state = game_states[self.game_id]

    async def disconnect(self, close_code):
        # Remove the WebSocket connection from the group
        try:
            await self.channel_layer.group_discard(
                self.game_group_name,
                self.channel_name
            )
            print(f"User disconnected from game group {self.game_group_name}.")
        except Exception as e:
            print(f"Error removing user from game group {self.game_group_name}: {e}")

        # Clean up game state, input queue, and loop if no more players are connected
        group = self.channel_layer.groups.get(self.game_group_name, set())
        if not group:
            if self.game_id in game_loops:
                game_loops[self.game_id].cancel()
                del game_loops[self.game_id]
                print(f"Cancelled game loop for game {self.game_id}.")
            if self.game_id in game_states:
                del game_states[self.game_id]
                print(f"Deleted game state for game {self.game_id}.")
            if self.game_id in input_queues:
                del input_queues[self.game_id]
                print(f"Deleted input queue for game {self.game_id}.")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            player = data.get("player")  # "player1" or "player2"
            direction = data.get("direction")  # "up" or "down"

            if player not in ['player1', 'player2']:
                print(f"Invalid player identifier: {player}")
                return

            if direction not in ['up', 'down']:
                print(f"Invalid direction input: {direction}")
                return

            # Add the input to the queue for the game loop to process
            await input_queues[self.game_id].put((player, direction))
            print(f"Received input from {player}: {direction}")
        except json.JSONDecodeError:
            print("Received invalid JSON data.")
        except Exception as e:
            print(f"Error processing received data: {e}")

    async def send_game_state(self, event):
        try:
            await self.send(text_data=json.dumps(event["game_state"]))
            print(f"Sent game state to clients: {event['game_state']}")
        except Exception as e:
            print(f"Error sending game state: {e}")

    async def game_loop(self, game_state, input_queue):
        game_state.game_is_active = True
        try:
            while game_state.game_is_active:
                # Process all inputs in the queue
                while not input_queue.empty():
                    player, direction = await input_queue.get()
                    game_state.update_paddle(player, direction)
                    print(f"Updated paddle for {player}: {direction}")

                # Update ball position
                game_state.update_ball_position()
                print("Updated ball position.")

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
        except asyncio.CancelledError:
            print(f"Game loop for {self.game_id} has been cancelled.")
        except Exception as e:
            print(f"Error in game loop for {self.game_id}: {e}")
            game_state.game_is_active = False
        finally:
            # Notify players that the game is over
            winner = 'player1' if game_state.score1 >= game_state.winning_score else 'player2'
            await self.channel_layer.group_send(
                self.game_group_name,
                {
                    'type': 'game_over',
                    'winner': winner
                }
            )
            print(f"Game {self.game_id} over. Winner: {winner}")

    async def game_over(self, event):
        try:
            winner = event["winner"]
            await self.send(text_data=json.dumps({'game_over': True, 'winner': winner}))
            print(f"Sent game over notification to clients: Winner - {winner}")
        except Exception as e:
            print(f"Error sending game over notification: {e}")



class MatchmakingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            print(f"Authenticated user: {self.user.username}")
        else:
            await self.close()
            print("Unauthenticated connection rejected.")
            return

        self.user_group_name = f"user_{self.user.username}"

        try:
            await self.channel_layer.group_add(
                self.user_group_name,
                self.channel_name
            )
            await self.accept()
            print(f"User {self.user.username} connected to MatchmakingConsumer.")
        except Exception as e:
            print(f"Error connecting user {self.user.username} to group: {e}")
            await self.close()

    async def disconnect(self, close_code):
            # try:
                await self.channel_layer.group_discard(
                    self.user_group_name,
                    self.channel_name
                )
                print(f"User {self.user.username} disconnected from MatchmakingConsumer.")

            #     # Remove user from matchmaking queue if present
            #     async with matchmaking_lock:
            #         if self.user in matchmaking_queue:
            #             matchmaking_queue.remove(self.user)
            #             print(f"User {self.user.username} removed from matchmaking queue due to disconnection.")
            # except Exception as e:
            #     print(f"Error during disconnection of user {self.user.username}: {e}")

    async def send_match_found(self, event):
        try:
            match_data = event["data"]
            await self.send(text_data=json.dumps(match_data))
            print(f"Sent match found data to {self.user.username}: {match_data}")
        except Exception as e:
            print(f"Error sending match found to {self.user.username}: {e}")


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
