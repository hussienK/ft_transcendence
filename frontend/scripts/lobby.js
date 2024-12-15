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

  async function updateStat() {
    if (statsData.length > 1 && statsData[currentStatIndex] == "<h2>No data available</h2>")
        currentStatIndex = (currentStatIndex + 1) % statsData.length
    const stat_cont = document.getElementById('stats-container');
    if (stat_cont)
    {
      stat_cont.innerHTML =
      statsData[currentStatIndex];  
      currentStatIndex = (currentStatIndex + 1) % statsData.length;
    }
    else 
    {
      clearInterval(updateStat);
      interval = null;
    }
  }

  fetchStats(-42)
    .then((data) => {
      const stats = {
        longest_current_streak: data.longest_current_streak || 0,
        longest_win_streak: data.longest_win_streak || 0,
        games_won: data.games_won || 0,
        games_lost: data.games_lost || 0,
        total_games: data.total_games || 0,
      };

      let statsHTML = "<h2>Stats</h2>";
      Object.keys(stats).forEach((key) => {
        statsHTML += `
          <div class="stat-item">
            <strong>${key.replace(/_/g, ' ')}</strong><br> ${stats[key]}
          </div>
        `;
      });
      statsData.push(statsHTML);
      updateStat();
    })
    .catch((error) => {
      console.error('Error fetching stats:', error);
    });

  fetchMatchHistory(-42)
    .then((data) => {
      let historyHTML = "<h2>History</h2>";
      data.forEach((element, index) => {
        const opponentUsername = element.opponent || 'Unknown';
        const winnerPoints = element.points_scored_by_winner || 0;
        const loserPoints = element.points_conceded_by_loser || 0;
        const result = element.result || 'Not Available';
        const isWinner = result === 'Win';
        historyHTML += `
          <div id="opponent-card-${index}" class="d-flex gap-2">
            <div class="friend-avatar">
              <img src="${
                element.opponent_avatar || './assets/default_avatar.png'
              }" alt="avatar">
            </div>
            <div class="friend-info">
              <p class="friend-displayname">${opponentUsername}</p>
              <p class="friend-username">3 Days Ago</p>
            </div>
            <div style="margin-left: auto; width: 75px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
              <div style="background-color: ${
                isWinner ? 'rgb(37, 168, 37)' : 'rgb(168, 37, 37)'
              }; display: flex; justify-content: center; align-items: center; width: 100%; color: white; font-size: 16px; font-weight: 600; border-top-left-radius: 5px; border-top-right-radius: 5px;">
                ${isWinner ? 'Won' : 'Lost'}
              </div>
              <div style="display: flex; justify-content: center; align-items: center; background-color: white;">
                ${
                  isWinner
                    ? `${winnerPoints} - ${loserPoints}`
                    : `${loserPoints} - ${winnerPoints}`
                }
              </div>
            </div>
          </div>
        `;
      });

      statsData.push(historyHTML);
      updateStat();
    })
    .catch((error) => {
      console.error('Error fetching match history:', error);
    });

  fetchRank()
    .then((data) => {
      const RankItem = document.getElementById('rank-container');
      RankItem.innerHTML = `
        <div class="friend-avatar" style="width: 100px; height: 100px;">
          <img src="${data.avatar || './assets/default_avatar.png'}" alt="${data.user}'s avatar">
        </div>
        <h3>Rank: ${data.rank}<br>${data.total_players} Players Total</h3>
      `;
    })
    .catch((error) => {
      console.error('Error fetching rank:', error);
    });

    interval = setInterval(updateStat, 5000);
}
