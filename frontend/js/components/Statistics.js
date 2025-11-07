// Statistics Component

const StatisticsComponent = {
    /**
     * Load statistics data
     * @param {string} selectedDate - Selected date
     * @param {number} days - Number of days
     * @returns {Promise<void>}
     */
    async load(selectedDate, days = 7) {
        try {
            const data = await API.getStatistics({
                date: selectedDate,
                days: days
            });
            window.AppStore.setStatisticsData(data);
            this.render(data, days);
        } catch (error) {
            throw new Error('統計數據載入失敗');
        }
    },

    /**
     * Render statistics
     * @param {Object} data - Statistics data
     * @param {number} days - Current days selection
     */
    render(data, days) {
        const container = document.getElementById('statistics-content');

        if (!data) {
            container.innerHTML = '<p class="text-white text-center py-12 font-medium">暫無統計數據</p>';
            return;
        }

        container.innerHTML = `
            <!-- Date Range Selector -->
            <div class="bg-gray-800 rounded-lg shadow p-4 mb-6">
                <div class="flex items-center justify-between">
                    <h3 class="text-lg font-semibold text-white">統計時間範圍</h3>
                    <div class="flex space-x-2">
                        <button onclick="app().changeStatsDays(1)"
                                class="px-4 py-2 rounded-lg transition ${days === 1 ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-200 hover:bg-gray-600'}">
                            今天
                        </button>
                        <button onclick="app().changeStatsDays(7)"
                                class="px-4 py-2 rounded-lg transition ${days === 7 ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-200 hover:bg-gray-600'}">
                            7 天
                        </button>
                        <button onclick="app().changeStatsDays(30)"
                                class="px-4 py-2 rounded-lg transition ${days === 30 ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-200 hover:bg-gray-600'}">
                            30 天
                        </button>
                    </div>
                </div>
            </div>

            <!-- Statistics Cards -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                ${CardTemplates.statCard('總會話數', data.total_sessions, 'blue')}
                ${CardTemplates.statCard('平均風險分數', data.average_risk_score?.toFixed(1) || '0', 'purple')}
                ${CardTemplates.statCard('需審查數量', data.requires_review_count, 'orange')}
            </div>

            <!-- Charts -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="bg-gray-800 rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold text-white mb-4">威脅等級分佈</h3>
                    <canvas id="threatLevelChart"></canvas>
                </div>
                <div class="bg-gray-800 rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold text-white mb-4">攻擊類型分佈</h3>
                    <canvas id="attackDistChart"></canvas>
                </div>
            </div>

            <!-- Top IP Table -->
            <div class="bg-gray-800 rounded-lg shadow p-6 mt-6">
                <h3 class="text-lg font-semibold text-white mb-4">Top 來源 IP</h3>
                ${TableTemplates.topIPsTable(data.top_source_ips || {})}
            </div>
        `;

        setTimeout(() => {
            window.Charts.renderDoughnutChart('threatLevelChart', data.threat_level_distribution || {}, '威脅等級');
            window.Charts.renderHorizontalBarChart('attackDistChart', data.attack_type_distribution || {}, '攻擊分佈');
        }, 100);
    }
};

window.StatisticsComponent = StatisticsComponent;
