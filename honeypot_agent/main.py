from agent import TannerAgent
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
TANNER_API_URL = "http://localhost:8081"
INGESTION_API_URL = "http://localhost:8082/ingest"
AGENT_RUN_INTERVAL_SECONDS = 60  # Run every 60 seconds

if __name__ == "__main__":
    logging.info("=" * 80)
    logging.info("Starting Honeypot Agent")
    logging.info("=" * 80)
    logging.info(f"Tanner API: {TANNER_API_URL}")
    logging.info(f"Ingestion API: {INGESTION_API_URL}")
    logging.info(f"Collection interval: {AGENT_RUN_INTERVAL_SECONDS} seconds")
    logging.info("=" * 80)

    agent = TannerAgent(
        tanner_api_url=TANNER_API_URL,
        ingestion_api_url=INGESTION_API_URL
    )

    try:
        agent.run_periodically(interval_seconds=AGENT_RUN_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        logging.info("\nHoneypot Agent stopped by user.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
