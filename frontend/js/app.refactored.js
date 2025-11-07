// Main Application Controller
// Refactored from 1301 lines God Object to clean modular architecture

function app() {
    const store = window.AppStore;

    return {
        // Expose state for Alpine.js reactivity
        get currentTab() { return store.currentTab; },
        get loading() { return store.loading; },
        get error() { return store.error; },
        get successMessage() { return store.successMessage; },
        get selectedDate() { return store.selectedDate; },
        get availableDates() { return store.availableDates; },
        get sessionDetailModal() { return store.sessionDetailModal; },

        // Initialization
        async init() {
            dayjs.extend(window.dayjs_plugin_relativeTime);
            await this.loadAvailableDates();
            await this.loadData();
        },

        // Load available dates
        async loadAvailableDates() {
            try {
                const response = await API.getDates();
                const dates = response.dates || [];
                store.setAvailableDates(dates);

                if (dates.length > 0) {
                    store.setSelectedDate(dates[0]);
                } else {
                    console.warn('No available dates from API, falling back to today.');
                    const today = new Date().toISOString().split('T')[0];
                    store.setSelectedDate(today);
                    store.setAvailableDates([today]);
                }
            } catch (error) {
                console.error('Failed to load dates:', error);
                const today = new Date().toISOString().split('T')[0];
                store.setSelectedDate(today);
                store.setAvailableDates([today]);
            }
        },

        // Load data based on current tab
        async loadData() {
            store.clearError();
            store.setLoading(true);

            try {
                switch (store.currentTab) {
                    case 'dashboard':
                        await DashboardComponent.load(store.selectedDate);
                        break;
                    case 'sessions':
                        await SessionsComponent.load(store.selectedDate);
                        break;
                    case 'alerts':
                        await AlertsComponent.load(store.selectedDate);
                        break;
                    case 'statistics':
                        await StatisticsComponent.load(store.selectedDate, store.statsDays);
                        break;
                    case 'intel':
                        await ThreatIntelComponent.load(store.selectedDate);
                        break;
                }
            } catch (error) {
                store.showError(`載入資料失敗: ${error.message}`);
                console.error('Load data error:', error);
            } finally {
                store.setLoading(false);
            }
        },

        // Session list methods
        async applySessionFilters() {
            const params = SessionsComponent.applyFilters();
            await SessionsComponent.load(store.selectedDate, params);
        },

        async nextPageSessions() {
            store.nextSessionsPage();
            await SessionsComponent.load(store.selectedDate);
        },

        async prevPageSessions() {
            store.prevSessionsPage();
            await SessionsComponent.load(store.selectedDate);
        },

        // Alert list methods
        async nextPageAlerts() {
            store.nextAlertsPage();
            await AlertsComponent.load(store.selectedDate);
        },

        async prevPageAlerts() {
            store.prevAlertsPage();
            await AlertsComponent.load(store.selectedDate);
        },

        // Statistics methods
        async changeStatsDays(days) {
            store.setStatsDays(days);
            await StatisticsComponent.load(store.selectedDate, days);
        },

        // Session detail modal
        async showSessionDetail(uuid) {
            await SessionDetailModal.show(uuid);
        },

        copySessionDetail() {
            if (store.sessionDetailModal.data) {
                ClipboardUtils.copy(store.sessionDetailModal.data);
            }
        },

        // Utility methods
        copyToClipboard(data) {
            ClipboardUtils.copy(data);
        },

        // Error handling
        showError(message, duration = 5000) {
            store.showError(message, duration);
        },

        showSuccess(message, duration = 3000) {
            store.showSuccess(message, duration);
        },

        // Loading skeleton (still needed for Alpine.js templates)
        createLoadingSkeleton(type = 'card') {
            return SkeletonLoader.create(type);
        }
    };
}
