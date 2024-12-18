import asyncio
import math
from asgiref.sync import sync_to_async
import time
import random

class GameState:
    def __init__(self, game_id, channel_layer, group_name, is_local=False, canvas_width=800, canvas_height=600, paddle_width=10, paddle_height=100, ball_radius=10):
        self.game_id = game_id
        self.score1 = 0
        self.score2 = 0
        self.winning_score = 10
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.paddle_width = paddle_width
        self.paddle_height = paddle_height
        self.ball_radius = ball_radius

        # Initialize paddle positions (centered vertically)
        self.paddle1_position = (canvas_height - paddle_height) // 2
        self.paddle2_position = (canvas_height - paddle_height) // 2

        # Initialize ball in the center with a random direction
        self.ball_position = [canvas_width // 2, canvas_height // 2]
        self.reset_ball_velocity()

        self.game_is_active = False
        self.players_ready = 0  # Track players who have joined

        self.update_task = None  # Placeholder for the game loop task

        self.channel_layer = channel_layer
        self.group_name = group_name

        self.player1 = None
        self.player2 = None
        self.winner = None
        self.loser = None

        self.is_local = is_local

    def reset_ball_velocity(self):
        angle = random.uniform(45, 135) if random.choice([True, False]) else random.uniform(225, 315)  # Tighter angles 
        speed = 4  # Reset speed to a reasonable value
        self.ball_velocity = [speed * math.cos(angle), speed * math.sin(angle)]

    def start_game(self):
        if not self.game_is_active and (self.players_ready >= 2 or self.is_local):
            self.game_is_active = True
            self.update_task = asyncio.create_task(self.game_loop())

    def stop_game(self):
        self.game_is_active = False

    async def game_loop(self):
        try:
            last_time = time.monotonic()
            while self.game_is_active:
                current_time = time.monotonic()
                elapsed_time = current_time - last_time
                last_time = current_time

                self.update_ball_position()
                await self.broadcast_state()

                await asyncio.sleep(max(0, 0.016 - elapsed_time))  # Ensure consistent frame rate

            if self.winner:
                await self.broadcast_final_state()
        except asyncio.CancelledError:
            pass

    async def handle_game_end(self, winner, loser, forfeit = False):
        self.winner = winner.username if winner else None

        await self.broadcast_final_state()

        try:
            # Call the synchronous save function in a thread-safe manner
            await sync_to_async(save_match_results_sync, thread_sensitive=False)(
                self.game_id, self.score1, self.score2, forfeit
            )
        except Exception as e:
            print(f"Error in async game end handler: {e}")


    def update_paddle(self, player, direction):
        if player == 'player1':
            new_position = self.paddle1_position + (-15 if direction == 'up' else 15)
            self.paddle1_position = max(0, min(new_position, self.canvas_height - self.paddle_height))
        elif player == 'player2':
            new_position = self.paddle2_position + (-15 if direction == 'up' else 15)
            self.paddle2_position = max(0, min(new_position, self.canvas_height - self.paddle_height))

    def update_ball_position(self):
        # Update ball position based on velocity
        self.ball_position[0] += self.ball_velocity[0]
        self.ball_position[1] += self.ball_velocity[1]

        # Collision with top and bottom walls
        if self.ball_position[1] - self.ball_radius < 0:
            self.ball_position[1] = self.ball_radius
            self.ball_velocity[1] *= -1
        elif self.ball_position[1] + self.ball_radius > self.canvas_height:
            self.ball_position[1] = self.canvas_height - self.ball_radius
            self.ball_velocity[1] *= -1

        # Collision with paddles
        # Left paddle
        if self.ball_position[0] - self.ball_radius <= self.paddle_width:
            if self.paddle1_position <= self.ball_position[1] <= self.paddle1_position + self.paddle_height:
                self.ball_position[0] = self.paddle_width + self.ball_radius
                self.ball_velocity[0] *= -1
                offset = (self.ball_position[1] - (self.paddle1_position + self.paddle_height / 2)) / (self.paddle_height / 2)
                self.ball_velocity[1] = offset * 5

        # Right paddle
        if self.ball_position[0] + self.ball_radius >= self.canvas_width - self.paddle_width:
            if self.paddle2_position <= self.ball_position[1] <= self.paddle2_position + self.paddle_height:
                self.ball_position[0] = self.canvas_width - self.paddle_width - self.ball_radius
                self.ball_velocity[0] *= -1
                offset = (self.ball_position[1] - (self.paddle2_position + self.paddle_height / 2)) / (self.paddle_height / 2)
                self.ball_velocity[1] = offset * 5

        # Check for scoring
        if self.ball_position[0] < 0:
            self.score2 += 1
            self.reset_ball()
        elif self.ball_position[0] > self.canvas_width:
            self.score1 += 1
            self.reset_ball()

        # Check for game over
        if self.score1 >= self.winning_score or self.score2 >= self.winning_score:
            self.game_is_active = False
            if self.score1 > self.score2:
                asyncio.create_task(self.handle_game_end(self.player1, self.player2))
            else:
                asyncio.create_task(self.handle_game_end(self.player2, self.player1))


    def reset_ball(self):
        self.ball_position = [self.canvas_width // 2, self.canvas_height // 2]
        self.reset_ball_velocity()

    def to_dict(self):
        return {
            'score1': self.score1,
            'score2': self.score2,
            'paddle1_position': self.paddle1_position,
            'paddle2_position': self.paddle2_position,
            'ball_position': self.ball_position,
            'game_is_active': self.game_is_active,
            'game_over': not self.game_is_active,
            'winner': 'player1' if self.score1 > self.score2 else 'player2'
        }

    async def broadcast_state(self):
        game_state_dict = self.to_dict()
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'broadcast_game_state',
                'game_state': game_state_dict
            }
        )

    async def broadcast_final_state(self):
        game_state_dict = self.to_dict()
        print(f"\n\n{game_state_dict}\n\n\n")
        game_state_dict['game_over'] = True
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'broadcast_game_state',
                'game_state': game_state_dict
            }
        )

        # if not self.is_local:
        #     self.save_match_results()

    def debug_state(self):
        print(f"Ball position: {self.ball_position}, Velocity: {self.ball_velocity}")
        print(f"Paddle1 position: {self.paddle1_position}, Paddle2 position: {self.paddle2_position}")

def save_match_results_sync(game_id, score1, score2, forfeit):
    """Synchronously save match results to the database."""
    from .models import GameSession, MatchHistory

    try:
        # Fetch the GameSession object
        game_session = GameSession.objects.get(session_id=game_id)

        # Create a MatchHistory entry
        MatchHistory.objects.create(
            game_session=game_session,
            player1=game_session.player1,
            player2=game_session.player2,
            forfeit=forfeit,
            player1_score=score1,
            player2_score=score2,
        )

        print("Match history updated successfully")
    except Exception as e:
        print(f"Error updating match history: {e}")