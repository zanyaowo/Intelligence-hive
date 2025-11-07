"""
Query API - 前端資料查詢服務

提供端點讓前端查詢已處理的蜜罐資料
"""

from fastapi import FastAPI, Query, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import os
from pathlib import Path as PathLib

# 載入環境變數
from dotenv import load_dotenv
load_dotenv()

from data_reader import (
    get_sessions,
    get_session_by_uuid,
    get_alerts,
    get_statistics,
    get_dashboard_data,
    get_threat_intelligence,
    get_available_dates
)

# 顯示數據目錄配置
DATA_DIR = os.getenv("DATA_DIR", "/app/data")
print(f"🗂️  使用數據目錄: {DATA_DIR}")
from models import (
    SessionListResponse,
    SessionDetailResponse,
    AlertListResponse,
    StatisticsResponse,
    DashboardResponse,
    ThreatIntelligenceResponse
)

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 創建 FastAPI 應用
app = FastAPI(
    title="Honeypot Query API",
    description="API for querying processed honeypot data",
    version="1.0.0"
)

# 配置 CORS（允許前端跨域請求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境應該限制為特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """API 根端點"""
    return {
        "service": "Honeypot Query API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "sessions": "/api/sessions",
            "session_detail": "/api/sessions/{uuid}",
            "alerts": "/api/alerts",
            "statistics": "/api/statistics",
            "dashboard": "/api/dashboard",
            "threat_intelligence": "/api/threat-intelligence",
            "dates": "/api/dates"
        }
    }


@app.get("/health")
async def health_check():
    """健康檢查"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/sessions", response_model=SessionListResponse)
async def list_sessions(
    date: Optional[str] = Query(None, description="日期 (YYYY-MM-DD)，預設今天"),
    threat_level: Optional[str] = Query(None, description="威脅等級過濾: CRITICAL, HIGH, MEDIUM, LOW, INFO"),
    attack_type: Optional[str] = Query(None, description="攻擊類型過濾: sqli, xss, cmd_exec, etc."),
    min_risk: Optional[int] = Query(None, ge=0, le=100, description="最小風險分數 (0-100)"),
    peer_ip: Optional[str] = Query(None, description="來源 IP 過濾 (支援部分匹配)"),
    sess_uuid: Optional[str] = Query(None, description="會話 UUID 過濾 (支援部分匹配)"),
    requires_review: Optional[bool] = Query(None, description="是否需要人工審查"),
    limit: int = Query(50, ge=1, le=500, description="每頁數量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    sort_by: str = Query("processed_at", description="排序欄位: processed_at, risk_score"),
    order: str = Query("desc", description="排序順序: asc, desc")
):
    """
    獲取會話列表

    支援過濾、分頁、排序功能

    **範例請求**:
    ```
    GET /api/sessions?threat_level=HIGH&limit=20&offset=0
    GET /api/sessions?date=2025-10-26&min_risk=50
    GET /api/sessions?attack_type=sqli&sort_by=risk_score&order=desc
    ```
    """
    try:
        # 如果沒有指定日期或日期為 'null' 字串，使用今天
        if not date or date == "null":
            date = datetime.utcnow().strftime("%Y-%m-%d")

        # 驗證日期格式
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        # 獲取資料
        result = get_sessions(
            date=date,
            threat_level=threat_level,
            attack_type=attack_type,
            min_risk=min_risk,
            peer_ip=peer_ip,
            sess_uuid=sess_uuid,
            requires_review=requires_review,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            order=order
        )

        logger.info(f"📊 Sessions query: date={date}, filters={threat_level}/{attack_type}, returned {len(result['sessions'])} items")

        return result

    except Exception as e:
        logger.error(f"Error querying sessions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{uuid}", response_model=SessionDetailResponse)
async def get_session_detail(
    uuid: str = Path(..., description="Session UUID")
):
    """
    獲取單個會話的完整詳情

    **範例請求**:
    ```
    GET /api/sessions/test-sqli-attack-001
    ```
    """
    try:
        session = get_session_by_uuid(uuid)

        if not session:
            raise HTTPException(status_code=404, detail=f"Session {uuid} not found")

        logger.info(f"🔍 Session detail requested: {uuid}")

        return session

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session detail: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alerts", response_model=AlertListResponse)
async def list_alerts(
    date: Optional[str] = Query(None, description="日期 (YYYY-MM-DD)"),
    alert_level: Optional[str] = Query(None, description="警報等級: CRITICAL, HIGH"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    獲取高風險警報列表

    **範例請求**:
    ```
    GET /api/alerts?alert_level=CRITICAL
    GET /api/alerts?date=2025-10-26&limit=10
    ```
    """
    try:
        if not date:
            date = datetime.utcnow().strftime("%Y-%m-%d")

        result = get_alerts(
            date=date,
            alert_level=alert_level,
            limit=limit,
            offset=offset
        )

        logger.info(f"🚨 Alerts query: date={date}, level={alert_level}, returned {len(result['alerts'])} items")

        return result

    except Exception as e:
        logger.error(f"Error querying alerts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/statistics", response_model=StatisticsResponse)
