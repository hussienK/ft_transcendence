function attachProfileEventListeners(userName = -42) {
    const isCurrentUser = userName === -42;

    // Modal elements
    const modal = document.getElementById('edit-profile-modal');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const editProfileForm = document.getElementById('edit-profile-form');
    const editProfileBtn = document.getElementById('edit-profile-btn');
  
    // Show the modal
    editProfileBtn.addEventListener('click', () => {
      modal.classList.remove('hidden'); // Show the modal
    });
  
    // Hide the modal
    closeModalBtn.addEventListener('click', () => {
      modal.classList.add('hidden'); // Hide the modal
      editProfileForm.reset();
    });
  
    // Handle form submission
    editProfileForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // Prevent default form submission
      
        const formData = new FormData(editProfileForm); // Use FormData directly
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
      
            alert('Profile updated successfully!');
            modal.classList.add('hidden'); // Hide the modal
          }
        } catch (error) {
            showAlert("Please provide valid credentials", 'danger');
            console.error('Error updating profile:', error.response?.data || error.message);
        }
      });



      fetchStats(userName)
      .then(data => {
          console.log(data);
  
          // Visualization data
          const visualizationData = data.visualization_data;
  
          // Render Bar Chart
          Plotly.newPlot('bar-chart', [{
              x: visualizationData.bar_chart.x,
              y: visualizationData.bar_chart.y,
              type: visualizationData.bar_chart.type,
              name: visualizationData.bar_chart.name,
              marker: {
                  color: ['#4caf50', '#ff0000']  // Green for games won, red for games lost
              }
          }], {
              title: 'Games Won vs. Games Lost',
              xaxis: { title: 'Category' },
              yaxis: { title: 'Count' }
          });
  
          // Render Gauge Chart
          Plotly.newPlot('gauge-chart', [{
              type: visualizationData.gauge_chart.type,
              mode: visualizationData.gauge_chart.mode,
              value: visualizationData.gauge_chart.value,
              title: visualizationData.gauge_chart.title,
              gauge: visualizationData.gauge_chart.gauge
          }], {
              title: 'Win Ratio',
          });
  
          // Render Pie Chart
          Plotly.newPlot('pie-chart', [{
              labels: visualizationData.pie_chart.labels,
              values: visualizationData.pie_chart.values,
              type: visualizationData.pie_chart.type,
              name: visualizationData.pie_chart.name,
                marker: {
                    color: ['#4caf50', '#ff0000']
                },
              hole: 0.4, // Optional: For a donut-style chart
          }], {
              title: 'Points Scored vs. Points Conceded',
          });

          const streaks = data.visualization_data.streaks;

          // Render Streaks Chart
          Plotly.newPlot('streak-chart', [{
              x: streaks.labels,
              y: streaks.values,
              type: 'bar',
              marker: {
                  color: ['#4caf50', '#ff0000', '#2196f3'],  // Green, red, blue for the streaks
              },
          }], {
              title: 'Streaks Overview',
              xaxis: { title: 'Streak Type' },
              yaxis: { title: 'Streak Length' },
          });

          const reactionTimeGauge = data.visualization_data.reaction_time_gauge;

            // Render Reaction Time Gauge Chart
            Plotly.newPlot('reaction-time-gauge', [{
                type: reactionTimeGauge.type,
                mode: reactionTimeGauge.mode,
                value: reactionTimeGauge.value,
                title: reactionTimeGauge.title,
                gauge: reactionTimeGauge.gauge,
            }], {
                title: 'Average Reaction Time',
            });

            // Bar Chart: Total Ball Hits and Longest Rallies
            const rallyBarChart = data.visualization_data.rally_bar_chart;

            Plotly.newPlot('rally-bar-chart', [{
                x: rallyBarChart.x,
                y: rallyBarChart.y,
                type: rallyBarChart.type,
                name: rallyBarChart.name,
                marker: rallyBarChart.marker,
            }], {
                title: 'Total Ball Hits and Longest Rallies',
                xaxis: { title: 'Category' },
                yaxis: { title: 'Count' },
            });

            // Bubble Chart: Longest Rally vs. Average Ball Speed
            const rallyBubbleChart = data.visualization_data.rally_bubble_chart;

            Plotly.newPlot('rally-bubble-chart', [{
                x: rallyBubbleChart.x,  // Longest rallies
                y: rallyBubbleChart.y,  // Average ball speed
                text: rallyBubbleChart.text,  // Tooltip for bubbles
                mode: rallyBubbleChart.mode,
                type: rallyBubbleChart.type,
                marker: rallyBubbleChart.marker,
            }], {
                title: 'Longest Rally vs. Average Ball Speed',
                xaxis: { title: 'Longest Rally (Hits)' },
                yaxis: { title: 'Average Ball Speed (km/h)' },
            });

            const victoryBoxPlot = data.visualization_data.victory_box_plot;

            Plotly.newPlot('victory-box-plot', [{
                y: victoryBoxPlot.all_margins,  // All margins
                type: 'box',
                name: 'Victory Margins',
                boxpoints: 'all',  // Display all points
                marker: { color: '#4caf50' },  // Green for boxplot
            }], {
                title: 'Victory Margin Range',
                yaxis: { title: 'Victory Margin' },
            });

      })
      .catch(error => {
            console.log(error);
          showAlert(error.response?.data.error, "danger");
      });
  

    fetchProfile(userName)
        .then(data => {
            document.getElementById("profile-display_name").innerHTML = data.display_name || "";
            document.getElementById("profile-username").innerHTML = data.username || "";
            document.getElementById("profile-bio").innerHTML = data.bio || "";
            document.getElementById("profile-email").innerHTML = data.email || "";
            document.getElementById("profile-avatar").src = data.avatar || "./assets/default_avatar.png";

            const statusIndicator = document.getElementById("profile-status-indicator");
            if (data.is_online) {
                statusIndicator.style.backgroundColor = "green";
                statusIndicator.setAttribute("title", "Online");
            } else {
                statusIndicator.style.backgroundColor = "gray";
                statusIndicator.setAttribute("title", "Offline");
            }

            if (!data.editable) {
                document.getElementById("edit-profile-btn").style.display = "none";
                document.getElementById("logout-btn").style.display = "none";
                document.getElementById("2fa-btn").style.display = "none";
            } else {
                document.getElementById("edit-profile-btn").style.display = "block";
                document.getElementById("logout-btn").style.display = "block";
                document.getElementById("2fa-btn").style.display = "block";
                if (data.two_factor_enabled)
                {
                    document.getElementById("2fa-btn").innerHTML = "2FA Enabled"
                    document.getElementById("2fa-btn").disabled = true;
                }

                document.getElementById("logout-btn").addEventListener('click', async () => {
                    const logged_out = await logout();
                    localStorage.clear();
                    if (logged_out)
                    {
                        window.location.hash = 'login';
                    }
                });

                document.getElementById("2fa-btn").addEventListener('click', async () => {
                    const setup_successful = await setup2fa();
                    if (setup_successful)
                    {
                        document.getElementById("2fa-btn").innerHTML = '2FA Enabled'
                        document.getElementById("2fa-btn").disabled = true;
                    }
                });

                document.getElementById("delete-btn").addEventListener('click', async () => {
                    const delete_successfull = await deleteAccount();
                    if (delete_successfull)
                    {
                        window.location.hash = "login";
                    }
                });
            }
        })
        .catch(error => {
            showAlert(error.response?.data.error, "danger");
        });

    fetchMatchHistory(userName)
    .then(data => {                                                                              
        console.log(data);
        const HistoryContainer = document.getElementById("matches-container");
        HistoryContainer.innerHTML = "";
        data.forEach(element => {
            const matchId = element.id; // Assuming the match ID is present in the `element`
            const opponentUsername = element.opponent || 'Unknown';
            const score = element.player1_score || 0;
            const score2 = element.player2_score || 0;
            const forfeit = element.forfeit;
            const result = element.result || 'Not Available';
            const isWinner = result === "Win";

            const createdAt = new Date(element.created_at);
            const timeAgo = getTimeAgo(createdAt);

            // Add event listener for each match card
            const matchCardHTML = `
            <div id="opponent-card" class="d-flex gap-2" data-match-id="${matchId}" style="cursor: pointer;">
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
        });

        // Add event listener to all match cards
        document.querySelectorAll('#opponent-card').forEach(card => {
            card.addEventListener('click', function () {
                const matchId = this.getAttribute('data-match-id');
                // Change the hash to include the match ID
                window.location.hash = `match?matchId=${matchId}`;
            });
        });
    })
    .catch(error => {
        showAlert(error.response?.data.error, "danger");
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
