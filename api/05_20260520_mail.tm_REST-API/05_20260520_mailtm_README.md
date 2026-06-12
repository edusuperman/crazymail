# Mail.tm REST API 客户端

> 📧 **完全免费的临时邮箱服务** | 🔐 **JWT 认证** | 🚀 **8 QPS 速率限制**

---

## 📋 项目信息

- **服务名称**: Mail.tm
- **官方网站**: https://mail.tm/
- **API 文档**: https://docs.mail.tm/
- **项目状态**: ✅ 完成
- **测试状态**: ✅ 已测试
- **创建日期**: 2026-05-20
- **版本**: 1.0.0

---

## 🌟 服务特点

### 核心优势

- ✅ **完全免费** - 无需注册或 API Key
- ✅ **开源项目** - GitHub 上的开源实现
- ✅ **REST API** - 标准的 RESTful API 设计
- ✅ **JWT 认证** - 安全的 Token 认证机制
- ✅ **JSON-LD** - 使用 JSON-LD + Hydra 标准
- ✅ **永久保留** - 邮箱不会自动删除
- ✅ **40MB 配额** - 每个邮箱 40MB 存储空间

### 技术规格

| 项目 | 值 |
|------|-----|
| API 基础URL | `https://api.mail.tm` |
| 认证方式 | JWT (JSON Web Token) |
| 速率限制 | 8 QPS (每秒8个请求) |
| Token 有效期 | 1小时 |
| 邮箱配额 | 40 MB |
| 响应格式 | JSON (JSON-LD) |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 基础使用

```python
from mailtm_client import MailTmClient

# 创建客户端
with MailTmClient() as client:
    # 创建账户
    email, password = client.create_account()
    print(f"临时邮箱: {email}")
    print(f"密码: {password}")
    
    # 获取 Token
    client.get_token()
    
    # 等待接收邮件
    messages = client.wait_for_message(timeout=300, check_interval=10)
    
    # 读取邮件
    if messages:
        for msg in messages:
            detail = client.get_message(msg['id'])
            print(f"发件人: {detail['from']['address']}")
            print(f"主题: {detail['subject']}")
            print(f"内容: {detail['text']}")
```

### 3. 运行测试

```bash
# 运行完整测试套件
python tests/05_20260520_test_mailtm.py

# 运行客户端示例
python 05_20260520_mail.tm_REST-API/mailtm_client.py
```

---

## 📚 API 端点

### 核心端点

| 端点 | 方法 | 描述 | 认证 |
|------|------|------|------|
| `/domains` | GET | 获取可用域名 | ❌ |
| `/accounts` | POST | 创建账户 | ❌ |
| `/token` | POST | 获取 JWT Token | ❌ |
| `/accounts/{id}` | GET | 获取账户信息 | ✅ |
| `/messages` | GET | 获取邮件列表 | ✅ |
| `/messages/{id}` | GET | 获取邮件详情 | ✅ |
| `/messages/{id}` | PATCH | 标记邮件 | ✅ |
| `/messages/{id}` | DELETE | 删除邮件 | ✅ |
| `/accounts/{id}` | DELETE | 删除账户 | ✅ |

---

## 💻 客户端功能

### MailTmClient 类

```python
class MailTmClient:
    """Mail.tm API 客户端"""
    
    # 域名管理
    def get_domains() -> List[Dict]
    
    # 账户管理
    def create_account(address=None, password=None) -> tuple[str, str]
    def get_token(address=None, password=None) -> str
    def get_account_info(account_id=None) -> Dict
    def delete_account(account_id=None) -> bool
    
    # 邮件管理
    def get_messages(page=1) -> List[Dict]
    def get_message(message_id) -> Dict
    def mark_as_read(message_id) -> bool
    def delete_message(message_id) -> bool
    
    # 工具方法
    def wait_for_message(timeout=300, check_interval=10) -> Optional[List[Dict]]
```

### 主要特性

- ✅ **自动域名选择** - 自动选择可用域名
- ✅ **Token 管理** - 自动刷新过期 Token
- ✅ **速率限制** - 内置 125ms 延迟
- ✅ **错误重试** - 指数退避重试机制
- ✅ **上下文管理** - 支持 with 语句
- ✅ **类型提示** - 完整的类型注解
- ✅ **日志记录** - 详细的操作日志

---

## 📖 使用示例

### 示例 1: 创建账户并接收邮件

```python
from mailtm_client import MailTmClient

client = MailTmClient()

# 创建账户
email, password = client.create_account()
print(f"邮箱: {email}")

# 获取 Token
client.get_token()

# 等待邮件
print("等待接收邮件...")
messages = client.wait_for_message(timeout=300)

if messages:
    print(f"收到 {len(messages)} 封邮件")
else:
    print("未收到邮件")

client.close()
```

### 示例 2: 使用现有账户

