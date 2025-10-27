# 🎯 Query API 資料格式完整說明

本文檔詳細說明 Query API 返回的所有資料格式和欄位定義。

---

## 📊 會話資料格式 (Session)

### 完整會話物件結構

```json
{
  // ===== 基本識別資訊 =====
  "sess_uuid": "test-sqli-attack-001",           // 會話唯一ID
  "peer_ip": "192.168.1.100",                    // 攻擊來源IP
  "peer_port": 54321,                            // 攻擊來源端口
  "user_agent": "sqlmap/1.7.2",                  // User Agent字串
  "snare_uuid": "snare-001",                     // 蜜罐UUID
  "processed_at": "2025-10-26T14:00:58.374263",  // 處理時間 (ISO 8601)

  // ===== 攻擊資訊 =====
  "attack_types": ["sqli", "sqli", "sqli"],      // 攻擊類型序列
  "attack_count": {                              // 攻擊類型計數
    "sqli": 3
  },
  "total_requests": 2,                           // 總請求數
  "unique_attack_types": 1,                      // 唯一攻擊類型數
  "has_malicious_activity": true,                // 是否有惡意活動

  // ===== 請求詳情 =====
  "paths": [
    {
      "path": "/login?id=1 UNION SELECT * FROM users--",  // 請求路徑
      "method": "GET",                                     // HTTP方法
      "timestamp": null,                                   // 請求時間
      "response_status": 200,                             // HTTP狀態碼
      "attack_type": "sqli",                              // 此請求的攻擊類型
      "headers": {},                                       // HTTP headers
      "cookies": {},                                       // Cookies
      "query_params": {},                                  // 查詢參數
      "post_data": ""                                      // POST資料
    }
  ],

  // ===== 地理位置 =====
  "location": {
    "country": "Taiwan",               // 國家
    "country_code": "TW",             // 國家代碼
    "city": "Taipei",                 // 城市
    "zip_code": "",                   // 郵遞區號
    "latitude": 25.0330,              // 緯度
    "longitude": 121.5654             // 經度
  },

  // ===== 威脅情報 =====
  "threat_intelligence": {
    "severity": "high",                      // 嚴重性 (critical/high/medium/low/info)
    "confidence": 0.8,                       // 可信度 (0.0-1.0)
    "attack_categories": [                   // 攻擊分類
      "Web Application Attack",
      "Remote Code Execution"
    ],
    "is_automated": true,                    // 是否自動化攻擊
    "is_targeted": false,                    // 是否針對性攻擊
    "threat_actor_type": "unknown"           // 威脅行為者類型
  },

  // ===== 攻擊模式分析 =====
  "attack_patterns": {
    "attack_sequence": ["sqli", "sqli", "sqli"],  // 攻擊序列
    "repeated_attacks": {                          // 重複攻擊統計
      "sqli": 3
    },
    "escalation_detected": false,                  // 是否檢測到攻擊升級
    "pattern_signature": "sqli"                    // 攻擊模式簽名
  },

  // ===== User Agent 分析 =====
  "user_agent_info": {
    "is_bot": false,                    // 是否為Bot
    "is_scanner": true,                 // 是否為掃描工具
    "is_browser": false,                // 是否為瀏覽器
    "tool_identified": "sqlmap",        // 識別的工具名稱
    "suspicious": true                  // 是否可疑
  },

  // ===== 請求模式分析 =====
  "request_patterns": {
    "http_methods": {                  // HTTP方法統計
      "GET": 1,
      "POST": 1
    },
    "status_codes": {                  // 狀態碼統計
      "200": 1,
      "500": 1
    },
    "unique_paths": 2,                 // 唯一路徑數
    "path_diversity": 1.0,             // 路徑多樣性 (0.0-1.0)
    "has_repeated_paths": false        // 是否有重複路徑
  },

  // ===== Payload 分析 =====
  "payload_analysis": {
    "has_sql_keywords": true,          // 是否包含SQL關鍵字
    "has_xss_patterns": false,         // 是否包含XSS模式
    "has_command_injection": false,    // 是否包含命令注入
    "has_path_traversal": false,       // 是否包含路徑遍歷
    "has_encoded_content": false,      // 是否包含編碼內容
    "suspicious_patterns": [           // 可疑模式列表
      "sql_keywords"
    ]
  },

  // ===== IP 信譽 =====
  "ip_reputation": {
    "is_private": false,               // 是否私有IP
    "is_tor": false,                   // 是否Tor節點
    "is_vpn": false,                   // 是否VPN
    "is_cloud": false,                 // 是否雲端服務
    "reputation_score": 0.5,           // 信譽分數 (0.0-1.0)
    "notes": []                        // 備註
  },

  // ===== 時間模式 =====
  "temporal_patterns": {
    "duration_seconds": 0.0,           // 會話持續時間（秒）
    "request_rate": 2.5,               // 請求速率（請求/秒）
    "time_of_day": "afternoon",        // 時段 (morning/afternoon/evening/night)
    "is_prolonged": false              // 是否長時間會話
  },

  // ===== 行為標籤 =====
  "behavior_tags": [
    "severity:high",
    "automated_attack",
    "scanner_detected",
    "tool:sqlmap",
    "sql_injection_attempt",
    "malicious_activity"
  ],

  // ===== 攻擊階段 (Cyber Kill Chain) =====
  "attack_phases": [
    "exploitation"                     // reconnaissance/scanning/exploitation/persistence_attempt
  ],

  // ===== 風險評估 =====
  "risk_score": 51,                    // 綜合風險分數 (0-100)
  "risk_breakdown": {                  // 風險分數分解
    "severity_score": 24,              // 嚴重性分數 (0-30)
    "complexity_score": 4,             // 複雜度分數 (0-20)
    "automation_score": 13,            // 自動化分數 (0-15)
    "payload_score": 5,                // Payload危險性 (0-15)
    "targeting_score": 5,              // 目標明確性 (0-10)
    "persistence_score": 0             // 持續性分數 (0-10)
  },
  "threat_level": "HIGH",              // 威脅等級
  "priority": "P2-HIGH",               // 處理優先級
  "confidence_score": 0.83,            // 檢測可信度 (0.0-1.0)
  "exploitation_likelihood": "MEDIUM", // 利用可能性

  // ===== 影響評估 (CIA Triad) =====
  "impact_assessment": {
    "confidentiality": "HIGH",         // 機密性影響
    "integrity": "HIGH",               // 完整性影響
    "availability": "NONE",            // 可用性影響
    "scope": "APPLICATION",            // 影響範圍 (LIMITED/APPLICATION/SYSTEM)
    "financial_risk": "HIGH",          // 財務風險
    "reputation_risk": "HIGH"          // 聲譽風險
  },

  // ===== 應對建議 =====
  "recommendations": [
    "🚨 立即封鎖來源 IP: 192.168.1.100",
    "📊 進行深度取證分析",
    "🔍 檢查相同來源的其他活動",
    "🛡️ 修補 SQL 注入漏洞：使用參數化查詢",
    "🔒 啟用 WAF SQL 注入防護規則",
    "🤖 檢測到自動化掃描工具，建議實施速率限制",
    "🔧 識別到工具: sqlmap，更新 WAF 規則",
    "📝 記錄此事件到 SIEM 系統",
    "👥 通知安全團隊進行審查"
  ],

  // ===== 標記 =====
  "requires_review": true,             // 是否需要人工審查
  "alert_level": "HIGH"                // 警報等級
}
```

