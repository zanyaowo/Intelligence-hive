// Sessions Component

const SessionsComponent = {
    /**
     * Load sessions data
     * @param {string} selectedDate - Selected date
     * @param {Object} params - Additional query parameters
     * @returns {Promise<void>}
     */
    async load(selectedDate, params = {}) {
        try {
            const store = window.AppStore;
            const defaultParams = {
                date: selectedDate,
                limit: store.pagination.sessions.limit,
                offset: store.pagination.sessions.offset,
                ...params
            };
            const data = await API.getSessions(defaultParams);
            store.setSessionsData(data);
            this.render(data);
        } catch (error) {
            throw new Error('會話列表載入失敗');
        }
    },

    /**
     * Render sessions list
     * @param {Object} data - Sessions data
     */
    render(data) {
        const container = document.getElementById('sessions-content');
        const store = window.AppStore;

        if (!data || !data.sessions || data.sessions.length === 0) {
            container.innerHTML = '<p class="text-black text-center py-12 font-medium">暫無會話數據</p>';
            return;
        }

        container.innerHTML = `
            <!-- Filters -->
            <div class="bg-gray-800 rounded-lg shadow p-4 mb-4">
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-200 mb-1">威脅等級</label>
                        <select class="w-full border-gray-600 bg-gray-700 text-white rounded-md shadow-sm" id="threat-level-filter">
                            <option value="">全部</option>
                            <option value="CRITICAL">CRITICAL</option>
                            <option value="HIGH">HIGH</option>
                            <option value="MEDIUM">MEDIUM</option>
                            <option value="LOW">LOW</option>
                            <option value="INFO">INFO</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-200 mb-1">攻擊類型</label>
                        <select class="w-full border-gray-600 bg-gray-700 text-white rounded-md shadow-sm" id="attack-type-filter">
                            <option value="">全部</option>
                            <option value="sqli">SQL 注入</option>
                            <option value="xss">XSS</option>
                            <option value="cmd_exec">命令執行</option>
                            <option value="lfi">本地檔案包含</option>
                            <option value="rfi">遠端檔案包含</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-200 mb-1">最小風險分數</label>
                        <input type="number" min="0" max="100" placeholder="0-100"
                               class="w-full border-gray-600 bg-gray-700 text-white rounded-md shadow-sm" id="min-risk-filter">
                    </div>
                    <div class="flex items-end">
                        <button onclick="app().applySessionFilters()"
                                class="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                            篩選
                        </button>
                    </div>
                </div>
            </div>

            <!-- Sessions Table -->
            <div class="bg-gray-800 rounded-lg shadow overflow-hidden">
                <div class="overflow-x-auto">
                    ${TableTemplates.sessionsTable(data.sessions)}
                </div>

                <!-- Pagination -->
                <div class="px-6 py-4 border-t border-gray-700 flex items-center justify-between">
                    <div class="text-sm text-white">
                        顯示 ${store.pagination.sessions.offset + 1}-${store.pagination.sessions.offset + data.sessions.length} 條，共 ${data.total} 條
                    </div>
                    <div class="flex space-x-2">
                        <button onclick="app().prevPageSessions()"
                                ${store.pagination.sessions.offset === 0 ? 'disabled' : ''}
                                class="px-4 py-2 bg-gray-700 text-white border border-gray-600 rounded hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed">
                            ← 上一頁
                        </button>
                        <button onclick="app().nextPageSessions()"
                                ${!data.has_more ? 'disabled' : ''}
                                class="px-4 py-2 bg-gray-700 text-white border border-gray-600 rounded hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed">
                            下一頁 →
                        </button>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Apply filters to sessions list
     */
    applyFilters() {
        const threatLevel = document.getElementById('threat-level-filter')?.value;
        const attackType = document.getElementById('attack-type-filter')?.value;
        const minRisk = document.getElementById('min-risk-filter')?.value;

        const store = window.AppStore;
        store.resetSessionsPagination();

        const params = {};
        if (threatLevel) params.threat_level = threatLevel;
        if (attackType) params.attack_type = attackType;
        if (minRisk) params.min_risk = minRisk;

        return params;
    }
};

window.SessionsComponent = SessionsComponent;
