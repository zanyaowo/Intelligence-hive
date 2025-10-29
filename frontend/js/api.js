// API 調用模組
const API = {
    baseURL: 'http://localhost:8083/api',

    // 通用請求方法
    async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    },

    // 獲取儀表板資料
    async getDashboard(date = null) {
        const params = date ? `?date=${date}` : '';
        return await this.request(`/dashboard${params}`);
    },

    // 獲取會話列表
    async getSessions(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return await this.request(`/sessions${queryString ? '?' + queryString : ''}`);
    },

    // 獲取單個會話詳情
    async getSession(uuid) {
        return await this.request(`/sessions/${uuid}`);
    },

    // 獲取告警列表
    async getAlerts(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return await this.request(`/alerts${queryString ? '?' + queryString : ''}`);
    },

    // 獲取統計資料
    async getStatistics(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return await this.request(`/statistics${queryString ? '?' + queryString : ''}`);
    },

    // 獲取威脅情報
    async getThreatIntelligence(date = null) {
        const params = date ? `?date=${date}` : '';
        return await this.request(`/threat-intelligence${params}`);
    },

    // 獲取可用日期列表
    async getDates() {
        return await this.request('/dates');
    }
};
