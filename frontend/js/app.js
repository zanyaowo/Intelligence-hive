// 主應用邏輯
function app() {
    return {
        // 狀態管理
        currentTab: 'dashboard',
        loading: false,
        error: null,
        selectedDate: null,
        availableDates: [],

        // 數據緩存
        dashboardData: null,
        sessionsData: null,
        alertsData: null,
        statisticsData: null,
        intelData: null,

        // 會話詳情彈窗
        sessionDetailModal: {
            isOpen: false,
            data: null,
            loading: false
        },

        // 分頁狀態
        pagination: {
            sessions: { offset: 0, limit: 50 },
            alerts: { offset: 0, limit: 50 }
        },

        // 統計頁面狀態
        statsDays: 7,  // 預設 7 天

        // 錯誤顯示計時器
        errorTimer: null,

        // 成功訊息
        successMessage: '',
        successTimer: null,

        // 初始化
        async init() {
            dayjs.extend(window.dayjs_plugin_relativeTime);
            await this.loadAvailableDates();
            await this.loadData();
        },

        // 顯示錯誤訊息（自動消失）
        showError(message, duration = 5000) {
            this.error = message;

            // 清除之前的計時器
            if (this.errorTimer) {
                clearTimeout(this.errorTimer);
            }

            // 設置新的自動消失計時器
            if (duration > 0) {
                this.errorTimer = setTimeout(() => {
                    this.error = '';
                }, duration);
            }
        },

        // 顯示成功訊息（自動消失）
        showSuccess(message, duration = 3000) {
            this.successMessage = message;

            // 清除之前的計時器
            if (this.successTimer) {
                clearTimeout(this.successTimer);
            }

            // 設置新的自動消失計時器
            if (duration > 0) {
                this.successTimer = setTimeout(() => {
                    this.successMessage = '';
                }, duration);
            }
        },

        // 創建加載骨架屏
        createLoadingSkeleton(type = 'card') {
            switch (type) {
                case 'card':
                    return `
                        <div class="animate-pulse">
                            <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                            <div class="h-8 bg-gray-200 rounded w-1/2"></div>
                        </div>
                    `;
                case 'table':
                    return `
                        <div class="animate-pulse space-y-2">
                            ${Array(5).fill(0).map(() => `
                                <div class="h-12 bg-gray-200 rounded"></div>
                            `).join('')}
                        </div>
                    `;
                case 'chart':
                    return `
                        <div class="animate-pulse flex items-center justify-center h-64">
                            <div class="w-48 h-48 bg-gray-200 rounded-full"></div>
                        </div>
                    `;
                default:
                    return `
                        <div class="animate-pulse">
                            <div class="h-4 bg-gray-200 rounded mb-2"></div>
                            <div class="h-4 bg-gray-200 rounded w-5/6"></div>
                        </div>
                    `;
            }
        },

        // 載入可用日期
        async loadAvailableDates() {
            try {
                const response = await API.getDates();
                this.availableDates = response.dates || [];
                if (this.availableDates.length > 0) {
                    this.selectedDate = this.availableDates[0]; // 選擇最新日期
                }
            } catch (error) {
                console.error('Failed to load dates:', error);
                // 如果失敗，使用今天的日期
                this.selectedDate = new Date().toISOString().split('T')[0];
                this.availableDates = [this.selectedDate];
            }
        },

        // 根據當前標籤載入對應數據
        async loadData() {
            this.error = null;
            this.loading = true;

            try {
                switch (this.currentTab) {
                    case 'dashboard':
                        await this.loadDashboard();
                        break;
                    case 'sessions':
                        await this.loadSessions();
                        break;
                    case 'alerts':
                        await this.loadAlerts();
                        break;
                    case 'statistics':
                        await this.loadStatistics();
                        break;
                    case 'intel':
                        await this.loadThreatIntel();
                        break;
                }
            } catch (error) {
                this.showError(`載入資料失敗: ${error.message}`);
                console.error('Load data error:', error);
            } finally {
                this.loading = false;
            }
        },

        // 載入儀表板數據
        async loadDashboard() {
            try {
                this.dashboardData = await API.getDashboard(this.selectedDate);
                this.renderDashboard();
            } catch (error) {
                throw new Error('儀表板數據載入失敗');
            }
        },

        // 載入會話列表
        async loadSessions(params = {}) {
            try {
                const defaultParams = {
                    date: this.selectedDate,
                    limit: this.pagination.sessions.limit,
                    offset: this.pagination.sessions.offset,
                    ...params
                };
                this.sessionsData = await API.getSessions(defaultParams);
                this.renderSessions();
            } catch (error) {
                throw new Error('會話列表載入失敗');
            }
        },

        // 載入告警列表
        async loadAlerts(params = {}) {
            try {
                const defaultParams = {
                    date: this.selectedDate,
                    limit: 50,
                    ...params
                };
                this.alertsData = await API.getAlerts(defaultParams);
                this.renderAlerts();
            } catch (error) {
                throw new Error('告警數據載入失敗');
            }
        },

        // 載入統計數據
        async loadStatistics(days = 7) {
            try {
                this.statisticsData = await API.getStatistics({
                    date: this.selectedDate,
                    days: days
                });
                this.renderStatistics();
            } catch (error) {
                throw new Error('統計數據載入失敗');
            }
        },

        // 載入威脅情報
        async loadThreatIntel() {
            try {
                this.intelData = await API.getThreatIntelligence(this.selectedDate);
                this.renderThreatIntel();
            } catch (error) {
                throw new Error('威脅情報載入失敗');
            }
        },

        // 渲染儀表板
        renderDashboard() {
            const container = document.getElementById('dashboard-content');
            const data = this.dashboardData;

            if (!data || !data.today_summary) {
                container.innerHTML = '<p class="text-black text-center py-12 font-medium">暫無數據</p>';
                return;
            }

            const summary = data.today_summary;
            const recentAlerts = data.recent_alerts || [];
            const topThreats = data.top_threats || {};

            container.innerHTML = `
                <!-- 概覽卡片 -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
                    ${this.createStatCard('總攻擊次數', summary.total_sessions, 'blue')}
                    ${this.createStatCard('高風險會話', summary.high_risk_count, 'orange')}
                    ${this.createStatCard('關鍵告警', summary.critical_alerts, 'red')}
                    ${this.createStatCard('平均風險', summary.average_risk?.toFixed(1) || '0', 'purple')}
                    ${this.createStatCard('獨立IP數', summary.unique_ips, 'green')}
                </div>

                <!-- 圖表區域 -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                    <!-- 攻擊類型分佈 -->
                    <div class="bg-gray-800 rounded-lg shadow p-6">
                        <h3 class="text-lg font-semibold text-white mb-4">攻擊類型分佈</h3>
                        <canvas id="attackTypeChart"></canvas>
                    </div>

                    <!-- Top 攻擊來源 -->
                    <div class="bg-gray-800 rounded-lg shadow p-6">
                        <h3 class="text-lg font-semibold text-white mb-4">Top 攻擊來源 IP</h3>
                        <canvas id="topIPsChart"></canvas>
                    </div>
                </div>

                <!-- 最近告警 -->
                <div class="bg-gray-800 rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold text-white mb-4">最近告警</h3>
                    <div class="overflow-x-auto">
                        ${recentAlerts.length > 0 ? this.createAlertsTable(recentAlerts) : '<p class="text-white text-center py-4 font-medium">暫無告警</p>'}
                    </div>
                </div>
            `;

            // 繪製圖表
            setTimeout(() => {
                this.renderAttackTypeChart(topThreats.top_attacks || {});
                this.renderTopIPsChart(topThreats.top_ips || {});
            }, 100);
        },

        // 渲染會話列表
        renderSessions() {
            const container = document.getElementById('sessions-content');
            const data = this.sessionsData;

            if (!data || !data.sessions || data.sessions.length === 0) {
                container.innerHTML = '<p class="text-black text-center py-12 font-medium">暫無會話數據</p>';
                return;
            }

            container.innerHTML = `
                <!-- 過濾器 -->
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

                <!-- 會話表格 -->
                <div class="bg-gray-800 rounded-lg shadow overflow-hidden">
                    <div class="overflow-x-auto">
                        ${this.createSessionsTable(data.sessions)}
                    </div>

                    <!-- 分頁 -->
                    <div class="px-6 py-4 border-t border-gray-700 flex items-center justify-between">
                        <div class="text-sm text-white">
                            顯示 ${this.pagination.sessions.offset + 1}-${this.pagination.sessions.offset + data.sessions.length} 條，共 ${data.total} 條
                        </div>
                        <div class="flex space-x-2">
                            <button onclick="app().prevPageSessions()"
                                    ${this.pagination.sessions.offset === 0 ? 'disabled' : ''}
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

        // 渲染告警列表
        renderAlerts() {
            const container = document.getElementById('alerts-content');
            const data = this.alertsData;

            if (!data || !data.alerts || data.alerts.length === 0) {
                container.innerHTML = '<p class="text-white text-center py-12 font-medium">暫無告警</p>';
                return;
            }

            const criticalCount = data.alerts.filter(a => a.alert_level === 'CRITICAL').length;
            const highCount = data.alerts.filter(a => a.alert_level === 'HIGH').length;

            container.innerHTML = `
                <!-- 告警統計 -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    ${this.createStatCard('CRITICAL 告警', criticalCount, '🔴', 'red')}
                    ${this.createStatCard('HIGH 告警', highCount, '🟠', 'orange')}
                    ${this.createStatCard('總告警數', data.total, '📢', 'blue')}
                </div>

                <!-- 告警列表 -->
                <div class="bg-gray-800 rounded-lg shadow overflow-hidden">
                    ${this.createAlertsTable(data.alerts)}
                </div>
            `;
        },

        // 渲染統計圖表
        renderStatistics() {
            const container = document.getElementById('statistics-content');
            const data = this.statisticsData;

            if (!data) {
                container.innerHTML = '<p class="text-white text-center py-12 font-medium">暫無統計數據</p>';
                return;
            }

            container.innerHTML = `
                <!-- 日期範圍選擇器 -->
                <div class="bg-gray-800 rounded-lg shadow p-4 mb-6">
                    <div class="flex items-center justify-between">
                        <h3 class="text-lg font-semibold text-white">統計時間範圍</h3>
                        <div class="flex space-x-2">
                            <button onclick="app().changeStatsDays(1)"
                                    class="px-4 py-2 rounded-lg transition ${this.statsDays === 1 ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-200 hover:bg-gray-600'}">
                                今天
                            </button>
                            <button onclick="app().changeStatsDays(7)"
                                    class="px-4 py-2 rounded-lg transition ${this.statsDays === 7 ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-200 hover:bg-gray-600'}">
                                7 天
                            </button>
                            <button onclick="app().changeStatsDays(30)"
                                    class="px-4 py-2 rounded-lg transition ${this.statsDays === 30 ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-200 hover:bg-gray-600'}">
                                30 天
                            </button>
                        </div>
                    </div>
                </div>

                <!-- 統計卡片 -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    ${this.createStatCard('總會話數', data.total_sessions, 'blue')}
                    ${this.createStatCard('平均風險分數', data.average_risk_score?.toFixed(1) || '0', 'purple')}
                    ${this.createStatCard('需審查數量', data.requires_review_count, 'orange')}
                </div>

                <!-- 圖表 -->
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

                <!-- Top IP 表格 -->
                <div class="bg-gray-800 rounded-lg shadow p-6 mt-6">
                    <h3 class="text-lg font-semibold text-white mb-4">Top 來源 IP</h3>
                    ${this.createTopIPsTable(data.top_source_ips || {})}
                </div>
            `;

            setTimeout(() => {
                this.renderThreatLevelChart(data.threat_level_distribution || {});
                this.renderAttackDistChart(data.attack_type_distribution || {});
            }, 100);
        },

        // 渲染威脅情報
        renderThreatIntel() {
            const container = document.getElementById('intel-content');
            const data = this.intelData;

            if (!data) {
                container.innerHTML = '<p class="text-white text-center py-12 font-medium">暫無威脅情報</p>';
                return;
            }

            container.innerHTML = `
                <!-- 統計卡片 -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    ${this.createStatCard('惡意 IP', data.malicious_ips_count || 0, 'red')}
                    ${this.createStatCard('攻擊特徵', data.attack_signatures_count || 0, 'orange')}
                    ${this.createStatCard('惡意 UA', (data.malicious_user_agents || []).length, 'purple')}
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <!-- 惡意 IP 列表 -->
                    <div class="bg-gray-800 rounded-lg shadow p-6">
                        <div class="flex justify-between items-center mb-4">
                            <h3 class="text-lg font-semibold text-white">惡意 IP 列表</h3>
                            <button onclick="app().copyToClipboard(${JSON.stringify(data.malicious_ips || []).replace(/"/g, '&quot;')})"
                                    class="text-sm text-blue-400 hover:text-blue-300">
                                複製
                            </button>
                        </div>
                        <div class="max-h-96 overflow-y-auto">
                            ${this.createIPList(data.malicious_ips || [])}
                        </div>
                    </div>

                    <!-- 惡意 User Agent -->
                    <div class="bg-gray-800 rounded-lg shadow p-6">
                        <h3 class="text-lg font-semibold text-white mb-4">🤖 惡意 User Agent</h3>
                        <div class="max-h-96 overflow-y-auto">
                            ${this.createUAList(data.malicious_user_agents || [])}
                        </div>
                    </div>
                </div>

                <!-- 攻擊特徵 -->
                <div class="bg-gray-800 rounded-lg shadow p-6 mt-6">
                    <h3 class="text-lg font-semibold text-white mb-4">攻擊特徵</h3>
                    <div class="flex flex-wrap gap-2">
                        ${this.createSignatureList(data.attack_signatures || [])}
                    </div>
                </div>
            `;
        },

        // === 輔助方法 ===

        // 創建統計卡片
        createStatCard(title, value, color) {
            const colors = {
                blue: 'border-blue-500',
                red: 'border-red-500',
                orange: 'border-orange-500',
                green: 'border-green-500',
                purple: 'border-purple-500'
            };

            return `
                <div class="bg-gray-800 rounded-lg shadow p-6 border-l-4 ${colors[color]}">
                    <p class="text-sm text-gray-300 mb-1">${title}</p>
                    <p class="text-3xl font-bold text-white">${value}</p>
                </div>
            `;
        },

        // 創建告警表格
        createAlertsTable(alerts) {
            return `
                <table class="min-w-full divide-y divide-gray-700">
                    <thead class="bg-gray-900">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">時間</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">來源 IP</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">告警等級</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">風險分數</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">攻擊類型</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">工具</th>
                        </tr>
                    </thead>
                    <tbody class="bg-gray-800 divide-y divide-gray-700">
                        ${alerts.map(alert => `
                            <tr class="hover:bg-gray-700 cursor-pointer" onclick="app().showSessionDetail('${alert.sess_uuid}')">
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                                    ${new Date(alert.processed_at).toLocaleString('zh-TW')}
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-mono text-white">${alert.peer_ip}</td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    ${this.getThreatBadge(alert.alert_level)}
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <span class="text-lg font-bold ${this.getRiskColor(alert.risk_score)}">${alert.risk_score}</span>
                                </td>
                                <td class="px-6 py-4 text-sm text-gray-300">
                                    ${alert.attack_types.slice(0, 2).join(', ')}
                                    ${alert.attack_types.length > 2 ? `<span class="text-gray-500">+${alert.attack_types.length - 2}</span>` : ''}
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-300">${alert.tool_identified || '-'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        },

        // 創建會話表格
        createSessionsTable(sessions) {
            return `
                <table class="min-w-full divide-y divide-gray-700">
                    <thead class="bg-gray-900">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">來源 IP</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">User Agent</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">攻擊類型</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">風險</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">威脅等級</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">時間</th>
                        </tr>
                    </thead>
                    <tbody class="bg-gray-800 divide-y divide-gray-700">
                        ${sessions.map(session => `
                            <tr class="hover:bg-gray-700 cursor-pointer" @click="showSessionDetail('${session.sess_uuid}')">
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-mono text-white">${session.peer_ip}</td>
                                <td class="px-6 py-4 text-sm text-gray-300 max-w-xs truncate">${session.user_agent}</td>
                                <td class="px-6 py-4 text-sm text-gray-300">
                                    ${[...new Set(session.attack_types)].slice(0, 2).join(', ')}
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <span class="text-lg font-bold ${this.getRiskColor(session.risk_score)}">${session.risk_score}</span>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    ${this.getThreatBadge(session.threat_level)}
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                                    ${new Date(session.processed_at).toLocaleString('zh-TW', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        },

        // 創建 Top IPs 表格
        createTopIPsTable(ips) {
            const sortedIPs = Object.entries(ips).sort((a, b) => b[1] - a[1]).slice(0, 10);
            if (sortedIPs.length === 0) {
                return '<p class="text-white text-center py-4 font-medium">暫無數據</p>';
            }

            return `
                <table class="min-w-full">
                    <thead>
                        <tr class="border-b border-gray-700">
                            <th class="px-4 py-2 text-left text-gray-300">#</th>
                            <th class="px-4 py-2 text-left text-gray-300">IP 位址</th>
                            <th class="px-4 py-2 text-right text-gray-300">攻擊次數</th>
                            <th class="px-4 py-2 text-right text-gray-300">佔比</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${sortedIPs.map(([ip, count], index) => {
                            const total = sortedIPs.reduce((sum, [, c]) => sum + c, 0);
                            const percentage = ((count / total) * 100).toFixed(1);
                            return `
                                <tr class="border-b border-gray-700 hover:bg-gray-700">
                                    <td class="px-4 py-2 text-gray-300">${index + 1}</td>
                                    <td class="px-4 py-2 font-mono text-white">${ip}</td>
                                    <td class="px-4 py-2 text-right font-semibold text-white">${count}</td>
                                    <td class="px-4 py-2 text-right text-gray-400">${percentage}%</td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            `;
        },

        // 創建 IP 列表
        createIPList(ips) {
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

        // 創建 UA 列表
        createUAList(uas) {
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

        // 創建特徵列表
        createSignatureList(signatures) {
            if (signatures.length === 0) {
                return '<p class="text-white font-medium">暫無數據</p>';
            }
            return signatures.map(sig => `
                <span class="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">
                    ${sig}
                </span>
            `).join('');
        },

        // 獲取威脅等級徽章
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

        // 獲取風險分數顏色
        getRiskColor(score) {
            if (score >= 90) return 'text-red-600';
            if (score >= 70) return 'text-orange-600';
            if (score >= 40) return 'text-yellow-600';
            if (score >= 20) return 'text-green-600';
            return 'text-gray-600';
        },

        // 顯示會話詳情
        async showSessionDetail(uuid) {
            try {
                // 打開彈窗
                this.sessionDetailModal.isOpen = true;
                this.sessionDetailModal.loading = true;
                this.sessionDetailModal.data = { sess_uuid: uuid };

                // 顯示加載狀態
                const container = document.getElementById('session-detail-content');
                container.innerHTML = `
                    <div class="space-y-6">
                        ${this.createLoadingSkeleton('card')}
                        ${this.createLoadingSkeleton('card')}
                        ${this.createLoadingSkeleton('card')}
                    </div>
                `;

                // 獲取詳細資料
                const sessionDetail = await API.getSession(uuid);
                this.sessionDetailModal.data = sessionDetail;
                this.sessionDetailModal.loading = false;

                // 渲染詳情內容
                this.renderSessionDetail(sessionDetail);
            } catch (error) {
                console.error('Failed to load session detail:', error);
                this.sessionDetailModal.isOpen = false;
                this.sessionDetailModal.loading = false;
                this.showError(`無法載入會話詳情: ${error.message}`);
            }
        },

        // 渲染會話詳情
        renderSessionDetail(session) {
            const container = document.getElementById('session-detail-content');

            container.innerHTML = `
                <!-- 基本資訊 -->
                <div class="mb-6">
                    <h3 class="text-lg font-semibold mb-3 flex items-center">
                        <span class="w-2 h-2 bg-blue-600 rounded-full mr-2"></span>
                        基本資訊
                    </h3>
                    <div class="bg-gray-50 rounded-lg p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                        ${this.createInfoRow('會話 UUID', session.sess_uuid)}
                        ${this.createInfoRow('來源 IP', session.peer_ip)}
                        ${this.createInfoRow('來源端口', session.peer_port)}
                        ${this.createInfoRow('User Agent', session.user_agent, true)}
                        ${this.createInfoRow('開始時間', new Date(session.start_time).toLocaleString('zh-TW'))}
                        ${this.createInfoRow('結束時間', session.end_time ? new Date(session.end_time).toLocaleString('zh-TW') : '未結束')}
                        ${this.createInfoRow('處理時間', new Date(session.processed_at).toLocaleString('zh-TW'))}
                        ${this.createInfoRow('總請求數', session.total_requests)}
                    </div>
                </div>

                <!-- 威脅評估 -->
                <div class="mb-6">
                    <h3 class="text-lg font-semibold mb-3 flex items-center">
                        <span class="w-2 h-2 bg-red-600 rounded-full mr-2"></span>
                        威脅評估
                    </h3>
                    <div class="bg-red-50 rounded-lg p-4">
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                            <div class="text-center">
                                <div class="text-3xl font-bold ${this.getRiskColor(session.risk_score)}">${session.risk_score}</div>
                                <div class="text-sm text-gray-900 mt-1">風險分數</div>
                            </div>
                            <div class="text-center">
                                ${this.getThreatBadge(session.threat_level)}
                                <div class="text-sm text-gray-900 mt-1">威脅等級</div>
                            </div>
                            <div class="text-center">
                                ${this.getThreatBadge(session.alert_level)}
                                <div class="text-sm text-gray-900 mt-1">告警等級</div>
                            </div>
                            <div class="text-center">
                                <div class="text-lg font-semibold text-gray-900">${session.priority || 'N/A'}</div>
                                <div class="text-sm text-gray-900 mt-1">優先級</div>
                            </div>
                        </div>
                        ${session.has_malicious_activity ? '<div class="bg-red-100 border border-red-300 text-red-800 px-4 py-2 rounded-lg text-sm">偵測到惡意活動</div>' : ''}
                    </div>
                </div>

                <!-- 攻擊資訊 -->
                <div class="mb-6">
                    <h3 class="text-lg font-semibold mb-3 flex items-center">
                        <span class="w-2 h-2 bg-orange-600 rounded-full mr-2"></span>
                        攻擊資訊
                    </h3>
                    <div class="bg-orange-50 rounded-lg p-4">
                        <div class="mb-3">
                            <div class="text-sm text-gray-600 mb-2">攻擊類型</div>
                            <div class="flex flex-wrap gap-2">
                                ${[...new Set(session.attack_types)].map(type => `
                                    <span class="px-3 py-1 bg-orange-200 text-orange-800 rounded-full text-sm font-medium">
                                        ${type}
                                    </span>
                                `).join('')}
                            </div>
                        </div>
                        ${session.tool_identified ? `
                            <div class="mt-3 p-3 bg-yellow-100 border border-yellow-300 rounded-lg">
                                <div class="text-sm font-medium text-yellow-800">🔧 識別的工具: ${session.tool_identified}</div>
                            </div>
                        ` : ''}
                        ${session.is_scanner ? `
                            <div class="mt-3 p-3 bg-purple-100 border border-purple-300 rounded-lg">
                                <div class="text-sm font-medium text-purple-800">🤖 偵測為自動化掃描器</div>
                            </div>
                        ` : ''}
                    </div>
                </div>

                <!-- 地理位置 -->
                ${session.location && session.location.country ? `
                <div class="mb-6">
                    <h3 class="text-lg font-semibold mb-3 flex items-center">
                        <span class="w-2 h-2 bg-green-600 rounded-full mr-2"></span>
                        地理位置
                    </h3>
                    <div class="bg-green-50 rounded-lg p-4 grid grid-cols-2 md:grid-cols-4 gap-4">
                        ${this.createInfoRow('國家', `${session.location.country_code} ${session.location.country}`)}
                        ${this.createInfoRow('城市', session.location.city || '-')}
                        ${session.location.latitude ? this.createInfoRow('座標', `${session.location.latitude}, ${session.location.longitude}`) : ''}
                    </div>
                </div>
                ` : ''}

                <!-- IP 信譽資訊 -->
                ${session.ip_reputation ? this.renderIPReputation(session.ip_reputation, session.peer_ip) : ''}

                <!-- 應對建議 -->
                ${session.recommendations && session.recommendations.length > 0 ? `
                <div class="mb-6">
                    <h3 class="text-lg font-semibold mb-3 flex items-center">
                        <span class="w-2 h-2 bg-purple-600 rounded-full mr-2"></span>
                        應對建議
                    </h3>
                    <div class="bg-purple-50 rounded-lg p-4">
                        <ul class="space-y-2">
                            ${session.recommendations.map(rec => `
                                <li class="flex items-start">
                                    <span class="text-purple-600 mr-2">▸</span>
                                    <span class="text-gray-700">${rec}</span>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                </div>
                ` : ''}

                <!-- 請求詳情 -->
                ${session.paths && session.paths.length > 0 ? `
                <div class="mb-6">
                    <h3 class="text-lg font-semibold mb-3 flex items-center">
                        <span class="w-2 h-2 bg-indigo-600 rounded-full mr-2"></span>
                        請求詳情 (${session.paths.length} 個請求)
                    </h3>
                    <div class="space-y-3">
                        ${session.paths.slice(0, 10).map(req => `
                            <details class="bg-indigo-50 rounded-lg border border-indigo-200">
                                <summary class="px-4 py-3 cursor-pointer hover:bg-indigo-100 transition font-medium flex items-center justify-between">
                                    <span>
                                        <span class="text-indigo-600">${req.method}</span>
                                        <span class="text-gray-700 ml-2">${req.path}</span>
                                    </span>
                                    <span class="text-sm text-gray-500">${req.attack_type || 'normal'}</span>
                                </summary>
                                <div class="px-4 py-3 border-t border-indigo-200 space-y-2">
                                    ${this.createInfoRow('時間戳', new Date(req.timestamp).toLocaleString('zh-TW'))}
                                    ${this.createInfoRow('狀態碼', req.response_status)}
                                    ${this.createInfoRow('攻擊類型', req.attack_type || '-')}
                                    ${req.query_params && Object.keys(req.query_params).length > 0 ? `
                                        <div class="mt-2">
                                            <div class="text-sm font-medium text-gray-700 mb-1">查詢參數:</div>
                                            <pre class="bg-gray-800 text-green-400 p-3 rounded text-xs overflow-x-auto">${JSON.stringify(req.query_params, null, 2)}</pre>
                                        </div>
                                    ` : ''}
                                    ${req.post_data ? `
                                        <div class="mt-2">
                                            <div class="text-sm font-medium text-gray-700 mb-1">POST 數據:</div>
                                            <pre class="bg-gray-800 text-green-400 p-3 rounded text-xs overflow-x-auto">${JSON.stringify(req.post_data, null, 2)}</pre>
                                        </div>
                                    ` : ''}
                                    ${req.headers && Object.keys(req.headers).length > 0 ? `
                                        <div class="mt-2">
                                            <div class="text-sm font-medium text-gray-700 mb-1">Headers:</div>
                                            <pre class="bg-gray-800 text-gray-300 p-3 rounded text-xs overflow-x-auto">${JSON.stringify(req.headers, null, 2)}</pre>
                                        </div>
                                    ` : ''}
                                </div>
                            </details>
                        `).join('')}
                        ${session.paths.length > 10 ? `
                            <div class="text-center py-2 text-sm text-gray-500">
                                顯示前 10 個請求，共 ${session.paths.length} 個
                            </div>
                        ` : ''}
                    </div>
                </div>
                ` : ''}

                <!-- 完整 JSON 數據 -->
                <div class="mb-6">
                    <h3 class="text-lg font-semibold mb-3 flex items-center">
                        <span class="w-2 h-2 bg-gray-600 rounded-full mr-2"></span>
                        完整數據 (JSON)
                    </h3>
                    <div class="relative">
                        <button onclick="app().copyToClipboard(${JSON.stringify(session).replace(/"/g, '&quot;')})"
                                class="absolute top-3 right-3 px-3 py-1 bg-gray-700 text-white text-xs rounded hover:bg-gray-600 transition">
                            複製
                        </button>
                        <pre class="bg-gray-900 text-green-400 p-4 rounded-lg text-xs overflow-x-auto max-h-96">${JSON.stringify(session, null, 2)}</pre>
                    </div>
                </div>
            `;
        },

        // 創建資訊行
        createInfoRow(label, value, fullWidth = false) {
            return `
                <div class="${fullWidth ? 'md:col-span-2' : ''}">
                    <div class="text-sm text-gray-600">${label}</div>
                    <div class="text-gray-900 font-medium mt-1 ${fullWidth ? 'truncate' : ''}">${value || '-'}</div>
                </div>
            `;
        },

        // 渲染 IP 信譽資訊
        renderIPReputation(reputation, ip) {
            if (!reputation) return '';

            // 計算信譽分數的顏色和等級
            const getReputationColor = (score) => {
                if (score >= 0.8) return { color: 'green', text: '良好', bg: 'bg-green-50', border: 'border-green-200' };
                if (score >= 0.5) return { color: 'blue', text: '中立', bg: 'bg-blue-50', border: 'border-blue-200' };
                if (score >= 0.3) return { color: 'yellow', text: '可疑', bg: 'bg-yellow-50', border: 'border-yellow-200' };
                return { color: 'red', text: '惡意', bg: 'bg-red-50', border: 'border-red-200' };
            };

            const repColor = getReputationColor(reputation.reputation_score);
            const scorePercentage = (reputation.reputation_score * 100).toFixed(0);

            return `
                <div class="mb-6">
                    <h3 class="text-lg font-semibold mb-3 flex items-center">
                        <span class="w-2 h-2 bg-cyan-600 rounded-full mr-2"></span>
                        IP 信譽分析
                    </h3>
                    <div class="${repColor.bg} ${repColor.border} border rounded-lg p-4">
                        <!-- 信譽摘要 -->
                        <div class="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
                            <div class="text-center">
                                <div class="text-3xl font-bold text-${repColor.color}-600">${scorePercentage}</div>
                                <div class="text-sm text-gray-600 mt-1">信譽分數</div>
                                <div class="text-xs text-${repColor.color}-600 font-medium mt-1">${repColor.text}</div>
                            </div>
                            <div class="text-center">
                                <div class="text-lg font-semibold ${reputation.is_private ? 'text-blue-600' : 'text-gray-400'}">
                                    ${reputation.is_private ? '是' : '否'}
                                </div>
                                <div class="text-sm text-gray-600 mt-1">私有 IP</div>
                            </div>
                            <div class="text-center">
                                <div class="text-lg font-semibold ${reputation.is_tor ? 'text-orange-600' : 'text-gray-400'}">
                                    ${reputation.is_tor ? '是' : '否'}
                                </div>
                                <div class="text-sm text-gray-600 mt-1">Tor 節點</div>
                            </div>
                            <div class="text-center">
                                <div class="text-lg font-semibold ${reputation.is_vpn ? 'text-purple-600' : 'text-gray-400'}">
                                    ${reputation.is_vpn ? '是' : '否'}
                                </div>
                                <div class="text-sm text-gray-600 mt-1">VPN</div>
                            </div>
                            <div class="text-center">
                                <div class="text-lg font-semibold ${reputation.is_cloud ? 'text-cyan-600' : 'text-gray-400'}">
                                    ${reputation.is_cloud ? '是' : '否'}
                                </div>
                                <div class="text-sm text-gray-600 mt-1">雲端服務</div>
                            </div>
                        </div>

                        <!-- 備註 -->
                        ${reputation.notes && reputation.notes.length > 0 ? `
                            <div class="mb-4 p-3 bg-white rounded border border-${repColor.color}-200">
                                <div class="text-sm font-medium text-gray-700 mb-2">分析備註:</div>
                                <ul class="space-y-1">
                                    ${reputation.notes.map(note => `
                                        <li class="flex items-start text-sm">
                                            <span class="text-${repColor.color}-600 mr-2">•</span>
                                            <span class="text-gray-700">${note}</span>
                                        </li>
                                    `).join('')}
                                </ul>
                            </div>
                        ` : ''}

                        <!-- 外部資料來源 -->
                        ${reputation.external_sources && Object.keys(reputation.external_sources).length > 0 ? `
                            <div class="space-y-3">
                                <div class="text-sm font-medium text-gray-700">外部威脅情報來源:</div>

                                <!-- Shodan 資訊 -->
                                ${reputation.external_sources.shodan ? `
                                    <details class="bg-white rounded-lg border border-cyan-200">
                                        <summary class="px-4 py-3 cursor-pointer hover:bg-cyan-50 transition font-medium flex items-center justify-between">
                                            <span class="flex items-center">
                                                <span class="text-cyan-600 mr-2">🔍</span>
                                                <span>Shodan - 網路設備搜尋引擎</span>
                                            </span>
                                            <span class="text-xs text-gray-500">展開查看</span>
                                        </summary>
                                        <div class="px-4 py-3 border-t border-cyan-200 space-y-2">
                                            ${this.createInfoRow('組織', reputation.external_sources.shodan.org || '-')}
                                            ${this.createInfoRow('ISP', reputation.external_sources.shodan.isp || '-')}
                                            ${this.createInfoRow('國家', reputation.external_sources.shodan.country_name || '-')}
                                            ${reputation.external_sources.shodan.ports && reputation.external_sources.shodan.ports.length > 0 ? `
                                                <div>
                                                    <div class="text-sm text-gray-600 mb-2">開放端口 (${reputation.external_sources.shodan.ports.length}):</div>
                                                    <div class="flex flex-wrap gap-1">
                                                        ${reputation.external_sources.shodan.ports.map(port => `
                                                            <span class="px-2 py-1 bg-cyan-100 text-cyan-700 rounded text-xs font-mono">${port}</span>
                                                        `).join('')}
                                                    </div>
                                                </div>
                                            ` : ''}
                                            ${reputation.external_sources.shodan.tags && reputation.external_sources.shodan.tags.length > 0 ? `
                                                <div>
                                                    <div class="text-sm text-gray-600 mb-2">標籤:</div>
                                                    <div class="flex flex-wrap gap-1">
                                                        ${reputation.external_sources.shodan.tags.map(tag => `
                                                            <span class="px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-xs">${tag}</span>
                                                        `).join('')}
                                                    </div>
                                                </div>
                                            ` : ''}
                                        </div>
                                    </details>
                                ` : ''}

                                <!-- AbuseIPDB 資訊 -->
                                ${reputation.external_sources.abuseipdb ? `
                                    <details class="bg-white rounded-lg border border-red-200">
                                        <summary class="px-4 py-3 cursor-pointer hover:bg-red-50 transition font-medium flex items-center justify-between">
                                            <span class="flex items-center">
                                                <span class="text-red-600 mr-2">🚨</span>
                                                <span>AbuseIPDB - 惡意 IP 資料庫</span>
                                            </span>
                                            <span class="text-xs text-red-600 font-semibold">
                                                ${reputation.external_sources.abuseipdb.abuseConfidenceScore || 0}% 惡意信心度
                                            </span>
                                        </summary>
                                        <div class="px-4 py-3 border-t border-red-200 space-y-2">
                                            ${this.createInfoRow('惡意信心度', `${reputation.external_sources.abuseipdb.abuseConfidenceScore || 0}%`)}
                                            ${this.createInfoRow('報告次數', reputation.external_sources.abuseipdb.totalReports || 0)}
                                            ${this.createInfoRow('最後報告', reputation.external_sources.abuseipdb.lastReportedAt ? new Date(reputation.external_sources.abuseipdb.lastReportedAt).toLocaleString('zh-TW') : '-')}
                                            ${this.createInfoRow('使用類型', reputation.external_sources.abuseipdb.usageType || '-')}
                                            ${reputation.external_sources.abuseipdb.isTor ? '<div class="p-2 bg-orange-100 text-orange-700 rounded text-sm">Tor 出口節點</div>' : ''}
                                        </div>
                                    </details>
                                ` : ''}

                                <!-- VirusTotal 資訊 -->
                                ${reputation.external_sources.virustotal ? `
                                    <details class="bg-white rounded-lg border border-purple-200">
                                        <summary class="px-4 py-3 cursor-pointer hover:bg-purple-50 transition font-medium flex items-center justify-between">
                                            <span class="flex items-center">
                                                <span class="text-purple-600 mr-2">🛡️</span>
                                                <span>VirusTotal - 多引擎威脅分析</span>
                                            </span>
                                            <span class="text-xs ${reputation.external_sources.virustotal.last_analysis_stats?.malicious > 0 ? 'text-red-600 font-semibold' : 'text-green-600'}">
                                                ${reputation.external_sources.virustotal.last_analysis_stats?.malicious || 0} 引擎標記為惡意
                                            </span>
                                        </summary>
                                        <div class="px-4 py-3 border-t border-purple-200">
                                            ${reputation.external_sources.virustotal.last_analysis_stats ? `
                                                <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                                                    <div class="text-center p-2 bg-red-50 rounded">
                                                        <div class="text-2xl font-bold text-red-600">${reputation.external_sources.virustotal.last_analysis_stats.malicious || 0}</div>
                                                        <div class="text-xs text-gray-600">惡意</div>
                                                    </div>
                                                    <div class="text-center p-2 bg-yellow-50 rounded">
                                                        <div class="text-2xl font-bold text-yellow-600">${reputation.external_sources.virustotal.last_analysis_stats.suspicious || 0}</div>
                                                        <div class="text-xs text-gray-600">可疑</div>
                                                    </div>
                                                    <div class="text-center p-2 bg-green-50 rounded">
                                                        <div class="text-2xl font-bold text-green-600">${reputation.external_sources.virustotal.last_analysis_stats.harmless || 0}</div>
                                                        <div class="text-xs text-gray-600">安全</div>
                                                    </div>
                                                    <div class="text-center p-2 bg-gray-50 rounded">
                                                        <div class="text-2xl font-bold text-gray-600">${reputation.external_sources.virustotal.last_analysis_stats.undetected || 0}</div>
                                                        <div class="text-xs text-gray-600">未檢測</div>
                                                    </div>
                                                </div>
                                            ` : ''}
                                        </div>
                                    </details>
                                ` : ''}

                                <!-- AlienVault OTX 資訊 -->
                                ${reputation.external_sources.alienvault_otx ? `
                                    <details class="bg-white rounded-lg border border-indigo-200">
                                        <summary class="px-4 py-3 cursor-pointer hover:bg-indigo-50 transition font-medium flex items-center justify-between">
                                            <span class="flex items-center">
                                                <span class="text-indigo-600 mr-2">🌐</span>
                                                <span>AlienVault OTX - 開放威脅情報</span>
                                            </span>
                                            <span class="text-xs ${reputation.external_sources.alienvault_otx.pulse_count > 0 ? 'text-orange-600 font-semibold' : 'text-gray-500'}">
                                                ${reputation.external_sources.alienvault_otx.pulse_count || 0} 個威脅情報
                                            </span>
                                        </summary>
                                        <div class="px-4 py-3 border-t border-indigo-200">
                                            ${reputation.external_sources.alienvault_otx.pulse_count > 0 ? `
                                                <div class="mb-3">
                                                    <div class="text-sm font-medium text-gray-700 mb-2">發現 ${reputation.external_sources.alienvault_otx.pulse_count} 個相關威脅情報</div>
                                                    ${reputation.external_sources.alienvault_otx.pulses && reputation.external_sources.alienvault_otx.pulses.length > 0 ? `
                                                        <div class="space-y-2">
                                                            ${reputation.external_sources.alienvault_otx.pulses.slice(0, 5).map(pulse => `
                                                                <div class="p-2 bg-orange-50 rounded border border-orange-200">
                                                                    <div class="text-sm font-medium text-orange-800">${pulse.name || 'Unknown'}</div>
                                                                    ${pulse.description ? `<div class="text-xs text-gray-600 mt-1">${pulse.description.substring(0, 100)}${pulse.description.length > 100 ? '...' : ''}</div>` : ''}
                                                                </div>
                                                            `).join('')}
                                                            ${reputation.external_sources.alienvault_otx.pulses.length > 5 ? `
                                                                <div class="text-xs text-gray-500 text-center py-1">還有 ${reputation.external_sources.alienvault_otx.pulses.length - 5} 個威脅情報...</div>
                                                            ` : ''}
                                                        </div>
                                                    ` : ''}
                                                </div>
                                            ` : `
                                                <div class="text-sm text-green-600">此 IP 未發現威脅情報記錄</div>
                                            `}
                                        </div>
                                    </details>
                                ` : ''}
                            </div>
                        ` : `
                            <div class="text-sm text-gray-500 italic">未查詢外部威脅情報服務</div>
                        `}
                    </div>
                </div>
            `;
        },

        // 複製會話詳情
        copySessionDetail() {
            if (this.sessionDetailModal.data) {
                this.copyToClipboard(JSON.stringify(this.sessionDetailModal.data, null, 2));
            }
        },

        // 應用會話過濾器
        applySessionFilters() {
            const threatLevel = document.getElementById('threat-level-filter').value;
            const attackType = document.getElementById('attack-type-filter').value;
            const minRisk = document.getElementById('min-risk-filter').value;

            // 重置分頁
            this.pagination.sessions.offset = 0;

            const params = {};
            if (threatLevel) params.threat_level = threatLevel;
            if (attackType) params.attack_type = attackType;
            if (minRisk) params.min_risk = minRisk;

            this.loadSessions(params);
        },

        // 會話列表 - 下一頁
        nextPageSessions() {
            this.pagination.sessions.offset += this.pagination.sessions.limit;
            this.loadSessions();
        },

        // 會話列表 - 上一頁
        prevPageSessions() {
            this.pagination.sessions.offset = Math.max(0, this.pagination.sessions.offset - this.pagination.sessions.limit);
            this.loadSessions();
        },

        // 切換統計日期範圍
        changeStatsDays(days) {
            this.statsDays = days;
            this.loadStatistics(days);
        },

        // 告警列表 - 下一頁
        nextPageAlerts() {
            this.pagination.alerts.offset += this.pagination.alerts.limit;
            this.loadAlerts();
        },

        // 告警列表 - 上一頁
        prevPageAlerts() {
            this.pagination.alerts.offset = Math.max(0, this.pagination.alerts.offset - this.pagination.alerts.limit);
            this.loadAlerts();
        },

        // 複製到剪貼板
        copyToClipboard(data) {
            const text = Array.isArray(data) ? data.join('\n') : JSON.stringify(data, null, 2);
            navigator.clipboard.writeText(text).then(() => {
                this.showSuccess('已成功複製到剪貼板');
            }).catch(err => {
                console.error('Copy failed:', err);
                this.showError('複製失敗，請重試');
            });
        },

        // 圖表渲染方法（調用 charts.js）
        renderAttackTypeChart(data) {
            window.Charts.renderPieChart('attackTypeChart', data, '攻擊類型');
        },

        renderTopIPsChart(data) {
            window.Charts.renderBarChart('topIPsChart', data, 'Top IPs');
        },

        renderThreatLevelChart(data) {
            window.Charts.renderDoughnutChart('threatLevelChart', data, '威脅等級');
        },

        renderAttackDistChart(data) {
            window.Charts.renderHorizontalBarChart('attackDistChart', data, '攻擊分佈');
        }
    };
}
