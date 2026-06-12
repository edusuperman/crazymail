# 通用测试邮件发送器使用指南

## 概述

`send_test_email.py` 是一个智能的、通用的测试邮件发送器，支持任意临时邮箱服务的真实邮件测试。

## 核心特性

### 1. 自动服务识别
- 从邮箱地址自动提取服务名称
- 例如：`test@mail.tm` → 服务名称：`Mail`

### 2. 随机化内容
- **3种主题模板**：随机选择，避免被识别为机器人
- **3种正文模板**：不同风格，增加自然度
- **唯一测试ID**：每次测试生成唯一标识

### 3. 智能信息生成
- 自动包含测试日期和时间
- 自动包含目标服务名称
- 自动生成测试ID（格式：`TEST-YYYYMMDDHHMMSS-XXXX`）

### 4. 测试记录
- 自动保存测试记录到 `test_email_records.json`
- 包含完整的测试信息和时间戳

## 使用方法

### 方式1：使用默认测试信息文件（最简单）

```bash
# 自动使用 mailtm_test_info.json
python 06_20260520_mailfence.com_Automation/send_test_email.py
```

### 方式2：指定邮箱地址

```bash
# 直接指定收件人
python 06_20260520_mailfence.com_Automation/send_test_email.py test@mail.tm

# 指定服务名称
python 06_20260520_mailfence.com_Automation/send_test_email.py test@mail.tm --service "Mail.tm"
```

### 方式3：从测试信息文件读取

```bash
# 使用 -f 参数指定文件
python 06_20260520_mailfence.com_Automation/send_test_email.py -f mailtm_test_info.json

# 或直接传入文件路径
python 06_20260520_mailfence.com_Automation/send_test_email.py mailtm_test_info.json
```

### 方式4：自定义主题和正文

```bash
# 完全自定义
python 06_20260520_mailfence.com_Automation/send_test_email.py \
    test@mail.tm \
    --subject "My Custom Subject" \
    --body "My custom email body"
```

## 命令行参数

```
positional arguments:
  recipient             收件人邮箱地址（或测试信息文件路径）

optional arguments:
  -h, --help            显示帮助信息
  --service, -s         服务名称（如果不提供，从邮箱地址自动提取）
  --subject             自定义邮件主题
  --body                自定义邮件正文
  --file, -f            从测试信息文件读取
```

## 邮件内容示例

### 主题示例（随机选择）

1. `Mail.tm Email Reception Test - 2026-05-20`
2. `Testing Mail.tm Service on 2026-05-20`
3. `Mail.tm Real Email Verification 2026-05-20`
4. `Email Test for Mail.tm - 2026-05-20`
5. `Mail.tm Service Validation 2026-05-20`

### 正文示例（随机选择）

**模板1**：
```
Hello,

This is a real email test for the Mail.tm service.

Test Information:
- Target Service: Mail.tm
- Test Date: 2026-05-20
- Test Time: 14:30:45
- Recipient: test@mail.tm
- Sender: Mailfence (4qvwxanaqn@mailfence.com)
- Test ID: TEST-20260520143045-1234

If you receive this email, the Mail.tm service is working correctly!

This test is part of the IBM CrazyMail project for temporary email service analysis.

Best regards,
Automated Testing System
```

**模板2**：
```
Greetings,

You are receiving this message as part of our Mail.tm service testing.

Details:
• Service Under Test: Mail.tm
• Test Timestamp: 2026-05-20 14:30:45
• Destination: test@mail.tm
• Test Reference: TEST-20260520143045-1234

Successful receipt of this email confirms that Mail.tm is operational.

---
IBM CrazyMail Project
Automated Email Testing
```

**模板3**：
```
Hi there!

This is an automated test email for Mail.tm.

Test Parameters:
→ Service: Mail.tm
→ Date: 2026-05-20
→ Time: 14:30:45
→ To: test@mail.tm
→ Test Code: TEST-20260520143045-1234

If you're reading this, Mail.tm successfully received and delivered this email!

Thank you for being part of our testing process.

Cheers,
The Testing Team
```

