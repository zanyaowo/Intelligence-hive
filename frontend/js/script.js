document.addEventListener('DOMContentLoaded', () => {
    // Placeholder data - in a real application, you would fetch this from your API
    const totalAttacks = 1234;
    const uniqueIps = 567;
    const topAttackType = 'SQL Injection';
    const recentEvents = [
        { timestamp: new Date().toISOString(), type: 'XSS', ip: '192.168.1.101', details: 'Attempted XSS on /login' },
        { timestamp: new Date().toISOString(), type: 'SQL Injection', ip: '10.0.0.5', details: 'UNION SELECT on /products' },
        { timestamp: new Date().toISOString(), type: 'Directory Traversal', ip: '172.16.0.20', details: '../../etc/passwd' },
        { timestamp: new Date().toISOString(), type: 'Port Scan', ip: '203.0.113.15', details: 'Nmap scan on port 22' },
    ];

    // Update overview cards
    document.getElementById('total-attacks').textContent = totalAttacks;
    document.getElementById('unique-ips').textContent = uniqueIps;
    document.getElementById('top-attack-type').textContent = topAttackType;

    // Populate recent events
    const eventList = document.getElementById('event-list');
    eventList.innerHTML = ''; // Clear existing items
    recentEvents.forEach(event => {
        const li = document.createElement('li');
        li.textContent = `[${new Date(event.timestamp).toLocaleString()}] ${event.type} from ${event.ip} - ${event.details}`;
        eventList.appendChild(li);
    });
});
