import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

class ThreatEvaluator:
    def __init__(self):
        self.attack_history = {}
        self.threat_scores = {
            'sql_injection': 8,
            'xss': 7,
            'command_injection': 9,
            'path_traversal': 6,
            'brute_force': 5
        }
        logging.info("ThreatEvaluator initialized")

    def calculate_base_score(self, attack_types: List[str]) -> float:
        """計算基礎威脅分數"""
        if not attack_types:
            return 1.0
        
        return max(self.threat_scores.get(attack_type, 3) for attack_type in attack_types)

    def calculate_frequency_multiplier(self, source_ip: str) -> float:
        """根據攻擊頻率計算乘數"""
        now = datetime.utcnow()
        recent_attacks = [
            timestamp for timestamp in self.attack_history.get(source_ip, [])
            if timestamp > now - timedelta(hours=24)
        ]
        
        # 更新歷史記錄
        self.attack_history[source_ip] = recent_attacks + [now]
        
        # 根據24小時內的攻擊次數計算乘數
        attack_count = len(recent_attacks)
        if attack_count > 100:
            return 2.0
        elif attack_count > 50:
            return 1.5
        elif attack_count > 10:
            return 1.2
        return 1.0

    def evaluate_payload_complexity(self, payload: str) -> float:
        """評估攻擊載荷的複雜度"""
        complexity_indicators = {
            'basic': ['admin', 'password', '1=1', 'test'],
            'intermediate': ['union select', 'information_schema', '<script>alert'],
            'advanced': ['hex_encoding', 'base64', 'obfuscated']
        }

        payload = str(payload).lower()
        
        for level, indicators in complexity_indicators.items():
            if any(indicator in payload for indicator in indicators):
                if level == 'advanced':
                    return 1.5
                elif level == 'intermediate':
                    return 1.2
        return 1.0

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """評估威脅等級"""
        try:
            source_ip = data.get('source_ip', '')
            attack_types = data.get('attack_info', {}).get('attack_types', [])
            payload = data.get('payload', '')

            # 計算總體威脅分數
            base_score = self.calculate_base_score(attack_types)
            frequency_multiplier = self.calculate_frequency_multiplier(source_ip)
            complexity_multiplier = self.evaluate_payload_complexity(payload)

            final_score = base_score * frequency_multiplier * complexity_multiplier

            # 確定威脅等級
            threat_level = 'critical' if final_score >= 8 else \
                          'high' if final_score >= 6 else \
                          'medium' if final_score >= 4 else \
                          'low'

            evaluation_result = {
                'threat_score': round(final_score, 2),
                'threat_level': threat_level,
                'evaluation_factors': {
                    'base_score': base_score,
                    'frequency_multiplier': frequency_multiplier,
                    'complexity_multiplier': complexity_multiplier
                },
                'timestamp': datetime.utcnow().isoformat()
            }

            return evaluation_result

        except Exception as e:
            logging.error(f"Error in threat evaluation: {e}")
            raise
