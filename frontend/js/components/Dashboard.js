// Dashboard Component

const DashboardComponent = {
    /**
     * Load dashboard data
     * @param {string} selectedDate - Selected date
     * @returns {Promise<void>}
     */
    async load(selectedDate) {
        try {
            const data = await API.getDashboard(selectedDate);
            window.AppStore.setDashboardData(data);
            this.render(data);
        } catch (error) {
            throw new Error('儀表板數據載入失敗');
        }
    },

    /**
     * Render dashboard
     * @param {Object} data - Dashboard data
     */
    render(data) {
        const container = document.getElementById('dashboard-content');

        if (!data || !data.today_summary) {
            container.innerHTML = '<p class="text-black text-center py-12 font-medium">暫無數據</p>';
            return;
        }

        const summary = data.today_summary;
        const recentAlerts = data.recent_alerts || [];
        const topThreats = data.top_threats || {};

        container.innerHTML = `
            <!-- Overview Cards -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
                ${CardTemplates.statCard('總攻擊次數', summary.total_sessions, 'blue')}
                ${CardTemplates.statCard('高風險會話', summary.high_risk_count, 'orange')}
                ${CardTemplates.statCard('關鍵告警', summary.critical_alerts, 'red')}
                ${CardTemplates.statCard('平均風險', summary.average_risk?.toFixed(1) || '0', 'purple')}
                ${CardTemplates.statCard('獨立IP數', summary.unique_ips, 'green')}
            </div>

            <!-- Charts Area -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                <!-- Attack Type Distribution -->
                <div class="bg-gray-800 rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold text-white mb-4">攻擊類型分佈</h3>
                    <canvas id="attackTypeChart"></canvas>
                </div>

                <!-- Top Attack Sources -->
                <div class="bg-gray-800 rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold text-white mb-4">Top 攻擊來源 IP</h3>
                    <canvas id="topIPsChart"></canvas>
                </div>
            </div>

            <!-- Recent Alerts -->
            <div class="bg-gray-800 rounded-lg shadow p-6">
                <h3 class="text-lg font-semibold text-white mb-4">最近告警</h3>
                <div class="overflow-x-auto">
                    ${recentAlerts.length > 0 ? TableTemplates.alertsTable(recentAlerts) : '<p class="text-white text-center py-4 font-medium">暫無告警</p>'}
                </div>
            </div>
        `;

        // Render charts after DOM update
        setTimeout(() => {
            window.Charts.renderPieChart('attackTypeChart', topThreats.top_attacks || {}, '攻擊類型');
            window.Charts.renderBarChart('topIPsChart', topThreats.top_ips || {}, 'Top IPs');
        }, 100);
    }
};

window.DashboardComponent = DashboardComponent;