---

## 📈 統計資料格式 (Statistics)

```json
{
  "date": "2025-10-26",
  "total_sessions": 150,

  // 威脅等級分布
  "threat_level_distribution": {
    "CRITICAL": 5,
    "HIGH": 20,
    "MEDIUM": 50,
    "LOW": 45,
    "INFO": 30
  },

  // 風險分數分布
  "risk_score_distribution": {
    "critical": 5,    // >= 70
    "high": 20,       // 50-69
    "medium": 50,     // 30-49
    "low": 45,        // 15-29
    "info": 30        // 0-14
  },

  // 攻擊類型分布
  "attack_type_distribution": {
    "sqli": 30,
    "xss": 25,
    "lfi": 15,
    "cmd_exec": 10,
    "rfi": 5,
    "index": 70
  },

  // TOP 10 攻擊來源 IP
  "top_source_ips": {
    "192.168.1.100": 15,
    "10.0.0.50": 12,
    "172.16.0.99": 8
  },

  // TOP 10 User Agents
  "top_user_agents": {
    "sqlmap/1.7.2": 10,
    "curl/7.68.0": 8,
    "Mozilla/5.0": 5
  },

  // 警報等級統計
  "alert_counts": {
    "CRITICAL": 5,
    "HIGH": 20,
    "MEDIUM": 50,
    "LOW": 45,
    "INFO": 30
  },

  // 平均風險分數
  "average_risk_score": 42.5,

  // 需要審查的數量
  "requires_review_count": 25
}
```

---

## 🚨 警報資料格式 (Alert)

```json
{
  "sess_uuid": "test-sqli-attack-001",
  "peer_ip": "192.168.1.100",
  "alert_level": "HIGH",
  "threat_level": "HIGH",
  "risk_score": 51,
  "attack_types": ["sqli"],
  "tool_identified": "sqlmap",
  "processed_at": "2025-10-26T14:00:58.374263",
  "recommendations_count": 9
}
```

---

## 🎯 儀表板資料格式 (Dashboard)

