import logging
from time import sleep
from tasks import process_honeypot_data
from enricher import DataEnricher
from evaluator import ThreatEvaluator
from normalizer import DataNormalizer

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AnalyticsWorker:
    def __init__(self):
        self.enricher = DataEnricher()
        self.evaluator = ThreatEvaluator()
        self.normalizer = DataNormalizer()
        logging.info("Analytics Worker initialized")

    def process_data(self, data):
        try:
            # 1. 標準化數據
            normalized_data = self.normalizer.normalize(data)
            logging.info("Data normalized successfully")

            # 2. 擴充數據
            enriched_data = self.enricher.enrich(normalized_data)
            logging.info("Data enriched successfully")

            # 3. 評估威脅
            evaluation_results = self.evaluator.evaluate(enriched_data)
            logging.info("Threat evaluation completed")

            return evaluation_results

        except Exception as e:
            logging.error(f"Error processing data: {e}")
            raise

    def run(self, interval_seconds=60):
        """持續運行數據處理"""
        logging.info(f"Starting Analytics Worker with {interval_seconds}s interval")
        while True:
            try:
                # 處理蜜罐數據
                process_honeypot_data(self.process_data)
                logging.info("Completed processing cycle")
            except Exception as e:
                logging.error(f"Error in processing cycle: {e}")
            
            sleep(interval_seconds)

if __name__ == "__main__":
    worker = AnalyticsWorker()
    worker.run()