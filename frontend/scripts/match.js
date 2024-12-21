function attachMatchEventListeners(matchid = -42) {
    //   fetchStats(userName)
    //   .then(data => {
    //   })
    //   .catch(error => {
    //         console.log(error);
    //       showAlert(error.response?.data.error, "danger");
    //   });
  

    // fetchProfile(userName)
    //     .then(data => {
    //         document.getElementById("profile-display_name").innerHTML = data.display_name || "";
    //         document.getElementById("profile-username").innerHTML = data.username || "";
    //         document.getElementById("profile-bio").innerHTML = data.bio || "";
    //         document.getElementById("profile-email").innerHTML = data.email || "";
    //         document.getElementById("profile-avatar").src = data.avatar || "./assets/default_avatar.png";

    //         const statusIndicator = document.getElementById("profile-status-indicator");
    //         if (data.is_online) {
    //             statusIndicator.style.backgroundColor = "green";
    //             statusIndicator.setAttribute("title", "Online");
    //         } else {
    //             statusIndicator.style.backgroundColor = "gray";
    //             statusIndicator.setAttribute("title", "Offline");
    //         }

    //         if (!data.editable) {
    //             document.getElementById("edit-profile-btn").style.display = "none";
    //             document.getElementById("logout-btn").style.display = "none";
    //             document.getElementById("2fa-btn").style.display = "none";
    //         } else {
    //             document.getElementById("edit-profile-btn").style.display = "block";
    //             document.getElementById("logout-btn").style.display = "block";
    //             document.getElementById("2fa-btn").style.display = "block";
    //             if (data.two_factor_enabled)
    //             {
    //                 document.getElementById("2fa-btn").innerHTML = "2FA Enabled"
    //                 document.getElementById("2fa-btn").disabled = true;
    //             }

    //             document.getElementById("logout-btn").addEventListener('click', async () => {
    //                 const logged_out = await logout();
    //                 localStorage.clear();
    //                 if (logged_out)
    //                 {
    //                     window.location.hash = 'login';
    //                 }
    //             });

    //             document.getElementById("2fa-btn").addEventListener('click', async () => {
    //                 const setup_successful = await setup2fa();
    //                 if (setup_successful)
    //                 {
    //                     document.getElementById("2fa-btn").innerHTML = '2FA Enabled'
    //                     document.getElementById("2fa-btn").disabled = true;
    //                 }
    //             });

    //             document.getElementById("delete-btn").addEventListener('click', async () => {
    //                 const delete_successfull = await deleteAccount();
    //                 if (delete_successfull)
    //                 {
    //                     window.location.hash = "login";
    //                 }
    //             });
    //         }
    //     })
    //     .catch(error => {
    //         showAlert(error.response?.data.error, "danger");
    //     });

	fetchMatch(matchid)
    .then(element => {
        const infoContainer = document.getElementById("match-box");
        const player1Name = element.match_stats.player1 || 'Unknown';
        const player2Name = element.match_stats.player2 || 'Unknown';
        const player1Score = element.match_stats.player1_score || 0;
        const player2Score = element.match_stats.player2_score || 0;
        const forfeit = element.match_stats.forfeit;
        const winner = element.match_stats.winner || 'Unknown';
        const loser = element.match_stats.loser || 'Unknown';
        const createdAt = new Date(element.match_stats.created_at);
        const timeAgo = getTimeAgo(createdAt);

        // Determine styles for scores
        const player1ScoreStyle = winner === player1Name ? 'color: green;' : 'color: red;';
        const player2ScoreStyle = winner === player2Name ? 'color: green;' : 'color: red;';

        // Clear the existing content
        infoContainer.innerHTML = '';

        // Add the updated content
        infoContainer.innerHTML = `
        <div class="match-details-container d-flex flex-column align-items-center gap-3">
            <div class="score-card d-flex align-items-center justify-content-between p-4 rounded-3" 
                style="box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); width: 100%; max-width: 600px; height: 400px">

                <div class="player-info d-flex flex-column align-items-center">
                    <img src="${element.player1_avatar || './assets/default_avatar.png'}" alt="Player 1 Avatar" 
                         class="rounded-circle" style="width: 80px; height: 80px; object-fit: cover;">
                    <h3 class="mt-2 text-white">${player1Name}</h3>
                    <p class="score fs-2 fw-bold" style="${player1ScoreStyle}">${player1Score}</p>
                </div>

                <div class="vs text-center">
                    <p class="text-muted">${forfeit ? 'Forfeit' : ''}</p>
                </div>

                <div class="player-info d-flex flex-column align-items-center">
                    <img src="${element.player2_avatar || './assets/default_avatar.png'}" alt="Player 2 Avatar" 
                         class="rounded-circle" style="width: 80px; height: 80px; object-fit: cover;">
                    <h3 class="mt-2 text-white">${player2Name}</h3>
                    <p class="score fs-2 fw-bold" style="${player2ScoreStyle}">${player2Score}</p>
                </div>
            </div>
        </div>
        `;

	const matchData = element;
		// Bar Chart: Scores Comparison
		const barData = [
			{
			x: [matchData.match_stats.player1, matchData.match_stats.player2],
			y: [matchData.match_stats.player1_score, matchData.match_stats.player2_score],
			type: 'bar',
			marker: {
				color: ['#36A2EB', '#FF6384'],
			},
			},
		];
		const barLayout = {
			title: 'Scores Comparison',
			xaxis: { title: 'Players' },
			yaxis: { title: 'Scores' },
		};
		Plotly.newPlot('scoreBarChart', barData, barLayout);
		
		// Pie Chart: Ball Hits Distribution
		const pieData = [
			{
			labels: [matchData.match_stats.player1, matchData.match_stats.player2],
			values: [
				matchData.match_stats.total_ball_hits / 2, // Assuming equal split for now
				matchData.match_stats.total_ball_hits / 2,
			],
			type: 'pie',
			marker: {
				colors: ['#36A2EB', '#FF6384'],
			},
			},
		];
		const pieLayout = {
			title: 'Ball Hits Distribution',
		};
		Plotly.newPlot('ballHitsPieChart', pieData, pieLayout);
		
		// Radar Chart: Performance Metrics Comparison
		const radarData = [
			{
			type: 'scatterpolar',
			r: [
				matchData.match_stats.player1_score,
				matchData.match_stats.reaction_time_player1,
				matchData.match_stats.total_ball_hits / 2,
				matchData.match_stats.victory_margin,
			],
			theta: ['Scores', 'Reaction Time', 'Ball Hits', 'Victory Margin'],
			fill: 'toself',
			name: matchData.match_stats.player1,
			},
			{
			type: 'scatterpolar',
			r: [
				matchData.match_stats.player2_score,
				matchData.match_stats.reaction_time_player2,
				matchData.match_stats.total_ball_hits / 2,
				-matchData.match_stats.victory_margin,
			],
			theta: ['Scores', 'Reaction Time', 'Ball Hits', 'Victory Margin'],
			fill: 'toself',
			name: matchData.match_stats.player2,
			},
		];
		const radarLayout = {
			title: 'Performance Metrics Comparison',
			polar: {
			radialaxis: {
				visible: true,
				range: [0, Math.max(matchData.match_stats.player1_score, matchData.match_stats.player2_score) + 5],
			},
			},
		};
		Plotly.newPlot('performanceRadarChart', radarData, radarLayout);
		
		// Line Chart: Match Timeline (Score Progression)
		const timelineData = [
			{
			x: ['Start', 'Middle', 'End'], // Placeholder for timeline
			y: [matchData.match_stats.player1_score / 3, matchData.match_stats.player1_score / 2, matchData.match_stats.player1_score],
			type: 'scatter',
			mode: 'lines+markers',
			name: matchData.match_stats.player1,
			line: { color: 'rgba(75, 192, 192, 1)' },
			},
			{
			x: ['Start', 'Middle', 'End'], // Placeholder for timeline
			y: [matchData.match_stats.player2_score / 3, matchData.match_stats.player2_score / 2, matchData.match_stats.player2_score],
			type: 'scatter',
			mode: 'lines+markers',
			name: matchData.match_stats.player2,
			line: { color: 'rgba(255, 99, 132, 1)' },
			},
		];
		const timelineLayout = {
			title: 'Match Timeline (Score Progression)',
			xaxis: { title: 'Timeline' },
			yaxis: { title: 'Scores' },
		};
		Plotly.newPlot('matchTimelineChart', timelineData, timelineLayout);
		
		// Line Chart: Ball Speed Progression
		const speedData = [
			{
			x: ['Start', 'Middle', 'End'], // Placeholder for rally timestamps
			y: [matchData.match_stats.avg_ball_speed, matchData.match_stats.max_ball_speed, matchData.match_stats.max_ball_speed],
			type: 'scatter',
			mode: 'lines+markers',
			name: 'Ball Speed (km/h)',
			line: { color: 'rgba(153, 102, 255, 1)' },
			},
		];
		const speedLayout = {
			title: 'Ball Speed Progression',
			xaxis: { title: 'Timeline' },
			yaxis: { title: 'Speed (km/h)' },
		};
		Plotly.newPlot('ballSpeedLineChart', speedData, speedLayout);
		
		// Bubble Chart: Rally Analysis
		const rallyData = [
			{
			x: [5, 10, 15], // Placeholder rally lengths
			y: [3, 6, 9], // Placeholder points scored
			text: ['Intensity: 1', 'Intensity: 2', 'Intensity: 3'], // Placeholder intensity
			mode: 'markers',
			marker: {
				size: [5, 10, 15], // Placeholder bubble sizes
				color: 'rgba(255, 159, 64, 0.8)',
			},
			},
		];
		const rallyLayout = {
			title: 'Rally Analysis',
			xaxis: { title: 'Rally Length' },
			yaxis: { title: 'Points Scored' },
		};
		Plotly.newPlot('rallyBubbleChart', rallyData, rallyLayout);
		
		// Box Plot: Victory Margins
		const boxData = [
			{
			y: [matchData.match_stats.victory_margin], // Victory margin distribution
			type: 'box',
			name: 'Victory Margins',
			boxpoints: 'all',
			jitter: 0.5,
			pointpos: -1.8,
			},
		];
		const boxLayout = {
			title: 'Victory Margins',
			yaxis: { title: 'Margin' },
		};
		Plotly.newPlot('victoryMarginBoxPlot', boxData, boxLayout);
		
	
    });


        function getTimeAgo(date) {
            const now = new Date();
            const diff = now - date; // Difference in milliseconds
        
            const seconds = Math.floor(diff / 1000);
            const minutes = Math.floor(seconds / 60);
            const hours = Math.floor(minutes / 60);
            const days = Math.floor(hours / 24);
        
            if (days > 0) {
                return `${days} day${days > 1 ? 's' : ''} ago`;
            } else if (hours > 0) {
                return `${hours} hour${hours > 1 ? 's' : ''} ago`;
            } else if (minutes > 0) {
                return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
            } else {
                return `Just now`;
            }
        }
}
