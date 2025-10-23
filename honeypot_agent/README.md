# Honeypot Agent - Tanner 資料收集器

輕量級的代理程式，從 Tanner 蜜罐 API 收集已分析的會話資料，並轉發到 Ingestion API 進行後續處理。

## 概述

此代理程式作為 Tanner（蜜罐分析引擎）與資料管線之間的資料橋接。它定期從 Tanner API 獲取已分析的會話資料，並轉發到 Ingestion API，不進行額外處理，確保資料一致性和簡潔性。

## 功能特色

### 核心功能

1. **基於 API 的資料收集**
   - 從 Tanner API (`http://tanner:8081`) 獲取已分析的會話
   - 從所有已註冊的 Snare 蜜罐收集資料
   - 追蹤已處理的會話以避免重複

2. **簡單的資料轉發**
   - 將完整的會話資料轉發到 Ingestion API
   - 不進行資料轉換或豐富化（由 Tanner 處理）
   - 保留所有來自 Tanner 的分析結果

3. **可靠性設計**
   - 錯誤處理與日誌記錄
   - 定期輪詢機制
   - 支援優雅關閉
   - 執行期間的會話去重

## 安裝

### 安裝依賴套件

```bash
cd /path/to/honeypot_agent
pip3 install -r requirements.txt
```

**依賴套件：**
- `requests` - HTTP 客戶端函式庫

就這麼簡單！不需要額外設定。

## 使用方式

### 正式運作（持續輪詢）

```bash
python3 main.py
```

代理程式會：
1. 每 60 秒從 Tanner API 獲取會話
2. 過濾已處理的會話
3. 將新會話轉發到 Ingestion API
4. 記錄所有操作

### 停止代理程式

按 `Ctrl+C` 優雅地停止代理程式。

## 配置說明

編輯 `main.py` 來配置代理程式：

```python
# Tanner API 位址
TANNER_API_URL = "http://localhost:8081"

# Ingestion API 位址
INGESTION_API_URL = "http://localhost:8082/ingest"

# 資料收集間隔（秒）
AGENT_RUN_INTERVAL_SECONDS = 60
```

## 資料流程

```
Snare 蜜罐 (Port 80)
    ↓ 接收攻擊請求
Tanner 服務 (Port 8090)
    ↓ 分析攻擊並儲存到 Redis
    ↓ (包含: GeoIP、攻擊檢測、會話統計)
Tanner API (Port 8081)
    ↓ 透過 REST API 提供已分析的資料
Honeypot Agent
    ↓ 獲取並轉發
Ingestion API (Port 8082)
    ↓ 進一步處理與儲存
資料管線
```

## 資料結構

轉發到 Ingestion API 的每個會話包含：

### 會話層級欄位
- `sess_uuid`: 會話唯一識別碼
- `peer_ip`: 攻擊者 IP 位址
- `peer_port`: 攻擊者來源端口
- `user_agent`: User-Agent 字串
- `snare_uuid`: 來源 Snare 蜜罐 UUID
- `snare_id`: 由代理程式新增，用於追蹤
- `start_time`: 會話開始時間戳記
- `end_time`: 會話結束時間戳記
- `requests_in_second`: 請求頻率
- `approx_time_between_requests`: 請求間平均時間
- `accepted_paths`: 訪問的路徑數量
- `errors`: 錯誤數量
- `hidden_links`: 訪問的隱藏連結數量
- `referer`: HTTP Referer 標頭
- `cookies`: 會話 cookies
- `possible_owners`: 使用者行為分類（user/attacker/tool/crawler）

### 攻擊分析欄位
- `attack_types`: 偵測到的攻擊類型陣列
- `attack_count`: 攻擊類型頻率統計
- `location`: GeoIP 地理位置資料
  - `country`: 國家名稱
  - `country_code`: ISO 國家代碼
  - `city`: 城市名稱
  - `zip_code`: 郵遞區號

### 請求層級欄位（在 `paths` 陣列中）
每個請求包含：
- `path`: 請求路徑
- `timestamp`: 請求時間戳記
- `response_status`: HTTP 回應狀態
- `method`: HTTP 方法（GET/POST/PUT/PATCH）
- `headers`: 完整 HTTP headers（dict）
- `cookies`: 請求 cookies（dict）
- `query_params`: URL 查詢參數（dict）
- `post_data`: POST 請求主體（用於 POST/PUT/PATCH）
- `attack_type`: Tanner 的攻擊分類

