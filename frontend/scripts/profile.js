const dummyProfile = {
    username: "john_doe_123",
    display_name: "John Doe",
    email: "john.doe@example.com",
    bio: "Gamer, programmer, and sports enthusiast. Always up for a challenge!",
    avatar: "https://www.example.com/avatars/john_doe.png",  // Replace with actual avatar URL
    is_online: true,
    last_seen: "2024-11-22T18:30:00Z",
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
    stats: {
        wins: 150,
        losses: 75,
        gamesPlayed: 225,
        points_for: 650,
        points_against: 520,
        highest_win_streak: 8,
        tournaments_won: 5,
        tournaments_played: 10
    }
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
    let progress1 = 0;
    let end1 = parseInt(percentageText1.textContent) || 0;

    let progress2 = 0;
    let end2 = parseInt(percentageText2.textContent) || 0;

    // Function to update progress for both canvases
    function updateProgress() {
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

    // Start updating progress for both progress bars
    updateProgress();
}
