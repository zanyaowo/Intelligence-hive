# Query API - 蜜罐資料查詢服務

提供 REST API 端點讓前端查詢已處理的蜜罐資料。

## 🚀 快速開始

### 使用 Docker

```bash
# 啟動服務
docker-compose up -d query_api

# 查看日誌
docker logs -f query_api
```

### 本地開發

```bash
cd services/query_api

# 安裝依賴
pip install -r requirements.txt

# 啟動服務
python main.py
```

服務將在 `http://localhost:8083` 啟動。

---

## 📡 API 端點

### 1. 獲取會話列表

```http
GET /api/sessions
```

**查詢參數**：
- `date` (optional): 日期 (YYYY-MM-DD)，預設今天
- `threat_level` (optional): 威脅等級過濾 (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- `attack_type` (optional): 攻擊類型過濾 (sqli, xss, cmd_exec, etc.)
- `min_risk` (optional): 最小風險分數 (0-100)
- `limit` (optional): 每頁數量，預設 50
- `offset` (optional): 偏移量，預設 0
- `sort_by` (optional): 排序欄位 (processed_at, risk_score)
- `order` (optional): 排序順序 (asc, desc)

**範例請求**：
```bash
# 獲取今日高風險會話
curl "http://localhost:8083/api/sessions?threat_level=HIGH&limit=20"

# 獲取 SQL 注入攻擊
curl "http://localhost:8083/api/sessions?attack_type=sqli&sort_by=risk_score&order=desc"

# 獲取風險分數 >= 50 的會話
curl "http://localhost:8083/api/sessions?min_risk=50"
```

**響應格式**：
```json
{
  "sessions": [
    {
      "sess_uuid": "test-sqli-attack-001",
      "peer_ip": "192.168.1.100",
      "peer_port": 54321,
      "user_agent": "sqlmap/1.7.2",
      "attack_types": ["sqli", "sqli", "sqli"],
      "risk_score": 51,
      "threat_level": "HIGH",
      "alert_level": "HIGH",
      "processed_at": "2025-10-26T14:00:58.374263",
      "total_requests": 2,
      "has_malicious_activity": true,
      "is_scanner": true,
      "tool_identified": "sqlmap"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0,
  "has_more": true
}
```

---

### 2. 獲取會話詳情

```http
GET /api/sessions/{uuid}
```

**範例請求**：
```bash
curl "http://localhost:8083/api/sessions/test-sqli-attack-001"
```

**響應格式**：
完整的會話資料，包含所有分析結果、風險評估、建議等。

---

### 3. 獲取警報列表

```http
GET /api/alerts
```

**查詢參數**：
- `date` (optional): 日期 (YYYY-MM-DD)
- `alert_level` (optional): 警報等級 (CRITICAL, HIGH)
- `limit` (optional): 每頁數量
- `offset` (optional): 偏移量

**範例請求**：
```bash
# 獲取所有高風險警報
curl "http://localhost:8083/api/alerts"

# 獲取 CRITICAL 等級警報
curl "http://localhost:8083/api/alerts?alert_level=CRITICAL"
```

**響應格式**：
```json
{
  "alerts": [
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
  ],
  "total": 25,
  "limit": 50,
  "offset": 0,
  "has_more": false
}
```

---

### 4. 獲取統計資料

```http
GET /api/statistics
```

**查詢參數**：
- `date` (optional): 日期 (YYYY-MM-DD)
- `days` (optional): 統計天數 (1-30)，預設 1

**範例請求**：
```bash
# 獲取今日統計
curl "http://localhost:8083/api/statistics"

# 獲取最近 7 天統計
curl "http://localhost:8083/api/statistics?days=7"
```

**響應格式**：
```json
{
  "date": "2025-10-26",
  "total_sessions": 150,
  "threat_level_distribution": {
    "CRITICAL": 5,
    "HIGH": 20,
    "MEDIUM": 50,
    "LOW": 45,
    "INFO": 30
  },
  "attack_type_distribution": {
    "sqli": 30,
    "xss": 25,
    "lfi": 15,
    "cmd_exec": 10,
    "index": 70
  },
  "top_source_ips": {
    "192.168.1.100": 15,
    "10.0.0.50": 12
  },
  "average_risk_score": 42.5,
  "requires_review_count": 25
}
```

---

### 5. 獲取儀表板資料

```http
GET /api/dashboard
```

**範例請求**：
```bash
curl "http://localhost:8083/api/dashboard"
```

**響應格式**：
```json
{
  "today_summary": {
    "total_sessions": 150,
    "high_risk_count": 25,
    "critical_alerts": 5,
    "average_risk": 42.5,
    "unique_ips": 45
  },
  "recent_alerts": [...],
  "hourly_trend": [...],
  "top_threats": {
    "top_ips": {...},
    "top_attacks": {...}
  }
}
```

---

### 6. 獲取威脅情報

```http
GET /api/threat-intelligence
```

**查詢參數**：
- `date` (optional): 日期 (YYYY-MM-DD)

**範例請求**：
```bash
curl "http://localhost:8083/api/threat-intelligence"
```

**響應格式**：
```json
{
  "date": "2025-10-26",
  "malicious_ips": ["192.168.1.100", "10.0.0.50"],
  "malicious_ips_count": 2,
  "attack_signatures": ["sqli", "cmd_exec-rfi"],
  "attack_signatures_count": 2,
  "malicious_user_agents": ["sqlmap/1.7.2"],
  "sample_payloads": [...]
}
```

---

### 7. 獲取可用日期列表

```http
GET /api/dates
```

**範例請求**：
```bash
curl "http://localhost:8083/api/dates"
```

**響應格式**：
```json
{
  "dates": ["2025-10-26", "2025-10-25", "2025-10-24"],
  "count": 3
}
```

---

## 📊 資料格式說明

### 會話摘要 (SessionSummary)

| 欄位 | 類型 | 說明 |
|------|------|------|
| `sess_uuid` | string | 會話唯一識別碼 |
| `peer_ip` | string | 攻擊來源 IP |
| `peer_port` | int | 攻擊來源端口 |
| `user_agent` | string | User Agent |
| `attack_types` | array | 攻擊類型列表 |
| `risk_score` | int | 風險分數 (0-100) |
| `threat_level` | string | 威脅等級 |
| `alert_level` | string | 警報等級 |
| `processed_at` | string | 處理時間 (ISO 8601) |
| `total_requests` | int | 總請求數 |
| `has_malicious_activity` | bool | 是否包含惡意活動 |
| `is_scanner` | bool | 是否為掃描工具 |
| `tool_identified` | string | 識別的工具名稱 |

### 會話詳情 (SessionDetailResponse)

包含所有處理階段的完整資料：

- **基本資訊**: UUID, IP, User Agent, 時間戳
- **攻擊資訊**: 攻擊類型、數量、請求詳情
- **威脅情報**: 嚴重性、可信度、攻擊分類
- **攻擊模式**: 攻擊序列、重複攻擊、升級檢測
- **User Agent 分析**: 工具識別、Bot 檢測
- **Payload 分析**: SQL/XSS/CMD 模式檢測
- **風險評估**: 多維度風險分數、威脅等級
- **影響評估**: CIA Triad 評估
- **應對建議**: 自動生成的建議列表

### 威脅等級 (ThreatLevel)

- `CRITICAL` - 嚴重威脅，需立即響應
- `HIGH` - 高風險，1小時內響應
- `MEDIUM` - 中等風險，4小時內響應
- `LOW` - 低風險，24小時內響應
- `INFO` - 資訊性，記錄即可

### 攻擊類型 (AttackType)

- `sqli` - SQL 注入
- `xss` - 跨站腳本攻擊
- `lfi` - 本地檔案包含
- `rfi` - 遠端檔案包含
- `cmd_exec` - 命令執行
- `php_code_injection` - PHP 程式碼注入
- `template_injection` - 模板注入
- `xxe_injection` - XXE 注入
- `crlf` - CRLF 注入
- `index` - 正常頁面訪問

---

## 🔧 配置

### 環境變數

```bash
# 資料目錄（需要與 analytics_worker 共享）
DATA_DIR=/app/data
```

### Docker Volume 共享

Query API 需要訪問 analytics_worker 生成的資料，因此需要共享 volume：

```yaml
volumes:
  - analytics_data:/app/data
```

---

## 🎯 前端整合範例

### JavaScript/TypeScript

```typescript
// 獲取今日高風險會話
async function getHighRiskSessions() {
  const response = await fetch(
    'http://localhost:8083/api/sessions?threat_level=HIGH&limit=20'
  );
  const data = await response.json();
  return data.sessions;
}

// 獲取會話詳情
async function getSessionDetail(uuid: string) {
  const response = await fetch(
    `http://localhost:8083/api/sessions/${uuid}`
  );
  return await response.json();
}

