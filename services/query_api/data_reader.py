"""
資料讀取模組

從檔案系統讀取已處理的蜜罐資料
"""

import json
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# 資料目錄（與 analytics_worker 共享）
DATA_DIR = os.getenv("DATA_DIR", "/app/data")


def read_jsonl_file(file_path: Path) -> List[Dict[str, Any]]:
    """讀取 JSONL 檔案"""
    sessions = []

    if not file_path.exists():
        return sessions

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    sessions.append(json.loads(line))
        return sessions
    except Exception as e:
        logger.error(f"Error reading JSONL file {file_path}: {e}")
        return []


def get_sessions(
    date: str,
    threat_level: Optional[str] = None,
    attack_type: Optional[str] = None,
    min_risk: Optional[int] = None,
    peer_ip: Optional[str] = None,
    sess_uuid: Optional[str] = None,
    requires_review: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0,
    sort_by: str = "processed_at",
    order: str = "desc"
) -> Dict[str, Any]:
    """
    獲取會話列表（支援過濾、分頁、排序）
    """
    # 讀取檔案
    file_path = Path(DATA_DIR) / "processed" / date / "sessions.jsonl"
    all_sessions = read_jsonl_file(file_path)

    # 過濾
    filtered_sessions = []
    for session in all_sessions:
        # 威脅等級過濾
        if threat_level and session.get('threat_level') != threat_level:
            continue

        # 攻擊類型過濾
        if attack_type:
            session_attacks = session.get('attack_types', [])
            if attack_type not in session_attacks:
                continue

        # 最小風險分數過濾
        if min_risk is not None:
            if session.get('risk_score', 0) < min_risk:
                continue

        # 來源 IP 過濾 (支援部分匹配)
        if peer_ip:
            session_ip = session.get('peer_ip', '')
            if peer_ip.lower() not in session_ip.lower():
                continue

        # 會話 UUID 過濾 (支援部分匹配)
        if sess_uuid:
            session_uuid = session.get('sess_uuid', '')
            if sess_uuid.lower() not in session_uuid.lower():
                continue

        # 需要人工審查過濾
        if requires_review is not None:
            if session.get('requires_review', False) != requires_review:
                continue

        filtered_sessions.append(session)

    # 排序
    reverse = (order == "desc")

    if sort_by == "risk_score":
        filtered_sessions.sort(
            key=lambda x: x.get('risk_score', 0),
            reverse=reverse
        )
    elif sort_by == "processed_at":
        filtered_sessions.sort(
            key=lambda x: x.get('processed_at', ''),
            reverse=reverse
        )

    # 分頁
    total = len(filtered_sessions)
    paginated_sessions = filtered_sessions[offset:offset + limit]

    # 轉換為摘要格式
    session_summaries = []
    for session in paginated_sessions:
        ua_info = session.get('user_agent_info', {})

        summary = {
            "sess_uuid": session.get('sess_uuid'),
            "peer_ip": session.get('peer_ip'),
            "peer_port": session.get('peer_port'),
            "user_agent": session.get('user_agent'),
            "attack_types": session.get('attack_types', []),
            "risk_score": session.get('risk_score'),
            "threat_level": session.get('threat_level'),
            "alert_level": session.get('alert_level'),
            "processed_at": session.get('processed_at'),
            "total_requests": session.get('total_requests'),
            "has_malicious_activity": session.get('has_malicious_activity'),
            "is_scanner": ua_info.get('is_scanner'),
            "tool_identified": ua_info.get('tool_identified')
        }
        session_summaries.append(summary)

    return {
        "sessions": session_summaries,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total
    }


