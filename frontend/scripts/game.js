function attachGameEventListeners(roomName, player) {
    console.log(player);
    const ws_path = "wss://" + window.location.host + '/ws/game/' + roomName + `/?is_local=false&player=${player}&token=` + localStorage.getItem('accessToken');
    console.log("WebSocket URL:", ws_path);
    const socket = new WebSocket(ws_path);

    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');

    let latestGameState = null;
    let previousGameState = null;
    let currentPhase = 'running'; // Online game phase
    let lastUpdateTime = null;

    const button = document.getElementById('back-to-lobby-button');
    if (button) {
        button.addEventListener('click', () => {
            window.location.hash = 'lobby'; // Redirect to the lobby
            location.reload();
        });
    }

    let keyIntervals = {
        [player]: null,
    };
    let currentDirections = {
        [player]: null,
    };

    socket.onopen = function (event) {
        console.log("WebSocket connection established for Online Game.");
    };

    socket.onmessage = function (event) {
        let data = JSON.parse(event.data);

        if (data.phase) currentPhase = data.phase;
        else currentPhase = "playing";

        if (currentPhase === 'countdown' && data.countdown) {
            renderCountdown(data.countdown);
        } else {
            previousGameState = latestGameState;
            latestGameState = data;
            lastUpdateTime = data.timestamp;
        }
    };

    socket.onclose = function (event) {
        console.log("WebSocket connection closed.");
        currentPhase = 'ended';
    };

    socket.onerror = function (error) {
        console.error("WebSocket error observed:", error);
    };

    document.addEventListener('keydown', function (event) {
        if (['w', 's', 'ArrowUp', 'ArrowDown'].includes(event.key)) {
            let direction = null;

            if (event.key === 'w' && player === 'player1') {
                direction = 'up';
            } else if (event.key === 's' && player === 'player1') {
                direction = 'down';
            } else if (event.key === 'ArrowUp' && player === 'player2') {
                direction = 'up';
            } else if (event.key === 'ArrowDown' && player === 'player2') {
                direction = 'down';
            }

            if (direction && currentDirections[player] !== direction) {
                // Clear existing interval for the player
                if (keyIntervals[player]) {
                    clearInterval(keyIntervals[player]);
                }

                // Update the current direction and start a new interval
                currentDirections[player] = direction;
                sendDirection(player, direction);
                keyIntervals[player] = setInterval(() => sendDirection(player, direction), 50);
                event.preventDefault();
            }
        }
    });

    document.addEventListener('keyup', function (event) {
        if (['w', 's', 'ArrowUp', 'ArrowDown'].includes(event.key)) {
            if (
                (event.key === 'w' || event.key === 's') && player === 'player1' ||
                (event.key === 'ArrowUp' || event.key === 'ArrowDown') && player === 'player2'
            ) {
                // Clear the interval and reset the direction
                clearInterval(keyIntervals[player]);
                keyIntervals[player] = null;
                currentDirections[player] = null;
                sendDirection(player, null);
                event.preventDefault();
            }
        }
    });

    function sendDirection(player, direction) {
        const message = {
            'player': player,
            'direction': direction,
        };
        socket.send(JSON.stringify(message));
    }

    function renderCountdown(countdown) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        ctx.font = '100px Arial';
        ctx.fillStyle = 'yellow';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        ctx.fillText(countdown, canvas.width / 2, canvas.height / 2);
    }

    function render() {
        if (currentPhase === 'ended') {
            return;
        }
        if (currentPhase === 'countdown') {
            requestAnimationFrame(render);
            return;
        }

        if (!latestGameState) {
            requestAnimationFrame(render);
            return;
        }

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        if (latestGameState.match_duration) {
            ctx.font = '20px Arial';
            ctx.fillStyle = 'white';
            ctx.fillText(`${latestGameState.match_duration.toFixed(2)}s`, canvas.width / 2, 80);
        }
        if (!latestGameState.game_is_active && !latestGameState.winner) {
            ctx.font = '50px Arial';
            ctx.fillStyle = 'white';
            ctx.fillText("Game Over", canvas.width / 2 - 100, canvas.height / 2);
        } else if (!latestGameState.game_is_active && latestGameState.winner) {
            ctx.font = '50px Arial';
            if (latestGameState.winner === player) {
                ctx.fillStyle = 'green';
                ctx.fillText("You Won!", canvas.width / 2, canvas.height / 2);
            } else {
                ctx.fillStyle = 'red';
                ctx.fillText("You Lost!", canvas.width / 2, canvas.height / 2);
            }

            currentPhase = 'ended';
            showBackToLobbyButton();
        } else {
            hideBackToLobbyButton();
            let gs = latestGameState;
            if (previousGameState && previousGameState.timestamp) {
                let dt = gs.timestamp - previousGameState.timestamp;
                let now = performance.now() / 1000;
                let renderDelay = 0.05;
                let t = 1.0;
                if (dt > 0) {
                    t = (now - previousGameState.timestamp - renderDelay) / dt;
                    t = Math.max(0, Math.min(t, 1));
                }
                gs = interpolateGameState(previousGameState, gs, t);
            }

            const ballPosition = gs.ball_position;
            ctx.fillStyle = 'white';
            ctx.beginPath();
            ctx.arc(ballPosition[0], ballPosition[1], 10, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = 'white';
            ctx.fillRect(10, gs.paddle1_position, 10, 100);
            ctx.fillRect(canvas.width - 20, gs.paddle2_position, 10, 100);

            ctx.font = '30px Arial';
            ctx.fillText(gs.score1, canvas.width / 2 - 50, 50);
            ctx.fillText(gs.score2, canvas.width / 2 + 30, 50);
        }

        requestAnimationFrame(render);
    }

    function interpolateGameState(prev, curr, t) {
        function lerp(a, b, t) { return a + (b - a) * t; }
        return {
            ball_position: [
                lerp(prev.ball_position[0], curr.ball_position[0], t),
                lerp(prev.ball_position[1], curr.ball_position[1], t),
            ],
            paddle1_position: lerp(prev.paddle1_position, curr.paddle1_position, t),
            paddle2_position: lerp(prev.paddle2_position, curr.paddle2_position, t),
            score1: curr.score1,
            score2: curr.score2,
            game_is_active: curr.game_is_active,
            winner: curr.winner,
            match_duration: lerp(prev.match_duration, curr.match_duration, t),
        };
    }

    requestAnimationFrame(render);

    function showBackToLobbyButton() {
        if (button) {
            button.style.display = 'block';
        }
    }

    function hideBackToLobbyButton() {
        if (button) {
            button.style.display = 'none';
        }
    }
}
