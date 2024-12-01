const dummyProfile = {
    matchesHistory: [
        {
            username: "john_doe_123",
            opponentUsername: "jane_doe_456",
            score: "3-1",
            result: "win",
            playedAt: "2024-11-22T15:00:00Z"
        },
        {
            username: "john_doe_123",
            opponentUsername: "mark_smith_789",
            score: "2-3",
            result: "loss",
            playedAt: "2024-11-20T12:30:00Z"
        },
        {
            username: "john_doe_123",
            opponentUsername: "lucy_james_101",
            score: "1-1",
            result: "draw",
            playedAt: "2024-11-18T08:15:00Z"
        }
    ],
};

function attachProfileEventListeners() {
    // Get the canvases and the percentage text elements for each progress bar
    const canvas1 = document.getElementById('progressCanvas1');
    const ctx1 = canvas1.getContext('2d');
    const percentageText1 = document.getElementById('percentageText1');
    
    const canvas2 = document.getElementById('progressCanvas2');
    const ctx2 = canvas2.getContext('2d');
    const percentageText2 = document.getElementById('percentageText2');

    const radius = 75; 
    const lineWidth = 25; 
    const center = canvas1.width / 2;  // Both canvases are the same size, so we use one center.

    // Function to draw progress on a given canvas and percentage text
    function drawProgress(canvas, ctx, percentage, percentageText) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw the background circle (empty circle)
        ctx.beginPath();
        ctx.arc(center, center, radius, 0, 2 * Math.PI);
        ctx.lineWidth = lineWidth;
        ctx.strokeStyle = '#e6e6e6'; // Light gray for background
        ctx.stroke();

        // Draw the progress circle
        ctx.beginPath();
        const endAngle = (percentage / 100) * 2 * Math.PI;
        ctx.arc(center, center, radius, 0, endAngle, false);
        ctx.lineWidth = lineWidth;
        ctx.strokeStyle = '#4caf50'; // Green for progress
        ctx.stroke();

        // Update the percentage text
        percentageText.textContent = `${Math.round(percentage)}%`;
    }

    // Initial progress values from the text elements
    let end1 = parseInt(percentageText1.textContent) || 0;

    let end2 = parseInt(percentageText2.textContent) || 0;

    // Function to update progress for both canvases
    function updateProgress(progress1, progress2) {
        if (progress1 <= end1) {
            drawProgress(canvas1, ctx1, progress1, percentageText1);
            progress1++;
        }
        
        if (progress2 <= end2) {
            drawProgress(canvas2, ctx2, progress2, percentageText2);
            progress2++;
        }

        // Continue the update loop if either progress bar is not finished
        if (progress1 <= end1 || progress2 <= end2) {
            setTimeout(updateProgress, 20);
        }
    }

    fetchStats()
        .then(data => {
            document.getElementById("profile-total_games").innerHTML = data.total_games || 0;
            document.getElementById("profile-games_Won").innerHTML = data.games_won || 0;
            document.getElementById("profile-games_lost").innerHTML = data.games_lost || 0;
            document.getElementById("profile-current_streak").innerHTML = data.longest_current_streak || 0;
            document.getElementById("profile-win_streak").innerHTML = data.longest_win_streak || 0;
            document.getElementById("profile-lose_streak").innerHTML = data.longest_loss_streak || 0;
            document.getElementById("profile-points_scored").innerHTML = data.points_scored || 0;
            document.getElementById("profile-points_conceded").innerHTML = data.points_conceded || 0;
            const pointsRatio = data.points_ratio ? Math.round(data.points_ratio) : 0;
            const winRatio = data.win_ratio ? Math.round(data.win_ratio) : 0;
            updateProgress(winRatio, pointsRatio)
        })
        .catch(error => {
            showAlert(error.response?.data.error, "danger");
        });

    fetchProfile(-42)
    .then(data => {
        document.getElementById("profile-display_name").innerHTML = data.display_name || "";
        document.getElementById("profile-username").innerHTML = data.username || "";
        document.getElementById("profile-bio").innerHTML = data.bio || "";
        document.getElementById("profile-email").innerHTML = data.email || "";
        const is_online = data.is_online || False;
        const statusIndicator = document.getElementById("profile-status-indicator");
        if (is_online) {
            statusIndicator.style.backgroundColor = "green";
            statusIndicator.setAttribute("title", "Online");
        } else {
            statusIndicator.style.backgroundColor = "gray";
            statusIndicator.setAttribute("title", "Offline");
        }
        const is_editable = data.editable || False;
        if (is_editable == false)
        {
            document.getElementById("edit-profile-btn").style.display = "none";
        }
    })
    .catch(error => {
        showAlert(error.response?.data.error, "danger");
    });

    fetchMatchHistory()
    .then(data => {
        console.log(data);
        const HistoryContainer = document.getElementById("matches-container");
        data.forEach(element => {
            const opponentUsername = element.opponent || 'Unknown';
            const winnerPoints = element.points_scored_by_winner || 0;
            const loserPoints = element.points_conceded_by_loser || 0;
            const result = element.result || 'Not Available';
            const isWinner = result === "Win";
            HistoryContainer.innerHTML += `
            <div id="opponent-card" class="d-flex gap-2">
                <div class="friend-avatar">
                    <img src="./avatar2.png" alt="avatar">
                </div>
                <div class="friend-info">
                    <p class="friend-displayname">${opponentUsername}</p>
                    <p class="friend-username">3 Days Ago</p> <!-- Replace with actual timestamp if available -->
                </div>
                <div style="margin-left: auto; width: 75px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                    <div style="background-color: ${isWinner ? 'rgb(37, 168, 37)' : 'rgb(168, 37, 37)'}; 
                                display: flex; justify-content: center; align-items: center; 
                                width: 100%; color: white; font-size: 16px; font-weight: 600; 
                                border-top-left-radius: 5px; border-top-right-radius: 5px;">
                        ${isWinner ? 'Won' : 'Lost'}
                    </div>
                    <div style="display: flex; justify-content: center; align-items: center;">
                        ${isWinner ? `${winnerPoints} - ${loserPoints}` : `${loserPoints} - ${winnerPoints}`}
                    </div>
                </div>
            </div>
            `;
        });
        
    })
    .catch(error => {
        showAlert(error.response?.data.error, "danger");
    });
}
