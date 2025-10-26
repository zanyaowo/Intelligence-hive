import os
import time
import json
import logging
import redis
from typing import List, Dict, Any, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    processed = 0

    for msg_id, msg_data in messages:
        try:
            # 解析數據
            data_bytes = msg_data.get(b'data', b'{}')
            session = json.loads(data_bytes)

            # TODO: 實際處理邏輯
            # 1. normalize(session)
            # 2. enrich(session)
            # 3. evaluate(session)
            # 4. save_to_db(session)

            # 暫時只記錄
            sess_uuid = session.get('sess_uuid', 'unknown')
            peer_ip = session.get('peer_ip', 'unknown')
            attack_types = session.get('attack_types', [])

            logging.debug(f"Processed session {sess_uuid} from {peer_ip}: {attack_types}")
            processed += 1

            # ACK 消息（標記為已處理）
            redis_client.xack(REDIS_STREAM, CONSUMER_GROUP, msg_id)

        except Exception as e:
            logging.error(f"Error processing message {msg_id}: {e}")
            # 不 ACK 失敗的消息，之後可以重試

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
