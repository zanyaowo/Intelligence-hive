import json
import time
import uuid
import yarl
from urllib.parse import urlparse

from tanner.config import TannerConfig
from tanner.utils import aiodocker_helper
from tanner.utils.mysql_db_helper import MySQLDBHelper
from tanner.utils.sqlite_db_helper import SQLITEDBHelper


class Session:
    KEEP_ALIVE_TIME = 300

    def __init__(self, data):
        try:
            self.ip = data["peer"]["ip"]
            self.port = data["peer"]["port"]
            self.user_agent = data["headers"]["user-agent"]
            self.snare_uuid = data["uuid"]

            # Normalize path to match how server.py normalizes it
            normalized_path = yarl.URL(data["path"]).human_repr()

            path_entry = {
                "path": normalized_path,
                "timestamp": time.time(),
                "response_status": data["status"],
                "method": data.get("method", "GET"),
                "headers": dict(data.get("headers", {})),
                "cookies": dict(data.get("cookies", {})),
            }

            if data.get("method") in ["POST", "PUT", "PATCH"]:
                path_entry["post_data"] = data.get("post_data", "")

            if "?" in data["path"]:
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(data["path"])
                path_entry["query_params"] = parse_qs(parsed.query)

            self.paths = [path_entry]
            self.referer = None
            if "referer" in data["headers"]:
                ref = urlparse(data["headers"]["referer"])
                self.referer = ref.path
            self.cookies = data["cookies"]
            self.associated_db = None
            self.associated_env = None
        except KeyError:
            raise

        self.sess_uuid = uuid.uuid4()
        self.start_timestamp = time.time()
        self.timestamp = time.time()
        self.count = 1

    def update_session(self, data):
        self.timestamp = time.time()
        self.count += 1

        # Normalize path to match how server.py normalizes it
        normalized_path = yarl.URL(data["path"]).human_repr()

        path_entry = {
            "path": normalized_path,
            "timestamp": time.time(),
            "response_status": data["status"],
            "method": data.get("method", "GET"),
            "headers": dict(data.get("headers", {})),
            "cookies": dict(data.get("cookies", {})),
        }

        if data.get("method") in ["POST", "PUT", "PATCH"]:
            path_entry["post_data"] = data.get("post_data", "")

        if "?" in data["path"]:
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(data["path"])
            path_entry["query_params"] = parse_qs(parsed.query)

        self.paths.append(path_entry)

        for (key, value) in data["cookies"].items():
            self.cookies.update({key: value})

    def is_expired(self):
        exp_time = self.timestamp + self.KEEP_ALIVE_TIME
        time_diff = time.time() - exp_time
        if time_diff > 0:
            return True
        return False

    def to_json(self):
        sess = dict(
            peer=dict(ip=self.ip, port=self.port),
            user_agent=self.user_agent,
            snare_uuid=self.snare_uuid,
            sess_uuid=self.sess_uuid.hex,
            start_time=self.start_timestamp,
            end_time=self.timestamp,
            count=self.count,
            paths=self.paths,
            cookies=self.cookies,
            referer=self.referer,
        )
        return json.dumps(sess)

    def set_attack_type(self, path, attack_type):
        for sess_path in self.paths:
            if sess_path["path"] == path:
                sess_path.update({"attack_type": attack_type})

    def associate_db(self, db_name):
        self.associated_db = db_name

    async def remove_associated_db(self):
        if TannerConfig.get("SQLI", "type") == "MySQL":
            await MySQLDBHelper().delete_db(self.associated_db)
        else:
            SQLITEDBHelper().delete_db(self.associated_db)

    def associate_env(self, env):
        self.associated_env = env

    async def remove_associated_env(self):
        await aiodocker_helper.AIODockerHelper().delete_container(self.associated_env)

    def get_uuid(self):
        return str(self.sess_uuid)
