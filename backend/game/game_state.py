# game_state.py

import asyncio

class GameState:
    def __init__(self, game_id):
        self.game_id = game_id
        self.score1 = 0
        self.score2 = 0
        self.winning_score = 10
        self.paddle1_position = 0
        self.paddle2_position = 0
        self.ball_position = [0, 0]
        self.ball_velocity = [1, 1]
        self.game_is_active = False
        # Add any other necessary initialization

    def update_paddle(self, player, direction):
        if player == 'player1':
            if direction == 'up':
                self.paddle1_position -= 1
            elif direction == 'down':
                self.paddle1_position += 1
        elif player == 'player2':
            if direction == 'up':
                self.paddle2_position -= 1
            elif direction == 'down':
                self.paddle2_position += 1

    def update_ball_position(self):
        # Simple ball movement logic
        self.ball_position[0] += self.ball_velocity[0]
        self.ball_position[1] += self.ball_velocity[1]
        # Add collision detection and scoring logic as needed

        # Example collision with top/bottom
        if self.ball_position[1] <= 0 or self.ball_position[1] >= 100:
            self.ball_velocity[1] *= -1

        # Example scoring
        if self.ball_position[0] <= 0:
            self.score2 += 1
            self.reset_ball()
        elif self.ball_position[0] >= 100:
            self.score1 += 1
            self.reset_ball()

        # Check for game over
        if self.score1 >= self.winning_score or self.score2 >= self.winning_score:
            self.game_is_active = False

    def reset_ball(self):
        self.ball_position = [50, 50]
        self.ball_velocity = [1, 1]

    def to_dict(self):
        return {
            'score1': self.score1,
            'score2': self.score2,
            'paddle1_position': self.paddle1_position,
            'paddle2_position': self.paddle2_position,
            'ball_position': self.ball_position,
            'game_is_active': self.game_is_active,
        }
