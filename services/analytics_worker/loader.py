"""
資料持久化模組

負責將處理後的資料保存到檔案系統或資料庫
"""

import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# 配置
DATA_DIR = os.getenv("DATA_DIR", "/app/data")
OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "jsonl")  # jsonl, json, or database
BATCH_WRITE = os.getenv("BATCH_WRITE", "false").lower() == "true"


def save_session(session: Dict[str, Any]) -> bool:
    """
    保存單個 session 資料

    Args:
        session: 完整處理後的 session 資料

    Returns:
        bool: 是否成功保存
    """
    try:
        if OUTPUT_FORMAT == "jsonl":
            return save_to_jsonl(session)
        elif OUTPUT_FORMAT == "json":
            return save_to_json(session)
        elif OUTPUT_FORMAT == "database":
            return save_to_database(session)
        else:
            logger.warning(f"Unknown output format: {OUTPUT_FORMAT}, defaulting to JSONL")
            return save_to_jsonl(session)

    except Exception as e:
        logger.error(f"❌ Error saving session {session.get('sess_uuid', 'unknown')}: {e}", exc_info=True)
        return False


def save_to_jsonl(session: Dict[str, Any]) -> bool:
    """
    保存為 JSONL 格式（每行一個 JSON 物件）

    檔案組織：
    - data/processed/YYYY-MM-DD/sessions.jsonl
    - data/alerts/YYYY-MM-DD/high_risk.jsonl (高風險警報)
    """
    try:
        # 建立目錄結構
        today = datetime.utcnow().strftime("%Y-%m-%d")
        processed_dir = Path(DATA_DIR) / "processed" / today
        processed_dir.mkdir(parents=True, exist_ok=True)

        # 主檔案：所有 session
        main_file = processed_dir / "sessions.jsonl"

        with open(main_file, "a", encoding="utf-8") as f:
            json.dump(session, f, ensure_ascii=False)
            f.write("\n")

        # 如果是高風險，額外保存到警報檔案
        alert_level = session.get('alert_level', 'INFO')
        if alert_level in ['CRITICAL', 'HIGH']:
            alerts_dir = Path(DATA_DIR) / "alerts" / today
            alerts_dir.mkdir(parents=True, exist_ok=True)

            alert_file = alerts_dir / f"{alert_level.lower()}_alerts.jsonl"

            with open(alert_file, "a", encoding="utf-8") as f:
                json.dump(session, f, ensure_ascii=False)
                f.write("\n")

        logger.debug(f"✅ Saved session {session.get('sess_uuid', 'unknown')} to JSONL")
        return True

    except Exception as e:
        logger.error(f"❌ Error saving to JSONL: {e}", exc_info=True)
        return False


def save_to_json(session: Dict[str, Any]) -> bool:
    """
    保存為獨立 JSON 檔案

    檔案組織：
    - data/processed/YYYY-MM-DD/{sess_uuid}.json
    """
    try:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        processed_dir = Path(DATA_DIR) / "processed" / today
        processed_dir.mkdir(parents=True, exist_ok=True)

        sess_uuid = session.get('sess_uuid', 'unknown')
        filename = processed_dir / f"{sess_uuid}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(session, f, ensure_ascii=False, indent=2)

        logger.debug(f"✅ Saved session {sess_uuid} to JSON")
        return True

    except Exception as e:
        logger.error(f"❌ Error saving to JSON: {e}", exc_info=True)
        return False


def save_to_database(session: Dict[str, Any]) -> bool:
    """
    保存到資料庫（PostgreSQL/MongoDB/Elasticsearch）

    這是一個占位實作，實際使用時需要配置資料庫連接

    未來實作：
    - PostgreSQL: 關聯式資料庫，適合結構化查詢
    - MongoDB: 文件資料庫，適合靈活的 schema
    - Elasticsearch: 搜尋引擎，適合全文搜尋和分析
    """
    try:
        # TODO: 實作資料庫保存邏輯
        # 範例：
        # import psycopg2
        # conn = psycopg2.connect(DATABASE_URL)
        # cursor = conn.cursor()
        # cursor.execute("INSERT INTO sessions (...) VALUES (...)")
        # conn.commit()

        logger.warning("Database storage not implemented yet, falling back to JSONL")
        return save_to_jsonl(session)

    except Exception as e:
        logger.error(f"❌ Error saving to database: {e}", exc_info=True)
        return False