def get_session_by_uuid(uuid: str, max_days: int = 30) -> Optional[Dict[str, Any]]:
    """
    根據 UUID 獲取完整會話資料

    會在最近 max_days 天的資料中搜尋，如果找不到則搜尋所有可用日期
    """
    # 先搜尋最近幾天的資料（快速路徑）
    for i in range(max_days):
        date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        file_path = Path(DATA_DIR) / "processed" / date / "sessions.jsonl"

        if not file_path.exists():
            continue

        sessions = read_jsonl_file(file_path)

        for session in sessions:
            if session.get('sess_uuid') == uuid:
                return session

    # 如果最近 max_days 天找不到，搜尋所有可用日期（慢速路徑）
    available_dates = get_available_dates()
    for date in available_dates:
        # 跳過已經搜尋過的日期
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            days_ago = (datetime.utcnow() - date_obj).days
            if days_ago < max_days:
                continue  # 已經在快速路徑搜尋過了
        except ValueError:
            continue

        file_path = Path(DATA_DIR) / "processed" / date / "sessions.jsonl"
        sessions = read_jsonl_file(file_path)

        for session in sessions:
            if session.get('sess_uuid') == uuid:
                return session

    return None


def get_alerts(
    date: str,
    alert_level: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """獲取警報列表"""
    # 確定檔案路徑
    alerts_dir = Path(DATA_DIR) / "alerts" / date

    all_alerts = []

    # 讀取不同等級的警報檔案
    if alert_level:
        # 只讀取特定等級
        file_path = alerts_dir / f"{alert_level.lower()}_alerts.jsonl"
        all_alerts = read_jsonl_file(file_path)
    else:
        # 讀取所有警報
        for level in ['critical', 'high']:
            file_path = alerts_dir / f"{level}_alerts.jsonl"
            all_alerts.extend(read_jsonl_file(file_path))

    # 排序（按風險分數降序）
    all_alerts.sort(key=lambda x: x.get('risk_score', 0), reverse=True)

    # 分頁
    total = len(all_alerts)
    paginated_alerts = all_alerts[offset:offset + limit]

    # 轉換為摘要格式
    alert_summaries = []
    for alert in paginated_alerts:
        ua_info = alert.get('user_agent_info', {})

        summary = {
            "sess_uuid": alert.get('sess_uuid'),
            "peer_ip": alert.get('peer_ip'),
            "alert_level": alert.get('alert_level'),
            "threat_level": alert.get('threat_level'),
            "risk_score": alert.get('risk_score'),
            "attack_types": list(set(alert.get('attack_types', []))),  # 去重
            "tool_identified": ua_info.get('tool_identified'),
            "processed_at": alert.get('processed_at'),
            "recommendations_count": len(alert.get('recommendations', []))
        }
        alert_summaries.append(summary)

    return {
        "alerts": alert_summaries,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total
    }


def get_statistics(date: str, days: int = 1) -> Dict[str, Any]:
    """
    獲取統計資料

    如果 days > 1，會聚合多天的統計
    """
    if days == 1:
        # 單日統計
        stats_file = Path(DATA_DIR) / "statistics" / date / "summary.json"

        if stats_file.exists():
            with open(stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return generate_empty_stats(date)
    else:
        # 多日統計聚合
        aggregated_stats = None

        for i in range(days):
            current_date = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=i)).strftime("%Y-%m-%d")
            stats_file = Path(DATA_DIR) / "statistics" / current_date / "summary.json"

            if stats_file.exists():
                with open(stats_file, 'r', encoding='utf-8') as f:
                    day_stats = json.load(f)

                if aggregated_stats is None:
                    aggregated_stats = day_stats
                else:
                    # 聚合統計
                    aggregated_stats = merge_statistics(aggregated_stats, day_stats)

        return aggregated_stats or generate_empty_stats(date)


def merge_statistics(stats1: Dict, stats2: Dict) -> Dict:
    """合併兩個統計資料"""
    merged = stats1.copy()

    # 合併數字
    merged['total_sessions'] = stats1['total_sessions'] + stats2['total_sessions']

    # 合併分布（字典相加）
    for key in ['attack_type_distribution', 'threat_level_distribution', 'top_source_ips', 'top_user_agents']:
        if key in stats2:
            for k, v in stats2[key].items():
                merged[key][k] = merged[key].get(k, 0) + v

    # 重新計算平均風險分數
    total1 = stats1['total_sessions']
    total2 = stats2['total_sessions']
    avg1 = stats1.get('average_risk_score', 0)
    avg2 = stats2.get('average_risk_score', 0)

    merged['average_risk_score'] = (avg1 * total1 + avg2 * total2) / (total1 + total2) if (total1 + total2) > 0 else 0

    return merged


