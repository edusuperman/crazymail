# Guerrilla Mail Python 客户端

Guerrilla Mail 临时邮箱服务的 Python API 客户端实现。

## 特性

- ✅ 即时创建临时邮箱（无需注册）
- ✅ 支持自定义邮箱用户名
- ✅ 邮箱有效期60分钟
- ✅ 支持11种语言
- ✅ 完整的邮件管理功能
- ✅ 自动会话管理
- ✅ 内置错误处理和重试机制
- ✅ 类型提示支持

## 安装

### 依赖

```bash
pip install requests
```

### 文件

将以下文件复制到你的项目：
- `guerrillamail_client.py` - 主客户端文件

## 快速开始

### 基础使用

```python
from guerrillamail_client import GuerrillaMailClient

# 创建客户端
client = GuerrillaMailClient()

# 获取临时邮箱
info = client.get_email_address()
print(f"临时邮箱: {info['email_addr']}")
print(f"有效期: 60分钟")

# 检查邮件
result = client.check_email()
print(f"收到 {len(result['list'])} 封邮件")

# 读取邮件详情
for mail in result['list']:
    detail = client.fetch_email(mail['mail_id'])
    print(f"\n发件人: {detail['mail_from']}")
    print(f"主题: {detail['mail_subject']}")
    print(f"内容: {detail['mail_body'][:200]}...")
```

### 自定义邮箱用户名

```python
# 设置自定义用户名
client.set_email_user('myname')
print(f"自定义邮箱: {client.email_address}")
# 输出: myname@guerrillamailblock.com
```

### 等待新邮件

```python
# 等待邮件到达（最多60秒）
print("等待新邮件...")
mails = client.wait_for_email(timeout=60, check_interval=5)

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
client.del_email([1, 2, 3])  # 删除ID为1,2,3的邮件

# 获取邮件列表（分页）
page1 = client.get_email_list(offset=0)   # 第1-20封
page2 = client.get_email_list(offset=20)  # 第21-40封

# 忘记邮箱（从会话中移除）
client.forget_me()
```

### 多语言支持

```python
# 创建中文界面的客户端
client = GuerrillaMailClient(lang='zh')

# 支持的语言：
# en, fr, nl, ru, tr, uk, ar, ko, jp, zh, zh-hant
```

## API 参考

### GuerrillaMailClient

#### 初始化参数

```python
client = GuerrillaMailClient(
    base_url="http://api.guerrillamail.com",  # API基础URL
    timeout=30,                                # 请求超时（秒）
    max_retries=3,                            # 最大重试次数
    retry_delay=2,                            # 重试延迟（秒）
    lang="en"                                 # 语言代码
)
```

#### 主要方法

##### get_email_address()
获取或创建临时邮箱地址。

```python
info = client.get_email_address()
# 返回: {'email_addr': str, 'email_timestamp': int, 'alias': str, 'sid_token': str}
```

##### set_email_user(email_user: str)
设置自定义邮箱用户名。

```python
info = client.set_email_user('myname')
# 返回: {'email_addr': str, 'email_timestamp': int}
```

##### check_email(seq: int = 0)
检查新邮件。

```python
result = client.check_email()
# 返回: {'list': List[Dict], 'count': str, 'email': str, 'ts': int, 'sid_token': str}
```

##### get_email_list(offset: int = 0, seq: Optional[int] = None)
获取邮件列表（支持分页）。

```python
result = client.get_email_list(offset=0)
# 返回格式同 check_email()
```

##### fetch_email(email_id: int)
获取邮件完整内容。

```python
mail = client.fetch_email(1)
# 返回: {'mail_id': int, 'mail_from': str, 'mail_subject': str, 'mail_body': str, ...}
```

##### del_email(email_ids: List[int])
删除邮件。

```python
result = client.del_email([1, 2, 3])
# 返回: {'deleted_ids': List[int]}
```

##### forget_me(email_addr: Optional[str] = None)
忘记邮箱地址（从会话中移除）。

```python
client.forget_me()
# 返回: bool
```

##### wait_for_email(timeout: int = 60, check_interval: int = 5, min_count: int = 1)
等待新邮件到达。

```python
mails = client.wait_for_email(timeout=60)
# 返回: Optional[List[Dict]]
```

##### get_remaining_time()
获取邮箱剩余有效时间（秒）。

```python
remaining = client.get_remaining_time()
# 返回: Optional[int]
```

##### is_expired()
检查邮箱是否已过期。

```python
if client.is_expired():
    print("邮箱已过期")
# 返回: bool
```

## 错误处理

### 异常类型

```python
from guerrillamail_client import (
    GuerrillaMailAPIError,      # 基础API错误
    AuthenticationError,         # 认证错误
    RateLimitError              # 速率限制错误
)
```

### 错误处理示例

```python
try:
    client = GuerrillaMailClient()
    info = client.get_email_address()
    
except AuthenticationError as e:
    print(f"认证失败: {e}")
    
except RateLimitError as e:
    print(f"请求过于频繁: {e}")
    
except GuerrillaMailAPIError as e:
    print(f"API错误: {e}")
```

## 完整示例

### 示例1: 接收验证邮件

```python
from guerrillamail_client import GuerrillaMailClient
import time

# 创建客户端
client = GuerrillaMailClient()

# 获取邮箱
info = client.get_email_address()
email = info['email_addr']
print(f"临时邮箱: {email}")
print("请使用此邮箱注册服务...")

# 等待验证邮件
print("\n等待验证邮件...")
mails = client.wait_for_email(timeout=120, check_interval=5)

if mails:
    # 查找验证邮件
    for mail in mails:
        if 'verify' in mail['mail_subject'].lower():
            detail = client.fetch_email(mail['mail_id'])
            print(f"\n收到验证邮件:")
            print(f"主题: {detail['mail_subject']}")
            print(f"内容: {detail['mail_body']}")
            break
else:
    print("未收到验证邮件")
```

