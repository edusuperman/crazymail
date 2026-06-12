# Mail.tm API 逆向工程文档

> 📅 **创建日期**: 2026-05-20  
> 📊 **版本**: 1.0.0  
> ✅ **状态**: 完成  
> 🧪 **测试状态**: 已测试

---

## 📋 目录

- [基础信息](#-基础信息)
- [认证机制](#-认证机制)
- [API端点](#-api端点)
- [使用流程](#-使用流程)
- [Python客户端实现](#-python客户端实现)
- [技术特性](#-技术特性)
- [限制和约束](#-限制和约束)
- [错误处理](#-错误处理)
- [最佳实践](#-最佳实践)
- [注意事项](#-注意事项)
- [更新日志](#-更新日志)

---

## 📌 基础信息

- **网站**: https://mail.tm/
- **API 基础URL**: `https://api.mail.tm`
- **API类型**: REST API
- **请求方式**: GET, POST, PATCH, DELETE
- **响应格式**: JSON (JSON-LD / Hydra)
- **认证方式**: JWT (JSON Web Token)
- **API 文档**: https://docs.mail.tm/
- **交互式文档**: https://api.mail.tm/

### 快速参考

| 项目 | 值 |
|------|-----|
| 轮询间隔 | 10秒（建议） |
| Token 有效期 | 1小时 |
| 邮箱保留期 | 永久（直到删除） |
| 速率限制 | 8 QPS (每秒8个请求) |
| 邮箱配额 | 40 MB |
| 完全免费 | ✅ 无需 API Key |

---

## 🔐 认证机制

### 认证类型

Mail.tm 使用 **JWT (JSON Web Token)** 认证机制。

### 认证流程

1. **创建账户** - 使用 POST `/accounts` 创建新账户
2. **获取 Token** - 使用 POST `/token` 获取 JWT Token
3. **使用 Token** - 在请求头中添加 `Authorization: Bearer {token}`

### 1. 创建账户

```http
POST /accounts
Content-Type: application/json

{
  "address": "username@domain.com",
  "password": "your_password"
}
```

**响应示例**:
```json
{
  "@context": "/contexts/Account",
  "@id": "/accounts/6a0daa09d2df389ac30d54bc",
  "@type": "Account",
  "id": "6a0daa09d2df389ac30d54bc",
  "address": "username@wshu.net",
  "quota": 40000000,
  "used": 0,
  "isDisabled": false,
  "isDeleted": false,
  "createdAt": "2026-05-20T12:33:13+00:00",
  "updatedAt": "2026-05-20T12:33:13+00:00"
}
```

### 2. 获取 JWT Token

```http
POST /token
Content-Type: application/json

{
  "address": "username@domain.com",
  "password": "your_password"
}
```

**响应示例**:
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9...",
  "@id": "/accounts/6a0daa09d2df389ac30d54bc",
  "id": "6a0daa09d2df389ac30d54bc"
}
```

### 3. 使用 Token

在所有需要认证的请求中添加以下请求头：

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9...
```

---

## 🔌 API端点

### 1. 获取可用域名

**端点**: `/domains`

**方法**: GET

**描述**: 获取可用的邮箱域名列表

**请求头**:
```http
Accept: application/json
```

**请求示例**:
```bash
curl -X GET https://api.mail.tm/domains
```

**成功响应** (200 OK):
```json
{
  "@context": "/contexts/Domain",
  "@id": "/domains",
  "@type": "hydra:Collection",
  "hydra:totalItems": 1,
  "hydra:member": [
    {
      "@id": "/domains/69fbf6b9ab3b957d116c6be8",
      "@type": "Domain",
      "id": "69fbf6b9ab3b957d116c6be8",
      "domain": "wshu.net",
      "isActive": true,
      "isPrivate": false,
      "createdAt": "2026-05-07T00:00:00+00:00",
      "updatedAt": "2026-05-07T00:00:00+00:00"
    }
  ]
}
```

---

### 2. 创建账户

**端点**: `/accounts`

**方法**: POST

**描述**: 创建新的邮箱账户

**请求头**:
```http
Content-Type: application/json
Accept: application/json
```

**请求参数**:

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| address | string | 是 | 完整的邮箱地址 |
| password | string | 是 | 账户密码（至少8个字符） |

**请求示例**:
```http
POST /accounts HTTP/1.1
Host: api.mail.tm
Content-Type: application/json

{
  "address": "test123@wshu.net",
  "password": "SecurePass123"
}
```

**成功响应** (201 Created):
```json
{
  "@context": "/contexts/Account",
  "@id": "/accounts/6a0daa09d2df389ac30d54bc",
  "@type": "Account",
  "id": "6a0daa09d2df389ac30d54bc",
  "address": "test123@wshu.net",
  "quota": 40000000,
  "used": 0,
  "isDisabled": false,
  "isDeleted": false,
  "createdAt": "2026-05-20T12:33:13+00:00",
  "updatedAt": "2026-05-20T12:33:13+00:00"
}
```

**响应字段说明**:
- `id`: 账户唯一标识符
- `address`: 邮箱地址
- `quota`: 邮箱配额（字节）
- `used`: 已使用空间（字节）
- `isDisabled`: 是否被禁用
- `isDeleted`: 是否被删除

---

### 3. 获取 JWT Token

**端点**: `/token`

**方法**: POST

**描述**: 使用邮箱地址和密码获取 JWT Token

**请求参数**:

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| address | string | 是 | 邮箱地址 |
| password | string | 是 | 账户密码 |

**请求示例**:
```http
POST /token HTTP/1.1
Host: api.mail.tm
Content-Type: application/json

{
  "address": "test123@wshu.net",
  "password": "SecurePass123"
}
```

**成功响应** (200 OK):
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE3NzkyNzk3MDgsInJvbGVzIjpbIlJPTEVfVVNFUiJdLCJhZGRyZXNzIjoicGpkeHBtOGZxdEB3c2h1Lm5ldCIsImlkIjoiNmEwZGE3NWFmZTliYTgzNDUyMGU1YTFjIiwibWVyY3VyZSI6eyJzdWJzY3JpYmUiOlsiL2FjY291bnRzLzZhMGRhNzVhZmU5YmE4MzQ1MjBlNWExYyJdfX0.B2RVMv8apRS6xVUGLFgZfjeSLlQ0Porz8bcPfZf3BuE6SCSL5BE8DVMig1YNnpBHyiHKb9oOO8gEpo2qzs9fXQ",
  "@id": "/accounts/6a0daa09d2df389ac30d54bc",
  "id": "6a0daa09d2df389ac30d54bc"
}
```

---

### 4. 获取账户信息

**端点**: `/accounts/{id}`

**方法**: GET

**描述**: 获取指定账户的详细信息

**认证**: 需要 JWT Token

**请求头**:
```http
Authorization: Bearer {token}
Accept: application/json
```

**请求示例**:
```bash
curl -X GET https://api.mail.tm/accounts/6a0daa09d2df389ac30d54bc \
  -H "Authorization: Bearer {token}"
```

**成功响应** (200 OK):
```json
{
  "@context": "/contexts/Account",
  "@id": "/accounts/6a0daa09d2df389ac30d54bc",
  "@type": "Account",
  "id": "6a0daa09d2df389ac30d54bc",
  "address": "test123@wshu.net",
  "quota": 40000000,
  "used": 0,
  "isDisabled": false,
  "isDeleted": false,
  "createdAt": "2026-05-20T12:33:13+00:00",
  "updatedAt": "2026-05-20T12:33:13+00:00"
}
```

---

### 5. 获取邮件列表

**端点**: `/messages`

**方法**: GET

**描述**: 获取当前账户的邮件列表

**认证**: 需要 JWT Token

**请求参数**:

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| page | integer | 否 | 页码（默认为1） |

**请求示例**:
```bash
curl -X GET https://api.mail.tm/messages?page=1 \
  -H "Authorization: Bearer {token}"
```

**成功响应** (200 OK):
```json
{
  "@context": "/contexts/Message",
  "@id": "/messages",
  "@type": "hydra:Collection",
  "hydra:totalItems": 2,
  "hydra:member": [
    {
      "@id": "/messages/6a0daa14ed5c3c8bf30682a8",
      "@type": "Message",
      "id": "6a0daa14ed5c3c8bf30682a8",
      "accountId": "6a0daa09d2df389ac30d54bc",
      "msgid": "<message-id@example.com>",
      "from": {
        "address": "sender@example.com",
        "name": "Sender Name"
      },
      "to": [
        {
          "address": "test123@wshu.net",
          "name": ""
        }
      ],
      "subject": "Test Email",
      "intro": "This is the first 100 characters of the email...",
      "seen": false,
      "isDeleted": false,
      "hasAttachments": false,
      "size": 1234,
      "downloadUrl": "/messages/6a0daa14ed5c3c8bf30682a8/download",
      "createdAt": "2026-05-20T12:35:00+00:00",
      "updatedAt": "2026-05-20T12:35:00+00:00"
    }
  ]
}
```

---

### 6. 获取邮件详情

**端点**: `/messages/{id}`

**方法**: GET

**描述**: 获取指定邮件的完整内容

**认证**: 需要 JWT Token

**请求示例**:
```bash
curl -X GET https://api.mail.tm/messages/6a0daa14ed5c3c8bf30682a8 \
  -H "Authorization: Bearer {token}"
```

**成功响应** (200 OK):
```json
{
  "@context": "/contexts/Message",
  "@id": "/messages/6a0daa14ed5c3c8bf30682a8",
  "@type": "Message",
  "id": "6a0daa14ed5c3c8bf30682a8",
  "accountId": "6a0daa09d2df389ac30d54bc",
  "msgid": "<message-id@example.com>",
  "from": {
    "address": "sender@example.com",
    "name": "Sender Name"
  },
  "to": [
    {
      "address": "test123@wshu.net",
      "name": ""
    }
  ],
  "cc": [],
  "bcc": [],
  "subject": "Test Email",
  "seen": false,
  "flagged": false,
  "isDeleted": false,
  "verifications": [],
  "retention": false,
  "retentionDate": null,
  "text": "Plain text content of the email",
  "html": ["<html><body>HTML content</body></html>"],
  "hasAttachments": false,
  "attachments": [],
  "size": 1234,
  "downloadUrl": "/messages/6a0daa14ed5c3c8bf30682a8/download",
  "createdAt": "2026-05-20T12:35:00+00:00",
  "updatedAt": "2026-05-20T12:35:00+00:00"
}
```

---

### 7. 标记邮件为已读

**端点**: `/messages/{id}`

**方法**: PATCH

**描述**: 标记邮件为已读或未读

**认证**: 需要 JWT Token

**请求参数**:

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| seen | boolean | 是 | true=已读, false=未读 |

**请求示例**:
```http
PATCH /messages/6a0daa14ed5c3c8bf30682a8 HTTP/1.1
Host: api.mail.tm
Authorization: Bearer {token}
Content-Type: application/json

{
  "seen": true
}
```

**成功响应** (200 OK):
```json
{
  "@context": "/contexts/Message",
  "@id": "/messages/6a0daa14ed5c3c8bf30682a8",
  "@type": "Message",
  "id": "6a0daa14ed5c3c8bf30682a8",
  "seen": true,
  ...
}
```

---

### 8. 删除邮件

**端点**: `/messages/{id}`

**方法**: DELETE

**描述**: 删除指定邮件

**认证**: 需要 JWT Token

**请求示例**:
```bash
curl -X DELETE https://api.mail.tm/messages/6a0daa14ed5c3c8bf30682a8 \
  -H "Authorization: Bearer {token}"
```

**成功响应** (204 No Content)

---

### 9. 删除账户

**端点**: `/accounts/{id}`

**方法**: DELETE

**描述**: 删除指定账户及其所有邮件

**认证**: 需要 JWT Token

**请求示例**:
```bash
curl -X DELETE https://api.mail.tm/accounts/6a0daa09d2df389ac30d54bc \
  -H "Authorization: Bearer {token}"
```

**成功响应** (204 No Content)

---

## 🔄 使用流程

### 完整使用示例

```python
from mailtm_client import MailTmClient

# 1. 创建客户端
client = MailTmClient()

# 2. 创建账户
email, password = client.create_account()
print(f"邮箱地址: {email}")

# 3. 获取 Token
client.get_token()

# 4. 获取账户信息
info = client.get_account_info()
print(f"配额: {info['quota']} 字节")

# 5. 等待接收邮件
messages = client.wait_for_message(timeout=300, check_interval=10)

# 6. 读取邮件
if messages:
    for msg in messages:
        detail = client.get_message(msg['id'])
        print(f"发件人: {detail['from']['address']}")
        print(f"主题: {detail['subject']}")
        print(f"内容: {detail['text']}")
        
        # 标记为已读
        client.mark_as_read(msg['id'])

# 7. 清理
client.close()
```

### 工作流程图

```
1. 获取可用域名
   ↓
2. 创建账户 (address + password)
   ↓
3. 获取 JWT Token
   ↓
4. 使用 Token 访问 API
   ↓
5. 获取邮件列表
   ↓
6. 读取邮件详情
   ↓
7. 标记/删除邮件
   ↓
8. 删除账户（可选）
```

---

## 🐍 Python客户端实现

完整的 Python 客户端实现请参考：[`mailtm_client.py`](./mailtm_client.py)

### 快速开始

```python
from mailtm_client import MailTmClient

# 使用上下文管理器
with MailTmClient() as client:
    # 创建账户并获取 Token
    email, password = client.create_account()
    client.get_token()
    
    # 获取邮件
    messages = client.get_messages()
    print(f"收到 {len(messages)} 封邮件")
```

### 主要功能

- ✅ 自动域名选择
- ✅ 账户创建和管理
- ✅ JWT Token 自动刷新
- ✅ 邮件接收和读取
- ✅ 邮件标记和删除
- ✅ 速率限制处理
- ✅ 错误重试机制
- ✅ 上下文管理器支持

---

## 🎯 技术特性

### 1. API 设计

**API 标准**: JSON-LD + Hydra
- 使用 JSON-LD 上下文
- 支持 Hydra 集合
- RESTful 设计原则

**响应格式**: 
- 所有响应使用 JSON
- 包含 `@context`, `@id`, `@type` 元数据
- 集合使用 `hydra:member` 数组

### 2. 安全特性

- ✅ HTTPS 加密（强制）
- ✅ JWT 认证
- ✅ 密码哈希存储
- ✅ 速率限制（8 QPS）
- ❌ 无 CSRF 保护（API only）
- ❌ 无 reCAPTCHA（完全开放）

### 3. 性能优化

- **速率限制**: 8 QPS（每秒8个请求）
- **Token 缓存**: JWT Token 有效期1小时
- **响应压缩**: 支持 gzip
- **CDN**: 使用 Cloudflare

### 4. 开源特性

- **完全免费**: 无需注册或 API Key
- **开源项目**: https://github.com/mail-tm/mail-tm
- **API 文档**: 完整的 OpenAPI 规范
- **社区支持**: 活跃的开发社区

---

## ⚠️ 限制和约束

### 1. 速率限制

- **请求频率**: 8 QPS（每秒8个请求）
- **建议间隔**: 125ms（0.125秒）
- **超限处理**: 返回 429 状态码

### 2. 数据限制

- **邮箱配额**: 40 MB
- **邮件大小**: 无明确限制
- **附件支持**: ✅ 支持
- **邮箱保留**: 永久（直到删除）

### 3. 功能限制

- **域名数量**: 当前仅1个可用域名（wshu.net）
- **并发连接**: 无明确限制
- **Token 有效期**: 1小时
- **账户数量**: 无限制

---

## 🔧 错误处理

### HTTP状态码

| 状态码 | 含义 | 处理方式 |
|--------|------|----------|
| 200 | 成功 | 正常处理 |
| 201 | 创建成功 | 账户创建成功 |
| 204 | 无内容 | 删除成功 |
| 400 | 错误请求 | 检查参数格式 |
| 401 | 未授权 | Token 无效或过期 |
| 404 | 未找到 | 资源不存在 |
| 422 | 无法处理 | 参数验证失败 |
| 429 | 请求过多 | 触发速率限制 |
| 500 | 服务器错误 | 稍后重试 |

### 错误响应格式

```json
{
  "@context": "/contexts/Error",
  "@type": "hydra:Error",
  "hydra:title": "An error occurred",
  "hydra:description": "Detailed error message"
}
```

### 常见错误及解决方案

1. **401 Unauthorized**
   - 原因：Token 无效或过期
   - 解决方案：重新获取 Token

2. **429 Too Many Requests**
   - 原因：超过速率限制（8 QPS）
   - 解决方案：添加延迟，等待后重试

3. **422 Unprocessable Entity**
   - 原因：参数验证失败
   - 解决方案：检查邮箱格式和密码长度

---

## 💡 最佳实践

### 1. Token 管理

```python
# 自动刷新 Token
def _ensure_authenticated(self):
    if not self.jwt_token:
        self.get_token()
    elif time.time() - self.token_time > 3600:  # 1小时
        self.get_token()
```

### 2. 速率限制处理

```python
# 添加延迟确保不超过 8 QPS
time.sleep(0.125)  # 125ms 延迟
```

### 3. 错误重试

```python
# 实现指数退避重试
for attempt in range(max_retries):
    try:
        return self._request(method, url, **kwargs)
    except Exception as e:
        if attempt == max_retries - 1:
            raise
        delay = retry_delay * (2 ** attempt)
        time.sleep(delay)
```

### 4. 资源清理

```python
# 使用上下文管理器
with MailTmClient() as client:
    # 使用客户端
    pass
# 自动清理资源
```

---

## 📝 注意事项

1. **完全免费** - Mail.tm 是完全免费的服务，无需 API Key
2. **速率限制** - 遵守 8 QPS 限制，避免被封禁
3. **Token 有效期** - JWT Token 有效期为1小时，需定期刷新
4. **数据隐私** - 不要用于处理敏感信息
5. **开源项目** - 这是一个开源项目，可能随时变更
6. **域名变化** - 可用域名可能会变化
7. **邮箱配额** - 每个邮箱有 40MB 配额限制
8. **永久保留** - 邮箱不会自动删除，需手动删除

---

## 🔄 更新日志

### Version 1.0.0 (2026-05-20)

**初始版本**
- ✅ 完成 API 端点分析
- ✅ 实现 Python 客户端
- ✅ 编写完整文档
- ✅ 添加测试脚本
- ✅ 所有测试通过

**核心功能**
- ✅ 账户创建和管理
- ✅ JWT 认证
- ✅ 邮件接收和读取
- ✅ 邮件标记和删除
- ✅ 速率限制处理
- ✅ 错误重试机制

---

## 📚 参考资源

### 官方资源
- 官方网站: https://mail.tm/
- API 文档: https://docs.mail.tm/
- 交互式 API: https://api.mail.tm/
- GitHub 仓库: https://github.com/mail-tm/mail-tm

### 项目文档
- [`mailtm_client.py`](./mailtm_client.py) - Python 客户端实现
- [`05_20260520_test_mailtm.py`](../tests/05_20260520_test_mailtm.py) - 测试脚本
- [`SERVICES_COMPARISON.md`](../docs/SERVICES_COMPARISON.md) - 服务对比
- [`SERVICE_CLASSIFICATION_AND_QUEUE.md`](../docs/SERVICE_CLASSIFICATION_AND_QUEUE.md) - 服务分类

### 技术栈
- **后端**: Symfony (PHP)
- **API**: JSON-LD + Hydra
- **认证**: JWT
- **部署**: Cloudflare CDN

---

## 📞 联系方式

**文档维护者**: IBM CrazyMail Project  
**创建日期**: 2026-05-20  
**最后更新**: 2026-05-20  
**版本**: 1.0.0  
**状态**: 完成 ✅

---

**免责声明**: 本文档基于逆向工程分析，仅供学习和研究目的。Mail.tm 是一个开源项目，使用时请遵守其服务条款和相关法律法规。

---

<div align="center">

**📖 [返回文档中心](../docs/) | 🏠 [返回主页](../README.md)**

</div>