```python
from mailtm_client import MailTmClient

client = MailTmClient()

# 使用现有账户登录
email = "existing@wshu.net"
password = "your_password"
client.get_token(email, password)

# 获取邮件列表
messages = client.get_messages()
print(f"收件箱中有 {len(messages)} 封邮件")

# 读取第一封邮件
if messages:
    detail = client.get_message(messages[0]['id'])
    print(f"主题: {detail['subject']}")
    print(f"内容: {detail['text']}")

client.close()
```

### 示例 3: 邮件管理

```python
from mailtm_client import MailTmClient

with MailTmClient() as client:
    # 登录
    client.email_address = "your@wshu.net"
    client.password = "your_password"
    client.get_token()
    
    # 获取所有邮件
    messages = client.get_messages()
    
    for msg in messages:
        # 标记为已读
        client.mark_as_read(msg['id'])
        
        # 删除邮件
        client.delete_message(msg['id'])
    
    print("所有邮件已处理")
```

---

## 🧪 测试

### 测试覆盖

测试脚本 [`05_20260520_test_mailtm.py`](../tests/05_20260520_test_mailtm.py) 包含以下测试：

1. ✅ **获取可用域名** - 测试域名列表获取
2. ✅ **创建账户** - 测试账户创建功能
3. ✅ **获取 Token** - 测试 JWT 认证
4. ✅ **获取账户信息** - 测试账户信息查询
5. ✅ **获取邮件列表** - 测试邮件列表获取
6. ✅ **完整工作流程** - 测试端到端流程

### 运行测试

```bash
# 运行所有测试
python tests/05_20260520_test_mailtm.py

# 预期输出
Mail.tm API 客户端测试
============================================================
测试 1: 获取可用域名
============================================================
[OK] 找到 1 个可用域名
  - wshu.net

============================================================
测试 2: 创建账户
============================================================
[OK] 账户创建成功
  邮箱: test@wshu.net
  密码: ************
  账户ID: ************

...

============================================================
所有测试通过！[OK]
============================================================
```

---

## ⚠️ 注意事项

### 速率限制

Mail.tm 有 **8 QPS** 的速率限制：

```python
# 客户端自动添加延迟
time.sleep(0.125)  # 125ms 延迟确保不超过 8 QPS
```

### Token 管理

JWT Token 有效期为 **1小时**：

```python
# 客户端自动检查并刷新 Token
def _ensure_authenticated(self):
    if not self.jwt_token:
        self.get_token()
    elif time.time() - self.token_time > 3600:  # 1小时
        self.get_token()
```

### 最佳实践

1. **使用上下文管理器** - 确保资源正确清理
2. **遵守速率限制** - 避免过快请求
3. **处理错误** - 实现完善的错误处理
4. **定期刷新 Token** - Token 有效期为1小时
5. **不存储敏感信息** - 这是临时邮箱服务

---

## 📁 项目结构

```
05_20260520_mail.tm_REST-API/
├── mailtm_client.py                          # Python 客户端实现
├── 05_20260520_mailtm_API_DOCUMENTATION.md   # 完整 API 文档
└── 05_20260520_mailtm_README.md              # 本文件

tests/
└── 05_20260520_test_mailtm.py                # 测试脚本
```

---

## 🔗 相关文档

- [API 文档](./05_20260520_mailtm_API_DOCUMENTATION.md) - 完整的 API 端点文档
- [测试脚本](../tests/05_20260520_test_mailtm.py) - 完整的测试套件
- [服务对比](../docs/SERVICES_COMPARISON.md) - 与其他服务的对比
- [服务分类](../docs/SERVICE_CLASSIFICATION_AND_QUEUE.md) - 服务评估和分类

---

## 📊 服务评分

根据项目评估体系，Mail.tm 获得 **S级（95分）**：

| 维度 | 得分 | 权重 | 加权得分 |
|------|------|------|----------|
| 技术可行性 | 100 | 30% | 30.0 |
| 商业价值 | 95 | 25% | 23.75 |
| 学习价值 | 95 | 20% | 19.0 |
| 逆向难度 | 95 | 15% | 14.25 |
| 项目适配度 | 95 | 10% | 9.5 |
| **总分** | **96.5** | **100%** | **96.5** |

### 评分理由

**优势**：
- ✅ 完全免费，无需 API Key
- ✅ 开源项目，代码透明
- ✅ 标准 REST API，易于集成
- ✅ JWT 认证，安全可靠
- ✅ 完整的 API 文档
- ✅ 活跃的社区支持

**劣势**：
- ⚠️ 速率限制较严格（8 QPS）
- ⚠️ 可用域名较少（当前仅1个）

---

## 🤝 贡献

本项目是 IBM CrazyMail 项目的一部分。

---

## 📄 许可证

本项目遵循 MIT 许可证。

---

## 📞 联系方式

**项目**: IBM CrazyMail  
**创建日期**: 2026-05-20  
**版本**: 1.0.0  
**状态**: ✅ 完成

---

<div align="center">

**📖 [API 文档](./05_20260520_mailtm_API_DOCUMENTATION.md) | 🧪 [测试脚本](../tests/05_20260520_test_mailtm.py) | 🏠 [返回主页](../README.md)**

</div>