def save_statistics(sessions: List[Dict[str, Any]]) -> bool:
    """
    保存統計摘要

    生成每日統計報告：
    - 總 session 數
    - 攻擊類型分布
    - 風險等級分布
    - TOP 攻擊來源 IP
    - 威脅趨勢
    """
    try:
        if not sessions:
            return True

        today = datetime.utcnow().strftime("%Y-%m-%d")
        stats_dir = Path(DATA_DIR) / "statistics" / today
        stats_dir.mkdir(parents=True, exist_ok=True)

        # 計算統計數據
        stats = {
            'date': today,
            'total_sessions': len(sessions),
            'attack_type_distribution': {},
            'threat_level_distribution': {},
            'risk_score_distribution': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'info': 0
            },
            'top_source_ips': {},
            'top_user_agents': {},
            'alert_counts': {
                'CRITICAL': 0,
                'HIGH': 0,
                'MEDIUM': 0,
                'LOW': 0,
                'INFO': 0
            },
            'average_risk_score': 0.0,
            'requires_review_count': 0
        }

        total_risk = 0

        for session in sessions:
            # 攻擊類型
            for attack_type in session.get('attack_types', []):
                stats['attack_type_distribution'][attack_type] = \
                    stats['attack_type_distribution'].get(attack_type, 0) + 1

            # 威脅等級
            threat_level = session.get('threat_level', 'INFO')
            stats['threat_level_distribution'][threat_level] = \
                stats['threat_level_distribution'].get(threat_level, 0) + 1

            # 風險分數
            risk_score = session.get('risk_score', 0)
            total_risk += risk_score

            if risk_score >= 70:
                stats['risk_score_distribution']['critical'] += 1
            elif risk_score >= 50:
                stats['risk_score_distribution']['high'] += 1
            elif risk_score >= 30:
                stats['risk_score_distribution']['medium'] += 1
            elif risk_score >= 15:
                stats['risk_score_distribution']['low'] += 1
            else:
                stats['risk_score_distribution']['info'] += 1

            # 來源 IP
            peer_ip = session.get('peer_ip', 'unknown')
            stats['top_source_ips'][peer_ip] = \
                stats['top_source_ips'].get(peer_ip, 0) + 1

            # User Agent
            user_agent = session.get('user_agent', 'unknown')
            stats['top_user_agents'][user_agent] = \
                stats['top_user_agents'].get(user_agent, 0) + 1

            # 警報等級
            alert_level = session.get('alert_level', 'INFO')
            stats['alert_counts'][alert_level] = \
                stats['alert_counts'].get(alert_level, 0) + 1

            # 需要審查
            if session.get('requires_review', False):
                stats['requires_review_count'] += 1

        # 平均風險分數
        stats['average_risk_score'] = round(total_risk / len(sessions), 2)

        # 排序 TOP 10
        stats['top_source_ips'] = dict(sorted(
            stats['top_source_ips'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10])

        stats['top_user_agents'] = dict(sorted(
            stats['top_user_agents'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10])

        # 保存統計報告
        stats_file = stats_dir / "summary.json"
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        logger.info(f"📊 Saved statistics: {stats['total_sessions']} sessions, avg risk: {stats['average_risk_score']}")
        return True

    except Exception as e:
        logger.error(f"❌ Error saving statistics: {e}", exc_info=True)
        return False


def save_threat_intelligence_feed(sessions: List[Dict[str, Any]]) -> bool:
    """
    生成威脅情報 Feed

    格式：
    - IP 黑名單
    - 攻擊模式簽名
    - IOC (Indicators of Compromise)
    """
    try:
        if not sessions:
            return True

        today = datetime.utcnow().strftime("%Y-%m-%d")
        intel_dir = Path(DATA_DIR) / "threat_intelligence" / today
        intel_dir.mkdir(parents=True, exist_ok=True)

        # 收集威脅情報
        malicious_ips = set()
        attack_signatures = set()
        malicious_user_agents = set()
        malicious_payloads = []

        for session in sessions:
            # 只收集高風險的情報
            risk_score = session.get('risk_score', 0)
            if risk_score < 50:
                continue

            # 惡意 IP
            peer_ip = session.get('peer_ip')
            if peer_ip and peer_ip != '0.0.0.0':
                malicious_ips.add(peer_ip)

            # 攻擊簽名
            attack_patterns = session.get('attack_patterns', {})
            signature = attack_patterns.get('pattern_signature', '')
            if signature:
                attack_signatures.add(signature)

            # 掃描工具
            ua_info = session.get('user_agent_info', {})
            if ua_info.get('is_scanner', False):
                user_agent = session.get('user_agent')
                if user_agent:
                    malicious_user_agents.add(user_agent)

            # 惡意 Payload (sample)
            payload_analysis = session.get('payload_analysis', {})
            suspicious_patterns = payload_analysis.get('suspicious_patterns', [])
            if suspicious_patterns:
                for path in session.get('paths', [])[:3]:  # 只取前3個
                    malicious_payloads.append({
                        'path': path.get('path'),
                        'method': path.get('method'),
                        'attack_type': path.get('attack_type'),
                        'patterns': suspicious_patterns
                    })

        # 保存 IP 黑名單
        ip_blacklist_file = intel_dir / "malicious_ips.txt"
        with open(ip_blacklist_file, "w", encoding="utf-8") as f:
            for ip in sorted(malicious_ips):
                f.write(f"{ip}\n")

        # 保存攻擊簽名
        signatures_file = intel_dir / "attack_signatures.txt"
        with open(signatures_file, "w", encoding="utf-8") as f:
            for sig in sorted(attack_signatures):
                f.write(f"{sig}\n")

        # 保存威脅情報摘要
        intel_summary = {
            'date': today,
            'malicious_ips_count': len(malicious_ips),
            'malicious_ips': list(malicious_ips),
            'attack_signatures_count': len(attack_signatures),
            'attack_signatures': list(attack_signatures),
            'malicious_user_agents': list(malicious_user_agents),
            'sample_payloads': malicious_payloads[:20]  # 只保存 20 個樣本
        }

        intel_file = intel_dir / "threat_intelligence.json"
        with open(intel_file, "w", encoding="utf-8") as f:
            json.dump(intel_summary, f, ensure_ascii=False, indent=2)

        logger.info(f"🔒 Saved threat intelligence: {len(malicious_ips)} IPs, {len(attack_signatures)} signatures")
        return True

    except Exception as e:
        logger.error(f"❌ Error saving threat intelligence: {e}", exc_info=True)
        return False


def cleanup_old_data(days_to_keep: int = 30) -> bool:
    """
    清理舊資料

    Args:
        days_to_keep: 保留天數

    Returns:
        bool: 是否成功清理
    """
    try:
        base_dir = Path(DATA_DIR)

        if not base_dir.exists():
            return True

        current_date = datetime.utcnow()

        # 遍歷所有日期目錄
        for category in ['processed', 'alerts', 'statistics', 'threat_intelligence']:
            category_dir = base_dir / category

            if not category_dir.exists():
                continue

            for date_dir in category_dir.iterdir():
                if not date_dir.is_dir():
                    continue

                try:
                    # 解析日期
                    dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
                    age_days = (current_date - dir_date).days

                    # 刪除過期目錄
                    if age_days > days_to_keep:
                        import shutil
                        shutil.rmtree(date_dir)
                        logger.info(f"🗑️  Deleted old data: {date_dir}")

                except ValueError:
                    # 不是日期格式的目錄，跳過
                    continue

        return True

    except Exception as e:
        logger.error(f"❌ Error cleaning up old data: {e}", exc_info=True)
        return False


def get_storage_stats() -> Dict[str, Any]:
    """獲取儲存統計資訊"""
    try:
        base_dir = Path(DATA_DIR)

        if not base_dir.exists():
            return {'error': 'Data directory does not exist'}

        stats = {
            'total_size_mb': 0,
            'file_counts': {},
            'latest_data_date': None
        }

        # 計算大小和檔案數
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                file_path = Path(root) / file
                stats['total_size_mb'] += file_path.stat().st_size / (1024 * 1024)

                ext = file_path.suffix
                stats['file_counts'][ext] = stats['file_counts'].get(ext, 0) + 1

        stats['total_size_mb'] = round(stats['total_size_mb'], 2)

        return stats

    except Exception as e:
        logger.error(f"❌ Error getting storage stats: {e}")
        return {'error': str(e)}
