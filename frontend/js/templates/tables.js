// Table Template Generators

const TableTemplates = {
    /**
     * Create alerts table
     * @param {Array} alerts - Alert data
     * @returns {string} Table HTML
     */
    alertsTable(alerts) {
        return `
            <table class="min-w-full divide-y divide-gray-700">
                <thead class="bg-gray-900">
                    <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">時間</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">來源 IP</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">告警等級</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">風險分數</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">攻擊類型</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">工具</th>
                    </tr>
                </thead>
                <tbody class="bg-gray-800 divide-y divide-gray-700">
                    ${alerts.map(alert => `
                        <tr class="hover:bg-gray-700 cursor-pointer" onclick="app().showSessionDetail('${alert.sess_uuid}')">
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                                ${new Date(alert.processed_at).toLocaleString('zh-TW')}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-mono text-white">${alert.peer_ip}</td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                ${Formatters.getThreatBadge(alert.alert_level)}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span class="text-lg font-bold ${Formatters.getRiskColor(alert.risk_score)}">${alert.risk_score}</span>
                            </td>
                            <td class="px-6 py-4 text-sm text-gray-300">
                                ${alert.attack_types.slice(0, 2).join(', ')}
                                ${alert.attack_types.length > 2 ? `<span class="text-gray-500">+${alert.attack_types.length - 2}</span>` : ''}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-300">${alert.tool_identified || '-'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    },

    /**
     * Create sessions table
     * @param {Array} sessions - Session data
     * @returns {string} Table HTML
     */
    sessionsTable(sessions) {
        return `
            <table class="min-w-full divide-y divide-gray-700">
                <thead class="bg-gray-900">
                    <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">來源 IP</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">User Agent</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">攻擊類型</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">風險</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">威脅等級</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">時間</th>
                    </tr>
                </thead>
                <tbody class="bg-gray-800 divide-y divide-gray-700">
                    ${sessions.map(session => `
                        <tr class="hover:bg-gray-700 cursor-pointer" onclick="app().showSessionDetail('${session.sess_uuid}')">
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-mono text-white">${session.peer_ip}</td>
                            <td class="px-6 py-4 text-sm text-gray-300 max-w-xs truncate">${session.user_agent}</td>
                            <td class="px-6 py-4 text-sm text-gray-300">
                                ${[...new Set(session.attack_types)].slice(0, 2).join(', ')}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span class="text-lg font-bold ${Formatters.getRiskColor(session.risk_score)}">${session.risk_score}</span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                ${Formatters.getThreatBadge(session.threat_level)}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                                ${new Date(session.processed_at).toLocaleString('zh-TW', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    },

    /**
     * Create top IPs table
     * @param {Object} ips - IP count map
     * @returns {string} Table HTML
     */
    topIPsTable(ips) {
        const sortedIPs = Object.entries(ips).sort((a, b) => b[1] - a[1]).slice(0, 10);
        if (sortedIPs.length === 0) {
            return '<p class="text-white text-center py-4 font-medium">暫無數據</p>';
        }

        const total = sortedIPs.reduce((sum, [, c]) => sum + c, 0);

        return `
            <table class="min-w-full">
                <thead>
                    <tr class="border-b border-gray-700">
                        <th class="px-4 py-2 text-left text-gray-300">#</th>
                        <th class="px-4 py-2 text-left text-gray-300">IP 位址</th>
                        <th class="px-4 py-2 text-right text-gray-300">攻擊次數</th>
                        <th class="px-4 py-2 text-right text-gray-300">佔比</th>
                    </tr>
                </thead>
                <tbody>
                    ${sortedIPs.map(([ip, count], index) => {
                        const percentage = ((count / total) * 100).toFixed(1);
                        return `
                            <tr class="border-b border-gray-700 hover:bg-gray-700">
                                <td class="px-4 py-2 text-gray-300">${index + 1}</td>
                                <td class="px-4 py-2 font-mono text-white">${ip}</td>
                                <td class="px-4 py-2 text-right font-semibold text-white">${count}</td>
                                <td class="px-4 py-2 text-right text-gray-400">${percentage}%</td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        `;
    }
};

window.TableTemplates = TableTemplates;
