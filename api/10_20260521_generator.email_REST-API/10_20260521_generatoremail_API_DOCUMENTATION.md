# Email Generator (generator.email) API 文档

## 服务概述

**服务名称**: Email Generator  
**官方网站**: https://generator.email  
**API类型**: REST API (HTTP POST)  
**认证方式**: 无需认证（公开访问）  
**评分**: 82分 (A级)  
**创建日期**: 2026-05-21  

### 服务特点

- ✅ **无需认证**: 完全公开访问，无需注册或API密钥
- ✅ **自定义邮箱**: 支持自定义用户名和域名
- ✅ **实时通知**: 通过WebSocket实时推送新邮件
- ✅ **多域名支持**: 提供90+个可用域名
- ✅ **域名搜索**: 支持TypeAhead搜索功能
- ✅ **邮件管理**: 支持删除、标记已读等操作
- ⚠️ **邮件ID加密**: 使用自定义加密算法（约100字符）

### 技术架构

- **后端**: PHP
- **实时通信**: Socket.IO (WebSocket)
- **前端**: jQuery + TypeAhead.js
- **请求格式**: application/x-www-form-urlencoded
- **响应格式**: JSON

---

## API端点

### 基础URL

```
https://generator.email
```

### 1. 搜索域名

**端点**: `GET /search.php`

**描述**: 搜索可用的邮箱域名（TypeAhead功能）

**请求参数**:
```
key: 搜索关键词（支持通配符，如 "mail*" 或 ".com"）
```

**请求示例**:
```bash
curl "https://generator.email/search.php?key=.com"
```

**响应示例**:
```json
[
  "rgin489232hg6892348923989283.ddnsgeek.com",
  "cepet.pengenemut.com",
  "e-mail.ardencreativestudio.com",
  "bot.hafidhhuda.com",
  "igoea.sedekah-mudah.com"
]
```

**Python示例**:
```python
import requests

response = requests.get(
    "https://generator.email/search.php",
    params={"key": ".com"}
)
domains = response.json()
print(f"找到 {len(domains)} 个域名")
```

---

### 2. 检查邮箱状态

**端点**: `POST /check_adres_validation3.php`

**描述**: 验证邮箱地址并获取域名状态

**请求参数**:
```
usr: 用户名
dmn: 域名
```

**请求示例**:
```bash
curl -X POST https://generator.email/check_adres_validation3.php \
  -d "usr=testuser" \
  -d "dmn=thichmmo.com"
```

**响应示例**:
```json
{
  "status": "good",
  "uptime": "136"
}
```

**响应字段**:
- `status`: 邮箱状态（"good" = 可用）
- `uptime`: 域名运行时间（天数）

**Python示例**:
```python
import requests

response = requests.post(
    "https://generator.email/check_adres_validation3.php",
    data={
        "usr": "testuser",
        "dmn": "thichmmo.com"
    }
)
result = response.json()
print(f"状态: {result['status']}, 运行时间: {result['uptime']}天")
```

---

### 3. 邮件操作

**端点**: `POST /del_mail.php`

**描述**: 执行各种邮件操作（获取、删除、标记）

#### 3.1 获取邮件列表

**请求参数**:
```
recieved: 完整邮箱地址
```

**请求示例**:
```bash
curl -X POST https://generator.email/del_mail.php \
  -d "recieved=testuser@thichmmo.com"
```

**响应**:
- 如果收件箱为空: 返回空字符串的MD5哈希 (`d41d8cd98f00b204e9800998ecf8427e`)
- 如果有邮件: 返回HTML或JSON格式的邮件列表

**Python示例**:
```python
import requests
import hashlib

response = requests.post(
    "https://generator.email/del_mail.php",
    data={"recieved": "testuser@thichmmo.com"}
)

# 检查是否为空
empty_md5 = hashlib.md5(b"").hexdigest()
if response.text.strip() == empty_md5:
    print("收件箱为空")
else:
    print("有新邮件")
```

#### 3.2 删除单个邮件

**请求参数**:
```
delll: 邮件ID（加密格式）
```

**请求示例**:
```bash
curl -X POST https://generator.email/del_mail.php \
  -d "delll=encrypted_message_id"
```

#### 3.3 删除所有邮件

**请求参数**:
```
dellall: 完整邮箱地址
```

**请求示例**:
```bash
curl -X POST https://generator.email/del_mail.php \
  -d "dellall=testuser@thichmmo.com"
```

#### 3.4 标记所有邮件为已读

**请求参数**:
```
markall: 完整邮箱地址
```

**请求示例**:
```bash
curl -X POST https://generator.email/del_mail.php \
  -d "markall=testuser@thichmmo.com"
```

---

## WebSocket实时通知

### 连接信息

**URL**: `wss://generator.email`  
**路径**: `/socket.io`  
**传输方式**: WebSocket  

### 订阅邮箱

```javascript
// 连接Socket.IO
var socket = io('wss://generator.email', {
    path: '/socket.io',
    transports: ['websocket']
});

// 订阅邮箱
var channel = 'username@domain.com';
socket.emit('watch_for_my_email', channel);

// 监听新邮件
socket.on('new_email', function(data) {
    console.log('收到新邮件!');
    window.location.reload();
});
```

### 自动重连机制

```javascript
var triger_recon = false;

// 每秒检查连接状态
setInterval(function() { 
    if (triger_recon && socket.id) {
        socket.emit('watch_for_my_email', channel);
        triger_recon = false;
    }
    if (socket.id == undefined) {
        triger_recon = true;
    }
}, 1000);
```

---

## 邮箱URL格式

### 访问邮箱

```
https://generator.email/{domain}/{username}
```

**示例**:
```
https://generator.email/thichmmo.com/testuser
```

### 随机用户名