def generate_empty_stats(date: str) -> Dict[str, Any]:
    """生成空的統計資料"""
    return {
        "date": date,
        "total_sessions": 0,
        "attack_type_distribution": {},
        "threat_level_distribution": {},
        "risk_score_distribution": {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0
        },
        "top_source_ips": {},
        "top_user_agents": {},
        "alert_counts": {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
            "INFO": 0
        },
        "average_risk_score": 0.0,
        "requires_review_count": 0
    }


def get_dashboard_data(date: str = None) -> Dict[str, Any]:
    """獲取儀表板資料"""
    if not date:
        date = datetime.utcnow().strftime("%Y-%m-%d")

    # 獲取指定日期的統計
    stats = get_statistics(date=date)

    # 獲取最近的高風險警報
    alerts_result = get_alerts(date=date, alert_level=None, limit=10, offset=0)

    # 讀取所有會話詳細數據以計算新指標
    file_path = Path(DATA_DIR) / "processed" / date / "sessions.jsonl"
    all_sessions = read_jsonl_file(file_path)

    # 計算唯一 IP
    unique_ips = len(set(s.get('peer_ip') for s in all_sessions if s.get('peer_ip')))

    # 1. 攻擊工具統計
    tool_stats = {}
    for session in all_sessions:
        # tool_identified 在 user_agent_info 裡面
        ua_info = session.get('user_agent_info', {})
        tool = ua_info.get('tool_identified') or 'Unknown'
        tool_stats[tool] = tool_stats.get(tool, 0) + 1

    # 2. 掃描器 vs 手動攻擊
    scanner_count = sum(1 for s in all_sessions if s.get('user_agent_info', {}).get('is_scanner'))
    manual_count = len(all_sessions) - scanner_count

    # 3. 每小時攻擊趨勢
    hourly_trend = {}
    for session in all_sessions:
        processed_time = session.get('processed_at', '')
        if processed_time:
            try:
                hour = datetime.fromisoformat(processed_time.replace('Z', '+00:00')).hour
                hour_label = f"{hour:02d}:00"
                hourly_trend[hour_label] = hourly_trend.get(hour_label, 0) + 1
            except:
                pass
    # 確保所有小時都有數據（0-23）
    for h in range(24):
        hour_label = f"{h:02d}:00"
        if hour_label not in hourly_trend:
            hourly_trend[hour_label] = 0

    # 4. Top 攻擊路徑
    path_stats = {}
    for session in all_sessions:
        for path_obj in session.get('paths', []):
            path = path_obj.get('path', '')
            if path:
                # 簡化路徑（移除查詢參數以便分組）
                base_path = path.split('?')[0]
                path_stats[base_path] = path_stats.get(base_path, 0) + 1

    # 5. HTTP 方法分布
    method_stats = {}
    for session in all_sessions:
        for path_obj in session.get('paths', []):
            method = path_obj.get('method', 'GET')
            method_stats[method] = method_stats.get(method, 0) + 1

    # 6. 平均會話持續時間
    durations = []
    for session in all_sessions:
        start = session.get('start_time')
        end = session.get('end_time')
        if start and end:
            try:
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                duration = (end_dt - start_dt).total_seconds()
                durations.append(duration)
            except:
                pass

    avg_duration = sum(durations) / len(durations) if durations else 0

    # TOP 威脅
    top_threats = {
        "top_ips": dict(list(stats.get('top_source_ips', {}).items())[:5]),
        "top_attacks": dict(list(stats.get('attack_type_distribution', {}).items())[:5]),
        "top_tools": dict(sorted(tool_stats.items(), key=lambda x: x[1], reverse=True)[:5]),
        "top_paths": dict(sorted(path_stats.items(), key=lambda x: x[1], reverse=True)[:10])
    }

    # 今日摘要（擴充）
    today_summary = {
        "total_sessions": stats['total_sessions'],
        "high_risk_count": stats['threat_level_distribution'].get('HIGH', 0) + stats['threat_level_distribution'].get('CRITICAL', 0),
        "critical_alerts": stats['alert_counts'].get('CRITICAL', 0),
        "average_risk": round(stats['average_risk_score'], 1),
        "unique_ips": unique_ips,
        "scanner_count": scanner_count,
        "manual_count": manual_count,
        "avg_session_duration": round(avg_duration, 2)
    }

    return {
        "today_summary": today_summary,
        "recent_alerts": alerts_result['alerts'][:10],
        "hourly_trend": dict(sorted(hourly_trend.items())),
        "top_threats": top_threats,
        "attack_analysis": {
            "tool_distribution": tool_stats,
            "scanner_vs_manual": {
                "scanner": scanner_count,
                "manual": manual_count
            },
            "method_distribution": method_stats
        }
    }


