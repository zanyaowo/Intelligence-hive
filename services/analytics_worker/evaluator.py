"""
風險評估模組

負責計算風險分數、評估威脅等級，並提供可操作的建議
"""

import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


def evaluate_session(session: Dict[str, Any]) -> Dict[str, Any]:
    """
    評估 session 的風險與威脅等級

    功能：
    - 計算綜合風險分數
    - 評估各維度威脅等級
    - 生成優先級建議
    - 提供應對建議

    Args:
        session: 豐富化後的 session 資料

    Returns:
        Dict: 包含評估結果的 session 資料
    """
    try:
        evaluated = session.copy()

        # === 1. 計算風險分數（0-100） ===
        risk_score, risk_breakdown = calculate_risk_score(session)
        evaluated['risk_score'] = risk_score
        evaluated['risk_breakdown'] = risk_breakdown

        # === 2. 威脅等級評估 ===
        evaluated['threat_level'] = determine_threat_level(risk_score)

        # === 3. 優先級評估 ===
        evaluated['priority'] = determine_priority(session, risk_score)

        # === 4. 可信度評估 ===
        evaluated['confidence_score'] = calculate_confidence_score(session)

        # === 5. 攻擊成功可能性 ===
        evaluated['exploitation_likelihood'] = assess_exploitation_likelihood(session)

        # === 6. 影響評估 ===
        evaluated['impact_assessment'] = assess_impact(session)

        # === 7. 應對建議 ===
        evaluated['recommendations'] = generate_recommendations(evaluated)

        # === 8. 需要人工審查標記 ===
        evaluated['requires_review'] = should_require_manual_review(evaluated)

        # === 9. 警報等級 ===
        evaluated['alert_level'] = determine_alert_level(evaluated)

        logger.debug(f"✅ Evaluated session {session.get('sess_uuid', 'unknown')} - Risk: {risk_score}/100, Threat: {evaluated['threat_level']}")

        return evaluated

    except Exception as e:
        logger.error(f"❌ Error evaluating session: {e}", exc_info=True)
        session['evaluation_error'] = str(e)
        return session


def calculate_risk_score(session: Dict[str, Any]) -> Tuple[int, Dict[str, int]]:
    """
    計算綜合風險分數（0-100）

    評估維度：
    - 攻擊嚴重性 (30%)
    - 攻擊複雜度 (20%)
    - 自動化程度 (15%)
    - Payload 危險性 (15%)
    - 目標明確性 (10%)
    - 持續時間 (10%)
    """
    breakdown = {
        'severity_score': 0,
        'complexity_score': 0,
        'automation_score': 0,
        'payload_score': 0,
        'targeting_score': 0,
        'persistence_score': 0
    }

    # === 1. 攻擊嚴重性分數 (0-30) ===
    threat_intel = session.get('threat_intelligence', {})
    severity = threat_intel.get('severity', 'info')

    severity_map = {
        'critical': 30,
        'high': 24,
        'medium': 18,
        'low': 12,
        'info': 6,
        'unknown': 0
    }
    breakdown['severity_score'] = severity_map.get(severity, 0)

    # === 2. 攻擊複雜度分數 (0-20) ===
    attack_patterns = session.get('attack_patterns', {})
    unique_attacks = session.get('unique_attack_types', 0)
    escalation = attack_patterns.get('escalation_detected', False)

    complexity_score = 0
    complexity_score += min(unique_attacks * 4, 12)  # 最多 12 分
    if escalation:
        complexity_score += 8  # 攻擊升級 +8

    breakdown['complexity_score'] = min(complexity_score, 20)

    # === 3. 自動化程度分數 (0-15) ===
    is_automated = threat_intel.get('is_automated', False)
    request_rate = session.get('requests_in_second', 0)

    automation_score = 0
    if is_automated:
        automation_score += 10

    if request_rate > 5:
        automation_score += 5
    elif request_rate > 2:
        automation_score += 3

    breakdown['automation_score'] = min(automation_score, 15)

    # === 4. Payload 危險性分數 (0-15) ===
    # 基於 Tanner 的攻擊類型分類（不重複檢測）
    attack_types = session.get('attack_types', [])
    payload_analysis = session.get('payload_analysis', {})

    payload_score = 0

    # 根據 Tanner 識別的攻擊類型計分
    if 'cmd_exec' in attack_types or 'rfi' in attack_types:
        payload_score += 6  # 最危險
    if 'sqli' in attack_types:
        payload_score += 5
    if 'lfi' in attack_types or 'xxe_injection' in attack_types:
        payload_score += 4
    if 'xss' in attack_types:
        payload_score += 3

    # 補充：編碼複雜度加分
    payload_complexity = payload_analysis.get('payload_complexity', 'low')
    if payload_complexity == 'high':
        payload_score += 3
    elif payload_complexity == 'medium':
        payload_score += 2

    # 補充：結構性特徵加分
    if payload_analysis.get('has_command_chaining', False):
        payload_score += 2  # 命令連接符表示更複雜的攻擊
    if payload_analysis.get('has_path_traversal_pattern', False):
        payload_score += 1  # 路徑遍歷模式

    breakdown['payload_score'] = min(payload_score, 15)

    # === 5. 目標明確性分數 (0-10) ===
    ua_info = session.get('user_agent_info', {})
    request_patterns = session.get('request_patterns', {})

    targeting_score = 0
    if ua_info.get('is_scanner', False):
        targeting_score += 5  # 使用專業工具
    if request_patterns.get('path_diversity', 0) < 0.3:
        targeting_score += 5  # 重複攻擊特定目標

    breakdown['targeting_score'] = min(targeting_score, 10)

    # === 6. 持續性分數 (0-10) ===
    temporal_patterns = session.get('temporal_patterns', {})
    is_prolonged = temporal_patterns.get('is_prolonged', False)
    total_requests = session.get('total_requests', 0)

    persistence_score = 0
    if is_prolonged:
        persistence_score += 5
    if total_requests > 20:
        persistence_score += 5
    elif total_requests > 10:
        persistence_score += 3

    breakdown['persistence_score'] = min(persistence_score, 10)

    # === 計算總分 ===
    total_score = sum(breakdown.values())

    return total_score, breakdown


