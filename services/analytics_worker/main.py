import os
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

REDIS_HOST = os.getenv("REDIS_HOST", "analytics_redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

logging.info(f"Analytics Worker starting...")
logging.info(f"Redis: {REDIS_HOST}:{REDIS_PORT}")


while True:
    logging.info("Worker running... (placeholder)")
    time.sleep(60)
