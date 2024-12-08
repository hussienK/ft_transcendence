import asyncio
import math
from asgiref.sync import sync_to_async

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
        angle = math.radians(30)  # Starting at 30 degrees
        speed = 30  # Initial speed
        self.ball_velocity = [speed * math.cos(angle), speed * math.sin(angle)]

        self.game_is_active = False
        self.players_ready = 0  # Track players who have joined

        self.update_task = None  # Placeholder for the game loop task

        self.channel_layer = channel_layer
        self.group_name = group_name

        self.player1 = "player1"
        self.player2 = "player2"
        self.winner = None
        self.loser = None

        self.is_local = is_local

    def start_game(self):
        if not self.game_is_active and (self.players_ready >= 2 or self.is_local):
            self.game_is_active = True
            self.update_task = asyncio.create_task(self.game_loop())

    def stop_game(self):
        self.game_is_active = False

    async def game_loop(self):
        try:
            while self.game_is_active:
                self.update_ball_position()
                await self.broadcast_state()
                await asyncio.sleep(0.016)

            if self.winner:
                await self.broadcast_final_state()
        except asyncio.CancelledError:
            pass

    def update_paddle(self, player, direction):
        if player == 'player1':
            if direction == 'up':
                self.paddle1_position -= 10  # Move paddle up by 10 pixels
            elif direction == 'down':
                self.paddle1_position += 10  # Move paddle down by 10 pixels

            # Constrain paddle within canvas
            self.paddle1_position = max(0, min(self.paddle1_position, self.canvas_height - self.paddle_height))

        elif player == 'player2':
            if direction == 'up':
                self.paddle2_position -= 10
            elif direction == 'down':
                self.paddle2_position += 10

            self.paddle2_position = max(0, min(self.paddle2_position, self.canvas_height - self.paddle_height))

    def update_ball_position(self):
        # Update ball position based on velocity
        self.ball_position[0] += self.ball_velocity[0]
        self.ball_position[1] += self.ball_velocity[1]

        # Collision with top and bottom walls
        if self.ball_position[1] - self.ball_radius <= 0 or self.ball_position[1] + self.ball_radius >= self.canvas_height:
            self.ball_velocity[1] *= -1  # Reverse Y direction

        # Collision with paddles
        # Left paddle
        if (self.ball_position[0] - self.ball_radius <= self.paddle_width):
            if self.paddle1_position <= self.ball_position[1] <= self.paddle1_position + self.paddle_height:
                self.ball_velocity[0] *= -1  # Reverse X direction
                # Adjust Y velocity based on where it hit the paddle
                offset = (self.ball_position[1] - (self.paddle1_position + self.paddle_height / 2)) / (self.paddle_height / 2)
                self.ball_velocity[1] = offset * 5  # Adjust Y velocity

        # Right paddle
        if (self.ball_position[0] + self.ball_radius >= self.canvas_width - self.paddle_width):
            if self.paddle2_position <= self.ball_position[1] <= self.paddle2_position + self.paddle_height:
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
                self.winner = self.player1
                self.loser = self.player2
            else:
                self.winner = self.player2
                self.loser = self.player1

    def reset_ball(self):
        self.ball_position = [self.canvas_width // 2, self.canvas_height // 2]
        angle = math.radians(30)  # Reset angle
        speed = 30  # Reset speed
        self.ball_velocity = [speed * math.cos(angle), speed * math.sin(angle)]

    def to_dict(self):
        return {
            'score1': self.score1,
            'score2': self.score2,
            'paddle1_position': self.paddle1_position,
            'paddle2_position': self.paddle2_position,
            'ball_position': self.ball_position,
            'game_is_active': self.game_is_active,
            'game_over': not self.game_is_active,
            'winner': self.winner
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
        game_state_dict['game_over'] = True
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'broadcast_game_state',
                'game_state': game_state_dict
            }
        )
