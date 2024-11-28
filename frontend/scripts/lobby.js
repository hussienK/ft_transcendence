function attachLobbyEventListeners() {
	const API_BASE_URL = 'https://localhost:8443/api/game';
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

}