## Tanner 偵測的攻擊類型

Tanner 自動偵測並分類：

- **index**: 正常頁面訪問
- **sqli**: SQL 注入（使用 pylibinjection）
- **xss**: 跨站腳本攻擊
- **lfi**: 本地檔案包含
- **rfi**: 遠端檔案包含
- **cmd_exec**: 命令執行
- **php_code_injection**: PHP 程式碼注入
- **php_object_injection**: PHP 物件注入
- **template_injection**: 模板注入
- **xxe_injection**: XML 外部實體注入
- **crlf**: CRLF 注入

所有攻擊偵測由 Tanner 執行，而非此代理程式。

## 範例會話資料

```json
{
  "sess_uuid": "4df8ed48392b44a29da71e51fcbda47c",
  "peer_ip": "185.199.110.153",
  "peer_port": 47194,
  "location": {
    "country": "Netherlands",
    "country_code": "NL",
    "city": null
  },
  "user_agent": "curl/8.7.1",
  "snare_uuid": "f06a04c3-545e-4aae-b874-96631bf532a3",
  "attack_types": ["index", "index"],
  "attack_count": {"index": 2},
  "paths": [
    {
      "path": "/?test=restart&status=working",
      "method": "GET",
      "headers": {
        "host": "localhost",
        "user-agent": "curl/8.7.1",
        "accept": "*/*",
        "x-test-header": "container-restarted"
      },
      "cookies": {"sess_uuid": null},
      "query_params": {
        "test": ["restart"],
        "status": ["working"]
      },
      "attack_type": "index"
    }
  ]
}
```

## 架構決策

### 為什麼不處理資料？

1. **單一職責**: 代理程式專注於資料收集，而非分析
2. **資料完整性**: 轉發原始 Tanner 資料確保一致性
3. **簡潔性**: 沒有重複邏輯，更易於維護
4. **信任 Tanner**: Tanner 是專業的蜜罐引擎，具有經過驗證的偵測能力

### 為什麼只使用 API 模式？

- Tanner API 提供完整、已分析的會話資料
- Redis 儲存在修復後穩定可靠（aioredis 2.x 相容性）
- 會話過期會自動觸發分析和儲存
- API 是官方的資料存取介面

## 疑難排解

### 沒有回傳會話

檢查會話是否已過期（預設：最後請求後 300 秒）：
```bash
# 會話只在過期後才會儲存到 Redis
# 最後一個請求後需等待 KEEP_ALIVE_TIME（300 秒）
```

### 連線被拒絕

確認服務正在運行：
```bash
docker ps | grep -E "tanner_service|ingestion_api"
```

### 重複的會話

代理程式在單次執行期間追蹤已處理的 `sess_uuid`。重啟代理程式會重置此追蹤。

## 開發資訊

- **程式語言**: Python 3.9+
- **依賴套件**: requests
- **架構**: 無狀態資料轉發器
- **程式碼大小**: ~88 行（agent.py）

## 專案結構

```
honeypot_agent/
├── agent.py              # 主要代理程式類別
├── main.py               # 進入點
├── requirements.txt      # Python 依賴套件
├── README.md             # 本檔案
├── TANNER_DETECTION_ANALYSIS.md  # Tanner 偵測分析
└── deprecated/           # 已移除/過時的程式碼
    ├── attack_detector.py    # 舊的攻擊偵測（未使用）
    └── sync_to_redis.py      # 舊的 Redis 同步工具
```

## 版本歷史

### v2.0 (2025-10-23)
- **簡化為僅 API 模式**
- 移除 JSON 檔案讀取模式
- 移除 GeoIP 豐富化（現由 Tanner 處理）
- 移除攻擊偵測（現由 Tanner 處理）
- 移除冗餘的依賴套件
- 程式碼大小減少 49%（226 → 88 行）
- 新增完整的 payload 捕獲（method、headers、cookies、query_params、post_data）

### v1.0 (2025-10-21)
- 初始實作，包含雙模式資料收集
- JSON 檔案模式與 API 模式
- GeoIP 豐富化
- 本地攻擊偵測