def get_threat_intelligence(date: str) -> Dict[str, Any]:
    """獲取威脅情報 Feed"""
    intel_file = Path(DATA_DIR) / "threat_intelligence" / date / "threat_intelligence.json"

    if intel_file.exists():
        with open(intel_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {
            "date": date,
            "malicious_ips": [],
            "malicious_ips_count": 0,
            "attack_signatures": [],
            "attack_signatures_count": 0,
            "malicious_user_agents": [],
            "sample_payloads": []
        }


def get_geo_distribution(date: str, days: int = 1) -> Dict[str, Any]:
    """
    獲取地理分布統計

    返回按國家聚合的攻擊數據
    """
    country_stats = {}

    for i in range(days):
        current_date = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=i)).strftime("%Y-%m-%d")
        file_path = Path(DATA_DIR) / "processed" / current_date / "sessions.jsonl"
        sessions = read_jsonl_file(file_path)

        for session in sessions:
            location = session.get('location', {})
            country_code = location.get('country_code', '').upper()
            country_name = location.get('country', 'Unknown')

            # 跳過空值或私有IP
            if not country_code or country_code == '':
                continue

            if country_code not in country_stats:
                country_stats[country_code] = {
                    'country_code': country_code,
                    'country_name': country_name,
                    'attack_count': 0,
                    'high_risk_count': 0,
                    'total_risk_score': 0,
                    'attack_types': {},
                    'unique_ips': set()
                }

            country_stats[country_code]['attack_count'] += 1
            country_stats[country_code]['total_risk_score'] += session.get('risk_score', 0)
            country_stats[country_code]['unique_ips'].add(session.get('peer_ip'))

            # 統計高風險攻擊
            if session.get('risk_score', 0) >= 70:
                country_stats[country_code]['high_risk_count'] += 1

            # 統計攻擊類型
            for attack_type in session.get('attack_types', []):
                country_stats[country_code]['attack_types'][attack_type] = \
                    country_stats[country_code]['attack_types'].get(attack_type, 0) + 1

    # 轉換為列表並計算平均風險分數
    geo_data = []
    for country_code, stats in country_stats.items():
        avg_risk = stats['total_risk_score'] / stats['attack_count'] if stats['attack_count'] > 0 else 0

        geo_data.append({
            'country_code': stats['country_code'],
            'country_name': stats['country_name'],
            'attack_count': stats['attack_count'],
            'high_risk_count': stats['high_risk_count'],
            'average_risk_score': round(avg_risk, 2),
            'unique_ip_count': len(stats['unique_ips']),
            'top_attack_types': dict(sorted(
                stats['attack_types'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3])  # Top 3 攻擊類型
        })

    # 按攻擊數量排序
    geo_data.sort(key=lambda x: x['attack_count'], reverse=True)

    return {
        'date_range': f"{(datetime.strptime(date, '%Y-%m-%d') - timedelta(days=days-1)).strftime('%Y-%m-%d')} to {date}" if days > 1 else date,
        'total_countries': len(geo_data),
        'countries': geo_data
    }


def get_available_dates() -> List[str]:
    """獲取有資料的日期列表"""
    dates = set()

    base_dir = Path(DATA_DIR)

    # 從 processed 目錄獲取日期
    processed_dir = base_dir / "processed"
    if processed_dir.exists():
        for date_dir in processed_dir.iterdir():
            if date_dir.is_dir():
                try:
                    # 驗證是否為日期格式
                    datetime.strptime(date_dir.name, "%Y-%m-%d")
                    dates.add(date_dir.name)
                except ValueError:
                    continue

    # 排序返回
    return sorted(list(dates), reverse=True)
