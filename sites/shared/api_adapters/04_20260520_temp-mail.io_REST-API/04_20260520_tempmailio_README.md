# Temp-Mail.io API 逆向工程

> 📅 创建日期: 2026-05-20  
> 📊 版本: 1.0.0  
> ✅ 状态: 完成  
> 🧪 测试状态: 待测试

---

## 📋 项目概述

本项目是对 [Temp-Mail.io](https://temp-mail.io/) 临时邮箱服务的完整API逆向工程，包括API文档、Python客户端实现和测试脚本。

### 主要特性

- ✅ 完整的API文档（625行）
- ✅ 功能完善的Python客户端（428行）
- ✅ 全面的测试套件（268行）
- ✅ 支持真实邮件接收测试
- ✅ 上下文管理器支持
- ✅ 完善的错误处理和重试机制

---

## 📁 项目结构

```
04_20260520_temp-mail.io_REST-API/
├── API_DOCUMENTATION.md      # 完整API文档（625行）
├── tempmailio_client.py      # Python客户端实现（428行）
├── test_tempmailio.py         # 测试脚本（268行）
└── README.md                  # 本文件
```

---

## 🚀 快速开始

### 安装依赖

```bash
pip install requests
```

### 基本使用

```python
from tempmailio_client import TempMailIOClient

# 创建客户端
with TempMailIOClient() as client:
    # 创建临时邮箱
    email, token = client.create_mailbox()
    print(f"邮箱地址: {email}")
    
    # 获取可用域名
    domains = client.get_domains()
    print(f"可用域名: {len(domains)} 个")
    
    # 等待接收邮件
    messages = client.wait_for_message(timeout=60)
    for msg in messages:
        print(f"收到邮件: {msg['subject']}")
```

---

## 🔌 API端点

### 1. 创建新邮箱

```http
POST /api/v3/email/new
```

**请求体**:
```json
{
  "min_name_length": 10,
  "max_name_length": 10
}
```

**响应**:
```json
{
  "email": "v1ehqgbcgc@gmeenramy.com",
  "token": "ijadPWbf7Y9w2WrFiuuE"
}
```

### 2. 获取邮件列表

```http
GET /api/v3/email/{email}/messages
```

**响应**:
```json
[
  {
    "id": "message_id",
    "from": "sender@example.com",
    "subject": "Test Email",
    "date": "2026-05-20T10:30:00Z",
    "body_text": "Email content",
    "body_html": "<p>Email content</p>"
  }
]
```

### 3. 获取可用域名

```http
GET /api/v4/domains
```

**响应**:
```json
{
  "domains": [
    {
      "name": "bltiwd.com",
      "type": "public",
      "forward_available": true,
      "forward_max_seconds": 7776000
    }
  ]
}
```

---

## 🧪 运行测试

### 快速测试（跳过邮件接收）

```bash
cd D:\Xcode\20260519_IBM_CrazyMail\04_20260520_temp-mail.io_REST-API
python test_tempmailio.py --mode quick
```

### 完整测试（包括邮件接收）

```bash
python test_tempmailio.py --mode full
```

**注意**: 完整测试需要使用Mailfence账号发送测试邮件。

---

## 📊 测试结果

### 测试覆盖

- ✅ 创建邮箱
- ✅ 获取域名列表
- ✅ 获取邮件列表
- ⏳ 真实邮件接收（待测试）
- ✅ 上下文管理器

### 测试统计

- 总测试数: 5
- 已通过: 4
- 待测试: 1（真实邮件接收）

---

## 💻 Python客户端API

### TempMailIOClient

主要客户端类，提供所有API功能。

#### 初始化

```python
client = TempMailIOClient(
    base_url="https://api.internal.temp-mail.io/api",
    timeout=30,
    max_retries=3,
    retry_delay=2
)
```

#### 方法

##### create_mailbox()

创建新的临时邮箱。

```python
email, token = client.create_mailbox(
    min_name_length=10,
    max_name_length=10
)
```

**返回**: `tuple[str, str]` - (邮箱地址, 认证令牌)

##### get_messages()

获取邮箱中的所有邮件。

```python
messages = client.get_messages(email=None)
```

**参数**:
- `email` (Optional[str]): 邮箱地址，默认使用当前邮箱

**返回**: `List[Dict[str, Any]]` - 邮件列表

##### get_domains()

获取所有可用的邮箱域名。

```python
domains = client.get_domains()
```

**返回**: `List[Dict[str, Any]]` - 域名列表

##### wait_for_message()

等待接收邮件（轮询方式）。

```python
messages = client.wait_for_message(
    email=None,
    timeout=300,
    poll_interval=5,
    expected_count=1
)
```

**参数**:
- `email` (Optional[str]): 邮箱地址
- `timeout` (int): 最大等待时间（秒）
- `poll_interval` (int): 轮询间隔（秒）
- `expected_count` (int): 期望接收的邮件数量

**返回**: `List[Dict[str, Any]]` - 接收到的邮件列表

##### get_message_content()

获取邮件的文本内容。

```python
content = client.get_message_content(message)
```

**参数**:
- `message` (Dict[str, Any]): 邮件对象

**返回**: `str` - 邮件文本内容

---

## 🎯 技术特性

### 优点

1. **简单易用**: API设计简洁，易于集成
2. **无需注册**: 不需要账号即可使用
3. **多域名支持**: 提供多个公共域名选择
4. **邮件转发**: 支持邮件转发功能
5. **实时更新**: 通过轮询可以实时获取新邮件

### 技术亮点

1. **RESTful设计**: 遵循REST API设计规范
2. **JSON格式**: 使用标准JSON格式交换数据
3. **自定义认证**: 使用自定义请求头进行认证
4. **版本控制**: API路径包含版本号（v3, v4）

---

## ⚠️ 限制和约束

### 已知限制

1. **邮箱生命周期**: 邮箱的具体保留时间未明确说明
2. **速率限制**: 未明确说明API调用频率限制
3. **邮件大小限制**: 未明确说明单封邮件大小限制
4. **附件支持**: 未确认是否支持附件
5. **邮件保留期**: 未明确说明邮件在邮箱中的保留时间

### 使用约束

1. 需要包含特定的请求头才能正常访问API
2. 邮箱用户名长度受min_name_length和max_name_length参数限制
3. 需要通过轮询方式检查新邮件（无WebSocket或推送机制）

---

## 💡 最佳实践

### 1. 使用上下文管理器

```python
with TempMailIOClient() as client:
    email, token = client.create_mailbox()
    # 使用客户端...
# 自动关闭连接
```

### 2. 错误处理

```python
from tempmailio_client import TempMailIOClient, TempMailIOError

try:
    client = TempMailIOClient()
    email, token = client.create_mailbox()
except TempMailIOError as e:
    print(f"API错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

### 3. 轮询策略

```python
# 使用指数退避策略
messages = client.wait_for_message(
    timeout=300,      # 5分钟超时
    poll_interval=5,  # 初始5秒间隔
    expected_count=1  # 期望1封邮件
)
```

---

## 📝 注意事项

### 安全性

1. **不要用于敏感信息**: 临时邮箱不应用于接收敏感或重要信息
2. **公开性质**: 所有邮件都可能被他人访问
3. **无加密保证**: 邮件内容可能未加密传输

### 稳定性

1. **服务可用性**: 服务可能随时变更或停止
2. **API变更**: API端点和参数可能在未通知的情况下变更
3. **数据持久性**: 邮件和邮箱可能随时被删除

### 合规性

1. **使用条款**: 使用前应阅读并遵守服务条款
2. **滥用防范**: 避免用于垃圾邮件或恶意用途
3. **频率限制**: 遵守合理的API调用频率

---

## 🔗 相关资源

- **官方网站**: https://temp-mail.io/
- **API文档**: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **Python客户端**: [tempmailio_client.py](./tempmailio_client.py)
- **测试脚本**: [test_tempmailio.py](./test_tempmailio.py)
- **项目主页**: D:\Xcode\20260519_IBM_CrazyMail\

---

## 📊 更新日志

### v1.0.0 (2026-05-20)

- ✅ 完成API逆向工程
- ✅ 识别3个主要API端点
- ✅ 创建完整API文档（625行）
- ✅ 实现Python客户端（428行）
- ✅ 创建测试套件（268行）
- 📝 待进行真实邮件测试

---

## 📞 技术支持

如有问题或建议，请参考项目文档或提交Issue。

---

**文档版本**: 1.0.0  
**最后更新**: 2026-05-20  
**维护者**: Bob (AI Assistant)