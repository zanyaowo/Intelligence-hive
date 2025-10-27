# Analytics Worker

> 🔬 蜜罐數據分析處理引擎 - 從 Redis Stream 消費原始會話數據，進行正規化、豐富化、風險評估，並持久化存儲。

## 📋 目錄

- [概述](#概述)
- [功能特色](#功能特色)
- [架構設計](#架構設計)
- [數據處理流程](#數據處理流程)
- [模組說明](#模組說明)
- [配置說明](#配置說明)
- [使用方式](#使用方式)
- [數據格式](#數據格式)
- [監控與日誌](#監控與日誌)
- [故障處理](#故障處理)

---

## 概述

Analytics Worker 是蜜罐數據平台的核心分析引擎，負責：

1. **消費數據**：從 Redis Stream 批次讀取原始蜜罐會話數據
2. **處理數據**：執行 4 階段處理流程（正規化 → 豐富化 → 評估 → 存儲）
3. **風險評估**：計算風險分數、威脅等級、優先級
4. **持久化**：將處理後的數據保存為結構化檔案

### 關鍵特性

- ✅ **可靠性**：基於 Redis Stream Consumer Group 保證消息不丟失
- ✅ **可擴展**：支援多 Worker 並行處理，自動負載均衡
- ✅ **容錯性**：失敗消息自動重試，錯誤隔離
- ✅ **可觀測**：詳細的日誌記錄，實時處理進度
- ✅ **高效能**：批次處理，減少 I/O 開銷

---

## 功能特色

### 1. 🔄 資料正規化 (Normalizer)

**目的**：清理和標準化原始數據

- 驗證必要欄位完整性
- 標準化時間戳格式（ISO 8601）
- 清理 IP 位址和端口資訊
- 標準化攻擊類型名稱
- 補充缺失欄位預設值
- 清理特殊字元和空白

### 2. 🌟 資料豐富化 (Enricher)

**目的**：添加情報和上下文資訊

- **威脅情報標籤**：已知惡意 IP、殭屍網路、掃描器識別
- **攻擊模式分析**：識別攻擊技術（SQLi、XSS、RCE...）
- **User Agent 分析**：識別自動化工具、爬蟲、殭屍網路
- **請求模式分析**：偵測異常請求頻率和序列
- **Payload 分析**：提取並分類惡意 Payload

**豐富化資訊**：
```json
{
  "threat_intelligence": {
    "is_known_malicious": true,
    "threat_categories": ["botnet", "scanner"],
    "reputation_score": 85
  },
  "attack_patterns": {
    "techniques": ["sql_injection", "path_traversal"],
    "sophistication": "medium"
  },
  "user_agent_info": {
    "is_bot": true,
    "tool_name": "sqlmap",
    "os": "linux"
  }
}
```

### 3. ⚖️ 風險評估 (Evaluator)

**目的**：計算風險分數和威脅等級

- **風險分數計算**（0-100）：
  - 攻擊類型嚴重性：30%
  - 請求數量與頻率：20%
  - Payload 危險度：25%
  - IP 信譽分數：15%
  - 攻擊複雜度：10%

- **威脅等級**：
  - `CRITICAL`：90-100 分，需立即處置
  - `HIGH`：70-89 分，優先處理
  - `MEDIUM`：40-69 分，正常監控
  - `LOW`：20-39 分，記錄追蹤
  - `INFO`：0-19 分，參考資訊

- **影響評估**：
  - 資料外洩風險
  - 系統入侵可能性
  - 服務中斷威脅
  - 資源消耗評估

- **建議動作**：
  - IP 封鎖建議
  - 規則更新建議
  - 告警通知建議
  - 調查優先級

### 4. 💾 資料持久化 (Loader)

**目的**：結構化存儲處理後的數據

**存儲格式**：JSONL (預設)
```
/app/data/
├── sessions/
│   ├── 2025-10-27/
│   │   ├── sessions.jsonl          # 所有會話
│   │   ├── high_risk_sessions.jsonl # 高風險會話
│   │   └── alerts.jsonl             # 告警事件
│   └── 2025-10-26/
│       └── ...
├── stats/
│   ├── 2025-10-27_stats.json       # 每日統計
│   └── ...
└── threat_intel/
    ├── malicious_ips.json          # 惡意 IP 列表
    ├── attack_patterns.json        # 攻擊模式
    └── payloads.json               # Payload 樣本
```

**檔案類型**：
- `sessions.jsonl`：所有已處理會話（按時間排序）
- `high_risk_sessions.jsonl`：風險分數 ≥ 70 的會話
- `alerts.jsonl`：需要告警的事件（CRITICAL/HIGH）
- `*_stats.json`：統計摘要（攻擊分布、Top IP...）

---

## 架構設計

### 系統架構

```
┌─────────────────┐
│ Ingestion API   │ 接收會話數據
└────────┬────────┘
         │ 寫入
         ▼
┌─────────────────┐
│  Redis Stream   │ 消息佇列（可靠、持久）
│ sessions_stream │
└────────┬────────┘
         │ 批次讀取
         ▼
┌─────────────────────────────────┐
│     Analytics Worker (本服務)    │
│  ┌──────────────────────────┐   │
│  │  1. Normalizer  (正規化)  │   │
│  └──────────┬───────────────┘   │
│             ▼                    │
│  ┌──────────────────────────┐   │
│  │  2. Enricher   (豐富化)   │   │
│  └──────────┬───────────────┘   │
│             ▼                    │
│  ┌──────────────────────────┐   │
│  │  3. Evaluator  (評估)     │   │
│  └──────────┬───────────────┘   │
│             ▼                    │
│  ┌──────────────────────────┐   │
│  │  4. Loader     (存儲)     │   │
│  └──────────┬───────────────┘   │
└─────────────┼───────────────────┘
              ▼
      ┌───────────────┐
      │  File System  │ 持久化存儲
      │  /app/data/   │
      └───────────────┘
              │
              ▼
      ┌───────────────┐
      │   Query API   │ 查詢服務
      └───────────────┘
```

### 處理流程

```
原始數據 → 正規化 → 豐富化 → 評估 → 存儲
  ↓         ↓         ↓        ↓      ↓
清理     添加情報   計算分數  分類保存
驗證     標籤化     威脅評級  索引建立
```

---

## 數據處理流程

### 完整處理週期

```python
# 1️⃣ 接收階段
messages = redis_client.xreadgroup(
    CONSUMER_GROUP, CONSUMER_NAME,
    {REDIS_STREAM: '>'},
    count=BATCH_SIZE, block=BLOCK_MS
)

# 2️⃣ 正規化階段
normalized = normalize_session(raw_session)
# - 清理 IP：192.168.1.1/24 → 192.168.1.1
# - 時間標準化：timestamp → ISO 8601
# - 類型映射：xss → cross_site_scripting

# 3️⃣ 豐富化階段
enriched = enrich_session(normalized)
# - 添加威脅情報標籤
# - 識別攻擊工具（sqlmap, nikto...）
# - 分析 Payload 模式

# 4️⃣ 評估階段
evaluated = evaluate_session(enriched)
# - 計算風險分數：75/100
# - 威脅等級：HIGH
# - 建議動作：["block_ip", "alert_soc"]

# 5️⃣ 存儲階段
saved = save_session(evaluated)
# - 寫入 sessions.jsonl
# - 寫入 high_risk_sessions.jsonl (如果 risk ≥ 70)
# - 更新統計資訊

# 6️⃣ 確認階段
redis_client.xack(REDIS_STREAM, CONSUMER_GROUP, msg_id)
```

### 錯誤處理邏輯

```
收到消息
  ├─ 解析成功？
  │   ├─ Yes → 正規化
  │   └─ No → 記錄錯誤 + ACK（避免重複處理）
  │
  ├─ 驗證通過？
  │   ├─ Yes → 豐富化
  │   └─ No → 記錄警告 + ACK
  │
  ├─ 處理成功？
  │   ├─ Yes → 存儲 + ACK
  │   └─ No → 記錄錯誤 + 不 ACK（待重試）
  │
  └─ 存儲成功？
      ├─ Yes → ACK
      └─ No → 不 ACK（待重試）
```

---

## 模組說明

### `main.py` - 主程序

**職責**：
- 初始化 Redis 連接
- 創建 Consumer Group
- 主循環：批次消費消息
- 協調各處理模組

**關鍵函數**：
```python
create_consumer_group()    # 創建消費者群組
process_batch(messages)    # 處理一批消息
main_loop()                # 主循環
```

### `normalizer.py` - 正規化模組

**職責**：
- 資料清理與驗證
- 格式標準化
- 補充預設值

**關鍵函數**：
```python
normalize_session(session)        # 正規化單個會話
validate_session(session)         # 驗證資料完整性
normalize_ip(ip)                  # IP 清理
normalize_timestamp(ts)           # 時間標準化
clean_string(s)                   # 字串清理
```

### `enricher.py` - 豐富化模組

**職責**：
- 添加威脅情報
- 模式識別
- 行為分析

**關鍵函數**：
```python
enrich_session(session)               # 豐富化會話
generate_threat_labels(session)       # 生成威脅標籤
analyze_attack_patterns(session)      # 攻擊模式分析
analyze_user_agent(ua)                # User Agent 分析
analyze_payloads(session)             # Payload 分析
```

### `evaluator.py` - 評估模組

**職責**：
- 計算風險分數
- 評估威脅等級
- 生成建議

**關鍵函數**：
```python
evaluate_session(session)             # 評估會話
calculate_risk_score(session)         # 計算風險分數
determine_threat_level(score)         # 威脅等級判定
assess_impact(session)                # 影響評估
generate_recommendations(session)     # 生成建議
```

### `loader.py` - 載入模組

**職責**：
- 資料持久化
- 檔案管理
- 統計更新

**關鍵函數**：
```python
save_session(session)              # 保存會話
save_to_jsonl(session)             # JSONL 格式存儲
update_statistics(session)         # 更新統計
create_alert_if_needed(session)    # 創建告警
```

---

## 配置說明

### 環境變數

| 變數名 | 預設值 | 說明 |
|--------|--------|------|
| `REDIS_HOST` | `analytics_redis` | Redis 主機名稱 |
| `REDIS_PORT` | `6379` | Redis 端口 |
| `REDIS_STREAM` | `sessions_stream` | Redis Stream 名稱 |
| `CONSUMER_GROUP` | `analytics_workers` | 消費者群組名稱 |
| `CONSUMER_NAME` | `worker-1` | 消費者名稱（多 Worker 時需唯一） |
| `BATCH_SIZE` | `100` | 每批次處理消息數量 |
| `BLOCK_MS` | `5000` | 阻塞等待時間（毫秒） |
| `DATA_DIR` | `/app/data` | 數據存儲目錄 |
| `OUTPUT_FORMAT` | `jsonl` | 輸出格式：`jsonl`, `json`, `database` |
| `BATCH_WRITE` | `false` | 是否批次寫入（減少 I/O） |

### Docker Compose 配置範例

```yaml
analytics_worker:
  build: ./services/analytics_worker
  container_name: analytics_worker
  restart: always
  networks:
    - analytics_network
  environment:
    - REDIS_HOST=analytics_redis
    - REDIS_PORT=6379
    - REDIS_STREAM=sessions_stream
    - CONSUMER_GROUP=analytics_workers
    - CONSUMER_NAME=worker-1  # 多 Worker 時遞增：worker-2, worker-3...
    - BATCH_SIZE=100
    - DATA_DIR=/app/data
  volumes:
    - analytics_data:/app/data  # 持久化數據
  depends_on:
    analytics_redis:
      condition: service_healthy
```

---

## 使用方式

### 1. 本地開發

```bash
# 安裝依賴
pip install -r requirements.txt

# 設定環境變數
export REDIS_HOST=localhost
export REDIS_PORT=6379

# 執行
python main.py
```

### 2. Docker 運行

```bash
# 構建映像
docker build -t analytics_worker .

# 運行容器
docker run -d \
  --name analytics_worker \
  -e REDIS_HOST=analytics_redis \
  -e REDIS_PORT=6379 \
  -v /path/to/data:/app/data \
  analytics_worker
```

### 3. Docker Compose 運行

```bash
# 啟動所有服務
docker-compose up -d analytics_worker

# 查看日誌
docker-compose logs -f analytics_worker

# 查看處理進度
docker-compose exec analytics_worker cat /app/data/sessions/$(date +%Y-%m-%d)/sessions.jsonl | wc -l
```

### 4. 多 Worker 擴展

```yaml
# docker-compose.yml
analytics_worker_1:
  extends: analytics_worker
  environment:
    - CONSUMER_NAME=worker-1

analytics_worker_2:
  extends: analytics_worker
  environment:
    - CONSUMER_NAME=worker-2

analytics_worker_3:
  extends: analytics_worker
  environment:
    - CONSUMER_NAME=worker-3
```

```bash
# 擴展到 3 個 Worker
docker-compose up -d --scale analytics_worker=3
```

---

## 數據格式

### 輸入數據格式（Redis Stream）

```json
{
  "sess_uuid": "attack-sqli-001",
  "peer_ip": "192.168.1.100",
  "peer_port": 54321,
  "user_agent": "sqlmap/1.5.2",
  "start_time": 1698364800,
  "attack_types": {
    "/login": "sqli"
  },
  "requests": [
    {
      "method": "POST",
      "path": "/login",
      "headers": {...},
      "cookies": {...}
    }
  ]
}
```

### 輸出數據格式（JSONL）

```json
{
  "sess_uuid": "attack-sqli-001",
  "peer_ip": "192.168.1.100",
  "peer_port": 54321,
  "user_agent": "sqlmap/1.5.2",
  "start_time": "2025-10-27T02:00:00Z",
  "end_time": "2025-10-27T02:05:30Z",
  "attack_types": ["sql_injection"],
  "request_count": 15,

  "threat_intelligence": {
    "is_known_malicious": true,
    "threat_categories": ["automated_scanner"],
    "reputation_score": 85
  },

  "attack_patterns": {
    "techniques": ["sql_injection", "authentication_bypass"],
    "sophistication": "medium",
    "indicators": ["union_based_sqli", "time_based_blind"]
  },

  "user_agent_info": {
    "is_bot": true,
    "tool_name": "sqlmap",
    "version": "1.5.2"
  },

  "risk_score": 85,
  "threat_level": "HIGH",
  "priority": "P1",
  "confidence_score": 95,

  "recommendations": [
    "block_ip_immediately",
    "update_waf_rules",
    "alert_security_team"
  ],

  "processed_at": "2025-10-27T02:06:00Z"
}
```

---

## 監控與日誌

### 日誌格式

```
2025-10-27 02:00:00 - INFO - Analytics Worker starting...
2025-10-27 02:00:00 - INFO - Redis: analytics_redis:6379
2025-10-27 02:00:00 - INFO - Stream: sessions_stream
2025-10-27 02:00:00 - INFO - Consumer Group: analytics_workers
2025-10-27 02:00:00 - INFO - ✅ Created consumer group: analytics_workers
2025-10-27 02:00:00 - INFO - 🚀 Worker started, waiting for messages...
2025-10-27 02:00:15 - INFO - 📦 Received batch of 50 messages
2025-10-27 02:00:18 - INFO - ✅ Processed attack-sqli-001 | Risk: 85/100 | Threat: HIGH | Alert: HIGH
2025-10-27 02:00:18 - INFO - ✅ Processed attack-xss-002 | Risk: 45/100 | Threat: MEDIUM | Alert: INFO
...
2025-10-27 02:00:20 - INFO - ✅ Processed 50/50 messages (Total: 50)
```

### 關鍵指標

**處理指標**：
- 總處理數量
- 成功/失敗比率
- 平均處理時間
- 當前佇列長度

**風險分布**：
- CRITICAL 數量
- HIGH 數量
- MEDIUM 數量
- LOW/INFO 數量

**攻擊類型分布**：
- SQL Injection 數量
- XSS 數量
- Command Execution 數量
- 其他類型

### 查看監控資訊

```bash
# 查看實時日誌
docker logs -f analytics_worker

# 查看處理統計
cat /app/data/stats/$(date +%Y-%m-%d)_stats.json

# 查看高風險會話
cat /app/data/sessions/$(date +%Y-%m-%d)/high_risk_sessions.jsonl

# 查看告警
cat /app/data/sessions/$(date +%Y-%m-%d)/alerts.jsonl
```

---

## 故障處理

### 常見問題

#### 1. Worker 無法連接 Redis

**症狀**：
```
ERROR - ❌ Redis error: Error 111 connecting to analytics_redis:6379. Connection refused.
```

**解決方案**：
```bash
# 檢查 Redis 是否運行
docker-compose ps analytics_redis

# 檢查網路連接
docker-compose exec analytics_worker ping analytics_redis

# 重啟 Redis
docker-compose restart analytics_redis
```

#### 2. 消息處理失敗

**症狀**：
```
WARNING - ⚠️  Invalid session unknown: Missing required field: sess_uuid
```

**解決方案**：
- 檢查 Ingestion API 是否正確發送數據
- 驗證數據格式是否符合規範
- 查看失敗消息詳情（未 ACK 的消息會保留在 Stream 中）

```bash
# 查看 Pending 消息
docker-compose exec analytics_redis redis-cli XPENDING sessions_stream analytics_workers
```

#### 3. 磁碟空間不足

**症狀**：
```
ERROR - ❌ Error saving session: [Errno 28] No space left on device
```

**解決方案**：
```bash
# 檢查磁碟使用
df -h /app/data

# 清理舊數據（保留最近 7 天）
find /app/data/sessions -type d -mtime +7 -exec rm -rf {} \;

# 啟用數據壓縮（後續優化）
```

#### 4. Worker 處理緩慢

**可能原因**：
- 批次大小設置過小
- I/O 瓶頸
- 單個消息處理時間過長

**解決方案**：
```yaml
# 調整批次大小
environment:
  - BATCH_SIZE=200  # 增加批次大小

# 啟用批次寫入
  - BATCH_WRITE=true

# 增加 Worker 數量
docker-compose up -d --scale analytics_worker=3
```

### 調試模式

```bash
# 啟用詳細日誌
docker-compose exec analytics_worker python -u main.py

# 查看處理細節
export LOG_LEVEL=DEBUG
```

---

## 效能調優

### 建議配置

**小規模部署**（< 1000 sessions/天）：
- Worker 數量：1
- Batch Size：50
- Block MS：5000

**中規模部署**（1000-10000 sessions/天）：
- Worker 數量：2-3
- Batch Size：100-200
- Block MS：3000

**大規模部署**（> 10000 sessions/天）：
- Worker 數量：5+
- Batch Size：500
- Block MS：1000
- 啟用 Batch Write

---

## 相關文檔

- [Ingestion API 文檔](../ingestion_api/README.md)
- [Query API 文檔](../query_api/README.md)
- [系統架構文檔](../../docs/architecture.md)
- [Redis Stream 官方文檔](https://redis.io/docs/data-types/streams/)

---

## 授權

MIT License

## 作者

Honeypot Data Platform Team

## 更新日誌

- **v1.0.0** (2025-10-27)
  - 初始版本發布
  - 支援 4 階段處理流程
  - JSONL 格式輸出
  - Consumer Group 可靠消費
