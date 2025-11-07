import os
import requests
import time
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TannerAgent:

    def __init__(self, tanner_api_url,  ingestion_api_url, api_key=None):
        """Initialize Tanner Agent.

        Args:
            tanner_api_url: Tanner API URL (e.g., http://localhost:8081)
            ingestion_api_url: Ingestion API URL (e.g., http://localhost:8082/ingest)
            api-key: key for authentication
        """
        self.metrics = {
            'start_time': time.time(),
            'total_runs': 0,
            'sessions_fetched': 0,
            'sessions_duplicated': 0,
            'sessions_sent': 0,
            'errors': 0,
            'last_run_time': None,
            'last_run_duration_seconds': None,
        }
        self.tanner_api_url = tanner_api_url
        self.ingestion_api_url = ingestion_api_url
        self.api_key = api_key
        self.processed_sessions = self._load_processed_sessions()
        logging.info(f"TannerAgent initialized. Tanner API: {tanner_api_url}, Ingestion API: {ingestion_api_url}")

    def fetch_tanner_data(self):
        """Fetch analyzed session data from Tanner API."""
        logging.info("Fetching analyzed sessions from Tanner API...")
        try:
            snares_response = requests.get(f"{self.tanner_api_url}/snares")
            snares_response.raise_for_status()
            snare_ids = snares_response.json().get("response", {}).get("message", [])

            if not snare_ids:
                logging.info("No active snares found.")
                return []

            all_sessions = []
            fetch_count = 0
            duplicate_count = 0

            for snare_id in snare_ids:
                sessions_response = requests.get(f"{self.tanner_api_url}/snare/{snare_id}")
                sessions_response.raise_for_status()
                response_data = sessions_response.json().get("response", {})
                sessions = response_data.get("message", [])

                # Check if message is a string (error message) instead of a list
                if isinstance(sessions, str):
                    logging.warning(f"Skipping snare {snare_id}: {sessions}")
                    continue

                # Ensure sessions is a list
                if not isinstance(sessions, list):
                    logging.warning(f"Unexpected sessions type for snare {snare_id}: {type(sessions)}")
                    continue

                for session in sessions:
                    # Ensure session is a dictionary
                    if not isinstance(session, dict):
                        logging.warning(f"Skipping non-dict session: {type(session)}")
                        continue

                    fetch_count += 1
                    session["snare_id"] = snare_id
                    sess_uuid = session.get("sess_uuid")
                    if sess_uuid and sess_uuid not in self.processed_sessions:
                        all_sessions.append(session)
                        self.processed_sessions.add(sess_uuid)
                    else:
                        duplicate_count += 1

            self.metrics['sessions_fetched'] += fetch_count
            self.metrics['sessions_duplicated'] += duplicate_count

            logging.info(f"Fetched {len(all_sessions)} new sessions from Tanner API.")
            return all_sessions

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching data from Tanner API: {e}")
            raise

    def send_to_ingestion_api(self, data):
        """Send data to Ingestion API."""
        if not data:
            logging.info("No data to send to Ingestion API.")
            return

        logging.info(f"Sending {len(data)} sessions to Ingestion API...")
        try:
            headers = {}

            if self.api_key:
                headers["X-API-KEY"] = self.api_key

            response = requests.post(
                self.ingestion_api_url,
                json=data,
                headers=headers
            )
            response.raise_for_status()
            self.metrics['sessions_sent'] += len(data)
            logging.info(f"Data sent successfully. Response: {response.json()}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending data to Ingestion API: {e}")
            raise
    
    def _load_processed_sessions(self, path="./data/processed_sessions.json"):
        try:
            if os.path.exists(path):
                with open(path, "r") as f:
                    sessions = json.load(f)
                logging.info(f"Loaded {len(sessions)} processed sessions from {path}")
                return set(sessions)
            else:
                logging.info("No existing processed sessions file found. Starting fresh.")
        except Exception as e:
            logging.error(f"Error loading processed sessions: {e}")
            raise

        return set()

    def _save_processed_sessions(self, path="./data/processed_sessions.json"):
        try:
            if not os.path.exists(path):
                os.makedirs(path.rsplit('/', 1)[0], exist_ok=True)
            with open(path, "w") as f:
                json.dump(list(self.processed_sessions), f)
            logging.info(f"Processed sessions saved to {path}")
        except Exception as e:
            logging.error(f"Error saving processed sessions: {e}")
            raise

    def write_metrics(self, path="./data/tanner_agent_metrics.json"):
        """Write current metrics to a JSON file."""
        logging.info(f"Metrics: {self.metrics}")

        if not os.path.exists(path):
            os.makedirs(path.rsplit('/', 1)[0], exist_ok=True)

        with open(path, "w") as f:
            json.dump(self.metrics, f, indent=4)
        logging.info(f"Metrics written to {path}")

    def run_once(self):
        """Fetch sessions from Tanner API and send to Ingestion API."""
        start_time = time.time()
        try:
            sessions = self.fetch_tanner_data()
            if sessions:
                self.send_to_ingestion_api(sessions)
            else:
                logging.info("No new sessions to process.")
        finally:
            duration = time.time() - start_time
            self.metrics['last_run_duration_seconds'] = round(duration, 2)
            self.metrics['last_run_time'] = time.time()
            self.metrics['total_runs'] += 1

    def run_periodically(self, interval_seconds=60):
        """Run data collection periodically.

        Args:
            interval_seconds: Interval in seconds (default: 60)
        """
        logging.info(f"TannerAgent starting periodic run every {interval_seconds} seconds...")
        while True:
            try:
                self.run_once()
            except Exception as e:
                self.metrics['errors'] += 1
                logging.error(f"Error in run_once: {e}", exc_info=True)
            self.write_metrics()
            self._save_processed_sessions()
            time.sleep(interval_seconds)