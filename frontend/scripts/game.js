function attachGameEventListeners(roomName, player) {
    const ws_path = "wss://" + window.location.host + '/ws/game/' + roomName + '/' + '?token=' + localStorage.getItem('accessToken');
    console.log("WebSocket URL:", ws_path);
    const socket = new WebSocket(ws_path);

    // Canvas setup
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');

    // Game variables
    let gameState = null;
    let keyInterval = null; // Interval for continuous movement
    let currentDirection = null; // Track the current direction

    socket.onopen = function(event) {
        console.log("WebSocket connection established for Game.");
    };

    socket.onmessage = function(event) {
        // Parse the game state received from the server
        gameState = JSON.parse(event.data);
        // Render the game state
        renderGame();
    };

    socket.onclose = function(event) {
        console.log("WebSocket connection closed.");
        // Optionally, display a message or redirect
    };

    socket.onerror = function(error) {
        console.error("WebSocket error observed:", error);
    };

    // Event listeners for player input
    document.addEventListener('keydown', function(event) {
        if ((event.key === 'ArrowUp' || event.key === 'ArrowDown') && currentDirection !== event.key) {
            currentDirection = event.key; // Update the current direction
            sendDirection(event.key); // Send the initial direction

            // Start sending direction continuously
            keyInterval = setInterval(() => sendDirection(event.key), 50); // Adjust interval as needed
            event.preventDefault(); // Prevent default scrolling behavior
        }
    });

    document.addEventListener('keyup', function(event) {
        if (event.key === 'ArrowUp' || event.key === 'ArrowDown') {
            currentDirection = null; // Reset the current direction
            clearInterval(keyInterval); // Stop sending direction
            sendDirection(null); // Optionally, send a stop message
            event.preventDefault();
        }
    });

    function sendDirection(key) {
        let direction = null;
        if (key === 'ArrowUp') {
            direction = 'up';
        } else if (key === 'ArrowDown') {
            direction = 'down';
        }
        const message = {
            'player': player,
            'direction': direction
        };
        socket.send(JSON.stringify(message));
    }

    // Render the game state on the canvas
    function renderGame() {
        if (!gameState) return;

        // Clear the canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw the ball
        const ballPosition = gameState.ball_position;
        ctx.fillStyle = 'white';
        ctx.beginPath();
        ctx.arc(ballPosition[0], ballPosition[1], 10, 0, Math.PI * 2); // Adjust radius as needed
        ctx.fill();

        // Draw paddles
        ctx.fillStyle = 'white';
        ctx.fillRect(
            10, // Paddle 1 X position
            gameState.paddle1_position, // Paddle 1 Y position
            10, // Paddle width
            100 // Paddle height
        );

        ctx.fillRect(
            canvas.width - 20, // Paddle 2 X position
            gameState.paddle2_position, // Paddle 2 Y position
            10, // Paddle width
            100 // Paddle height
        );

        // Draw scores
        ctx.font = '30px Arial';
        ctx.fillText(gameState.score1, canvas.width / 2 - 50, 50); // Score for player 1
        ctx.fillText(gameState.score2, canvas.width / 2 + 30, 50); // Score for player 2

        // Check if the game is active
        if (!gameState.game_is_active) {
            ctx.font = '50px Arial';
            ctx.fillStyle = 'red';
            if (gameState.winner === player)
                ctx.fillText("You Won!", canvas.width / 2 - 100, canvas.height / 2);
            else
                ctx.fillText("Game Over", canvas.width / 2 - 100, canvas.height / 2);
            // Optionally, stop further rendering or show restart options
        }
    }

    // Optional: Use requestAnimationFrame for smoother rendering
    // function animate() {
    //     if (gameState) {
    //         renderGame();
    //     }
    //     requestAnimationFrame(animate);
    // }
    // animate();
}
