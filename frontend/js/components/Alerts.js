// Alerts Component

const AlertsComponent = {
    /**
     * Load alerts data
     * @param {string} selectedDate - Selected date
     * @param {Object} params - Additional query parameters
     * @returns {Promise<void>}
     */
    async load(selectedDate, params = {}) {
        try {
            const defaultParams = {
                date: selectedDate,
                limit: 50,
                ...params
            };
            const data = await API.getAlerts(defaultParams);
            window.AppStore.setAlertsData(data);
            this.render(data);
        } catch (error) {
            throw new Error('告警數據載入失敗');
        }
    },

    /**
     * Render alerts list
     * @param {Object} data - Alerts data
     */
    render(data) {
        const container = document.getElementById('alerts-content');

        if (!data || !data.alerts || data.alerts.length === 0) {
            container.innerHTML = '<p class="text-white text-center py-12 font-medium">暫無告警</p>';
            return;
        }

        const criticalCount = data.alerts.filter(a => a.alert_level === 'CRITICAL').length;
        const highCount = data.alerts.filter(a => a.alert_level === 'HIGH').length;

        container.innerHTML = `
            <!-- Alert Statistics -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                ${CardTemplates.statCard('CRITICAL 告警', criticalCount, 'red')}
                ${CardTemplates.statCard('HIGH 告警', highCount, 'orange')}
                ${CardTemplates.statCard('總告警數', data.total, 'blue')}
            </div>

            <!-- Alerts List -->
            <div class="bg-gray-800 rounded-lg shadow overflow-hidden">
                ${TableTemplates.alertsTable(data.alerts)}
            </div>
        `;
    }
};

window.AlertsComponent = AlertsComponent;
