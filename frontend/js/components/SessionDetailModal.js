// Session Detail Modal Component

const SessionDetailModal = {
    /**
     * Show session detail modal
     * @param {string} uuid - Session UUID
     * @returns {Promise<void>}
     */
    async show(uuid) {
        try {
            const store = window.AppStore;
            store.openModal({ sess_uuid: uuid });

            const container = document.getElementById('session-detail-content');
            container.innerHTML = `
                <div class="space-y-6">
                    ${SkeletonLoader.create('card')}
                    ${SkeletonLoader.create('card')}
                    ${SkeletonLoader.create('card')}
                </div>
            `;

            const sessionDetail = await API.getSession(uuid);
            store.setModalData(sessionDetail);
            this.render(sessionDetail);
        } catch (error) {
            console.error('Failed to load session detail:', error);
            window.AppStore.closeModal();
            window.AppStore.showError(`無法載入會話詳情: ${error.message}`);
        }
    },

    /**
     * Render session detail
     * @param {Object} session - Session data
     */
    render(session) {
        const container = document.getElementById('session-detail-content');

        container.innerHTML = `
            ${this.renderBasicInfo(session)}
            ${this.renderThreatAssessment(session)}
            ${this.renderAttackInfo(session)}
            ${this.renderGeolocation(session.location, session.peer_ip)}
            ${session.ip_reputation ? this.renderIPReputation(session.ip_reputation, session.peer_ip) : ''}
            ${this.renderRecommendations(session.recommendations)}
            ${this.renderRequests(session.paths, session.sess_uuid)}
            ${this.renderRawJSON(session)}
        `;
    },

    /**
     * Render basic information section
     */
    renderBasicInfo(session) {
        return `
            <div class="mb-6">
                <h3 class="text-lg font-semibold mb-3 flex items-center">
                    <span class="w-2 h-2 bg-blue-600 rounded-full mr-2"></span>
                    基本資訊
                </h3>
                <div class="bg-gray-50 rounded-lg p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                    ${CardTemplates.infoRow('會話 UUID', session.sess_uuid)}
                    ${CardTemplates.infoRow('來源 IP', session.peer_ip)}
                    ${CardTemplates.infoRow('來源端口', session.peer_port)}
                    ${CardTemplates.infoRow('User Agent', session.user_agent, true)}
                    ${CardTemplates.infoRow('開始時間', Formatters.formatTimestamp(session.start_time))}
                    ${CardTemplates.infoRow('結束時間', session.end_time ? Formatters.formatTimestamp(session.end_time) : '未結束')}
                    ${CardTemplates.infoRow('處理時間', Formatters.formatTimestamp(session.processed_at))}
                    ${CardTemplates.infoRow('總請求數', session.total_requests)}
                </div>
            </div>
        `;
    },

    /**
     * Render threat assessment section
     */
    renderThreatAssessment(session) {
        return `
            <div class="mb-6">
                <h3 class="text-lg font-semibold mb-3 flex items-center">
                    <span class="w-2 h-2 bg-red-600 rounded-full mr-2"></span>
                    威脅評估
                </h3>
                <div class="bg-red-50 rounded-lg p-4">
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                        <div class="text-center">
                            <div class="text-3xl font-bold ${Formatters.getRiskColor(session.risk_score)}">${session.risk_score}</div>
                            <div class="text-sm text-gray-900 mt-1">風險分數</div>
                        </div>
                        <div class="text-center">
                            ${Formatters.getThreatBadge(session.threat_level)}
                            <div class="text-sm text-gray-900 mt-1">威脅等級</div>
                        </div>
                        <div class="text-center">
                            ${Formatters.getThreatBadge(session.alert_level)}
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
        `;
    },

    /**
     * Render attack information section
     */
    renderAttackInfo(session) {
        return `
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
                            <div class="text-sm font-medium text-yellow-800">識別的工具: ${session.tool_identified}</div>
                        </div>
                    ` : ''}
                    ${session.is_scanner ? `
                        <div class="mt-3 p-3 bg-purple-100 border border-purple-300 rounded-lg">
                            <div class="text-sm font-medium text-purple-800">偵測為自動化掃描器</div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    },

    /**
     * Render geolocation section
     */
    renderGeolocation(location, ip) {
        const isPrivateIP = Formatters.isPrivateIP(ip);
        const hasLocation = location && (location.country || location.city);

        return `
            <div class="mb-6">
                <h3 class="text-lg font-semibold mb-3 flex items-center">
                    <span class="w-2 h-2 bg-green-600 rounded-full mr-2"></span>
                    地理位置
                </h3>
                <div class="bg-green-50 rounded-lg p-4 border border-green-200">
                    ${hasLocation ? `
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            ${location.country ? CardTemplates.infoRow('國家', `${location.country_code ? location.country_code + ' ' : ''}${location.country}`) : ''}
                            ${location.city ? CardTemplates.infoRow('城市', location.city) : CardTemplates.infoRow('城市', '-')}
                            ${location.zip_code ? CardTemplates.infoRow('郵遞區號', location.zip_code) : ''}
                            ${location.latitude && location.longitude ? CardTemplates.infoRow('座標', `${location.latitude}, ${location.longitude}`) : ''}
                        </div>
                        ${location.latitude && location.longitude ? `
                            <div class="mt-3 pt-3 border-t border-green-200">
                                <a href="https://www.google.com/maps?q=${location.latitude},${location.longitude}"
                                   target="_blank"
                                   class="inline-flex items-center text-sm text-green-700 hover:text-green-800 font-medium">
                                    在 Google Maps 中查看
                                </a>
                            </div>
                        ` : ''}
                    ` : `
                        <div class="flex items-center justify-center py-4">
                            ${isPrivateIP ? `
                                <div class="text-center">
                                    <div class="inline-flex items-center px-4 py-2 bg-blue-100 text-blue-800 rounded-lg">
                                        <span class="font-medium">私有 IP 地址</span>
                                    </div>
                                    <p class="text-sm text-gray-600 mt-2">此 IP 屬於本地網絡，無法獲取地理位置資訊</p>
                                </div>
                            ` : `
                                <div class="text-center">
                                    <div class="inline-flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg">
                                        <span class="font-medium">地理位置資訊不可用</span>
                                    </div>
                                    <p class="text-sm text-gray-600 mt-2">GeoIP 數據庫未配置或無法查詢此 IP</p>
                                </div>
                            `}
                        </div>
                    `}
                </div>
            </div>
        `;
    },

    /**
     * Render IP reputation section
     */
    renderIPReputation(reputation, ip) {
        if (!reputation) return '';

        const repColor = Formatters.getReputationColor(reputation.reputation_score);
        const scorePercentage = (reputation.reputation_score * 100).toFixed(0);

        return `
            <div class="mb-6">
                <h3 class="text-lg font-semibold mb-3 flex items-center">
                    <span class="w-2 h-2 bg-cyan-600 rounded-full mr-2"></span>
                    IP 信譽分析
                </h3>
                <div class="${repColor.bg} ${repColor.border} border rounded-lg p-4">
                    <!-- Reputation Summary -->
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
                </div>
            </div>
        `;
    },

    /**
     * Render recommendations section
     */
    renderRecommendations(recommendations) {
        if (!recommendations || recommendations.length === 0) return '';

        return `
            <div class="mb-6">
                <h3 class="text-lg font-semibold mb-3 flex items-center">
                    <span class="w-2 h-2 bg-purple-600 rounded-full mr-2"></span>
                    應對建議
                </h3>
                <div class="bg-purple-50 rounded-lg p-4">
                    <ul class="space-y-2">
                        ${recommendations.map(rec => `
                            <li class="flex items-start">
                                <span class="text-purple-600 mr-2">▸</span>
                                <span class="text-gray-700">${rec}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        `;
    },

    /**
     * Render requests section
     */
    renderRequests(paths, sessUuid) {
        if (!paths || paths.length === 0) return '';

        return `
            <div class="mb-6">
                <h3 class="text-lg font-semibold mb-3 flex items-center">
                    <span class="w-2 h-2 bg-indigo-600 rounded-full mr-2"></span>
                    請求詳情 (${paths.length} 個請求)
                </h3>
                <div class="space-y-3">
                    ${paths.slice(0, 10).map(req => `
                        <details class="bg-indigo-50 rounded-lg border border-indigo-200">
                            <summary class="px-4 py-3 cursor-pointer hover:bg-indigo-100 transition font-medium flex items-center justify-between">
                                <span>
                                    <span class="text-indigo-600">${req.method}</span>
                                    <span class="text-gray-700 ml-2">${req.path}</span>
                                </span>
                                <span class="text-sm text-gray-500">${req.attack_type || 'normal'}</span>
                            </summary>
                            <div class="px-4 py-3 border-t border-indigo-200 space-y-2">
                                ${CardTemplates.infoRow('時間戳', Formatters.formatTimestamp(req.timestamp))}
                                ${CardTemplates.infoRow('狀態碼', req.response_status)}
                                ${CardTemplates.infoRow('攻擊類型', req.attack_type || '-')}
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
                            </div>
                        </details>
                    `).join('')}
                    ${paths.length > 10 ? `
                        <div class="text-center py-2 text-sm text-gray-500">
                            顯示前 10 個請求，共 ${paths.length} 個
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    },

    /**
     * Render raw JSON section
     */
    renderRawJSON(session) {
        return `
            <div class="mb-6">
                <h3 class="text-lg font-semibold mb-3 flex items-center">
                    <span class="w-2 h-2 bg-gray-600 rounded-full mr-2"></span>
                    完整數據 (JSON)
                </h3>
                <div class="relative">
                    <button onclick="app().copySessionDetail()"
                            class="absolute top-3 right-3 px-3 py-1 bg-gray-700 text-white text-xs rounded hover:bg-gray-600 transition">
                        複製
                    </button>
                    <pre class="bg-gray-900 text-green-400 p-4 rounded-lg text-xs overflow-x-auto max-h-96">${JSON.stringify(session, null, 2)}</pre>
                </div>
            </div>
        `;
    }
};

window.SessionDetailModal = SessionDetailModal;
