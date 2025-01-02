function attachProfileEventListeners(userName = -42) {
    const isCurrentUser = userName === -42;

    fetchStats(userName)
    .then(data => {
      console.log(data);
  
      const visualizationData = data.visualization_data;
  
      // Global layout styling
      const globalLayout = {
        font: { family: 'Roboto, sans-serif', color: '#fff' },
        paper_bgcolor: '#1e1e1e',
        plot_bgcolor: '#1e1e1e',
        margin: { l: 50, r: 50, t: 50, b: 50 },
      };
  
      // Render Bar Chart
      Plotly.newPlot('bar-chart', [{
        x: visualizationData.bar_chart.x,
        y: visualizationData.bar_chart.y,
        type: visualizationData.bar_chart.type,
        name: visualizationData.bar_chart.name,
        marker: {
          color: ['#4caf50', '#ff0000'],  // Green for games won, red for games lost
        },
      }], {
        ...globalLayout,
        title: { text: 'Games Won vs. Games Lost', font: { size: 20 } },
        xaxis: { title: { text: 'Category', font: { color: '#fff' } } },
        yaxis: { title: { text: 'Count', font: { color: '#fff' } } },
      });
  
      // Render Gauge Chart
      Plotly.newPlot('gauge-chart', [{
        type: visualizationData.gauge_chart.type,
        mode: visualizationData.gauge_chart.mode,
        value: visualizationData.gauge_chart.value,
        title: { text: 'Win Ratio', font: { size: 20 } },
        gauge: {
          axis: { range: [0, 100], tickcolor: '#fff' },
          bar: { color: '#4caf50' },
          steps: [
            { range: [0, 50], color: '#ff0000' },
            { range: [50, 100], color: '#4caf50' },
          ],
        },
      }], { ...globalLayout });
  
      // Render Pie Chart
      Plotly.newPlot('pie-chart', [{
        labels: visualizationData.pie_chart.labels,
        values: visualizationData.pie_chart.values,
        type: visualizationData.pie_chart.type,
        name: visualizationData.pie_chart.name,
        hole: 0.4,  // Donut-style
        marker: {
          colors: ['#4caf50', '#ff0000'],  // Green for points scored, red for points conceded
        },
      }], {
        ...globalLayout,
        title: { text: 'Points Scored vs. Points Conceded', font: { size: 20 } },
      });
  
      // Render Streaks Chart
      Plotly.newPlot('streak-chart', [{
        x: visualizationData.streaks.labels,
        y: visualizationData.streaks.values,
        type: 'bar',
        marker: {
          color: ['#4caf50', '#ff0000', '#2196f3'],  // Green, red, blue for the streaks
        },
      }], {
        ...globalLayout,
        title: { text: 'Streaks Overview', font: { size: 20 } },
        xaxis: { title: { text: 'Streak Type', font: { color: '#fff' } } },
        yaxis: { title: { text: 'Streak Length', font: { color: '#fff' } } },
      });
  
      // Render Reaction Time Gauge Chart
      Plotly.newPlot('reaction-time-gauge', [{
        type: visualizationData.reaction_time_gauge.type,
        mode: visualizationData.reaction_time_gauge.mode,
        value: visualizationData.reaction_time_gauge.value,
        title: { text: 'Average Reaction Time', font: { size: 20 } },
        gauge: {
          axis: { range: [0, 500], tickcolor: '#fff' },
          bar: { color: '#2196f3' },
          steps: [
            { range: [0, 250], color: '#4caf50' },
            { range: [250, 500], color: '#ff0000' },
          ],
        },
      }], { ...globalLayout });
  
      // Render Rally Bar Chart
      Plotly.newPlot('rally-bar-chart', [{
        x: visualizationData.rally_bar_chart.x,
        y: visualizationData.rally_bar_chart.y,
        type: visualizationData.rally_bar_chart.type,
        name: visualizationData.rally_bar_chart.name,
        marker: {
          color: ['#4caf50', '#2196f3'],  // Green for hits, blue for longest rallies
        },
      }], {
        ...globalLayout,
        title: { text: 'Total Ball Hits and Longest Rallies', font: { size: 20 } },
        xaxis: { title: { text: 'Category', font: { color: '#fff' } } },
        yaxis: { title: { text: 'Count', font: { color: '#fff' } } },
      });
  
      // Render Rally Bubble Chart
      Plotly.newPlot('rally-bubble-chart', [{
        x: visualizationData.rally_bubble_chart.x,
        y: visualizationData.rally_bubble_chart.y,
        text: visualizationData.rally_bubble_chart.text,  // Tooltip for bubbles
        mode: visualizationData.rally_bubble_chart.mode,
        type: visualizationData.rally_bubble_chart.type,
        marker: {
          size: visualizationData.rally_bubble_chart.marker.size,
          color: visualizationData.rally_bubble_chart.marker.color,
          colorscale: 'Viridis',
        },
      }], {
        ...globalLayout,
        title: { text: 'Longest Rally vs. Average Ball Speed', font: { size: 20 } },
        xaxis: { title: { text: 'Longest Rally (Hits)', font: { color: '#fff' } } },
        yaxis: { title: { text: 'Average Ball Speed (km/h)', font: { color: '#fff' } } },
      });
  
      // Render Victory Box Plot
      Plotly.newPlot('victory-box-plot', [{
        y: visualizationData.victory_box_plot.all_margins,
        type: 'box',
        name: 'Victory Margins',
        boxpoints: 'all',  // Display all points
        marker: { color: '#4caf50' },
      }], {
        ...globalLayout,
        title: { text: 'Victory Margin Range', font: { size: 20 } },
        yaxis: { title: { text: 'Victory Margin', font: { color: '#fff' } } },
      });
    })
    .catch(error => {
      console.log(error);
      showAlert(error.response?.data.error, "danger");
    });
  
  

    fetchProfile(userName)
        .then(data => {
            console.log(data);
            document.getElementById("profile-display_name").innerHTML = data.display_name || "";
            document.getElementById("profile-username").innerHTML = data.username || "";
            document.getElementById("profile-bio").innerHTML = data.bio || "";
            document.getElementById("profile-email").innerHTML = data.email || "";
            document.getElementById("profile-avatar").src = data.avatar || "./assets/default_avatar.png";

            const statusIndicator = document.getElementById("profile-status-indicator");
            if (data.is_online) {
                statusIndicator.innerHTML = "Online"
                statusIndicator.style.color = "green";
            } else {
                statusIndicator.innerHTML = "Offline";
                statusIndicator.style.color = "gray";
            }

            if (data.two_factor_enabled)
            {
                document.getElementById("enable-2fa-btn").innerHTML = '2FA Enabled'
                document.getElementById("enable-2fa-btn").disabled = true;
            }

            if (data.editable) {
                function openActionPopup() {
                    document.getElementById('action-popup').classList.remove('hidden');
                }
                
                // Close the modal
                function closeActionPopup() {
                    document.getElementById('action-popup').classList.add('hidden');
                }
                
                // Add event listeners for close button
                document.getElementById('close-action-modal').addEventListener('click', closeActionPopup);
                
                // Example: Add button to open the modal
                document.getElementById('show-action-popup-btn').addEventListener('click', openActionPopup);
                
                document.getElementById('logout-btn').addEventListener('click', async () => {
                    const logged_out = await logout();
                    localStorage.clear();
                    if (logged_out)
                    {
                        window.location.hash = 'login';
                    }
                });
                
                document.getElementById('delete-account-btn').addEventListener('click', async () => {
                    const delete_successfull = await deleteAccount();
                    if (delete_successfull)
                    {
                        window.location.hash = "login";
                    }
                });
                
                document.getElementById('enable-2fa-btn').addEventListener('click', async () => {
                    const setup_successful = await setup2fa();
                    if (setup_successful)
                    {
                        document.getElementById("enable-2fa-btn").innerHTML = '2FA Enabled'
                        document.getElementById("enable-2fa-btn").disabled = true;
                    }
                });

                // Open the modal
                function openEditProfileModal() {
                    document.getElementById('edit-profile-modal').classList.remove('hidden');
                }

                // Close the modal
                function closeEditProfileModal() {
                    document.getElementById('edit-profile-modal').classList.add('hidden');
                    document.getElementById("edit-profile-form").reset();
                }

                // Add event listeners for close button
                document.getElementById('close-edit-profile-modal').addEventListener('click', closeEditProfileModal);
                document.getElementById('show-edit-profile-btn').addEventListener('click', openEditProfileModal);

                // Handle form submission
                document.getElementById('edit-profile-form').addEventListener('submit', async function (e) {
                    e.preventDefault(); // Prevent default form submission
                    const formData = new FormData(document.getElementById("edit-profile-form"));
                    try {
                        const response = await axios.put('/api/users/profile/', formData, {
                          headers: {
                            'Content-Type': 'multipart/form-data',
                            Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
                          },
                        });
                        if (response.status === 200) {
                          const updatedData = response.data;
                          console.log('Profile updated successfully:', updatedData);
                          // Update the UI with new profile information
                          document.getElementById('profile-display_name').innerHTML = updatedData.display_name;
                          document.getElementById('profile-bio').innerHTML = updatedData.bio;
                          // Update avatar in the UI
                          if (updatedData.avatar_url) {
                            document.getElementById('profile-avatar').src = updatedData.avatar_url;
                          }
                          showAlert('Profile updated successfully!', "success");
                        }
                      } catch (error) {
                          showAlert("Please provide valid credentials", 'danger');
                          console.error('Error updating profile:', error.response?.data || error.message);
                      }                    
                    closeEditProfileModal();
                });

            }
        })
        .catch(error => {
            console.log(error);
            showAlert(error.response?.data.error, "danger");
        });

        fetchMatchHistory(userName)
        .then(data => {
            const HistoryContainer = document.getElementById("match-details-container");
            HistoryContainer.innerHTML = "";
    
            // Create and append cards for each match
            data.forEach(element => {
                const matchId = element.id; // Assuming the match ID is present in the `element`
                const opponentUsername = element.opponent || 'Unknown';
                const score = element.player1_score || 0;
                const score2 = element.player2_score || 0;
                const forfeit = element.forfeit;
                const result = element.result || 'Not Available';
                console.log(result);
                const isWinner = result === "Win";
    
                const createdAt = new Date(element.created_at);
                const timeAgo = getTimeAgo(createdAt);
    
                // Create card HTML
                const matchCardHTML = `
                <div class="d-flex gap-2 match-card" data-match-id="${matchId}" style="cursor: pointer;">
                    <div class="friend-avatar">
                        <img src="${element.opponent_avatar || './assets/default_avatar.png'}" alt="avatar">
                    </div>
                    <div class="friend-info">
                        <p class="friend-displayname">${opponentUsername}</p>
                        <p class="friend-username">${timeAgo}</p>
                    </div>
                    <div style="margin-left: auto; width: 75px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                        <div style="background-color: ${isWinner ? 'rgb(37, 168, 37)' : 'rgb(168, 37, 37)'}; 
                                    display: flex; justify-content: center; align-items: center; 
                                    width: 100%; color: white; font-size: 16px; font-weight: 600; 
                                    border-top-left-radius: 5px; border-top-right-radius: 5px;">
                            ${isWinner ? 'Won' : 'Lost'}
                        </div>
                        <div style="display: flex; justify-content: center; align-items: center;">
                            ${forfeit ? "Forfeit": `${score} - ${score2}`}
                        </div>
                    </div>
                </div>
                `;
    
                HistoryContainer.innerHTML += matchCardHTML;

                document.querySelectorAll('.match-card').forEach(card => {
                    card.addEventListener('click', function () {
                        const matchId = this.getAttribute('data-match-id');
                        openMatchDetailsPopup(matchId);
                    });
                });
            });
    
            // Show modal with all match cards
            const modal = document.getElementById("match-details-modal");
    
            // Close modal
            document.getElementById("close-modal-btn").onclick = () => modal.classList.add("hidden");
        })
        .catch(error => {
            console.log(error);
            showAlert(error.response?.data.error, "danger");
        });
    


    document.getElementById("show-history-button").addEventListener("click", () => {
        document.getElementById("match-details-modal").classList.remove("hidden");  
    });

    // Function to open the modal
    function openVisualizationPopup() {
        document.getElementById('visualization-popup').classList.remove('hidden');
    }

    // Function to close the modal
    function closeVisualizationPopup() {
        document.getElementById('visualization-popup').classList.add('hidden');
    }

    // Add event listeners for close buttons
    document.getElementById('close-visualization-modal').addEventListener('click', closeVisualizationPopup);

    // Example: Attach this function to a button click to show the modal
    document.getElementById('show-visualization-button').addEventListener('click', openVisualizationPopup);
    

    function openMatchDetailsPopup(matchId) {
        const modal = document.getElementById('match-details-popup');
        modal.classList.remove('hidden');

        fetchMatch(matchId)
        .then(element => {
            const infoContainer = document.getElementById("match-box");
            const player1Name = element.match_stats.player1 || 'Unknown';
            const player2Name = element.match_stats.player2 || 'Unknown';
            const player1Score = element.match_stats.player1_score || 0;
            const player2Score = element.match_stats.player2_score || 0;
            const forfeit = element.match_stats.forfeit;
            const winner = element.match_stats.winner || 'Unknown';
            const loser = element.match_stats.loser || 'Unknown';
            console.log(winner);
            const createdAt = new Date(element.match_stats.created_at);
            const timeAgo = getTimeAgo(createdAt);
    
            // Determine styles for scores
            const player1ScoreStyle = winner === player1Name ? 'color: green;' : 'color: red;';
            const player2ScoreStyle = winner === player2Name ? 'color: green;' : 'color: red;';
    
            // Clear the existing content
            infoContainer.innerHTML = '';
    
            // Add the updated content
            infoContainer.innerHTML = `
            <div class="match-details-container d-flex flex-column align-items-center gap-4">
                <!-- Match Header -->
                <div class="match-header d-flex flex-column align-items-center p-4 rounded-3 neon-box" 
                     style="width: 100%; max-width: 600px;">
                    <h2 class="text-neon-blue mb-2">Match Details</h2>
                    <p class="text-muted">${timeAgo} ${forfeit ? '| Forfeit' : ''}</p>
                </div>
            
                <!-- Player Stats -->
                <div class="score-card d-flex align-items-center justify-content-between p-4 rounded-3 neon-box"
                     style="width: 100%; max-width: 600px;">
                    <!-- Player 1 Info -->
                    <div class="player-info d-flex flex-column align-items-center" style="width: 48%;">
                        <img src="${element.player1_avatar || './assets/default_avatar.png'}" 
                             alt="Player 1 Avatar" 
                             class="rounded-circle neon-avatar">
                        <h3 class="mt-2 text-neon-blue">${player1Name}</h3>
                        <p class="score fs-2 fw-bold" style="${player1ScoreStyle}">${player1Score}</p>
                    </div>
            
                    <!-- VS Info -->
                    <div class="vs text-center d-flex flex-column align-items-center">
                        <p class="vs-text text-neon-pink fs-4 fw-bold">VS</p>
                        <div class="divider" style="width: 1px; height: 50px; background-color: #fff;"></div>
                    </div>
            
                    <!-- Player 2 Info -->
                    <div class="player-info d-flex flex-column align-items-center" style="width: 48%;">
                        <img src="${element.player2_avatar || './assets/default_avatar.png'}" 
                             alt="Player 2 Avatar" 
                             class="rounded-circle neon-avatar">
                        <h3 class="mt-2 text-neon-pink">${player2Name}</h3>
                        <p class="score fs-2 fw-bold" style="${player2ScoreStyle}">${player2Score}</p>
                    </div>
                </div>
            </div>
            `;
            
    
            const matchData = element;
            const globalLayout = {
                font: { family: 'Roboto, sans-serif', color: '#fff' },
                paper_bgcolor: '#121212',
                plot_bgcolor: '#121212',
                margin: { l: 50, r: 50, t: 50, b: 50 },
            };
            
            // Bar Chart: Scores Comparison
            const barData = [
                {
                    x: [matchData.match_stats.player1, matchData.match_stats.player2],
                    y: [matchData.match_stats.player1_score, matchData.match_stats.player2_score],
                    type: 'bar',
                    marker: { color: ['#00d1ff', '#ff6ec7'] },
                },
            ];
            const barLayout = {
                ...globalLayout,
                title: { text: 'Scores Comparison', font: { size: 20 } },
                xaxis: { title: { text: 'Players', color: '#fff' } },
                yaxis: { title: { text: 'Scores', color: '#fff' } },
            };
            Plotly.newPlot('scoreBarChart', barData, barLayout);
            // Pie Chart: Ball Hits Distribution
            const pieData = [
                {
                    labels: [matchData.match_stats.player1, matchData.match_stats.player2],
                    values: [
                        matchData.match_stats.total_ball_hits / 2,
                        matchData.match_stats.total_ball_hits / 2,
                    ],
                    type: 'pie',
                    marker: { colors: ['#00d1ff', '#ff6ec7'] },
                },
            ];
            const pieLayout = {
                ...globalLayout,
                title: { text: 'Ball Hits Distribution', font: { size: 20 } },
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
                    marker: { color: '#00d1ff' },
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
                    marker: { color: '#ff6ec7' },
                },
            ];
            const radarLayout = {
                ...globalLayout,
                title: { text: 'Performance Metrics Comparison', font: { size: 20 } },
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
                    x: ['Start', 'Middle', 'End'],
                    y: [matchData.match_stats.player1_score / 3, matchData.match_stats.player1_score / 2, matchData.match_stats.player1_score],
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: matchData.match_stats.player1,
                    line: { color: '#00d1ff' },
                },
                {
                    x: ['Start', 'Middle', 'End'],
                    y: [matchData.match_stats.player2_score / 3, matchData.match_stats.player2_score / 2, matchData.match_stats.player2_score],
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: matchData.match_stats.player2,
                    line: { color: '#ff6ec7' },
                },
            ];
            const timelineLayout = {
                ...globalLayout,
                title: { text: 'Match Timeline (Score Progression)', font: { size: 20 } },
                xaxis: { title: { text: 'Timeline', color: '#fff' } },
                yaxis: { title: { text: 'Scores', color: '#fff' } },
            };
            Plotly.newPlot('matchTimelineChart', timelineData, timelineLayout);
            
            // Line Chart: Ball Speed Progression
            const speedData = [
                {
                    x: ['Start', 'Middle', 'End'],
                    y: [matchData.match_stats.avg_ball_speed, matchData.match_stats.max_ball_speed, matchData.match_stats.max_ball_speed],
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Ball Speed (km/h)',
                    line: { color: '#4caf50' },
                },
            ];
            const speedLayout = {
                ...globalLayout,
                title: { text: 'Ball Speed Progression', font: { size: 20 } },
                xaxis: { title: { text: 'Timeline', color: '#fff' } },
                yaxis: { title: { text: 'Speed (km/h)', color: '#fff' } },
            };
            Plotly.newPlot('ballSpeedLineChart', speedData, speedLayout);
            
            // Bubble Chart: Rally Analysis
            const rallyData = [
                {
                    x: [5, 10, 15],
                    y: [3, 6, 9],
                    text: ['Intensity: 1', 'Intensity: 2', 'Intensity: 3'],
                    mode: 'markers',
                    marker: {
                        size: [15, 20, 25],
                        color: ['#00d1ff', '#ff6ec7', '#4caf50'],
                        opacity: 0.8,
                    },
                },
            ];
            const rallyLayout = {
                ...globalLayout,
                title: { text: 'Rally Analysis', font: { size: 20 } },
                xaxis: { title: { text: 'Rally Length', color: '#fff' } },
                yaxis: { title: { text: 'Points Scored', color: '#fff' } },
            };
            Plotly.newPlot('rallyBubbleChart', rallyData, rallyLayout);
        });
    
        
        // Ensure charts are resized properly
        setTimeout(() => {
            ['scoreBarChart', 'ballHitsPieChart', 'performanceRadarChart', 'matchTimelineChart', 'ballSpeedLineChart', 'rallyBubbleChart']
            .forEach(chartId => Plotly.Plots.resize(document.getElementById(chartId)));
        }, 200);
    }
    
    // Close the modal
    function closeMatchDetailsPopup() {
        document.getElementById('match-details-popup').classList.add('hidden');
    }
    
    // Add event listeners for close buttons
    document.getElementById('close-match-details-modal').addEventListener('click', closeMatchDetailsPopup);
    
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
