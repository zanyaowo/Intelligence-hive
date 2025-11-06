// State Management Module
// Centralized application state management

class AppStore {
    constructor() {
        // UI State
        this.currentTab = 'dashboard';
        this.loading = false;
        this.error = null;
        this.selectedDate = null;
        this.availableDates = [];

        // Data Cache
        this.dashboardData = null;
        this.sessionsData = null;
        this.alertsData = null;
        this.statisticsData = null;
        this.intelData = null;

        // Modal State
        this.sessionDetailModal = {
            isOpen: false,
            data: null,
            loading: false
        };

        // Pagination State
        this.pagination = {
            sessions: { offset: 0, limit: 50 },
            alerts: { offset: 0, limit: 50 }
        };

        // Statistics Page State
        this.statsDays = 7;

        // Message Timers
        this.errorTimer = null;
        this.successMessage = '';
        this.successTimer = null;
    }

    // State Setters
    setCurrentTab(tab) {
        this.currentTab = tab;
    }

    setLoading(loading) {
        this.loading = loading;
    }

    setError(error) {
        this.error = error;
    }

    setSelectedDate(date) {
        this.selectedDate = date;
    }

    setAvailableDates(dates) {
        this.availableDates = dates;
    }

    setDashboardData(data) {
        this.dashboardData = data;
    }

    setSessionsData(data) {
        this.sessionsData = data;
    }

    setAlertsData(data) {
        this.alertsData = data;
    }

    setStatisticsData(data) {
        this.statisticsData = data;
    }

    setIntelData(data) {
        this.intelData = data;
    }

    setStatsDays(days) {
        this.statsDays = days;
    }

    // Modal Management
    openModal(data = null) {
        this.sessionDetailModal.isOpen = true;
        this.sessionDetailModal.data = data;
        this.sessionDetailModal.loading = true;
    }

    closeModal() {
        this.sessionDetailModal.isOpen = false;
        this.sessionDetailModal.data = null;
        this.sessionDetailModal.loading = false;
    }

    setModalData(data) {
        this.sessionDetailModal.data = data;
        this.sessionDetailModal.loading = false;
    }

    // Pagination Management
    resetSessionsPagination() {
        this.pagination.sessions.offset = 0;
    }

    nextSessionsPage() {
        this.pagination.sessions.offset += this.pagination.sessions.limit;
    }

    prevSessionsPage() {
        this.pagination.sessions.offset = Math.max(
            0,
            this.pagination.sessions.offset - this.pagination.sessions.limit
        );
    }

    nextAlertsPage() {
        this.pagination.alerts.offset += this.pagination.alerts.limit;
    }

    prevAlertsPage() {
        this.pagination.alerts.offset = Math.max(
            0,
            this.pagination.alerts.offset - this.pagination.alerts.limit
        );
    }

    // Message Management
    showError(message, duration = 5000) {
        this.error = message;

        if (this.errorTimer) {
            clearTimeout(this.errorTimer);
        }

        if (duration > 0) {
            this.errorTimer = setTimeout(() => {
                this.error = '';
            }, duration);
        }
    }

    showSuccess(message, duration = 3000) {
        this.successMessage = message;

        if (this.successTimer) {
            clearTimeout(this.successTimer);
        }

        if (duration > 0) {
            this.successTimer = setTimeout(() => {
                this.successMessage = '';
            }, duration);
        }
    }

    clearError() {
        this.error = null;
        if (this.errorTimer) {
            clearTimeout(this.errorTimer);
        }
    }

    clearSuccess() {
        this.successMessage = '';
        if (this.successTimer) {
            clearTimeout(this.successTimer);
        }
    }
}

// Export singleton instance
window.AppStore = new AppStore();
