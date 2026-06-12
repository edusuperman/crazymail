# Guerrilla Mail API 文档

## 服务信息

- **服务名称**: Guerrilla Mail
- **官方网站**: https://www.guerrillamail.com
- **API基础URL**: `http://api.guerrillamail.com/ajax.php`
- **API类型**: RESTful API (GET/POST)
- **认证方式**: 基于Cookie的会话认证（PHPSESSID）
- **速率限制**: 未明确说明，建议合理使用
- **邮箱有效期**: 60分钟（3600秒）

## 特点

✅ **优点**:
- 无需注册，即时创建
- 支持自定义邮箱用户名
- 邮件保留60分钟
- 支持多语言（11种语言）
- API简单易用
- 支持邮件删除
- 提供欢迎邮件示例

❌ **限制**:
- 邮箱有效期固定60分钟
- 不支持发送邮件
- 某些POST操作可能需要特殊参数格式
- 无附件下载API

## API端点

### 1. 获取邮箱地址

创建新的临时邮箱或获取现有邮箱信息。

**端点**: `GET /ajax.php`

**参数**:
```
f=get_email_address
ip=127.0.0.1
agent=Mozilla
lang=en (可选，默认en)
SUBSCR=<cookie_data> (可选)
```

**支持的语言代码**:
- `en` - English
- `fr` - Français
- `nl` - Nederlands
- `ru` - Русский
- `tr` - Türkçe
- `uk` - Українська
- `ar` - العربية
- `ko` - 한국어
- `jp` - 日本語
- `zh` - 简体中文
- `zh-hant` - 繁體中文

**响应示例**:
```json
{
  "email_addr": "pqdudhbf@guerrillamailblock.com",
  "email_timestamp": 1779291987,
  "alias": "xg1ntr+5gu2v6wwk7xis",
  "sid_token": "paa77ubei0mvehfept2a4vu5u3"
}
```

**字段说明**:
- `email_addr`: 完整的邮箱地址
- `email_timestamp`: Unix时间戳（邮箱创建时间）
- `alias`: 邮箱别名（用于内部标识）
- `sid_token`: 会话ID（存储在Cookie中）

---

### 2. 设置自定义用户名

自定义邮箱地址的用户名部分（@符号前）。

**端点**: `POST /ajax.php`

**参数**:
```
f=set_email_user
email_user=<custom_name>
lang=en
ip=127.0.0.1
agent=Mozilla
```

**响应示例**:
```json
{
  "email_addr": "custom_name@guerrillamailblock.com",
  "email_timestamp": 1779291987,
  "alias": "custom_name"
}
```

**注意事项**:
- 用户名必须唯一且可用
- 某些用户名可能已被占用
- 用户名长度和字符限制未明确说明

---

### 3. 检查新邮件

检查是否有新邮件到达。

**端点**: `GET /ajax.php`

**参数**:
```
f=check_email
seq=0 (最旧邮件的序列号，默认0)
ip=127.0.0.1
agent=Mozilla
```

**响应示例**:
```json
{
  "list": [
    {
      "mail_id": 1,
      "mail_from": "no-reply@guerrillamail.com",
      "mail_subject": "Welcome to Guerrilla Mail",
      "mail_excerpt": "Dear Random User, Thank you for using...",
      "mail_timestamp": 1779291987,
      "mail_read": 0,
      "mail_date": "15:46:27",
      "att": 0,
      "size": 1034
    }
  ],
  "count": "1",
  "email": "pqdudhbf@guerrillamailblock.com",
  "ts": 1779291987,
  "sid_token": "paa77ubei0mvehfept2a4vu5u3"
}
```

**字段说明**:
- `list`: 邮件列表（最多20封）
  - `mail_id`: 邮件唯一ID
  - `mail_from`: 发件人地址
  - `mail_subject`: 邮件主题
  - `mail_excerpt`: 邮件摘要
  - `mail_timestamp`: Unix时间戳
  - `mail_read`: 已读状态（0=未读，1=已读）
  - `mail_date`: 格式化的时间
  - `att`: 附件数量
  - `size`: 邮件大小（字节）
- `count`: 新邮件总数（字符串格式）
- `email`: 当前邮箱地址
- `ts`: 邮箱时间戳
- `sid_token`: 会话ID

---

### 4. 获取邮件列表

获取邮件列表，支持分页。

**端点**: `GET /ajax.php`

**参数**:
```
f=get_email_list
offset=0 (跳过的邮件数，用于分页)
seq=<number> (可选，第一封邮件的序列号)
ip=127.0.0.1
agent=Mozilla
```

