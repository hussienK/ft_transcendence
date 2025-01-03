import asyncio
import random
from asgiref.sync import sync_to_async
import time

class GameState:
    def __init__(self, game_id, channel_layer, group_name):
        self.game_id = game_id
        self.channel_layer = channel_layer
        self.group_name = group_name

        # Player and game state tracking
        self.players_ready = 0
        self.player1 = None
        self.player2 = None
        self.is_local = False
        self.is_updates = False
        self.game_is_active = False

        # Dimensions
        self.canvas_width = 800
        self.canvas_height = 600
        self.paddle_width = 10
        self.paddle_height = 100
        self.ball_radius = 10

        # Initial positions and scores
        self.paddle1_position = (self.canvas_height - self.paddle_height) // 2
        self.paddle2_position = (self.canvas_height - self.paddle_height) // 2
        self.score1 = 0
        self.score2 = 0
        self.winner = None

        # Ball state
        self.ball_position = [self.canvas_width // 2, self.canvas_height // 2]
        self.ball_velocity = [4, 4]  # Will be randomized at start
        self.speed_increment_factor = 1.05  # How much the ball speeds up on each paddle hit
        self.max_ball_speed = 12
        self.padd_speed = 18

        #stats
        self.match_start_time = None
        self.total_ball_hits = 0
        self.current_rally = 0  # Track ongoing rally (consecutive hits)
        self.longest_rally = 0
        self.total_ball_speed = 0.0  # Sum of all recorded ball speeds
        self.ball_speed_samples = 0  # Number of times speed is recorded
        self.max_ball_speed_reached = 0.0
        self.current_rally_hits = 0
        self.game_loop_task = None
        self.player1_reaction_times = []  # List to store reaction times for Player 1
        self.player2_reaction_times = []  # List to store reaction times for Player 2
        self.last_hit_time = None         # Timestamp of the last paddle hit
        self.last_hitter = None           # Tracks who hit the ball last ('player1' or 'player2')

    def start_game(self):
        # Reset and randomize the ball at the start or after a score
        self.match_start_time = time.time()
        self.reset_ball(random_direction=True)
        self.game_is_active = True
        # Start a background task to update the game state
        self.game_loop_task = asyncio.ensure_future(self.game_loop())

    def stop_game(self):
        self.game_is_active = False
        if self.game_loop_task and not self.game_loop_task.done():
            self.game_loop_task.cancel()

    async def game_loop(self):
        try:
            # Run the game loop at ~60 FPS
            while self.game_is_active:
                await self.update_ball_position()
                await self.broadcast_state()
                await asyncio.sleep(0.016)
        except asyncio.CancelledError:
            pass

    async def update_ball_position(self):
        # Move the ball
        self.ball_position[0] += self.ball_velocity[0]
        self.ball_position[1] += self.ball_velocity[1]

        # Calculate current ball speed
        current_speed = (self.ball_velocity[0]**2 + self.ball_velocity[1]**2)**0.5
        self.total_ball_speed += current_speed
        self.ball_speed_samples += 1
        if current_speed > self.max_ball_speed_reached:
            self.max_ball_speed_reached = current_speed

    # Check for collision with top and bottom walls
        if self.ball_position[1] <= self.ball_radius:  # Top border
            self.ball_position[1] = self.ball_radius  # Push the ball slightly inside
            self.ball_velocity[1] = abs(self.ball_velocity[1])  # Ensure positive velocity

        elif self.ball_position[1] >= (self.canvas_height - self.ball_radius):  # Bottom border
            self.ball_position[1] = self.canvas_height - self.ball_radius  # Push the ball slightly inside
            self.ball_velocity[1] = -abs(self.ball_velocity[1])  # Ensure negative velocity


        # Check paddle collisions
        # Left paddle (player1)
        if (self.ball_position[0] - self.ball_radius <= self.paddle_width + 10 and
            self.paddle1_position <= self.ball_position[1] <= self.paddle1_position + self.paddle_height):
            self.ball_position[0] = self.paddle_width + 10 + self.ball_radius
            self.calculate_paddle_bounce('player1')

        # Right paddle (player2)
        elif (self.ball_position[0] + self.ball_radius >= self.canvas_width - (self.paddle_width + 10) and
              self.paddle2_position <= self.ball_position[1] <= self.paddle2_position + self.paddle_height):
            self.ball_position[0] = self.canvas_width - (self.paddle_width + 10) - self.ball_radius
            self.calculate_paddle_bounce('player2')

        # Check scoring conditions
        if self.ball_position[0] < 0:
            self.score2 += 1
            self.current_rally_hits = 0  # Reset current rally
            self.last_hit_time = None  # Reset reaction time tracking
            self.last_hitter = None
            await self.check_winner()
            if self.game_is_active:
                self.reset_ball(random_direction=True)
        elif self.ball_position[0] > self.canvas_width:
            self.score1 += 1
            self.current_rally_hits = 0  # Reset current rally
            self.last_hit_time = None  # Reset reaction time tracking
            self.last_hitter = None
            await self.check_winner()
            if self.game_is_active:
                self.reset_ball(random_direction=True)

    def calculate_paddle_bounce(self, player):
        # Determine ball's vertical bounce based on where it hit the paddle
        if player == 'player1':
            relative_intersect_y = (self.ball_position[1] - self.paddle1_position) - (self.paddle_height / 2)
        else:
            relative_intersect_y = (self.ball_position[1] - self.paddle2_position) - (self.paddle_height / 2)

        normalized_intersect_y = relative_intersect_y / (self.paddle_height / 2)
        # Change ball angle depending on the intersection point
        # Max angle ~45 degrees
        max_angle = 45 * (3.14159 / 180)  # in radians
        bounce_angle = normalized_intersect_y * max_angle

        # Update ball velocity direction based on the bounce angle
        speed = (self.ball_velocity[0]**2 + self.ball_velocity[1]**2) ** 0.5
        # Ball always moves horizontally away from the paddle it just hit
        direction = 1 if player == 'player1' else -1

        # Calculate new velocities based on angle and speed
        self.ball_velocity[0] = direction * (speed * (1.0 / (2**0.5))) * 2 * (abs(bounce_angle) / max_angle + 0.5)
        self.ball_velocity[1] = (speed * (1.0 / (2**0.5))) * (abs(normalized_intersect_y) * 2) * (1 if bounce_angle > 0 else -1)

        # Ensure a minimum horizontal speed
        if abs(self.ball_velocity[0]) < 3:
            self.ball_velocity[0] = 3 * direction

        # Increase the speed slightly each time it hits a paddle
        self.ball_velocity[0] *= self.speed_increment_factor
        self.ball_velocity[1] *= self.speed_increment_factor
        
        self.clamp_ball_speed()

        self.total_ball_hits += 1

        # # # Increment current rally hits
        self.current_rally_hits += 1
        
        # # # Update longest rally if current rally exceeds it
        if self.current_rally_hits > self.longest_rally:
            self.longest_rally = self.current_rally_hits

        if self.last_hit_time and self.last_hitter != player:
            # Calculate reaction time
            reaction_time = time.time() - self.last_hit_time
            if player == 'player1':
                self.player1_reaction_times.append(reaction_time)
            elif player == 'player2':
                self.player2_reaction_times.append(reaction_time)
        
        # Update last hit time and hitter
        self.last_hit_time = time.time()
        self.last_hitter = player
        
    def clamp_ball_speed(self):
        # Ensure the ball's speed does not exceed the maximum allowed speed
        speed = (self.ball_velocity[0]**2 + self.ball_velocity[1]**2) ** 0.5
        if speed > self.max_ball_speed:
            factor = self.max_ball_speed / speed
            self.ball_velocity[0] *= factor
            self.ball_velocity[1] *= factor

    async def check_winner(self):
        if self.score1 >= 5:
            await self.handle_game_end(self.player1, self.player2, False)
        elif self.score2 >= 5:
            await self.handle_game_end(self.player2, self.player1, False)

    def reset_ball(self, random_direction=False):
        self.ball_position = [self.canvas_width // 2, self.canvas_height // 2]
        speed = 4
        if random_direction:
            # Randomize initial direction for variety
            angle = random.uniform(-0.5, 0.5)  # small angle variation
            direction = random.choice([-1, 1])
            self.ball_velocity = [direction * speed, speed * angle]
        else:
            self.ball_velocity = [4, 4]

    def update_paddle(self, player, direction):
        # Move the specified player's paddle with boundaries
        if player == 'player1':
            if direction == 'up':
                self.paddle1_position = max(self.paddle1_position - self.padd_speed, 0)
            elif direction == 'down':
                self.paddle1_position = min(self.paddle1_position + self.padd_speed, self.canvas_height - self.paddle_height)
        elif player == 'player2':
            if direction == 'up':
                self.paddle2_position = max(self.paddle2_position - self.padd_speed, 0)
            elif direction == 'down':
                self.paddle2_position = min(self.paddle2_position + self.padd_speed, self.canvas_height - self.paddle_height)

    async def handle_game_end(self, winner, loser, disconnected=False):
        self.game_is_active = False

        # Determine the winner explicitly
        if disconnected:
            # If a player disconnected, the remaining player is the winner
            if self.player1 == winner:
                self.winner = "player1"
            elif self.player2 == winner:
                self.winner = "player2"
        else:
            # Determine winner based on scores
            if self.score1 > self.score2:
                self.winner = "player1"
            elif self.score2 > self.score1:
                self.winner = "player2"
            else:
                self.winner = "draw"

        match_duration = round(time.time() - self.match_start_time, 2) if self.match_start_time else 0
        avg_ball_speed = self.total_ball_speed / self.ball_speed_samples if self.ball_speed_samples > 0 else 0.0

        # Calculate average reaction times
        avg_reaction_time_player1 = sum(self.player1_reaction_times) / len(self.player1_reaction_times) if self.player1_reaction_times else 0
        avg_reaction_time_player2 = sum(self.player2_reaction_times) / len(self.player2_reaction_times) if self.player2_reaction_times else 0

        victory_margin = abs(self.score1 - self.score2)

        # Broadcast the final state
        await self.broadcast_state()

        # Save the match results
        if not self.is_local:
            try:
                await sync_to_async(save_match_results_sync, thread_sensitive=False)(
                    self.game_id, self.score1, self.score2, disconnected, match_duration, self.total_ball_hits, self.longest_rally,
                    self.max_ball_speed_reached, avg_ball_speed, avg_reaction_time_player1, avg_reaction_time_player2, victory_margin, self.winner
                )
                print("Data saved to database")
            except Exception as e:
                print(f"Error saving match results: {e}")

        # Stop the game loop
        self.stop_game()


    async def broadcast_state(self):
        if (not self.is_updates):
            if self.channel_layer:
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'broadcast_game_state',
                        'game_state': self.to_dict()
                    }
                )

    def to_dict(self):
        match_duration = round(time.time() - self.match_start_time, 2) if self.match_start_time else 0
        return {
            'ball_position': self.ball_position,
            'paddle1_position': self.paddle1_position,
            'paddle2_position': self.paddle2_position,
            'score1': self.score1,
            'score2': self.score2,
            'game_is_active': self.game_is_active,
            'winner': self.winner,
            'match_duration': match_duration,
        }

