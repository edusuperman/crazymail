# Email Generator (generator.email) Python 客户端

一个功能完整的Python客户端，用于与Email Generator临时邮箱服务交互。

## 📋 目录

- [特性](#特性)
- [快速开始](#快速开始)
- [安装](#安装)
- [使用示例](#使用示例)
- [API参考](#api参考)
- [测试](#测试)
- [常见问题](#常见问题)
- [贡献](#贡献)

---

## ✨ 特性

- ✅ **无需认证** - 完全公开访问，无需API密钥
- ✅ **自定义邮箱** - 支持自定义用户名和域名
- ✅ **90+域名** - 提供多个可用域名选择
- ✅ **域名搜索** - 支持TypeAhead搜索功能
- ✅ **邮件管理** - 获取、删除、标记邮件
- ✅ **等待邮件** - 自动轮询等待新邮件
- ✅ **错误处理** - 完善的异常处理机制
- ✅ **类型提示** - 完整的类型注解
- ✅ **日志记录** - 详细的操作日志

---

## 🚀 快速开始

### 创建临时邮箱

```python
from generatoremail_client import GeneratorEmailClient

# 创建客户端
client = GeneratorEmailClient()

# 创建随机邮箱
email = client.create_mailbox()
print(f"邮箱地址: {email}")
print(f"访问URL: {client.get_mailbox_url()}")

# 检查邮件
messages = client.get_messages()
print(f"收到 {len(messages)} 封邮件")
```

### 等待验证邮件

```python
# 创建邮箱
client = GeneratorEmailClient()
email = client.create_mailbox()
print(f"请向 {email} 发送验证邮件")

# 等待邮件（最多60秒）
message = client.wait_for_message(
    timeout=60,
    subject_filter="Verification"
)

if message:
    print(f"收到验证邮件: {message['subject']}")
else:
    print("未收到邮件")
```

---

## 📦 安装

### 依赖项

```bash
pip install requests beautifulsoup4
```

### 文件结构

```
10_20260521_generator.email_REST-API/
├── generatoremail_client.py          # 主客户端
├── 10_20260521_generatoremail_API_DOCUMENTATION.md  # API文档
└── 10_20260521_generatoremail_README.md             # 本文件
```

---

## 📖 使用示例

### 1. 基本使用

```python
from generatoremail_client import GeneratorEmailClient

# 创建客户端
client = GeneratorEmailClient()

# 创建邮箱
email = client.create_mailbox()
print(f"邮箱: {email}")

# 获取邮件
messages = client.get_messages()
for msg in messages:
    print(f"发件人: {msg['from']}")
    print(f"主题: {msg['subject']}")
```

### 2. 自定义邮箱

```python
# 搜索可用域名
domains = client.search_domains(".com", limit=10)
print(f"找到 {len(domains)} 个.com域名")

# 使用指定域名创建邮箱
email = client.create_mailbox(
    username="myuser",
    domain=domains[0]
)
print(f"自定义邮箱: {email}")
```

### 3. 域名管理

```python
# 获取所有可用域名（带缓存）
all_domains = client.get_available_domains()
print(f"共有 {len(all_domains)} 个可用域名")

# 按后缀分类
com_domains = [d for d in all_domains if d.endswith('.com')]
org_domains = [d for d in all_domains if d.endswith('.org')]

print(f".com域名: {len(com_domains)}个")
print(f".org域名: {len(org_domains)}个")
```

### 4. 邮箱状态检查

```python
# 创建邮箱
email = client.create_mailbox()

# 检查状态
status = client.check_mailbox_status()
print(f"状态: {status['status']}")
print(f"运行时间: {status['uptime']}天")
print(f"邮箱: {status['email']}")
```

### 5. 邮件管理

```python
# 创建邮箱
client.create_mailbox()

# 标记所有邮件为已读
client.mark_all_as_read()

# 删除所有邮件
client.delete_all_messages()

# 删除单个邮件
messages = client.get_messages()
if messages:
    client.delete_message(messages[0]['id'])
```

### 6. 等待新邮件

```python
# 创建邮箱
email = client.create_mailbox()
print(f"邮箱: {email}")

# 等待包含特定主题的邮件
message = client.wait_for_message(
    timeout=120,           # 最多等待120秒
    check_interval=5,      # 每5秒检查一次
    subject_filter="验证"  # 主题包含"验证"
)

if message:
    print(f"收到邮件!")
    print(f"发件人: {message['from']}")
    print(f"主题: {message['subject']}")
    print(f"日期: {message['date']}")
```

### 7. 错误处理

```python
from generatoremail_client import (
    GeneratorEmailClient,
    GeneratorEmailAPIError,
    DomainNotAvailableError
)

client = GeneratorEmailClient()

try:
    # 尝试使用无效域名
    email = client.create_mailbox(
        username="test",
        domain="invalid-domain.com"
    )
except DomainNotAvailableError as e:
    print(f"域名不可用: {e}")
    # 使用随机域名
    email = client.create_mailbox()
    print(f"使用随机邮箱: {email}")

try:
    # 未创建邮箱时获取邮件
    messages = client.get_messages()
except GeneratorEmailAPIError as e:
    print(f"错误: {e}")
```

### 8. 自定义配置

```python
# 自定义超时和重试
client = GeneratorEmailClient(
    base_url="https://generator.email",
    timeout=60,        # 60秒超时
    max_retries=5,     # 最多重试5次
    retry_delay=3      # 重试间隔3秒
)

# 创建邮箱
email = client.create_mailbox()
```

---

## 📚 API参考

### GeneratorEmailClient

#### 初始化

```python
client = GeneratorEmailClient(
    base_url: str = "https://generator.email",
    timeout: int = 30,
    max_retries: int = 3,
    retry_delay: int = 2
)
```

#### 主要方法

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `search_domains(query, limit)` | 搜索域名 | `List[str]` |
| `get_available_domains(force_refresh)` | 获取所有域名 | `List[str]` |
| `create_mailbox(username, domain)` | 创建邮箱 | `str` |
| `check_mailbox_status(username, domain)` | 检查状态 | `Dict` |
| `get_messages(email_address)` | 获取邮件列表 | `List[Dict]` |
| `get_message_content(message_id)` | 获取邮件内容 | `Dict` |
| `delete_message(message_id)` | 删除邮件 | `bool` |
| `delete_all_messages(email_address)` | 删除所有邮件 | `bool` |
| `mark_all_as_read(email_address)` | 标记已读 | `bool` |
| `wait_for_message(timeout, check_interval, subject_filter)` | 等待邮件 | `Optional[Dict]` |
| `get_mailbox_url()` | 获取邮箱URL | `str` |

#### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `username` | `Optional[str]` | 当前用户名 |
| `domain` | `Optional[str]` | 当前域名 |
| `email_address` | `Optional[str]` | 完整邮箱地址 |

### 异常类

| 异常 | 说明 |
|------|------|
| `GeneratorEmailAPIError` | API错误基类 |
| `EmailNotFoundError` | 邮件未找到 |
| `DomainNotAvailableError` | 域名不可用 |

---

## 🧪 测试

### 运行测试

```bash
# 运行完整测试套件
python tests/10_20260521_test_generatoremail.py
```

### 测试覆盖

测试套件包含8个测试用例：

1. ✅ 域名搜索
2. ✅ 获取所有可用域名
3. ✅ 创建邮箱
4. ✅ 检查邮箱状态
5. ✅ 获取邮件列表
6. ✅ 邮箱操作
7. ✅ 等待新邮件
8. ✅ 错误处理

**测试结果**: 8/8 通过 (100%)

### 测试输出示例

```
============================================================
Email Generator API 测试套件
============================================================
开始时间: 2026-05-22 02:18:37

============================================================
测试 1: 域名搜索
============================================================
搜索.com域名...
[OK] 找到 10 个.com域名

============================================================
测试总结
============================================================
[OK] 通过: 域名搜索
[OK] 通过: 获取所有可用域名
[OK] 通过: 创建邮箱
[OK] 通过: 检查邮箱状态
[OK] 通过: 获取邮件列表
[OK] 通过: 邮箱操作
[OK] 通过: 等待新邮件
[OK] 通过: 错误处理

总计: 8/8 测试通过
成功率: 100.0%
```

---

## ❓ 常见问题

### Q1: 如何选择稳定的域名？

**A**: 选择运行时间长的域名：

```python
# 获取所有域名
domains = client.get_available_domains()

# 测试每个域名的运行时间
stable_domains = []
for domain in domains:
    try:
        status = client.check_mailbox_status(
            username="test",
            domain=domain
        )
        uptime = int(status.get('uptime', 0))
        if uptime > 30:  # 运行超过30天
            stable_domains.append((domain, uptime))
    except:
        pass

# 按运行时间排序
stable_domains.sort(key=lambda x: x[1], reverse=True)
print(f"最稳定的域名: {stable_domains[0][0]} ({stable_domains[0][1]}天)")
```

### Q2: 如何处理邮件接收延迟？

**A**: 使用`wait_for_message`方法：

```python
# 设置较长的超时时间和检查间隔
message = client.wait_for_message(
    timeout=300,        # 5分钟
    check_interval=10   # 每10秒检查
)
```

### Q3: 如何获取邮件的完整内容？

**A**: 当前API主要支持邮件列表。完整内容需要访问详情页面：

```python
messages = client.get_messages()
if messages:
    # 获取第一封邮件的详细内容
    detail = client.get_message_content(messages[0]['id'])
    print(detail['body_text'])
```

### Q4: 邮箱会过期吗？

**A**: 邮箱本身不会过期，但域名可能失效。建议：

```python
# 定期检查邮箱状态
status = client.check_mailbox_status()
if status['status'] != 'good':
    # 域名失效，创建新邮箱
    new_email = client.create_mailbox()
```

### Q5: 如何处理网络错误？

**A**: 客户端内置重试机制：

```python
# 自定义重试参数
client = GeneratorEmailClient(
    max_retries=5,    # 最多重试5次
    retry_delay=3     # 每次重试间隔3秒
)
```

### Q6: 可以同时使用多个邮箱吗？

**A**: 可以，创建多个客户端实例：

```python
# 邮箱1
client1 = GeneratorEmailClient()
email1 = client1.create_mailbox()

# 邮箱2
client2 = GeneratorEmailClient()
email2 = client2.create_mailbox()

# 分别检查邮件
messages1 = client1.get_messages()
messages2 = client2.get_messages()
```

---

## 🔧 高级用法

### 批量创建邮箱

```python
def create_multiple_mailboxes(count: int) -> List[str]:
    """批量创建邮箱"""
    emails = []
    client = GeneratorEmailClient()
    
    # 获取可用域名
    domains = client.get_available_domains()
    
    for i in range(count):
        try:
            email = client.create_mailbox(
                username=f"user{i}",
                domain=domains[i % len(domains)]
            )
            emails.append(email)
            print(f"创建邮箱 {i+1}/{count}: {email}")
        except Exception as e:
            print(f"创建失败: {e}")
    
    return emails

# 创建10个邮箱
emails = create_multiple_mailboxes(10)
```

### 邮件内容过滤

```python
def filter_messages(client, sender_filter=None, subject_filter=None):
    """过滤邮件"""
    messages = client.get_messages()
    filtered = []
    
    for msg in messages:
        # 发件人过滤
        if sender_filter and sender_filter not in msg.get('from', ''):
            continue
        
        # 主题过滤
        if subject_filter and subject_filter not in msg.get('subject', ''):
            continue
        
        filtered.append(msg)
    
    return filtered

# 使用示例
client = GeneratorEmailClient()
client.create_mailbox()

# 只获取来自特定发件人的邮件
messages = filter_messages(
    client,
    sender_filter="noreply@example.com"
)
```

### 自动化测试集成

```python
import unittest

class EmailTestCase(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        self.client = GeneratorEmailClient()
        self.email = self.client.create_mailbox()
    
    def test_receive_verification_email(self):
        """测试接收验证邮件"""
        # 触发验证邮件发送
        send_verification_email(self.email)
        
        # 等待邮件
        message = self.client.wait_for_message(
            timeout=60,
            subject_filter="Verification"
        )
        
        self.assertIsNotNone(message)
        self.assertIn("Verification", message['subject'])
    
    def tearDown(self):
        """测试后清理"""
        self.client.delete_all_messages()

if __name__ == '__main__':
    unittest.main()
```

---

## 📊 性能优化

### 1. 域名缓存

```python
# 域名列表会自动缓存1小时
domains = client.get_available_domains()  # 第一次：6秒
domains = client.get_available_domains()  # 第二次：0秒（使用缓存）

# 强制刷新
domains = client.get_available_domains(force_refresh=True)
```

### 2. 连接复用

```python
# 客户端使用requests.Session，自动复用连接
client = GeneratorEmailClient()

# 多次请求会复用同一个连接
for i in range(10):
    status = client.check_mailbox_status()
```

### 3. 批量操作

```python
# 一次性删除所有邮件（比逐个删除快）
client.delete_all_messages()

# 一次性标记所有为已读
client.mark_all_as_read()
```

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

### 开发环境设置

```bash
# 克隆仓库
git clone <repository-url>

# 安装依赖
pip install -r requirements.txt

# 运行测试
python tests/10_20260521_test_generatoremail.py
```

### 代码规范

- 遵循PEP 8
- 使用类型提示
- 编写文档字符串
- 添加单元测试

---

## 📄 许可证

本项目仅供学习和研究使用。请遵守Email Generator服务条款。

---

## 📞 联系方式

- **项目**: IBM CrazyMail - 临时邮箱API逆向工程
- **作者**: Bob (AI Assistant)
- **日期**: 2026-05-21
- **版本**: 1.0.0

---

## 🔗 相关链接

- [Email Generator官网](https://generator.email)
- [API文档](10_20260521_generatoremail_API_DOCUMENTATION.md)
- [测试脚本](../tests/10_20260521_test_generatoremail.py)
- [API分析](../assets/10_generator.email/generator_email_api_analysis.md)

---

**最后更新**: 2026-05-21  
**文档版本**: 1.0.0