class GameState:
	def __init__(self, game_id):
		self.game_id = game_id
		# Game dimensions
		self.width = 800
		self.height = 600

		# Ball properties
		self.ball_x = self.width / 2
		self.ball_y = self.height / 2
		self.ball_radius = 10
		self.ball_speed_x = 5  # Pixels per frame
		self.ball_speed_y = 5

		# Paddle properties
		self.paddle_width = 10
		self.paddle_height = 100
		self.paddle_speed = 10  # Pixels per input

		# Player 1 paddle
		self.paddle1_y = self.height / 2 - self.paddle_height / 2

		# Player 2 paddle
		self.paddle2_y = self.height / 2 - self.paddle_height / 2

		# Scores
		self.score1 = 0
		self.score2 = 0
        
		self.game_is_active = False
        
		

	def to_dict(self):
		return {
			"ball": {
				"x": self.ball_x,
				"y": self.ball_y,
				"radius": self.ball_radius,
			},
			"paddle1": {
				"y": self.paddle1_y,
				"width": self.paddle_width,
				"height": self.paddle_height,
			},
			"paddle2": {
				"y": self.paddle2_y,
				"width": self.paddle_width,
				"height": self.paddle_height,
			},
			"scores": {
				"player1": self.score1,
				"player2": self.score2,
			},
		}

	def update_ball_position(self):
		# Update ball position
		self.ball_x += self.ball_speed_x
		self.ball_y += self.ball_speed_y

		# Wall collision
		if self.ball_y <= 0 or self.ball_y >= self.height:
			self.ball_speed_y *= -1

		# Paddle collision (left)
		if (self.ball_x - self.ball_radius <= self.paddle_width and
			self.paddle1_y <= self.ball_y <= self.paddle1_y + self.paddle_height):
			self.ball_speed_x *= -1

		# Paddle collision (right)
		if (self.ball_x + self.ball_radius >= self.width - self.paddle_width and
			self.paddle2_y <= self.ball_y <= self.paddle2_y + self.paddle_height):
			self.ball_speed_x *= -1

		# Scoring
		if self.ball_x < 0:
			self.score2 += 1
			self.reset_ball()
		elif self.ball_x > self.width:
			self.score1 += 1
			self.reset_ball()
			
		#check for winners
		winning_score = 10
		if self.score1 >= winning_score or self.score2 >= winning_score:
			self.game_is_active = False
			# SAVE GAME DATA IN DB

	def update_paddle(self, player, direction):
		if player == "player1":
			if direction == "up":
				self.paddle1_y = max(0, self.paddle1_y - self.paddle_speed)
			elif direction == "down":
				self.paddle1_y = min(self.height - self.paddle_height, self.paddle1_y + self.paddle_speed)
		elif player == "player2":
			if direction == "up":
				self.paddle2_y = max(0, self.paddle2_y - self.paddle_speed)
			elif direction == "down":
				self.paddle2_y = min(self.height - self.paddle_height, self.paddle2_y + self.paddle_speed)

	def reset_ball(self):
		self.ball_x = self.width / 2
		self.ball_y = self.height / 2
		self.ball_speed_x *= -1
		self.ball_speed_y *= -1
