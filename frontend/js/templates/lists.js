// List Template Generators

const ListTemplates = {
    /**
     * Create IP list
     * @param {Array} ips - IP addresses
     * @returns {string} List HTML
     */
    ipList(ips) {
        if (ips.length === 0) {
            return '<p class="text-white text-center py-4 font-medium">暫無數據</p>';
        }
        return `
            <div class="space-y-1">
                ${ips.map(ip => `
                    <div class="px-3 py-2 bg-gray-700 rounded font-mono text-sm text-white hover:bg-gray-600">
                        ${ip}
                    </div>
                `).join('')}
            </div>
        `;
    },

    /**
     * Create User Agent list
     * @param {Array} uas - User agents
     * @returns {string} List HTML
     */
    uaList(uas) {
        if (uas.length === 0) {
            return '<p class="text-white text-center py-4 font-medium">暫無數據</p>';
        }
        return `
            <div class="space-y-2">
                ${uas.map(ua => `
                    <div class="px-3 py-2 bg-gray-700 rounded text-sm text-white hover:bg-gray-600">
                        ${ua}
                    </div>
                `).join('')}
            </div>
        `;
    },

    /**
     * Create signature list
     * @param {Array} signatures - Attack signatures
     * @returns {string} List HTML
     */
    signatureList(signatures) {
        if (signatures.length === 0) {
            return '<p class="text-white font-medium">暫無數據</p>';
        }
        return signatures.map(sig => `
            <span class="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">
                ${sig}
            </span>
        `).join('');
    }
};

window.ListTemplates = ListTemplates;
