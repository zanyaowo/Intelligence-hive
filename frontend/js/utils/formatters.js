// Formatting Utility Functions

const Formatters = {
    /**
     * Get risk score color class
     * @param {number} score - Risk score (0-100)
     * @returns {string} Tailwind color class
     */
    getRiskColor(score) {
        if (score >= 90) return 'text-red-600';
        if (score >= 70) return 'text-orange-600';
        if (score >= 40) return 'text-yellow-600';
        if (score >= 20) return 'text-green-600';
        return 'text-gray-600';
    },

    /**
     * Get threat level badge HTML
     * @param {string} level - Threat level (CRITICAL, HIGH, MEDIUM, LOW, INFO)
     * @returns {string} Badge HTML
     */
    getThreatBadge(level) {
        const badges = {
            CRITICAL: '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">CRITICAL</span>',
            HIGH: '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-orange-100 text-orange-800">HIGH</span>',
            MEDIUM: '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">MEDIUM</span>',
            LOW: '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">LOW</span>',
            INFO: '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">INFO</span>'
        };
        return badges[level] || badges.INFO;
    },

    /**
     * Format timestamp to localized string
     * @param {string} timestamp - ISO timestamp
     * @param {object} options - Intl.DateTimeFormat options
     * @returns {string} Formatted date string
     */
    formatTimestamp(timestamp, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        return new Date(timestamp).toLocaleString('zh-TW', { ...defaultOptions, ...options });
    },

    /**
     * Format bytes to human-readable string
     * @param {number} bytes - Bytes
     * @returns {string} Formatted string (e.g., "1.5 MB")
     */
    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    /**
     * Get reputation color and text
     * @param {number} score - Reputation score (0-1)
     * @returns {object} Color configuration
     */
    getReputationColor(score) {
        if (score >= 0.8) return { color: 'green', text: '良好', bg: 'bg-green-50', border: 'border-green-200' };
        if (score >= 0.5) return { color: 'blue', text: '中立', bg: 'bg-blue-50', border: 'border-blue-200' };
        if (score >= 0.3) return { color: 'yellow', text: '可疑', bg: 'bg-yellow-50', border: 'border-yellow-200' };
        return { color: 'red', text: '惡意', bg: 'bg-red-50', border: 'border-red-200' };
    },

    /**
     * Check if IP is private
     * @param {string} ip - IP address
     * @returns {boolean} True if private IP
     */
    isPrivateIP(ip) {
        if (!ip) return false;
        return (
            ip.startsWith('192.168.') ||
            ip.startsWith('10.') ||
            ip.startsWith('172.16.') ||
            ip.startsWith('172.17.') ||
            ip.startsWith('172.18.') ||
            ip.startsWith('172.19.') ||
            ip.startsWith('172.2') ||
            ip.startsWith('172.30.') ||
            ip.startsWith('172.31.') ||
            ip.startsWith('127.') ||
            ip === 'localhost'
        );
    }
};

window.Formatters = Formatters;
