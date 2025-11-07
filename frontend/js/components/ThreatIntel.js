// Threat Intelligence Component

const ThreatIntelComponent = {
    /**
     * Load threat intelligence data
     * @param {string} selectedDate - Selected date
     * @returns {Promise<void>}
     */
    async load(selectedDate) {
        try {
            const data = await API.getThreatIntelligence(selectedDate);
            window.AppStore.setIntelData(data);
            this.render(data);
        } catch (error) {
            throw new Error('威脅情報載入失敗');
        }
    },

    /**
     * Render threat intelligence
     * @param {Object} data - Threat intelligence data
     */
    render(data) {
        const container = document.getElementById('intel-content');

        if (!data) {
            container.innerHTML = '<p class="text-white text-center py-12 font-medium">暫無威脅情報</p>';
            return;
        }

        container.innerHTML = `
            <!-- Statistics Cards -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                ${CardTemplates.statCard('惡意 IP', data.malicious_ips_count || 0, 'red')}
                ${CardTemplates.statCard('攻擊特徵', data.attack_signatures_count || 0, 'orange')}
                ${CardTemplates.statCard('惡意 UA', (data.malicious_user_agents || []).length, 'purple')}
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Malicious IP List -->
                <div class="bg-gray-800 rounded-lg shadow p-6">
                    <div class="flex justify-between items-center mb-4">
                        <h3 class="text-lg font-semibold text-white">惡意 IP 列表</h3>
                        <button onclick="ClipboardUtils.copy(${JSON.stringify(data.malicious_ips || [])})"
                                class="text-sm text-blue-400 hover:text-blue-300">
                            複製
                        </button>
                    </div>
                    <div class="max-h-96 overflow-y-auto">
                        ${ListTemplates.ipList(data.malicious_ips || [])}
                    </div>
                </div>

                <!-- Malicious User Agents -->
                <div class="bg-gray-800 rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold text-white mb-4">惡意 User Agent</h3>
                    <div class="max-h-96 overflow-y-auto">
                        ${ListTemplates.uaList(data.malicious_user_agents || [])}
                    </div>
                </div>
            </div>

            <!-- Attack Signatures -->
            <div class="bg-gray-800 rounded-lg shadow p-6 mt-6">
                <h3 class="text-lg font-semibold text-white mb-4">攻擊特徵</h3>
                <div class="flex flex-wrap gap-2">
                    ${ListTemplates.signatureList(data.attack_signatures || [])}
                </div>
            </div>
        `;
    }
};

window.ThreatIntelComponent = ThreatIntelComponent;
