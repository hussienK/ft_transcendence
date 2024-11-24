function attachLobbyEventListeners() {
	const API_BASE_URL = 'https://localhost:8443/api/game';
    const WEBSOCKET_URL = 'ws://localhost:8080/ws/matchmaking';
    let websocket = null;
    let isConnected = false;

    const connectButton = document.getElementById('connectButton');

    connectButton.addEventListener('click', async () => {
      const token = localStorage.getItem('accessToken');

      if (!token) {
        alert('Access token is missing in localStorage');
        return;
      }

      if (!isConnected) {
        // Join the game queue
        try {
          await joinGameQueue(token);
          openWebSocket(token);
          connectButton.textContent = 'Cancel Connection';
          isConnected = true;
        } catch (error) {
          console.error('Error connecting to the game:', error);
          alert('Failed to connect. Please try again.');
        }
      } else {
        // Leave the game queue
        try {
          await leaveGameQueue(token);
          closeWebSocket();
          connectButton.textContent = 'Connect to Game';
          isConnected = false;
        } catch (error) {
          console.error('Error disconnecting from the game:', error);
          alert('Failed to disconnect. Please try again.');
        }
      }
    });

    async function joinGameQueue(token) {
      const response = await fetch(`${API_BASE_URL}/join-queue/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to join the game queue');
      }
    }

    async function leaveGameQueue(token) {
      const response = await fetch(`${API_BASE_URL}/leave-queue/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to leave the game queue');
      }
    }

    function openWebSocket(token) {
      websocket = new WebSocket(`${WEBSOCKET_URL}/?token=${token}`);

      websocket.onopen = () => {
        console.log('WebSocket connection opened');
      };

      websocket.onmessage = (event) => {
        console.log('Message from server:', event.data);
      };

      websocket.onclose = () => {
        console.log('WebSocket connection closed');
      };

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    }

    function closeWebSocket() {
      if (websocket) {
        websocket.close();
        websocket = null;
        console.log('WebSocket connection closed');
      }
    }
}