```json
{
  // 今日摘要
  "today_summary": {
    "total_sessions": 150,
    "high_risk_count": 25,
    "critical_alerts": 5,
    "average_risk": 42.5,
    "unique_ips": 45
  },

  // 最近的高風險警報（最多10條）
  "recent_alerts": [
    {
      "sess_uuid": "...",
      "peer_ip": "...",
      "alert_level": "HIGH",
      "risk_score": 51
    }
  ],

  // 24小時趨勢（每小時統計）
  "hourly_trend": [
    {
      "hour": "00:00",
      "session_count": 10,
      "high_risk_count": 2
    }
  ],

  // TOP 威脅
  "top_threats": {
    "top_ips": {
      "192.168.1.100": 15
    },
    "top_attacks": {
      "sqli": 30
    },
    "top_tools": {
      "sqlmap": 10
    }
  }
}
```

---

## 🔒 威脅情報格式 (Threat Intelligence)

```json
{
  "date": "2025-10-26",

  // 惡意IP列表
  "malicious_ips": [
    "192.168.1.100",
    "10.0.0.50"
  ],
  "malicious_ips_count": 2,

  // 攻擊模式簽名
  "attack_signatures": [
    "sqli",
    "cmd_exec-rfi",
    "lfi-xss"
  ],
  "attack_signatures_count": 3,

  // 惡意User Agents
  "malicious_user_agents": [
    "sqlmap/1.7.2",
    "nikto/2.1.6"
  ],

  // Payload樣本（最多20個）
  "sample_payloads": [
    {
      "path": "/login?id=1 UNION SELECT",
      "method": "GET",
      "attack_type": "sqli",
      "patterns": ["sql_keywords"]
    }
  ]
}
```

---

## 📝 列表響應格式 (Paginated Response)

所有列表端點都遵循統一的分頁響應格式：

```json
{
  "items": [...],           // 資料列表（欄位名因端點而異）
  "total": 150,            // 總數量
  "limit": 50,             // 每頁數量
  "offset": 0,             // 偏移量
  "has_more": true         // 是否還有更多資料
}
```

---

## 🏷️ 枚舉值說明

### 威脅等級 (ThreatLevel)

| 值 | 說明 | 風險分數範圍 |
|----|------|-------------|
| `CRITICAL` | 嚴重威脅 | >= 70 |
| `HIGH` | 高風險 | 50-69 |
| `MEDIUM` | 中等風險 | 30-49 |
| `LOW` | 低風險 | 15-29 |
| `INFO` | 資訊性 | 0-14 |

### 警報等級 (AlertLevel)

| 值 | 說明 | 響應時間 |
|----|------|---------|
| `CRITICAL` | 立即響應 | 立即 |
| `HIGH` | 高優先級 | 1小時內 |
| `MEDIUM` | 中優先級 | 4小時內 |
| `LOW` | 低優先級 | 24小時內 |
| `INFO` | 資訊性 | 記錄即可 |

### 優先級 (Priority)

| 值 | 說明 |
|----|------|
| `P1-URGENT` | 緊急處理 |
| `P2-HIGH` | 高優先級 |
| `P3-MEDIUM` | 中優先級 |
| `P4-LOW` | 低優先級 |
| `P5-INFO` | 資訊性 |

### 攻擊類型 (AttackType)

| 值 | 說明 |
|----|------|
| `sqli` | SQL注入 |
| `xss` | 跨站腳本攻擊 |
| `lfi` | 本地檔案包含 |
| `rfi` | 遠端檔案包含 |
| `cmd_exec` | 命令執行 |
| `php_code_injection` | PHP程式碼注入 |
| `php_object_injection` | PHP物件注入 |
| `template_injection` | 模板注入 |
| `xxe_injection` | XXE注入 |
| `crlf` | CRLF注入 |
| `index` | 正常頁面訪問 |

### 攻擊階段 (AttackPhase)

| 值 | 說明 |
|----|------|
| `reconnaissance` | 偵察 |
| `scanning` | 掃描 |
| `exploitation` | 利用 |
| `persistence_attempt` | 持久化嘗試 |

---

## 🔍 前端使用建議

### 1. 會話列表頁面

使用 `GET /api/sessions` 獲取摘要資料，顯示：
- IP、風險分數、威脅等級
- 攻擊類型、工具識別
- 處理時間

### 2. 會話詳情頁面

使用 `GET /api/sessions/{uuid}` 獲取完整資料，顯示：
- 所有請求詳情
- 完整的風險評估
- 應對建議列表

### 3. 儀表板頁面

使用 `GET /api/dashboard` 獲取儀表板資料，顯示：
- 今日統計卡片
- 最近警報列表
- 24小時趨勢圖表
- TOP威脅排行

### 4. 統計報表頁面

使用 `GET /api/statistics` 獲取統計資料，顯示：
- 威脅等級分布餅圖
- 攻擊類型分布柱狀圖
- TOP IP/UA 排行榜
- 時間趨勢線圖

---

## 💡 注意事項

1. **時間格式**：所有時間戳均為 ISO 8601 格式 UTC 時間
2. **分頁**：建議 limit 不超過 500，避免效能問題
3. **過濾**：可組合多個過濾條件
4. **快取**：統計資料可在前端快取 5-10 分鐘
5. **實時性**：資料更新可能有 1-2 秒延遲
