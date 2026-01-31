// Inside website/app.js

async function fetchRealTimeData() {
    try {
        // 1. Ask the Python Backend for the latest numbers
        const response = await fetch('http://127.0.0.1:5000/stream-data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ /* Simulating sensor data sending */ })
        });

        const data = await response.json();

        // 2. Update the HTML elements with the new data
        document.getElementById('activity-display').innerText = data.activity;
        document.getElementById('score-display').innerText = data.score + "%";

        // 3. Change color based on health score
        const scoreBox = document.getElementById('score-display');
        if (data.score < 50) {
            scoreBox.style.color = "red";
        } else {
            scoreBox.style.color = "green";
        }

    } catch (error) {
        console.error("Error connecting to Python backend:", error);
    }
}

// Run this function every 500 milliseconds (0.5 seconds)
setInterval(fetchRealTimeData, 500);