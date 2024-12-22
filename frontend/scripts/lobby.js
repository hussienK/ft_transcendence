function attachLobbyEventListeners() {
  const API_BASE_URL = 'https://localhost:8443/api/game';
  let websocket = null;
  let isConnected = false;

  const connectButton = document.getElementById('connectButton');
  const localButton = document.getElementById('localButton');
  const statsData = ["<h2>No data available</h2>"];
  let currentStatIndex = 0;
  let interval;

  async function joinGameQueue(token) {
    const response = await fetch(`${API_BASE_URL}/join-queue/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    if (!response.ok) throw new Error('Failed to join the game queue');
  }

  async function leaveGameQueue(token) {
    const response = await fetch(`${API_BASE_URL}/leave-queue/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    if (!response.ok) throw new Error('Failed to leave the game queue');
  }

  connectButton.addEventListener('click', async () => {
    const token = localStorage.getItem('accessToken');
    if (!token) {
      alert('Access token is missing or expired. Please log in again.');
      window.location.hash = 'login';
      return;
    }

    connectButton.disabled = true;
    try {
      if (!isConnected) {
        await joinGameQueue(token);
        connectButton.textContent = 'Cancel Connection';
        isConnected = true;
      } else {
        await leaveGameQueue(token);
        connectButton.textContent = 'Connect to Game';
        isConnected = false;
      }
    } catch (error) {
      console.error('Error toggling connection:', error);
      alert('Failed to toggle connection. Please try again.');
    } finally {
      connectButton.disabled = false;
    }
  });

  localButton.addEventListener('click', async () => {
    const token = localStorage.getItem('accessToken');
    if (!token) {
      alert('Access token is missing in localStorage');
      return;
    }

    try {
      await startLocalGame(token);
    } catch (error) {
      console.error('Error starting local game:', error);
      alert('Failed to start local game. Please try again.');
    }
  });

}
