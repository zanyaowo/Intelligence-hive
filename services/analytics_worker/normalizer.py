import logging
from typing import Dict, Any, Union
from datetime import datetime

class DataNormalizer:
    def __init__(self):
        logging.info("DataNormalizer initialized")

    def normalize_timestamp(self, timestamp: Union[str, int, float]) -> str:
        """標準化時間戳為 ISO 格式"""
        try:
            if isinstance(timestamp, (int, float)):
                dt = datetime.fromtimestamp(timestamp)
            elif isinstance(timestamp, str):
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except ValueError:
                    dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            else:
                dt = datetime.utcnow()
            
            return dt.isoformat()
        except Exception as e:
            logging.warning(f"Error normalizing timestamp {timestamp}: {e}")
            return datetime.utcnow().isoformat()

    def normalize_ip(self, ip: str) -> str:
        """標準化 IP 地址格式"""
        if not ip:
            return ''
        
        # 簡單的 IPv4 驗證和清理
        parts = ip.split('.')
        if len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
            return ip
        
        logging.warning(f"Invalid IP address format: {ip}")
        return ''

    def normalize_http_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """標準化 HTTP 請求數據"""
        normalized = {}
        
        if 'method' in data:
            normalized['http_method'] = str(data['method']).upper()
        
        if 'path' in data:
            normalized['http_path'] = str(data['path'])
        
        if 'headers' in data:
            normalized['http_headers'] = {
                k.lower(): str(v) for k, v in data['headers'].items()
            }
        
        if 'body' in data:
            normalized['http_body'] = str(data['body'])
        
        return normalized

    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """標準化輸入數據"""
        try:
            normalized_data = {}

            # 標準化基本字段
            normalized_data['session_id'] = str(data.get('session_id', ''))
            normalized_data['source_ip'] = self.normalize_ip(str(data.get('source_ip', '')))
            normalized_data['timestamp'] = self.normalize_timestamp(data.get('timestamp', datetime.utcnow()))

            # 標準化 HTTP 數據
            if 'http_request' in data:
                normalized_data.update(self.normalize_http_data(data['http_request']))

            # 標準化攻擊載荷
            if 'payload' in data:
                normalized_data['payload'] = str(data['payload'])

            # 標準化其他元數據
            normalized_data['metadata'] = {
                'honeypot_type': str(data.get('honeypot_type', 'unknown')),
                'sensor_id': str(data.get('sensor_id', '')),
                'normalized_at': datetime.utcnow().isoformat()
            }

            return normalized_data

        except Exception as e:
            logging.error(f"Error in data normalization: {e}")
            raise
