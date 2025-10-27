import os
import time
import json
import logging
import redis
from typing import List, Dict, Any, Tuple

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 配置
REDIS_HOST = os.getenv("REDIS_HOST", "analytics_redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_STREAM = os.getenv("REDIS_STREAM", "sessions_stream")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "analytics_workers")
CONSUMER_NAME = os.getenv("CONSUMER_NAME", "worker-1")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 100))
BLOCK_MS = int(os.getenv("BLOCK_MS", 5000))  # 5 秒

# 連接 Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=False)

logging.info(f"Analytics Worker starting...")
logging.info(f"Redis: {REDIS_HOST}:{REDIS_PORT}")
logging.info(f"Stream: {REDIS_STREAM}")
logging.info(f"Consumer Group: {CONSUMER_GROUP}")
logging.info(f"Batch Size: {BATCH_SIZE}")


def create_consumer_group():
    """創建消費者組（如果不存在）"""
    try:
        # 嘗試創建消費者組，從最新消息開始
        redis_client.xgroup_create(REDIS_STREAM, CONSUMER_GROUP, id='$', mkstream=True)
        logging.info(f"✅ Created consumer group: {CONSUMER_GROUP}")
    except redis.ResponseError as e:
        if "BUSYGROUP" in str(e):
            logging.info(f"Consumer group already exists: {CONSUMER_GROUP}")
        else:
            logging.error(f"Error creating consumer group: {e}")
            raise


def process_batch(messages: List[Tuple[bytes, Dict[bytes, bytes]]]) -> int:
    """
    處理一批消息

    Args:
        messages: 消息列表 [(msg_id, {b'data': b'...'}), ...]

    Returns:
        int: 處理成功的數量
    """
    from normalizer import normalize_session, validate_session
    from enricher import enrich_session
    from evaluator import evaluate_session
    from loader import save_session, update_daily_summary

    processed = 0

    for msg_id, msg_data in messages:
        try:
            # === 1. 解析資料 ===
            data_bytes = msg_data.get(b'data', b'{}')
            session = json.loads(data_bytes)

            sess_uuid = session.get('sess_uuid', 'unknown')

            # === 2. 正規化 ===
            normalized_session = normalize_session(session)

            # 驗證資料完整性
            is_valid, error_msg = validate_session(normalized_session)
            if not is_valid:
                logging.warning(f"⚠️  Invalid session {sess_uuid}: {error_msg}")
                # 仍然 ACK，但標記為無效
                redis_client.xack(REDIS_STREAM, CONSUMER_GROUP, msg_id)
                continue

            # === 3. 豐富化 ===
            enriched_session = enrich_session(normalized_session)

            # === 4. 評估 ===
            evaluated_session = evaluate_session(enriched_session)

            # === 5. 保存 ===
            saved = save_session(evaluated_session)

            if saved:
                # 記錄關鍵資訊
                risk_score = evaluated_session.get('risk_score', 0)
                threat_level = evaluated_session.get('threat_level', 'INFO')
                alert_level = evaluated_session.get('alert_level', 'INFO')

                logging.info(
                    f"✅ Processed {sess_uuid} | Risk: {risk_score}/100 | "
                    f"Threat: {threat: {threat_level} | Alert: {alert_level}"
                )

                processed += 1

                # ACK 消息（標記為已處理）
                redis_client.xack(REDIS_STREAM, CONSUMER_GROUP, msg_id)
            else:
                logging.error(f"❌ Failed to save session {sess_uuid}")
                # 不 ACK，允許重試

        except Exception as e:
            logging.error(f"❌ Error processing message {msg_id}: {e}", exc_info=True)
            # 不 ACK 失敗的消息，之後可以重試

    # 在處理完批次後更新每日摘要
    if processed > 0:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        update_daily_summary(today)

    return processed


def main_loop():
    """主循環：持續消費消息"""
    create_consumer_group()

    last_id = '>'  # > 表示只讀取新消息
    total_processed = 0

    logging.info(f"🚀 Worker started, waiting for messages...")

    while True:
        try:
            # 批次讀取消息
            # XREADGROUP 會阻塞直到有新消息或超時
            messages = redis_client.xreadgroup(
                CONSUMER_GROUP,
                CONSUMER_NAME,
                {REDIS_STREAM: last_id},
                count=BATCH_SIZE,
                block=BLOCK_MS
            )

            if messages:
                # messages 格式: [(stream_name, [(msg_id, msg_data), ...])]
                for stream_name, stream_messages in messages:
                    if stream_messages:
                        logging.info(f"📦 Received batch of {len(stream_messages)} messages")

                        # 處理批次
                        processed = process_batch(stream_messages)
                        total_processed += processed

                        logging.info(f"✅ Processed {processed}/{len(stream_messages)} messages (Total: {total_processed})")

            else:
                # 超時，沒有新消息
                logging.debug(f"No new messages, waiting...")

        except redis.RedisError as e:
            logging.error(f"❌ Redis error: {e}")
            time.sleep(5)  # 錯誤時等待 5 秒後重試

        except KeyboardInterrupt:
            logging.info("⚠️  Worker stopping...")
            break

        except Exception as e:
            logging.error(f"❌ Unexpected error: {e}", exc_info=True)
            time.sleep(5)


if __name__ == "__main__":
    main_loop()
