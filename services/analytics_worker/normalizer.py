"""
資料正規化模組

負責清理、驗證和標準化來自蜜罐的原始資料
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)


def normalize_session(session: Dict[str, Any]) -> Dict[str, Any]:
    """
    正規化單個 session 資料

    功能：
    - 清理和驗證必要欄位
    - 標準化時間戳格式
    - 清理 IP 位址
    - 標準化攻擊類型
    - 補充缺失欄位的預設值

    Args:
        session: 原始 session 資料

    Returns:
        Dict: 正規化後的 session 資料
    """
    normalized = {}

    try:
        # === 1. 必要欄位驗證 ===
        normalized['sess_uuid'] = str(session.get('sess_uuid', 'unknown')).strip()

        # === 2. IP 位址正規化 ===
        normalized['peer_ip'] = normalize_ip(session.get('peer_ip', '0.0.0.0'))
        normalized['peer_port'] = int(session.get('peer_port', 0))

        # === 3. 識別資訊 ===
        normalized['user_agent'] = clean_string(session.get('user_agent', 'unknown'))
        normalized['referer'] = clean_string(session.get('referer', ''))
        normalized['snare_uuid'] = str(session.get('snare_uuid', 'unknown')).strip()
        normalized['snare_id'] = session.get('snare_id', normalized['snare_uuid'])

        # === 4. 時間戳正規化 ===
        normalized['start_time'] = normalize_timestamp(session.get('start_time'))
        normalized['end_time'] = normalize_timestamp(session.get('end_time'))
        normalized['processed_at'] = datetime.utcnow().isoformat()

        # === 5. 攻擊資訊正規化 ===
        normalized['attack_types'] = normalize_attack_types(session.get('attack_types', []))
        normalized['attack_count'] = session.get('attack_count', {})

        # === 6. 地理位置資訊 ===
        location = session.get('location', {})
        if isinstance(location, dict):
            normalized['location'] = {
                'country': clean_string(location.get('country', '')),
                'country_code': clean_string(location.get('country_code', '')).upper(),
                'city': clean_string(location.get('city', '')),
                'zip_code': clean_string(location.get('zip_code', '')),
                'latitude': location.get('latitude'),
                'longitude': location.get('longitude')
            }
        else:
            normalized['location'] = create_empty_location()

        # === 7. 會話統計 ===
        normalized['requests_in_second'] = float(session.get('requests_in_second', 0.0))
        normalized['approx_time_between_requests'] = float(session.get('approx_time_between_requests', 0.0))
        normalized['accepted_paths'] = int(session.get('accepted_paths', 0))
        normalized['errors'] = int(session.get('errors', 0))
        normalized['hidden_links'] = int(session.get('hidden_links', 0))

        # === 8. 行為分類 ===
        normalized['possible_owners'] = session.get('possible_owners', {})

        # === 9. Cookies ===
        normalized['cookies'] = session.get('cookies', {})

        # === 10. 請求路徑正規化 ===
        paths = session.get('paths', [])
        normalized['paths'] = normalize_paths(paths)
        normalized['total_requests'] = len(normalized['paths'])

        # === 11. 計算衍生欄位 ===
        normalized['unique_attack_types'] = len(set(normalized['attack_types']))
        normalized['has_malicious_activity'] = has_malicious_attacks(normalized['attack_types'])

        logger.debug(f"✅ Normalized session {normalized['sess_uuid']}")

        return normalized

    except Exception as e:
        logger.error(f"❌ Error normalizing session: {e}", exc_info=True)
        # 返回帶有錯誤標記的基本資料
        return {
            'sess_uuid': session.get('sess_uuid', 'error'),
            'error': str(e),
            'raw_data': session,
            'processed_at': datetime.utcnow().isoformat()
        }


def normalize_ip(ip: str) -> str:
    """正規化 IP 位址"""
    if not ip or not isinstance(ip, str):
        return '0.0.0.0'

    ip = ip.strip()

    # 驗證 IPv4 格式
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ipv4_pattern, ip):
        # 驗證每個 octet 在 0-255 範圍內
        octets = ip.split('.')
        if all(0 <= int(octet) <= 255 for octet in octets):
            return ip

    # IPv6 簡單驗證
    if ':' in ip:
        return ip  # 保留 IPv6 原樣

    return '0.0.0.0'


def normalize_timestamp(timestamp: Any) -> Optional[str]:
    """正規化時間戳為 ISO 8601 格式"""
    if not timestamp:
        return None

    if isinstance(timestamp, str):
        # 已經是 ISO 格式
        if 'T' in timestamp:
            return timestamp

        # 嘗試解析其他格式
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.isoformat()
        except:
            pass

    if isinstance(timestamp, (int, float)):
        # Unix timestamp
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.isoformat()
        except:
            pass

    return None


def normalize_attack_types(attack_types: Any) -> List[str]:
    """正規化攻擊類型列表"""
    if not attack_types:
        return []

    if isinstance(attack_types, str):
        return [attack_types.lower().strip()]

    if isinstance(attack_types, list):
        return [str(at).lower().strip() for at in attack_types if at]

    return []


def normalize_paths(paths: Any) -> List[Dict[str, Any]]:
    """正規化請求路徑資料"""
    if not paths or not isinstance(paths, list):
        return []

    normalized_paths = []

    for path in paths:
        if not isinstance(path, dict):
            continue

        normalized_path = {
            'path': clean_string(path.get('path', '/')),
            'method': str(path.get('method', 'GET')).upper(),
            'timestamp': normalize_timestamp(path.get('timestamp')),
            'response_status': int(path.get('response_status', 0)),
            'attack_type': str(path.get('attack_type', 'unknown')).lower(),
            'headers': path.get('headers', {}),
            'cookies': path.get('cookies', {}),
            'query_params': path.get('query_params', {}),
            'post_data': path.get('post_data', '')
        }

        normalized_paths.append(normalized_path)

    return normalized_paths


def clean_string(value: Any) -> str:
    """清理字串欄位"""
    if not value:
        return ''

    if not isinstance(value, str):
        value = str(value)

    # 移除前後空白
    value = value.strip()

    # 移除控制字符（保留換行和tab）
    value = ''.join(char for char in value if char.isprintable() or char in '\n\t')

    return value


def create_empty_location() -> Dict[str, Any]:
    """建立空的地理位置物件"""
    return {
        'country': '',
        'country_code': '',
        'city': '',
        'zip_code': '',
        'latitude': None,
        'longitude': None
    }


def has_malicious_attacks(attack_types: List[str]) -> bool:
    """判斷是否包含惡意攻擊"""
    malicious_types = {
        'sqli', 'xss', 'lfi', 'rfi', 'cmd_exec',
        'php_code_injection', 'php_object_injection',
        'template_injection', 'xxe_injection', 'crlf'
    }

    return any(at in malicious_types for at in attack_types)


def validate_session(session: Dict[str, Any]) -> tuple[bool, str]:
    """
    驗證 session 資料完整性

    Returns:
        (is_valid, error_message)
    """
    required_fields = ['sess_uuid', 'peer_ip']

    for field in required_fields:
        if field not in session or not session[field]:
            return False, f"Missing required field: {field}"

    # 驗證 sess_uuid 不是 'unknown' 或 'error'
    if session['sess_uuid'] in ['unknown', 'error', '']:
        return False, "Invalid sess_uuid"

    return True, ""
