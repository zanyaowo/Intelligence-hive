# Intelligence Hive - 前端應用

## 📋 概述

基於 **Alpine.js + Tailwind CSS + Chart.js** 的輕量級單頁應用，用於可視化展示蜜罐威脅情報數據。

## 🎨 技術棧

- **Alpine.js 3.x** - 響應式框架（15KB）
- **Tailwind CSS** - 實用優先 CSS 框架
- **Chart.js 4.x** - 數據可視化
- **Day.js** - 日期處理
- **純 HTML/CSS/JS** - 無需構建流程

## 📂 文件結構

```
frontend/
├── index.html           # 主頁面
├── css/
│   └── style.css       # 自定義樣式
├── js/
│   ├── api.js          # API 調用封裝
│   ├── app.js          # 主應用邏輯
│   └── charts.js       # 圖表配置
├── Dockerfile          # Docker 構建文件
└── README.md           # 本文件
```

## 🚀 運行方式

### 方法 1: 使用 Docker（推薦）

```bash
# 從專案根目錄
docker-compose -f docker/docker-compose.all.yml up -d frontend

# 訪問
open http://localhost:8084
```

### 方法 2: 本地運行（開發）

```bash
cd frontend

# 使用 Python HTTP 服務器
python3 -m http.server 8080

# 或使用 Node.js
npx http-server -p 8080

# 訪問
open http://localhost:8080
```

### 方法 3: VS Code Live Server

1. 安裝 Live Server 擴展
2. 右鍵 `index.html` → "Open with Live Server"

## 🎯 功能模塊

### 1. 儀表板 (Dashboard)
- 📊 概覽統計卡片
- 📈 攻擊趨勢圖表
- 🚨 最近告警列表
- 🔥 Top 威脅展示

**API**: `GET /api/dashboard`

### 2. 會話列表 (Sessions)
- 🔍 多維度過濾（威脅等級、攻擊類型、風險分數）
- 📋 分頁瀏覽
- 👁️ 點擊查看詳情
- 🎨 顏色編碼（風險等級）

**API**: `GET /api/sessions`

### 3. 告警中心 (Alerts)
- 🚨 CRITICAL/HIGH 告警展示
- 📊 告警統計
- 🔔 實時更新（未來）

**API**: `GET /api/alerts`

### 4. 統計分析 (Statistics)
- 📅 日期範圍選擇（1/7/30天）
- 📊 威脅等級分佈圖
- 📊 攻擊類型分佈圖
- 🌐 Top IP 列表

**API**: `GET /api/statistics`

### 5. 威脅情報 (Threat Intelligence)
- 🌐 惡意 IP 列表（可複製）
- 🤖 惡意 User Agent
- 🎯 攻擊特徵
- 💉 Payload 樣本

**API**: `GET /api/threat-intelligence`

## 🔧 配置

### API 端點配置

編輯 `js/api.js`:

```javascript
const API = {
    baseURL: 'http://localhost:8083/api', // 修改為你的 Query API 地址
    // ...
};
```

### 自定義樣式

編輯 `css/style.css` 或在 `index.html` 中修改 Tailwind 配置。

## 🎨 配色方案

```css
威脅等級:
CRITICAL: #DC2626 (紅色)
HIGH:     #EA580C (橙色)
MEDIUM:   #F59E0B (黃色)
LOW:      #10B981 (綠色)
INFO:     #6B7280 (灰色)

主題色:
Primary:   #3B82F6 (藍色)
Secondary: #8B5CF6 (紫色)
```

## 📱 響應式設計

- **Desktop** (> 1024px): 5 列卡片布局
- **Tablet** (768px - 1024px): 2-3 列布局
- **Mobile** (< 768px): 1 列布局

## 🐛 故障排除

### CORS 錯誤

如果遇到跨域問題，確保 Query API 的 CORS 設置正確：

```python
# services/query_api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8084", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 無法載入數據

1. 確認 Query API 正在運行:
   ```bash
   curl http://localhost:8083/api/dashboard
   ```

2. 檢查瀏覽器開發者工具 Console 查看錯誤信息

3. 確認 `js/api.js` 中的 `baseURL` 設置正確

### 圖表不顯示

1. 確認 Chart.js 已正確載入（檢查 Console）
2. 確認 API 返回的數據格式正確
3. 檢查 Canvas 元素是否存在

## 🚀 未來計劃

- [ ] WebSocket 實時數據推送
- [ ] 會話詳情彈窗（目前僅 alert）
- [ ] 匯出功能（CSV, JSON, PDF）
- [ ] 深色模式
- [ ] 數據緩存優化
- [ ] 進階搜索與篩選
- [ ] 自定義儀表板配置
- [ ] 多語言支持

## 📊 性能

- **初始載入**: < 500ms (含 CDN 庫)
- **頁面大小**: < 100KB (未壓縮)
- **CDN 依賴**:
  - Tailwind CSS: ~70KB (gzip)
  - Alpine.js: ~15KB
  - Chart.js: ~180KB
  - Day.js: ~7KB

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 License

MIT License

---

**製作日期**: 2025-10-28
**版本**: 1.0.0