def determine_threat_level(risk_score: int) -> str:
    """根據風險分數確定威脅等級"""
    if risk_score >= 70:
        return 'CRITICAL'
    elif risk_score >= 50:
        return 'HIGH'
    elif risk_score >= 30:
        return 'MEDIUM'
    elif risk_score >= 15:
        return 'LOW'
    else:
        return 'INFO'


def determine_priority(session: Dict[str, Any], risk_score: int) -> str:
    """
    確定處理優先級

    考慮因素：
    - 風險分數
    - 攻擊成功可能性
    - 是否針對性攻擊
    """
    threat_intel = session.get('threat_intelligence', {})
    is_targeted = threat_intel.get('is_targeted', False)
    attack_phases = session.get('attack_phases', [])

    # 如果已進入利用階段，提高優先級
    has_exploitation = 'exploitation' in attack_phases or 'persistence_attempt' in attack_phases

    if risk_score >= 70 and (is_targeted or has_exploitation):
        return 'P1-URGENT'
    elif risk_score >= 50:
        return 'P2-HIGH'
    elif risk_score >= 30:
        return 'P3-MEDIUM'
    elif risk_score >= 15:
        return 'P4-LOW'
    else:
        return 'P5-INFO'


def calculate_confidence_score(session: Dict[str, Any]) -> float:
    """
    計算檢測可信度分數（0.0-1.0）

    基於：
    - 威脅情報可信度
    - 資料完整性
    - 多個指標的一致性
    """
    confidence = 0.0
    weight_sum = 0.0

    # 威脅情報可信度
    threat_intel = session.get('threat_intelligence', {})
    intel_confidence = threat_intel.get('confidence', 0.5)
    confidence += intel_confidence * 0.4
    weight_sum += 0.4

    # 資料完整性
    required_fields = ['sess_uuid', 'peer_ip', 'attack_types', 'paths']
    completeness = sum(1 for field in required_fields if session.get(field)) / len(required_fields)
    confidence += completeness * 0.3
    weight_sum += 0.3

    # User Agent 可信度
    ua_info = session.get('user_agent_info', {})
    if ua_info.get('is_scanner', False):
        confidence += 0.9 * 0.2  # 明確識別為掃描工具，高可信度
    else:
        confidence += 0.5 * 0.2
    weight_sum += 0.2

    # Payload 分析一致性
    payload_analysis = session.get('payload_analysis', {})
    attack_types = session.get('attack_types', [])

    consistency = 0.0
    if 'sqli' in attack_types and payload_analysis.get('has_sql_keywords', False):
        consistency += 0.3
    if 'xss' in attack_types and payload_analysis.get('has_xss_patterns', False):
        consistency += 0.3
    if 'cmd_exec' in attack_types and payload_analysis.get('has_command_injection', False):
        consistency += 0.4

    confidence += consistency * 0.1
    weight_sum += 0.1

    return round(confidence / weight_sum if weight_sum > 0 else 0.5, 2)


