import logging
import requests
from typing import Dict, Any

class DataEnricher:
    def __init__(self):
        self.ip_info_cache = {}
        logging.info("DataEnricher initialized")

    def enrich_ip_info(self, ip: str) -> Dict[str, Any]:
        """擴充 IP 地址相關信息"""
        if ip in self.ip_info_cache:
            return self.ip_info_cache[ip]

        try:
            response = requests.get(f"https://ipapi.co/{ip}/json/")
            if response.status_code == 200:
                ip_info = response.json()
                self.ip_info_cache[ip] = {
                    'country': ip_info.get('country_name'),
                    'region': ip_info.get('region'),
                    'city': ip_info.get('city'),
                    'org': ip_info.get('org'),
                    'as_number': ip_info.get('asn'),
                    'latitude': ip_info.get('latitude'),
                    'longitude': ip_info.get('longitude')
                }
                return self.ip_info_cache[ip]
        except Exception as e:
            logging.error(f"Error enriching IP info for {ip}: {e}")
        
        return {}

    def enrich_attack_type(self, data: Dict[str, Any]) -> Dict[str, str]:
        """根據攻擊特徵識別攻擊類型"""
        attack_signatures = {
            'sql_injection': ['SELECT', 'UNION', 'INSERT', 'DROP', 'UPDATE'],
            'xss': ['<script>', 'javascript:', 'onerror=', 'onload='],
            'command_injection': [';', '|', '&&', '`', '$(',],
            'path_traversal': ['../', '..\\', '/etc/passwd'],
            'brute_force': ['admin', 'password', 'login']
        }

        detected_attacks = []
        payload = str(data.get('payload', '')).lower()

        for attack_type, signatures in attack_signatures.items():
            if any(sig.lower() in payload for sig in signatures):
                detected_attacks.append(attack_type)

        return {
            'attack_types': detected_attacks,
            'attack_confidence': 'high' if detected_attacks else 'low'
        }

    def enrich(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """擴充數據"""
        try:
            enriched_data = data.copy()

            # 擴充 IP 信息
            if 'source_ip' in data:
                ip_info = self.enrich_ip_info(data['source_ip'])
                enriched_data['ip_info'] = ip_info

            # 擴充攻擊類型信息
            attack_info = self.enrich_attack_type(data)
            enriched_data['attack_info'] = attack_info

            # 添加時間戳
            from datetime import datetime
            enriched_data['enrichment_timestamp'] = datetime.utcnow().isoformat()

            return enriched_data

        except Exception as e:
            logging.error(f"Error in data enrichment: {e}")
            raise