```
https://generator.email/{domain}
```

**示例**:
```
https://generator.email/thichmmo.com
```
（系统会自动生成随机用户名）

---

## Python客户端使用

### 安装依赖

```bash
pip install requests beautifulsoup4
```

### 基本使用

```python
from generatoremail_client import GeneratorEmailClient

# 创建客户端
client = GeneratorEmailClient()

# 搜索域名
domains = client.search_domains(".com", limit=10)
print(f"找到 {len(domains)} 个.com域名")

# 创建邮箱
email = client.create_mailbox()
print(f"邮箱地址: {email}")
print(f"访问URL: {client.get_mailbox_url()}")

# 检查状态
status = client.check_mailbox_status()
print(f"状态: {status['status']}")
print(f"运行时间: {status['uptime']}天")

# 获取邮件
messages = client.get_messages()
print(f"收到 {len(messages)} 封邮件")

# 等待新邮件
message = client.wait_for_message(timeout=60)
if message:
    print(f"收到邮件: {message['subject']}")
```

### 自定义邮箱

```python
# 指定用户名和域名
email = client.create_mailbox(
    username="myuser",
    domain="thichmmo.com"
)
print(f"自定义邮箱: {email}")
```

### 邮件管理

```python
# 标记所有为已读
client.mark_all_as_read()

# 删除所有邮件
client.delete_all_messages()

# 删除单个邮件
client.delete_message(message_id)
```

---

## 错误处理

### 常见错误

#### 1. 域名不可用

**错误**: `DomainNotAvailableError`

**原因**: 指定的域名不存在或已失效

**解决方案**:
```python
try:
    client.create_mailbox(domain="invalid-domain.com")
except DomainNotAvailableError:
    # 使用随机域名
    client.create_mailbox()
```

#### 2. 未创建邮箱

**错误**: `GeneratorEmailAPIError: 未指定邮箱地址`

**原因**: 在创建邮箱前尝试获取邮件

**解决方案**:
```python
# 先创建邮箱
client.create_mailbox()
# 再获取邮件
messages = client.get_messages()
```

#### 3. 请求超时

**错误**: `GeneratorEmailAPIError: 请求超时`

**原因**: 网络问题或服务器响应慢

**解决方案**:
```python
# 增加超时时间
client = GeneratorEmailClient(timeout=60)
```

---

## 速率限制

### 观察到的限制

- **搜索API**: 无明显限制
- **邮箱创建**: 无明显限制
- **邮件检查**: 建议间隔2-5秒

### 最佳实践

```python
import time

# 轮询检查邮件
while True:
    messages = client.get_messages()
    if messages:
        break
    time.sleep(5)  # 等待5秒
```

---

## 域名列表

### 常见域名后缀

- `.com` - 15个域名
- `.org` - 15个域名
- `.net` - 15个域名
- `.id` - 15个域名
- `.my.id` - 15个域名
- `.biz.id` - 15个域名
- `.web.id` - 15个域名

### 获取完整列表

```python
# 获取所有可用域名（带缓存）
domains = client.get_available_domains()
print(f"共有 {len(domains)} 个可用域名")

# 强制刷新
domains = client.get_available_domains(force_refresh=True)
```

---

## 测试结果

### 测试环境

- **测试日期**: 2026-05-21
- **测试工具**: Python 3.x + requests
- **测试用例**: 8个

### 测试结果

| 测试项 | 结果 | 说明 |
|--------|------|------|
| 域名搜索 | ✅ 通过 | 成功搜索.com和mail关键词 |
| 获取所有域名 | ✅ 通过 | 获取90个域名，缓存工作正常 |
| 创建邮箱 | ✅ 通过 | 随机和自定义邮箱均成功 |
| 检查状态 | ✅ 通过 | 正确返回状态和运行时间 |
| 获取邮件 | ✅ 通过 | 空收件箱检测正常 |
| 邮箱操作 | ✅ 通过 | 标记和删除操作成功 |
| 等待邮件 | ✅ 通过 | 超时机制工作正常 |
| 错误处理 | ✅ 通过 | 正确抛出异常 |

**总体成功率**: 100% (8/8)

---

## 注意事项

### 1. 邮件ID加密

邮件ID使用自定义加密算法，长度约100字符。无法通过简单方式生成或预测。

### 2. HTML解析

邮件列表可能以HTML格式返回，需要使用BeautifulSoup解析。

### 3. WebSocket支持

完整的实时通知功能需要Socket.IO客户端支持。Python客户端目前使用轮询方式。

### 4. 域名稳定性

某些域名可能随时失效。建议：
- 使用运行时间长的域名（uptime > 30天）
- 实现域名失效时的自动切换
- 定期刷新域名列表缓存

### 5. 邮件内容获取

当前API主要支持邮件列表获取。完整邮件内容需要访问邮件详情页面并解析HTML。

---

## 相关资源

### 官方资源

- **官网**: https://generator.email
- **博客**: https://generator.email/blog

### 项目资源

- **客户端代码**: `generatoremail_client.py`
- **测试脚本**: `tests/10_20260521_test_generatoremail.py`
- **API分析**: `assets/10_generator.email/generator_email_api_analysis.md`

---

## 更新日志

### v1.0.0 (2026-05-21)

- ✅ 初始版本发布
- ✅ 实现域名搜索功能
- ✅ 实现邮箱创建和状态检查
- ✅ 实现邮件列表获取
- ✅ 实现邮件管理操作
- ✅ 实现等待邮件功能
- ✅ 完成8个测试用例（100%通过）

---

## 许可证

本文档和相关代码仅供学习和研究使用。请遵守Email Generator服务条款。

---

**文档版本**: 1.0.0  
**最后更新**: 2026-05-21  
**维护者**: Bob (AI Assistant)