def assess_exploitation_likelihood(session: Dict[str, Any]) -> str:
    """評估攻擊成功的可能性"""
    attack_types = session.get('attack_types', [])
    ua_info = session.get('user_agent_info', {})
    attack_patterns = session.get('attack_patterns', {})

    # 高可能性因素
    high_likelihood_factors = 0

    # 使用專業工具
    if ua_info.get('is_scanner', False):
        high_likelihood_factors += 1

    # 攻擊升級
    if attack_patterns.get('escalation_detected', False):
        high_likelihood_factors += 1

    # 嚴重攻擊類型
    critical_attacks = {'cmd_exec', 'rfi', 'php_code_injection', 'sqli'}
    if any(at in critical_attacks for at in attack_types):
        high_likelihood_factors += 1

    # 重複攻擊（持續嘗試）
    repeated_attacks = attack_patterns.get('repeated_attacks', {})
    if any(count > 3 for count in repeated_attacks.values()):
        high_likelihood_factors += 1

    if high_likelihood_factors >= 3:
        return 'HIGH'
    elif high_likelihood_factors >= 2:
        return 'MEDIUM'
    elif high_likelihood_factors >= 1:
        return 'LOW'
    else:
        return 'VERY_LOW'


def assess_impact(session: Dict[str, Any]) -> Dict[str, Any]:
    """
    評估潛在影響

    STRIDE 威脅模型：
    - Spoofing (偽造)
    - Tampering (篡改)
    - Repudiation (否認)
    - Information Disclosure (資訊洩露)
    - Denial of Service (拒絕服務)
    - Elevation of Privilege (權限提升)
    """
    impact = {
        'confidentiality': 'NONE',
        'integrity': 'NONE',
        'availability': 'NONE',
        'scope': 'LIMITED',
        'financial_risk': 'LOW',
        'reputation_risk': 'LOW'
    }

    attack_types = session.get('attack_types', [])

    # 機密性影響
    info_disclosure_attacks = {'lfi', 'sqli', 'xxe_injection'}
    if any(at in info_disclosure_attacks for at in attack_types):
        impact['confidentiality'] = 'HIGH'

    # 完整性影響
    tampering_attacks = {'sqli', 'xss', 'php_code_injection', 'template_injection'}
    if any(at in tampering_attacks for at in attack_types):
        impact['integrity'] = 'HIGH'

    # 可用性影響
    dos_attacks = {'cmd_exec', 'rfi'}
    if any(at in dos_attacks for at in attack_types):
        impact['availability'] = 'MEDIUM'

    # 範圍評估
    if 'cmd_exec' in attack_types or 'rfi' in attack_types:
        impact['scope'] = 'SYSTEM'  # 可能影響整個系統
    elif any(at in {'sqli', 'xss', 'lfi'} for at in attack_types):
        impact['scope'] = 'APPLICATION'  # 限於應用層

    # 財務風險
    if impact['confidentiality'] == 'HIGH' or impact['integrity'] == 'HIGH':
        impact['financial_risk'] = 'HIGH'
    elif impact['availability'] == 'MEDIUM':
        impact['financial_risk'] = 'MEDIUM'

    # 聲譽風險
    if impact['scope'] == 'SYSTEM':
        impact['reputation_risk'] = 'CRITICAL'
    elif impact['confidentiality'] == 'HIGH':
        impact['reputation_risk'] = 'HIGH'

    return impact


