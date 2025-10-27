"""
資料豐富化模組

負責為正規化後的資料添加額外的情報和上下文資訊
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import Counter
import re

logger = logging.getLogger(__name__)


def enrich_session(session: Dict[str, Any]) -> Dict[str, Any]:
    """
    豐富化 session 資料

    功能：
    - 添加威脅情報標籤
    - 分析攻擊模式
    - 識別攻擊工具/框架
    - 計算衍生指標
    - 添加行為標籤

    Args:
        session: 正規化後的 session 資料

    Returns:
        Dict: 豐富化後的 session 資料
    """
    try:
        enriched = session.copy()

        # === 1. 威脅情報標籤 ===
        enriched['threat_intelligence'] = generate_threat_labels(session)

        # === 2. 攻擊模式分析 ===
        enriched['attack_patterns'] = analyze_attack_patterns(session)

        # === 3. User Agent 分析 ===
        enriched['user_agent_info'] = analyze_user_agent(session.get('user_agent', ''))

        # === 4. 請求模式分析 ===
        enriched['request_patterns'] = analyze_request_patterns(session)

        # === 5. Payload 分析 ===
        enriched['payload_analysis'] = analyze_payloads(session)

        # === 6. IP 信譽標籤（簡化版，可整合外部 API）===
        enriched['ip_reputation'] = generate_ip_reputation(session.get('peer_ip', ''))

        # === 7. 時間模式分析 ===
        enriched['temporal_patterns'] = analyze_temporal_patterns(session)

        # === 8. 行為標籤 ===
        enriched['behavior_tags'] = generate_behavior_tags(enriched)

        # === 9. 攻擊階段識別 ===
        enriched['attack_phases'] = identify_attack_phases(session)

        logger.debug(f"✅ Enriched session {session.get('sess_uuid', 'unknown')}")

        return enriched

    except Exception as e:
        logger.error(f"❌ Error enriching session: {e}", exc_info=True)
        # 返回原始資料，添加錯誤標記
        session['enrichment_error'] = str(e)
        return session


def generate_threat_labels(session: Dict[str, Any]) -> Dict[str, Any]:
    """生成威脅情報標籤"""
    labels = {
        'severity': 'unknown',
        'confidence': 0.0,
        'attack_categories': [],
        'is_automated': False,
        'is_targeted': False,
        'threat_actor_type': 'unknown'
    }

    attack_types = session.get('attack_types', [])

    # 判斷嚴重性
    critical_attacks = {'cmd_exec', 'rfi', 'php_code_injection', 'php_object_injection'}
    high_attacks = {'sqli', 'xxe_injection', 'template_injection'}
    medium_attacks = {'xss', 'lfi', 'crlf'}

    if any(at in critical_attacks for at in attack_types):
        labels['severity'] = 'critical'
        labels['confidence'] = 0.9
    elif any(at in high_attacks for at in attack_types):
        labels['severity'] = 'high'
        labels['confidence'] = 0.8
    elif any(at in medium_attacks for at in attack_types):
        labels['severity'] = 'medium'
        labels['confidence'] = 0.7
    elif 'index' in attack_types:
        labels['severity'] = 'low'
        labels['confidence'] = 0.5
    else:
        labels['severity'] = 'info'
        labels['confidence'] = 0.3

    # 攻擊分類
    if any(at in {'sqli', 'xss', 'lfi', 'rfi'} for at in attack_types):
        labels['attack_categories'].append('Web Application Attack')

    if any(at in {'cmd_exec', 'php_code_injection'} for at in attack_types):
        labels['attack_categories'].append('Remote Code Execution')

    if any(at in {'xxe_injection', 'template_injection'} for at in attack_types):
        labels['attack_categories'].append('Injection Attack')

    # 判斷是否為自動化攻擊
    requests_per_second = session.get('requests_in_second', 0)
    if requests_per_second > 1.0:
        labels['is_automated'] = True

    return labels


def analyze_attack_patterns(session: Dict[str, Any]) -> Dict[str, Any]:
    """分析攻擊模式"""
    patterns = {
        'attack_sequence': [],
        'repeated_attacks': {},
        'escalation_detected': False,
        'pattern_signature': ''
    }

    attack_types = session.get('attack_types', [])

    # 攻擊序列
    patterns['attack_sequence'] = attack_types

    # 重複攻擊統計
    attack_counts = Counter(attack_types)
    patterns['repeated_attacks'] = dict(attack_counts.most_common(5))

    # 檢測攻擊升級
    severity_order = ['index', 'xss', 'lfi', 'sqli', 'cmd_exec', 'rfi']
    severity_levels = [severity_order.index(at) if at in severity_order else 0 for at in attack_types]

    if len(severity_levels) > 1:
        # 檢查是否有嚴重性遞增的趨勢
        increasing = all(severity_levels[i] <= severity_levels[i+1] for i in range(len(severity_levels)-1))
        if increasing and len(set(severity_levels)) > 1:
            patterns['escalation_detected'] = True

    # 模式簽名（用於聚類分析）
    unique_attacks = sorted(set(attack_types))
    patterns['pattern_signature'] = '-'.join(unique_attacks)

    return patterns


def analyze_user_agent(user_agent: str) -> Dict[str, Any]:
    """分析 User Agent"""
    ua_info = {
        'is_bot': False,
        'is_scanner': False,
        'is_browser': False,
        'tool_identified': None,
        'suspicious': False
    }

    if not user_agent or user_agent == 'unknown':
        ua_info['suspicious'] = True
        return ua_info

    ua_lower = user_agent.lower()

    # 常見掃描工具
    scanners = ['sqlmap', 'nikto', 'nmap', 'masscan', 'nessus', 'acunetix',
                'burp', 'zap', 'metasploit', 'wget', 'curl', 'python-requests',
                'go-http-client', 'scanner']

    for scanner in scanners:
        if scanner in ua_lower:
            ua_info['is_scanner'] = True
            ua_info['tool_identified'] = scanner
            ua_info['suspicious'] = True
            break

    # Bot 識別
    bots = ['bot', 'crawler', 'spider', 'scraper']
    if any(bot in ua_lower for bot in bots):
        ua_info['is_bot'] = True

    # 瀏覽器識別
    browsers = ['firefox', 'chrome', 'safari', 'edge', 'opera']
    if any(browser in ua_lower for browser in browsers):
        ua_info['is_browser'] = True

    # 可疑特徵
    if len(user_agent) < 10 or user_agent == '-':
        ua_info['suspicious'] = True

    return ua_info


def analyze_request_patterns(session: Dict[str, Any]) -> Dict[str, Any]:
    """分析請求模式"""
    patterns = {
        'http_methods': {},
        'status_codes': {},
        'unique_paths': 0,
        'path_diversity': 0.0,
        'has_repeated_paths': False
    }

    paths = session.get('paths', [])

    if not paths:
        return patterns

    # HTTP 方法統計
    methods = [p.get('method', 'GET') for p in paths]
    patterns['http_methods'] = dict(Counter(methods))

    # 狀態碼統計
    status_codes = [p.get('response_status', 0) for p in paths]
    patterns['status_codes'] = dict(Counter(status_codes))

    # 路徑多樣性
    path_strings = [p.get('path', '/') for p in paths]
    unique_paths = set(path_strings)
    patterns['unique_paths'] = len(unique_paths)

    if len(paths) > 0:
        patterns['path_diversity'] = len(unique_paths) / len(paths)

    # 檢測重複路徑
    path_counts = Counter(path_strings)
    patterns['has_repeated_paths'] = any(count > 1 for count in path_counts.values())

    return patterns


def analyze_payloads(session: Dict[str, Any]) -> Dict[str, Any]:
    """
    Payload 統計分析（補充 Tanner 的結果）

    專注於統計特徵，不重複攻擊檢測：
    1. 統計 payload 長度特徵
    2. 檢測編碼方式（URL編碼、Base64、Hex等）
    3. 評估 payload 複雜度
    """
    analysis = {
        'total_payload_length': 0,
        'longest_payload': 0,
        'avg_payload_length': 0,
        'has_encoded_content': False,
        'encoding_detected': [],
        'payload_complexity': 'low'
    }

    paths = session.get('paths', [])

    if not paths:
        return analysis

    # 收集所有 payload 內容
    payloads = []
    for path in paths:
        if not isinstance(path, dict):
            continue

        # 路徑本身
        path_str = path.get('path', '')
        payloads.append(path_str)

        # POST 資料
        post_data = path.get('post_data', '')
        if post_data:
            payloads.append(str(post_data))

        # Query 參數
        query_params = path.get('query_params', {})
        if query_params:
            payloads.extend(str(v) for v in query_params.values())

    if not payloads:
        return analysis

    # === 1. 長度統計 ===
    payload_lengths = [len(p) for p in payloads]
    analysis['total_payload_length'] = sum(payload_lengths)
    analysis['longest_payload'] = max(payload_lengths)
    analysis['avg_payload_length'] = analysis['total_payload_length'] / len(payloads)

    # === 2. 編碼檢測 ===
    combined = ' '.join(payloads).lower()

    # URL 編碼
    if re.search(r'%[0-9a-f]{2}', combined):
        analysis['encoding_detected'].append('url_encoded')

    # Base64 模式
    if re.search(r'[A-Za-z0-9+/]{20,}={0,2}', combined):
        analysis['encoding_detected'].append('base64_pattern')

    # Hex 編碼
    if re.search(r'(0x[0-9a-f]+|\\x[0-9a-f]{2})', combined):
        analysis['encoding_detected'].append('hex_encoded')

    # HTML entities
    if re.search(r'&#?[a-z0-9]+;', combined):
        analysis['encoding_detected'].append('html_entities')

    # Unicode 轉義
    if re.search(r'\\u[0-9a-f]{4}', combined):
        analysis['encoding_detected'].append('unicode_escaped')

    analysis['has_encoded_content'] = len(analysis['encoding_detected']) > 0

    # === 3. 複雜度評估 ===
    complexity_score = 0

    # 長度因素
    if analysis['longest_payload'] > 500:
        complexity_score += 2
    elif analysis['longest_payload'] > 200:
        complexity_score += 1

    # 編碼因素
    complexity_score += len(analysis['encoding_detected'])

    # 特殊字符密度
    special_chars = len(re.findall(r'[^a-zA-Z0-9\s]', combined))
    if len(combined) > 0 and special_chars > len(combined) * 0.3:
        complexity_score += 2

    # 評級
    if complexity_score >= 5:
        analysis['payload_complexity'] = 'high'
    elif complexity_score >= 2:
        analysis['payload_complexity'] = 'medium'
    else:
        analysis['payload_complexity'] = 'low'

    return analysis


def generate_ip_reputation(ip: str) -> Dict[str, Any]:
    """
    生成 IP 信譽資訊（簡化版）

    未來可整合：
    - AbuseIPDB
    - VirusTotal
    - Shodan
    - MaxMind GeoIP2
    """
    reputation = {
        'is_private': False,
        'is_tor': False,
        'is_vpn': False,
        'is_cloud': False,
        'reputation_score': 0.5,  # 0.0 (bad) to 1.0 (good)
        'notes': []
    }

    if not ip or ip == '0.0.0.0':
        return reputation

    # 檢查私有 IP
    private_ranges = [
        '10.', '172.16.', '172.17.', '172.18.', '172.19.',
        '172.20.', '172.21.', '172.22.', '172.23.', '172.24.',
        '172.25.', '172.26.', '172.27.', '172.28.', '172.29.',
        '172.30.', '172.31.', '192.168.', '127.'
    ]

    if any(ip.startswith(prefix) for prefix in private_ranges):
        reputation['is_private'] = True
        reputation['notes'].append('Private IP address')

    # 雲端服務 IP 範圍（簡化檢測）
    cloud_patterns = ['amazonaws', 'googlecloud', 'azure', 'digitalocean']
    # 實際應檢查 IP 範圍，這裡只是示意

    return reputation


def analyze_temporal_patterns(session: Dict[str, Any]) -> Dict[str, Any]:
    """分析時間模式"""
    patterns = {
        'duration_seconds': 0.0,
        'request_rate': 0.0,
        'time_of_day': None,
        'is_prolonged': False
    }

    start_time = session.get('start_time')
    end_time = session.get('end_time')

    if start_time and end_time:
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            duration = (end_dt - start_dt).total_seconds()
            patterns['duration_seconds'] = duration

            # 判斷是否為長時間會話
            if duration > 300:  # 5 分鐘
                patterns['is_prolonged'] = True

            # 時段分類
            hour = start_dt.hour
            if 6 <= hour < 12:
                patterns['time_of_day'] = 'morning'
            elif 12 <= hour < 18:
                patterns['time_of_day'] = 'afternoon'
            elif 18 <= hour < 24:
                patterns['time_of_day'] = 'evening'
            else:
                patterns['time_of_day'] = 'night'

        except:
            pass

    # 請求速率
    patterns['request_rate'] = session.get('requests_in_second', 0.0)

    return patterns


def generate_behavior_tags(session: Dict[str, Any]) -> List[str]:
    """生成行為標籤"""
    tags = []

    # 從各種分析結果生成標籤
    threat_info = session.get('threat_intelligence', {})
    ua_info = session.get('user_agent_info', {})
    attack_patterns = session.get('attack_patterns', {})
    payload_analysis = session.get('payload_analysis', {})

    # 嚴重性標籤
    severity = threat_info.get('severity', 'unknown')
    if severity in ['critical', 'high']:
        tags.append(f'severity:{severity}')

    # 自動化攻擊
    if threat_info.get('is_automated', False):
        tags.append('automated_attack')

    # 掃描工具
    if ua_info.get('is_scanner', False):
        tags.append('scanner_detected')
        tool = ua_info.get('tool_identified')
        if tool:
            tags.append(f'tool:{tool}')

    # 攻擊升級
    if attack_patterns.get('escalation_detected', False):
        tags.append('attack_escalation')

    # Payload 特徵
    if payload_analysis.get('has_sql_keywords', False):
        tags.append('sql_injection_attempt')

    if payload_analysis.get('has_xss_patterns', False):
        tags.append('xss_attempt')

    if payload_analysis.get('has_command_injection', False):
        tags.append('command_injection_attempt')

    if payload_analysis.get('has_path_traversal', False):
        tags.append('path_traversal_attempt')

    # 惡意活動
    if session.get('has_malicious_activity', False):
        tags.append('malicious_activity')

    # 多樣性攻擊
    unique_attacks = session.get('unique_attack_types', 0)
    if unique_attacks >= 3:
        tags.append('diverse_attacks')

    return tags


def identify_attack_phases(session: Dict[str, Any]) -> List[str]:
    """
    識別攻擊階段（基於 Cyber Kill Chain）

    階段：
    1. Reconnaissance (偵察)
    2. Scanning (掃描)
    3. Exploitation (利用)
    4. Persistence (持久化)
    5. Exfiltration (滲透)
    """
    phases = []

    attack_types = session.get('attack_types', [])
    paths = session.get('paths', [])

    # Reconnaissance - 只有 index 訪問
    if attack_types == ['index'] or all(at == 'index' for at in attack_types):
        phases.append('reconnaissance')

    # Scanning - 多路徑探測
    if len(paths) > 5:
        phases.append('scanning')

    # Exploitation - 有攻擊嘗試
    exploit_attacks = {'sqli', 'xss', 'lfi', 'rfi', 'cmd_exec', 'xxe_injection'}
    if any(at in exploit_attacks for at in attack_types):
        phases.append('exploitation')

    # 如果有 RCE 嘗試，可能進入 Persistence 階段
    if any(at in {'cmd_exec', 'rfi', 'php_code_injection'} for at in attack_types):
        phases.append('persistence_attempt')

    return phases if phases else ['unknown']