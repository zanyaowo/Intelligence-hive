# Docker 配置說明

本目錄包含所有 Docker Compose 配置文件。

## 📁 檔案說明

- **docker-compose.honeypot.yml** - 蜜罐服務（SNARE + Tanner + Ingestion API）
- **docker-compose.analytics.yml** - 分析服務（Redis + Analytics Worker）
- **docker-compose.all.yml** - 整合所有服務
- **.env.example** - 環境變數範例

## 🚀 快速開始

### 1. 啟動所有服務（推薦）

```bash
# 從專案根目錄執行
docker-compose -f docker/docker-compose.all.yml up -d
```

### 2. 分別啟動服務

```bash
# 只啟動蜜罐
docker-compose -f docker/docker-compose.honeypot.yml up -d

# 只啟動分析服務
docker-compose -f docker/docker-compose.analytics.yml up -d
```

### 3. 查看日誌

```bash
# 所有服務
docker-compose -f docker/docker-compose.all.yml logs -f

# 特定服務
docker-compose -f docker/docker-compose.all.yml logs -f analytics_worker
```

### 4. 停止服務

```bash
docker-compose -f docker/docker-compose.all.yml down
```

## 🔌 服務端點

| 服務 | 端口 | 說明 |
|------|------|------|
| SNARE 蜜罐 | 80 | HTTP 蜜罐 |
| Tanner 服務 | 8090 | 攻擊分析引擎 |
| Tanner API | 8081 | REST API |
| Tanner Web | 8091 | Web 儀表板 |
| Ingestion API | 8082 | 數據接收 API |
| Analytics Redis | 6380 | 消息隊列 |

## 📊 架構圖

```
攻擊者 → SNARE (80) → Tanner (8090) → Tanner API (8081)
                                             ↓
                                      Honeypot Agent
                                             ↓
                                   Ingestion API (8082)
                                             ↓
                                   Analytics Redis (6380)
                                             ↓
                                    Analytics Worker
                                             ↓
                                    Database (未來)
```

## ⚠️ 注意事項

1. 確保 `.env` 文件已配置（參考 `.env.example`）
2. 首次啟動需要構建映像，可能需要幾分鐘
3. 確保端口未被佔用（80, 8081, 8082, 8090, 8091, 6380）
4. 生產環境請修改預設密碼和 API Key

## 🔧 故障排除

### 端口衝突

```bash
# 檢查端口佔用
sudo lsof -i :80
sudo lsof -i :8082

# 修改 docker-compose.yml 中的端口映射
ports:
  - "8080:80"  # 改為其他端口
```

### 查看服務狀態

```bash
docker-compose -f docker/docker-compose.all.yml ps
```

### 重新構建映像

```bash
docker-compose -f docker/docker-compose.all.yml build --no-cache
```