def generate_recommendations(session: Dict[str, Any]) -> List[str]:
    """生成應對建議"""
    recommendations = []

    threat_level = session.get('threat_level', 'INFO')
    risk_score = session.get('risk_score', 0)
    attack_types = session.get('attack_types', [])
    behavior_tags = session.get('behavior_tags', [])
    peer_ip = session.get('peer_ip', 'unknown')

    # === 高危威脅建議 ===
    if threat_level in ['CRITICAL', 'HIGH']:
        recommendations.append(f"🚨 立即封鎖來源 IP: {peer_ip}")
        recommendations.append("📊 進行深度取證分析")
        recommendations.append("🔍 檢查相同來源的其他活動")

    # === 特定攻擊類型建議 ===
    if 'sqli' in attack_types:
        recommendations.append("🛡️  修補 SQL 注入漏洞：使用參數化查詢")
        recommendations.append("🔒 啟用 WAF SQL 注入防護規則")

    if 'xss' in attack_types:
        recommendations.append("🛡️  修補 XSS 漏洞：對輸出進行 HTML 轉義")
        recommendations.append("📋 實施 Content Security Policy (CSP)")

    if 'cmd_exec' in attack_types:
        recommendations.append("🚨 緊急修補命令注入漏洞")
        recommendations.append("⚙️  限制 Web 應用的系統命令執行權限")

    if 'lfi' in attack_types or 'rfi' in attack_types:
        recommendations.append("🛡️  限制文件包含路徑，使用白名單")
        recommendations.append("🔒 禁用 allow_url_include (PHP)")

    # === 掃描工具檢測建議 ===
    if 'scanner_detected' in behavior_tags:
        recommendations.append("🤖 檢測到自動化掃描工具，建議實施速率限制")
        tool = next((tag.split(':')[1] for tag in behavior_tags if tag.startswith('tool:')), None)
        if tool:
            recommendations.append(f"🔧 識別到工具: {tool}，更新 WAF 規則")

    # === 攻擊升級建議 ===
    if 'attack_escalation' in behavior_tags:
        recommendations.append("⚠️  檢測到攻擊升級模式，持續監控")

    # === 通用建議 ===
    if risk_score >= 30:
        recommendations.append("📝 記錄此事件到 SIEM 系統")
        recommendations.append("👥 通知安全團隊進行審查")

    # === 預防建議 ===
    if not recommendations:
        recommendations.append("✅ 攻擊已被蜜罐捕獲，持續監控")
        recommendations.append("📊 分析攻擊模式，更新威脅情報")

    return recommendations


def should_require_manual_review(session: Dict[str, Any]) -> bool:
    """判斷是否需要人工審查"""
    risk_score = session.get('risk_score', 0)
    threat_level = session.get('threat_level', 'INFO')
    exploitation_likelihood = session.get('exploitation_likelihood', 'VERY_LOW')
    confidence_score = session.get('confidence_score', 0.0)

    # 高風險必須審查
    if risk_score >= 60:
        return True

    # 威脅等級為 CRITICAL 或 HIGH
    if threat_level in ['CRITICAL', 'HIGH']:
        return True

    # 攻擊成功可能性高
    if exploitation_likelihood == 'HIGH':
        return True

    # 低可信度但高風險分數
    if confidence_score < 0.5 and risk_score >= 40:
        return True

    # 攻擊升級模式
    behavior_tags = session.get('behavior_tags', [])
    if 'attack_escalation' in behavior_tags:
        return True

    return False


def determine_alert_level(session: Dict[str, Any]) -> str:
    """
    確定警報等級

    等級：
    - CRITICAL: 立即響應
    - HIGH: 1小時內響應
    - MEDIUM: 4小時內響應
    - LOW: 24小時內響應
    - INFO: 記錄即可
    """
    threat_level = session.get('threat_level', 'INFO')
    requires_review = session.get('requires_review', False)
    exploitation_likelihood = session.get('exploitation_likelihood', 'VERY_LOW')

    if threat_level == 'CRITICAL' and requires_review:
        return 'CRITICAL'
    elif threat_level == 'HIGH' or (threat_level == 'MEDIUM' and exploitation_likelihood == 'HIGH'):
        return 'HIGH'
    elif threat_level == 'MEDIUM':
        return 'MEDIUM'
    elif threat_level == 'LOW':
        return 'LOW'
    else:
        return 'INFO'