def save_match_results_sync(game_id, score1, score2, forfeit=False, match_duration=0, total_ball_hits=0, longest_rally=0,
                            max_ball_speed_reached=0, avg_ball_speed=0, avg_reaction_time_player1=0, avg_reaction_time_player2=0, victory_margin=0, winner=None):
    """Synchronously save match results to the database."""
    from .models import GameSession, MatchHistory

    try:
        # Fetch the GameSession object
        game_session = GameSession.objects.get(session_id=game_id)

        # Determine forfeited player
        forfeited_by = None
        if forfeit:
            if winner == "player1":
                forfeited_by = game_session.player2
            elif winner == "player2":
                forfeited_by = game_session.player1
        print("\n\nForfeited by: ", forfeited_by)

        # Create a MatchHistory entry
        MatchHistory.objects.create(
            game_session=game_session,
            player1=game_session.player1,
            player2=game_session.player2,
            forfeit=forfeit,
            forfeited_by=forfeited_by,
            player1_score=score1,
            player2_score=score2,
            match_duration=match_duration,
            total_ball_hits=total_ball_hits,
            longest_rally=longest_rally,
            max_ball_speed=max_ball_speed_reached,
            avg_ball_speed=avg_ball_speed,
            reaction_time_player1=avg_reaction_time_player1,
            reaction_time_player2=avg_reaction_time_player2,
            victory_margin=victory_margin
        )

        print("Match history updated successfully")
    except GameSession.DoesNotExist:
        print(f"Error: Game session with ID {game_id} does not exist.")
    except Exception as e:
        print(f"Error updating match history: {e}")
