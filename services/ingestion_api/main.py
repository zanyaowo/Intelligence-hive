from fastapi import FastAPI, Request, Depends, HTTPException, status
import uvicorn
import logging
from datetime import datetime
from auth import verify_API_key
from redis_client import publish_sessions, get_stream_info, health_check

app = FastAPI(
    title="Intelligence Hive Ingestion API",
    description="API for receiving and queuing honeypot attack data",
    version="2.0.0"
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.get("/")
async def root():
    """服務根端點"""
    return {
        "service": "Intelligence Hive Ingestion API",
        "version": "2.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """健康檢查端點"""
    redis_healthy = health_check()

    return {
        "status": "healthy" if redis_healthy else "degraded",
        "redis": "connected" if redis_healthy else "disconnected",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/ingest")
async def ingest_data(
    request: Request,
    api_key: str = Depends(verify_API_key)
):
    """
    接收蜜罐數據並發布到 Redis Stream

    需要 Header: X-API-Key
    """
    try:
        data = await request.json()

        # 驗證數據格式
        if not isinstance(data, list):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Data must be a list of sessions"
            )

        if not data:
            return {
                "status": "success",
                "message": "No data to process",
                "sessions_queued": 0
            }

        # 發布到 Redis Stream
        published_count = publish_sessions(data)

        logging.info(f"✅ Queued {published_count} sessions from API key {api_key[:8]}...")

        return {
            "status": "success",
            "message": "Data queued for processing",
            "sessions_queued": published_count,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"❌ Error processing data: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/stats")
async def get_stats(api_key: str = Depends(verify_API_key)):
    """
    獲取 Redis Stream 統計信息

    需要 Header: X-API-Key
    """
    try:
        stream_info = get_stream_info()
        return {
            "stream_length": stream_info.get("length", 0),
            "stream_groups": stream_info.get("groups", 0),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logging.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