**响应格式**: 与 `check_email` 相同

**分页示例**:
```python
# 获取第1-20封邮件
client.get_email_list(offset=0)

# 获取第21-40封邮件
client.get_email_list(offset=20)

# 获取第41-60封邮件
client.get_email_list(offset=40)
```

---

### 5. 获取邮件详情

获取单封邮件的完整内容。

**端点**: `GET /ajax.php`

**参数**:
```
f=fetch_email
email_id=<mail_id>
ip=127.0.0.1
agent=Mozilla
```

**响应示例**:
```json
{
  "mail_id": 1,
  "mail_from": "no-reply@guerrillamail.com",
  "mail_subject": "Welcome to Guerrilla Mail",
  "mail_body": "<pre>Dear Random User,\n\nThank you for using Guerrilla Mail...</pre>",
  "mail_timestamp": 1779291987,
  "mail_date": "15:46:27",
  "mail_read": 0,
  "att": 0,
  "size": 1034,
  "sid_token": "paa77ubei0mvehfept2a4vu5u3"
}
```

**字段说明**:
- `mail_body`: 邮件正文（HTML格式，已过滤危险标签）
- 其他字段与邮件列表相同

**注意事项**:
- 邮件正文中的HTML已被过滤，只保留安全标签
- 图片和外部资源可能被移除
- 邮件正文可能包含 `<pre>` 标签

---

### 6. 删除邮件

删除一封或多封邮件。

**端点**: `POST /ajax.php`

**参数**:
```
f=del_email
email_ids[0]=<mail_id_1>
email_ids[1]=<mail_id_2>
...
ip=127.0.0.1
agent=Mozilla
```

**响应示例**:
```json
{
  "deleted_ids": [1, 2, 3]
}
```

**注意事项**:
- 可以一次删除多封邮件
- 参数格式为数组：`email_ids[0]`, `email_ids[1]`, ...
- 删除后无法恢复

---

### 7. 忘记邮箱

从当前会话中移除邮箱地址（不删除邮箱）。

**端点**: `POST /ajax.php`

**参数**:
```
f=forget_me
email_addr=<email_address>
ip=127.0.0.1
agent=Mozilla
```

**响应示例**:
```json
{
  "success": true
}
```

**注意事项**:
- 只是从会话中移除，邮箱仍然存在
- 可以通过重新获取邮箱地址来恢复访问
- 邮箱会在60分钟后自动过期

---

### 8. 获取更早的邮件

获取指定序列号之前的邮件。

**端点**: `GET /ajax.php`

**参数**:
```
f=get_older_list
seq=<sequence_number>
ip=127.0.0.1
agent=Mozilla
```

**响应格式**: 与 `check_email` 相同

---

## 会话管理

### Cookie机制

Guerrilla Mail使用Cookie进行会话管理：

1. **PHPSESSID**: 会话ID，存储在Cookie中
2. **自动管理**: 客户端自动处理Cookie
3. **会话持久化**: 保持Cookie可以访问同一邮箱

### 会话生命周期

```python
# 1. 创建会话
client = GuerrillaMailClient()
info = client.get_email_address()
# 会话ID存储在 client.sid_token

# 2. 使用会话
# 所有后续请求自动携带会话Cookie
messages = client.check_email()

# 3. 会话过期
# 60分钟后邮箱自动过期
# 可以通过 client.is_expired() 检查
```

---

## 错误处理

### 常见错误

1. **认证错误**:
```json
{
  "auth": {
    "success": false,
    "error_codes": ["INVALID_SESSION"]
  }
}
```

2. **速率限制**:
- HTTP 429 Too Many Requests
- 建议：添加请求间隔

3. **JSON解析错误**:
- 某些POST请求可能返回非JSON响应
- 需要特殊处理

### 错误处理示例

```python
from guerrillamail_client import (
    GuerrillaMailClient,
    GuerrillaMailAPIError,
    AuthenticationError,
    RateLimitError
)

try:
    client = GuerrillaMailClient()
    info = client.get_email_address()
except AuthenticationError as e:
    print(f"认证失败: {e}")
except RateLimitError as e:
    print(f"速率限制: {e}")
except GuerrillaMailAPIError as e:
    print(f"API错误: {e}")
```

---

## 使用限制

### 邮箱限制

- **有效期**: 60分钟（固定）
- **容量**: 未明确说明
- **邮件大小**: 未明确说明
- **附件**: 支持接收，但无下载API

### API限制

- **速率限制**: 未明确说明，建议合理使用
- **并发请求**: 建议使用单一会话
- **请求超时**: 建议设置30秒超时