async def get_stats(
    date: Optional[str] = Query(None, description="日期 (YYYY-MM-DD)"),
    days: int = Query(1, ge=1, le=30, description="統計天數")
):
    """
    獲取統計資料

    **範例請求**:
    ```
    GET /api/statistics?date=2025-10-26
    GET /api/statistics?days=7  # 最近7天
    ```
    """
    try:
        if not date:
            date = datetime.utcnow().strftime("%Y-%m-%d")

        result = get_statistics(date=date, days=days)

        logger.info(f"📊 Statistics query: date={date}, days={days}")

        return result

    except Exception as e:
        logger.error(f"Error getting statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    date: Optional[str] = Query(None, description="日期 (YYYY-MM-DD)，預設今天")
):
    """
    獲取儀表板資料

    包含：
    - 會話總數
    - 威脅等級分布
    - TOP 攻擊來源 IP
    - 最近的高風險警報
    - 攻擊類型分布
    - 24小時趨勢

    **範例請求**:
    ```
    GET /api/dashboard
    GET /api/dashboard?date=2025-01-06
    ```
    """
    try:
        if not date:
            date = datetime.utcnow().strftime("%Y-%m-%d")

        result = get_dashboard_data(date)

        logger.info(f"📊 Dashboard data requested for date={date}")

        return result

    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/threat-intelligence", response_model=ThreatIntelligenceResponse)
async def get_threat_intel(
    date: Optional[str] = Query(None, description="日期 (YYYY-MM-DD)")
):
    """
    獲取威脅情報 Feed

    包含：
    - 惡意 IP 黑名單
    - 攻擊模式簽名
    - 惡意 User Agents
    - Payload 樣本

    **範例請求**:
    ```
    GET /api/threat-intelligence?date=2025-10-26
    ```
    """
    try:
        if not date:
            date = datetime.utcnow().strftime("%Y-%m-%d")

        result = get_threat_intelligence(date=date)

        logger.info(f"🔒 Threat intelligence query: date={date}")

        return result

    except Exception as e:
        logger.error(f"Error getting threat intelligence: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/geo-distribution")
async def get_geo_dist(
    date: Optional[str] = Query(None, description="日期 (YYYY-MM-DD)"),
    days: int = Query(1, ge=1, le=30, description="統計天數")
):
    """
    獲取地理分布統計

    返回按國家聚合的攻擊數據，用於世界地圖可視化

    **範例請求**:
    ```
    GET /api/geo-distribution
    GET /api/geo-distribution?date=2025-10-26
    GET /api/geo-distribution?days=7  # 最近7天
    ```
    """
    try:
        if not date:
            date = datetime.utcnow().strftime("%Y-%m-%d")

        from data_reader import get_geo_distribution
        result = get_geo_distribution(date=date, days=days)

        logger.info(f"🌍 Geo distribution query: date={date}, days={days}, countries={result['total_countries']}")

        return result

    except Exception as e:
        logger.error(f"Error getting geo distribution: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dates")
async def list_available_dates():
    """
    獲取有資料的日期列表

    **範例請求**:
    ```
    GET /api/dates
    ```
    """
    try:
        dates = get_available_dates()

        return {
            "dates": dates,
            "count": len(dates)
        }

    except Exception as e:
        logger.error(f"Error getting available dates: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083)
