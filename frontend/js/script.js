document.addEventListener('DOMContentLoaded', () => {
    const API_URL = 'http://localhost:8083/api/dashboard';

    async function updateDashboard() {
        try {
            const response = await fetch(API_URL);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();

            // Update overview cards
            document.getElementById('total-attacks').textContent = data.today_summary.total_sessions;
            document.getElementById('unique-ips').textContent = data.today_summary.unique_ips;
            
            const topAttack = Object.entries(data.top_threats.top_attacks).sort(([,a],[,b]) => b-a)[0];
            document.getElementById('top-attack-type').textContent = topAttack ? topAttack[0] : '-';

            // Populate recent events
            const eventList = document.getElementById('event-list');
            eventList.innerHTML = ''; // Clear existing items
            if (data.recent_alerts && data.recent_alerts.length > 0) {
                data.recent_alerts.forEach(event => {
                    const li = document.createElement('li');
                    li.textContent = `[${new Date(event.processed_at).toLocaleString()}] ${event.attack_types.join(', ')} from ${event.peer_ip} - Risk: ${event.risk_score}`;
                    eventList.appendChild(li);
                });
            } else {
                const li = document.createElement('li');
                li.textContent = 'No recent events found.';
                eventList.appendChild(li);
            }
        } catch (error) {
            console.error('Failed to fetch dashboard data:', error);
            // Display error message to the user
            document.getElementById('overview').innerHTML = '<p>Error loading data. Please check the console for details.</p>';
            document.getElementById('recent-events').innerHTML = '';
        }
    }

    updateDashboard();
    // Optionally, refresh data every 30 seconds
    // setInterval(updateDashboard, 30000);
});