## 测试记录格式

测试记录保存在 `test_email_records.json`：

```json
[
  {
    "test_id": "TEST-20260520143045-1234",
    "service": "Mail.tm",
    "recipient": "test@mail.tm",
    "subject": "Mail.tm Email Reception Test - 2026-05-20",
    "timestamp": "2026-05-20T14:30:45.123456",
    "status": "sent"
  }
]
```

## 完整测试流程

### 测试 Mail.tm

```bash
# 1. 创建测试邮箱（如果还没有）
python tests/05_20260520_mailtm_real_email_test.py

# 2. 发送测试邮件（自动使用 mailtm_test_info.json）
python 06_20260520_mailfence.com_Automation/send_test_email.py

# 3. 验证邮件接收
python tests/05_20260520_check_mailtm_email.py
```

### 测试其他服务

```bash
# 假设你有 Tempimail 的测试邮箱
python 06_20260520_mailfence.com_Automation/send_test_email.py test@tempimail.org

# 或使用测试信息文件
python 06_20260520_mailfence.com_Automation/send_test_email.py -f tempimail_test_info.json
```

## 优势对比

### 旧方式（send_mailtm_test_email.py）
- ❌ 只能测试 Mail.tm
- ❌ 固定的邮件内容
- ❌ 容易被识别为机器人

### 新方式（send_test_email.py）
- ✅ 支持任意临时邮箱服务
- ✅ 随机化的邮件内容（3种模板）
- ✅ 自动服务识别
- ✅ 完整的测试记录
- ✅ 更自然，不易被识别为机器人

## 防机器人检测策略

1. **随机化主题**：3种不同的主题模板
2. **随机化正文**：3种不同风格的正文模板
3. **唯一标识**：每次测试生成唯一的测试ID
4. **时间戳**：包含真实的测试日期和时间
5. **服务名称**：动态包含目标服务名称
6. **自然语言**：使用人类化的表达方式

## 故障排除

### 问题1：找不到测试信息文件

```bash
# 确保文件存在
ls mailtm_test_info.json

# 或使用绝对路径
python 06_20260520_mailfence.com_Automation/send_test_email.py -f /path/to/test_info.json
```

### 问题2：登录失败

```bash
# 检查 Mailfence 账户状态
# 确保密码正确：100%Automann
```

### 问题3：邮件发送失败

```bash
# 检查网络连接
# 检查收件人邮箱地址是否有效
```

## 最佳实践

1. **优先使用自动模式**：让脚本自动生成内容
2. **定期更换模板**：如果需要大量测试，可以添加更多模板
3. **保存测试记录**：便于追踪和分析
4. **合理间隔**：避免短时间内发送大量邮件

## 扩展性

### 添加新的主题模板

编辑 `send_test_email.py`，在 `SUBJECT_TEMPLATES` 列表中添加：

```python
SUBJECT_TEMPLATES = [
    # 现有模板...
    "Your New Subject Template - {service} {date}",  # 新增
]
```

### 添加新的正文模板

编辑 `send_test_email.py`，在 `BODY_TEMPLATES` 列表中添加：

```python
BODY_TEMPLATES = [
    # 现有模板...
    """Your new email body template here
    
    Service: {service}
    Date: {date}
    Time: {time}
    Recipient: {recipient}
    Test ID: {test_id}
    """,  # 新增
]
```

## 相关文档

- `README.md` - Mailfence 自动化库详细文档
- `INDEX.md` - 目录索引
- `mailfence_automation.py` - 核心自动化库
- `send_mailtm_test_email.py` - 旧版 Mail.tm 专用脚本（保留用于参考）

## 版本信息

- **版本**: 1.0
- **创建日期**: 2026-05-20
- **状态**: 生产就绪