// 獲取儀表板資料
async function getDashboard() {
  const response = await fetch('http://localhost:8083/api/dashboard');
  return await response.json();
}
```

### React 範例

```tsx
import { useEffect, useState } from 'react';

function SessionList() {
  const [sessions, setSessions] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8083/api/sessions?limit=20')
      .then(res => res.json())
      .then(data => setSessions(data.sessions));
  }, []);

  return (
    <div>
      {sessions.map(session => (
        <div key={session.sess_uuid}>
          <h3>{session.peer_ip}</h3>
          <p>Risk: {session.risk_score}/100</p>
          <p>Threat: {session.threat_level}</p>
        </div>
      ))}
    </div>
  );
}
```

---

## 📖 API 文檔

啟動服務後，訪問以下 URL 查看完整的交互式 API 文檔：

- **Swagger UI**: `http://localhost:8083/docs`
- **ReDoc**: `http://localhost:8083/redoc`

---

## 🐛 故障排除

### 1. 無法讀取資料

檢查 volume 是否正確掛載：
```bash
docker exec query_api ls -la /app/data
```

### 2. CORS 錯誤

如果前端遇到 CORS 問題，請在 `main.py` 中修改 `allow_origins`：
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://your-frontend-domain.com"],
    ...
)
```

### 3. 性能優化

對於大量資料，考慮：
- 減少 `limit` 參數
- 使用更具體的過濾條件
- 實作資料庫索引（未來）

---

## 🚀 未來擴展

- [ ] WebSocket 支援（實時資料推送）
- [ ] 資料庫整合（提升查詢效能）
- [ ] 快取機制（Redis）
- [ ] 進階過濾（多條件組合）
- [ ] 匯出功能（CSV, JSON）
- [ ] 使用者認證（JWT）
