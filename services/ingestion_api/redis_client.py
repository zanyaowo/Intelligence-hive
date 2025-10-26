import os
import redis
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Redis 配置
REDIS_HOST = os.getenv("REDIS_HOST", "analytics_redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_STREAM = os.getenv("REDIS_STREAM", "sessions_stream")

# 創建 Redis 連接池
redis_pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    decode_responses=False,  # 保持 bytes 格式
    max_connections=20
)

def get_redis_client() -> redis.Redis:
    return redis.Redis(connection_pool=redis_pool)


def publish_sessions(sessions: List[Dict[str, Any]]) -> int:
    """
    發布 sessions 到 Redis Stream

    Args:
        sessions: Session 數據列表

    Returns:
        int: 成功發布的數量
    """
    client = get_redis_client()
    published_count = 0

    try:
        for session in sessions:
            # 使用 XADD 添加到 Stream
            message_id = client.xadd(
                REDIS_STREAM,
                {"data": json.dumps(session)},
                maxlen=100000  # 保留最近 10 萬筆（防止無限增長）
            )
            published_count += 1
            logger.debug(f"Published session {session.get('sess_uuid')} with ID {message_id}")

        logger.info(f"✅ Published {published_count} sessions to Redis Stream: {REDIS_STREAM}")
        return published_count

    except redis.RedisError as e:
        logger.error(f"❌ Redis error: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Error publishing to Redis: {e}")
        raise


def get_stream_info() -> Dict[str, Any]:
    client = get_redis_client()
    try:
        info = client.xinfo_stream(REDIS_STREAM)
        return {
            "length": info.get(b"length", 0),
            "first_entry": info.get(b"first-entry"),
            "last_entry": info.get(b"last-entry"),
            "groups": info.get(b"groups", 0)
        }
    except redis.ResponseError:
        return {"length": 0, "groups": 0}
    except Exception as e:
        logger.error(f"Error getting stream info: {e}")
        return {}


def health_check() -> bool:
    try:
        client = get_redis_client()
        return client.ping()
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return False
