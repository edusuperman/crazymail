# Mailfence 自动化工具

## 概述

本目录包含用于自动化 Mailfence 邮件操作的 Python 脚本，使用 Playwright 实现浏览器自动化。

## 文件说明

### 1. `mailfence_automation.py` - 核心自动化库（在 06_20260520_mailfence.com_Automation/ 目录）

可复用的 Mailfence 自动化类，提供以下功能：

- **登录功能**：自动登录 Mailfence 账户
- **撰写邮件**：填写收件人、主题、正文
- **发送邮件**：自动发送或保存为草稿
- **稳定选择器**：使用 CSS 和 XPath，不依赖位置

#### 核心类：`MailfenceAutomation`

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / '06_20260520_mailfence.com_Automation'))
from mailfence_automation import MailfenceAutomation, MailfenceConfig

# 方式1：使用上下文管理器（推荐）
async with MailfenceAutomation() as mf:
    await mf.login()
    await mf.send_test_email("recipient@example.com")

# 方式2：手动管理
mf = MailfenceAutomation()
await mf.start(headless=False)
await mf.login()
await mf.compose_email(
    to="test@example.com",
    subject="Test Subject",
    body="Test Body",
    send=True
)
await mf.close()
```

#### 选择器设计原则

所有选择器使用稳定的 CSS 和属性选择器，而非位置引用：

```python
SELECTORS = {
    # ✓ 好的选择器（基于属性和文本）
    'login_button': 'button:has-text("Log in")',
    'username_input': 'input[placeholder*="Username"]',
    'new_email_button': '[title="New"]',
    
    # ✗ 避免的选择器（基于位置）
    # 'login_button': 'e17',  # 位置引用，不稳定
    # 'username_input': 'div > div > input:nth-child(1)',  # 结构依赖
}
```

### 2. `send_mailtm_test_email.py` - Mail.tm 测试邮件发送器

专门用于向 Mail.tm 测试邮箱发送测试邮件的脚本。

**功能**：
- 读取 `mailtm_test_info.json` 获取测试邮箱地址
- 使用 Mailfence 自动化登录并发送测试邮件
- 提供详细的执行日志

**使用方法**：

```bash
# 确保已创建 Mail.tm 测试邮箱
python tests/05_20260520_mailtm_real_email_test.py

# 发送测试邮件
python 06_20260520_mailfence.com_Automation/send_mailtm_test_email.py

# 验证邮件接收
python tests/05_20260520_check_mailtm_email.py
```

## 依赖安装

```bash
# 安装 Playwright
pip install playwright

# 安装浏览器驱动
playwright install chromium
```

## 配置

### 默认配置

```python
@dataclass
class MailfenceConfig:
    email: str = "4qvwxanaqn@mailfence.com"
    password: str = "100%Automann"
    base_url: str = "https://mailfence.com"
    login_url: str = "https://mailfence.com/sw?type=L&state=0&lf=mailfence"
    timeout: int = 30000  # 30秒超时
```

### 自定义配置

```python
from tools.mailfence_automation import MailfenceAutomation, MailfenceConfig

# 创建自定义配置
config = MailfenceConfig(
    email="your_email@mailfence.com",
    password="your_password",
    timeout=60000  # 60秒超时
)

# 使用自定义配置
async with MailfenceAutomation(config) as mf:
    await mf.login()
    # ...
```

## 使用示例

### 示例1：发送简单邮件

```python
import asyncio
from tools.mailfence_automation import MailfenceAutomation

async def send_simple_email():
    async with MailfenceAutomation() as mf:
        await mf.login()
        await mf.compose_email(
            to="recipient@example.com",
            subject="Hello from Automation",
            body="This is an automated email.",
            send=True
        )

asyncio.run(send_simple_email())
```

### 示例2：保存为草稿

```python
async def save_draft():
    async with MailfenceAutomation() as mf:
        await mf.login()
        await mf.compose_email(
            to="recipient@example.com",
            subject="Draft Email",
            body="This will be saved as draft.",
            send=False  # 不发送，保存为草稿
        )

asyncio.run(save_draft())
```

### 示例3：批量发送

```python
async def send_batch_emails():
    recipients = [
        "user1@example.com",
        "user2@example.com",
        "user3@example.com"
    ]
    
    async with MailfenceAutomation() as mf:
        await mf.login()
        
        for recipient in recipients:
            await mf.compose_email(
                to=recipient,
                subject=f"Email to {recipient}",
                body=f"Hello {recipient}!",
                send=True
            )
            await asyncio.sleep(2)  # 避免发送过快

asyncio.run(send_batch_emails())
```

## 选择器维护

如果 Mailfence 更新了界面，可能需要更新选择器。以下是维护指南：

### 1. 使用浏览器开发者工具

```bash
# 启动浏览器并打开开发者工具
# 检查元素，找到稳定的属性
```

### 2. 优先级顺序

1. **文本内容**：`button:has-text("Send")`
2. **属性选择器**：`[title="New"]`, `[aria-label="Compose"]`
3. **占位符**：`input[placeholder*="Subject"]`
4. **类名**（谨慎使用）：`.compose-button`
5. **避免**：位置选择器、nth-child

### 3. 测试选择器

```python
# 在浏览器控制台测试
document.querySelector('button:has-text("Send")')
document.querySelectorAll('input[placeholder*="Subject"]')
```

## 故障排除

### 问题1：登录失败

**可能原因**：
- 密码错误
- 网络问题
- Mailfence 界面更新

**解决方法**：
```python
# 启用非无头模式查看问题
await mf.start(headless=False)
```

### 问题2：找不到元素

**可能原因**：
- 选择器过时
- 页面加载未完成

**解决方法**：
```python
# 增加超时时间
config = MailfenceConfig(timeout=60000)

# 或添加等待
await page.wait_for_timeout(5000)
```

### 问题3：邮件发送失败

**可能原因**：
- 收件人地址无效
- 撰写窗口未完全加载

**解决方法**：
```python
# 增加等待时间
await self.page.wait_for_timeout(3000)
```

## 最佳实践

1. **使用上下文管理器**：确保资源正确释放
2. **错误处理**：捕获并记录异常
3. **日志记录**：使用 logging 模块
4. **选择器稳定性**：定期检查和更新
5. **速率限制**：避免发送过快

## 集成到测试流程

```python
# 在测试脚本中使用
async def test_email_reception():
    # 1. 创建测试邮箱
    test_email = create_test_mailbox()
    
    # 2. 发送测试邮件
    async with MailfenceAutomation() as mf:
        await mf.login()
        await mf.send_test_email(test_email)
    
    # 3. 验证接收
    await asyncio.sleep(10)
    messages = check_mailbox(test_email)
    assert len(messages) > 0
```

## 许可证

本工具是 IBM CrazyMail 项目的一部分，仅用于测试目的。

## 贡献

如果发现选择器失效或有改进建议，请更新 `SELECTORS` 字典并提交。