### 示例2: 自定义邮箱名称

```python
from guerrillamail_client import GuerrillaMailClient

client = GuerrillaMailClient()

# 尝试设置自定义用户名
try:
    custom_name = "myproject_test"
    info = client.set_email_user(custom_name)
    print(f"自定义邮箱: {info['email_addr']}")
    
except Exception as e:
    print(f"用户名已被占用或无效: {e}")
    # 使用默认随机邮箱
    info = client.get_email_address()
    print(f"使用随机邮箱: {info['email_addr']}")
```

### 示例3: 邮件管理

```python
from guerrillamail_client import GuerrillaMailClient

client = GuerrillaMailClient()
client.get_email_address()

# 检查邮件
result = client.check_email()
print(f"收件箱: {len(result['list'])} 封邮件")

# 显示所有邮件
for mail in result['list']:
    print(f"\nID: {mail['mail_id']}")
    print(f"发件人: {mail['mail_from']}")
    print(f"主题: {mail['mail_subject']}")
    print(f"时间: {mail['mail_date']}")
    print(f"大小: {mail['size']} 字节")

# 删除已读邮件
read_ids = [m['mail_id'] for m in result['list'] if m['mail_read'] == 1]
if read_ids:
    client.del_email(read_ids)
    print(f"\n已删除 {len(read_ids)} 封已读邮件")
```

### 示例4: 监控邮箱

```python
from guerrillamail_client import GuerrillaMailClient
import time

client = GuerrillaMailClient()
info = client.get_email_address()
print(f"监控邮箱: {info['email_addr']}")

# 持续监控（直到邮箱过期）
while not client.is_expired():
    result = client.check_email()
    
    if result['list']:
        print(f"\n收到 {len(result['list'])} 封新邮件:")
        for mail in result['list']:
            print(f"- {mail['mail_from']}: {mail['mail_subject']}")
    
    # 显示剩余时间
    remaining = client.get_remaining_time()
    if remaining:
        print(f"剩余时间: {remaining // 60} 分钟")
    
    time.sleep(10)  # 每10秒检查一次

print("邮箱已过期")
```

## 最佳实践

### 1. 会话管理

```python
# ✅ 推荐：保持单一客户端实例
client = GuerrillaMailClient()
client.get_email_address()

# 检查过期
if client.is_expired():
    client.get_email_address()  # 重新创建

# ❌ 避免：频繁创建新实例
for i in range(10):
    client = GuerrillaMailClient()  # 不推荐
```

### 2. 错误处理

```python
# ✅ 推荐：使用内置重试机制
client = GuerrillaMailClient(max_retries=3, retry_delay=2)

# ✅ 推荐：捕获特定异常
try:
    result = client.check_email()
except RateLimitError:
    time.sleep(60)  # 等待后重试
```

### 3. 资源清理

```python
# ✅ 推荐：使用完毕后清理
try:
    client = GuerrillaMailClient()
    # ... 使用邮箱 ...
finally:
    client.forget_me()  # 清理会话
```

### 4. 超时设置

```python
# ✅ 推荐：根据需求设置超时
client = GuerrillaMailClient(timeout=30)

# 等待邮件时使用合理的超时
mails = client.wait_for_email(timeout=120)  # 2分钟
```

## 限制说明

### 邮箱限制
- 有效期固定60分钟，无法延长
- 过期后邮箱和邮件将被删除
- 不支持发送邮件

### API限制
- 速率限制未明确说明，建议合理使用
- 某些POST操作可能需要特殊参数格式
- 无附件下载API

### 功能限制
- 不支持邮件转发
- 不支持邮箱续期
- 不支持附件下载

## 故障排除

### 问题1: 无法获取邮箱

```python
# 检查网络连接
client = GuerrillaMailClient(timeout=60)  # 增加超时时间
```

### 问题2: 邮件未到达

```python
# 使用等待功能
mails = client.wait_for_email(timeout=120, check_interval=10)

# 检查垃圾邮件过滤
# 某些服务可能屏蔽临时邮箱
```

### 问题3: 自定义用户名失败

```python
# 用户名可能已被占用
try:
    client.set_email_user('myname')
except Exception:
    # 使用随机邮箱
    client.get_email_address()
```

## 测试

运行测试脚本：

```bash
python tests/07_20260520_test_guerrillamail.py
```

测试覆盖：
- ✅ 获取邮箱地址
- ✅ 检查邮件
- ✅ 获取邮件列表
- ✅ 获取邮件详情
- ✅ 剩余时间计算
- ⚠️ 自定义用户名（部分功能）
- ⚠️ 删除邮件（部分功能）
- ⚠️ 忘记邮箱（部分功能）

## 相关文档

- [API文档](./07_20260520_guerrillamail_API_DOCUMENTATION.md) - 完整的API参考
- [测试脚本](../tests/07_20260520_test_guerrillamail.py) - 功能测试
- [项目文档](../docs/) - 项目级文档

## 许可证

本项目属于 IBM CrazyMail Project，仅供学习和研究使用。

## 贡献

欢迎提交问题和改进建议！

---

**最后更新**: 2026-05-20  
**版本**: 1.0.0  
**作者**: IBM CrazyMail Project