### 功能限制

- ❌ 不支持发送邮件
- ❌ 不支持附件下载
- ❌ 不支持邮箱续期
- ❌ 不支持邮件转发
- ✅ 支持接收邮件
- ✅ 支持自定义用户名
- ✅ 支持邮件删除

---

## 最佳实践

### 1. 会话管理

```python
# 保持单一客户端实例
client = GuerrillaMailClient()

# 检查邮箱是否过期
if client.is_expired():
    # 重新创建邮箱
    client.get_email_address()
```

### 2. 错误重试

```python
# 客户端内置重试机制
client = GuerrillaMailClient(
    max_retries=3,      # 最大重试次数
    retry_delay=2       # 重试延迟（秒）
)
```

### 3. 等待邮件

```python
# 使用内置的等待功能
mails = client.wait_for_email(
    timeout=60,         # 最大等待时间
    check_interval=5,   # 检查间隔
    min_count=1         # 最少邮件数
)
```

### 4. 资源清理

```python
# 使用完毕后忘记邮箱
client.forget_me()

# 或让邮箱自然过期（60分钟）
```

---

## 完整示例

### 基础使用

```python
from guerrillamail_client import GuerrillaMailClient

# 创建客户端
client = GuerrillaMailClient()

# 获取邮箱地址
info = client.get_email_address()
print(f"临时邮箱: {info['email_addr']}")

# 检查邮件
result = client.check_email()
print(f"收到 {len(result['list'])} 封邮件")

# 读取邮件
for mail in result['list']:
    detail = client.fetch_email(mail['mail_id'])
    print(f"主题: {detail['mail_subject']}")
    print(f"正文: {detail['mail_body']}")
```

### 自定义用户名

```python
# 设置自定义用户名
client.set_email_user('myname')
print(f"新邮箱: {client.email_address}")
# 输出: myname@guerrillamailblock.com
```

### 等待邮件

```python
# 等待新邮件到达
print("等待邮件...")
mails = client.wait_for_email(timeout=60)

if mails:
    print(f"收到 {len(mails)} 封新邮件")
    for mail in mails:
        print(f"- {mail['mail_from']}: {mail['mail_subject']}")
else:
    print("未收到邮件（超时）")
```

### 邮件管理

```python
# 删除邮件
client.del_email([1, 2, 3])

# 忘记邮箱
client.forget_me()
```

---

## 技术细节

### HTTP请求格式

**GET请求示例**:
```
GET http://api.guerrillamail.com/ajax.php?f=get_email_address&ip=127.0.0.1&agent=Mozilla&lang=en
```

**POST请求示例**:
```
POST http://api.guerrillamail.com/ajax.php
Content-Type: application/x-www-form-urlencoded

f=set_email_user&email_user=myname&lang=en&ip=127.0.0.1&agent=Mozilla
```

### 请求头

```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Accept: application/json, text/javascript, */*; q=0.01
Accept-Language: en-US,en;q=0.9
Accept-Encoding: gzip, deflate
Connection: keep-alive
Cookie: PHPSESSID=<session_id>
```

### 响应格式

所有成功的响应都是JSON格式：
```json
{
  "field1": "value1",
  "field2": "value2",
  ...
}
```

---

## 与其他服务对比

| 特性 | Guerrilla Mail | TemporaryMail | Tempimail | Tempail |
|------|----------------|---------------|-----------|---------|
| 邮箱有效期 | 60分钟 | 10分钟 | 10分钟 | 10分钟 |
| 自定义用户名 | ✅ | ❌ | ❌ | ❌ |
| 多语言支持 | ✅ (11种) | ❌ | ❌ | ❌ |
| 邮件删除 | ✅ | ❌ | ❌ | ❌ |
| API复杂度 | 中等 | 简单 | 简单 | 简单 |
| 欢迎邮件 | ✅ | ❌ | ❌ | ❌ |

---

## 更新日志

### 2026-05-20
- 初始版本
- 完成核心API逆向工程
- 实现Python客户端
- 测试通过率: 62.5% (5/8)

---

## 参考资源

- **官方网站**: https://www.guerrillamail.com
- **API端点**: http://api.guerrillamail.com/ajax.php
- **GitHub项目**: IBM CrazyMail Project
- **客户端文件**: `guerrillamail_client.py`
- **测试文件**: `tests/07_20260520_test_guerrillamail.py`

---

## 许可证

本文档属于 IBM CrazyMail Project，仅供学习和研究使用。

**免责声明**: 本文档通过逆向工程获得，非官方API文档。使用时请遵守服务条款。