function attachGameEventListeners2()
{
        // Adjust the WebSocket URL according to your server setup
        const roomName = 'game399';  // Replace with your game room name
        const player = 'player2';  // Replace with 'player2' for the second player

        const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
        const ws_path = ws_scheme + '://' + window.location.host + '/ws/game/' + roomName + '/';
        const socket = new WebSocket(ws_path);

        // Canvas setup
        const canvas = document.getElementById('canvas2');
        const ctx = canvas.getContext('2d');

        // Game variables
        let gameState = null;

        socket.onopen = function(event) {
            console.log("WebSocket connection established.");
        };

        socket.onmessage = function(event) {
            // Parse the game state received from the server
            gameState = JSON.parse(event.data);
            // Render the game state
            renderGame();
        };

        socket.onclose = function(event) {
            console.log("WebSocket connection closed.");
        };

        socket.onerror = function(error) {
            console.error("WebSocket error observed:", error);
        };

        // Event listeners for player input
        document.addEventListener('keydown', function(event) {
            let direction = null;
            if (event.key === 'ArrowUp') {
                direction = 'up';
            } else if (event.key === 'ArrowDown') {
                direction = 'down';
            }

            if (direction) {
                const message = {
                    'player': player,
                    'direction': direction
                };
                socket.send(JSON.stringify(message));
            }
        });

        // Render the game state on the canvas
        function renderGame() {
            if (!gameState) return;

            // Clear the canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Draw the ball
            ctx.fillStyle = 'white';
            ctx.beginPath();
            ctx.arc(gameState.ball.x, gameState.ball.y, gameState.ball.radius, 0, Math.PI * 2);
            ctx.fill();

            // Draw paddles
            ctx.fillRect(
                10, // Paddle 1 X position
                gameState.paddle1.y,
                gameState.paddle1.width,
                gameState.paddle1.height
            );

            ctx.fillRect(
                canvas.width - gameState.paddle2.width - 10, // Paddle 2 X position
                gameState.paddle2.y,
                gameState.paddle2.width,
                gameState.paddle2.height
            );

            // Draw scores
            ctx.font = '30px Arial';
            ctx.fillText(gameState.scores.player1, canvas.width / 2 - 50, 50);
            ctx.fillText(gameState.scores.player2, canvas.width / 2 + 30, 50);
        }
}
