# Mailfence 自动化脚本库索引

## 目录信息

- **序号**: 06
- **创建日期**: 2026-05-20
- **服务域名**: mailfence.com
- **类型**: 邮件发送自动化脚本库

## 目录结构

```
06_20260520_mailfence.com_Automation/
├── mailfence_automation.py      # 核心自动化库 (254行)
├── send_mailtm_test_email.py    # Mail.tm 测试邮件发送器 (89行)
├── README.md                     # 详细使用文档 (283行)
└── INDEX.md                      # 本文件 - 目录索引
```

## 文件说明

### 1. mailfence_automation.py
**核心自动化库**，提供可复用的 Mailfence 操作类。

**主要功能**：
- 自动登录 Mailfence
- 撰写和发送邮件
- 使用稳定的 CSS 选择器
- 完整的异步支持和错误处理

**核心类**：
- `MailfenceAutomation` - 主自动化类
- `MailfenceConfig` - 配置类

### 2. send_mailtm_test_email.py
**Mail.tm 测试邮件发送器**，专门用于向 Mail.tm 测试邮箱发送测试邮件。

**功能**：
- 读取 `mailtm_test_info.json` 获取测试邮箱
- 使用 Mailfence 自动化登录并发送
- 提供详细的执行日志

### 3. README.md
**完整的使用文档**，包含：
- 工具概述和功能说明
- 详细的使用示例
- 选择器维护指南
- 故障排除方法
- 最佳实践建议

## 使用方法

### 基础用法

```python
import sys
from pathlib import Path

# 添加脚本库到路径
sys.path.insert(0, str(Path(__file__).parent.parent / '06_20260520_mailfence.com_Automation'))

from mailfence_automation import MailfenceAutomation

async def main():
    async with MailfenceAutomation() as mf:
        await mf.login()
        await mf.compose_email(
            to="test@example.com",
            subject="Test",
            body="Test email",
            send=True
        )
```

### Mail.tm 测试

```bash
# 从项目根目录运行
python 06_20260520_mailfence.com_Automation/send_mailtm_test_email.py
```

## 依赖要求

```bash
pip install playwright
playwright install chromium
```

## 技术特点

1. **稳定选择器**：使用 CSS 和 getByRole，不依赖位置
2. **完全自动化**：无需人工干预
3. **模块化设计**：易于复用和扩展
4. **异步支持**：高性能的 asyncio 实现
5. **完整文档**：详细的使用和维护指南

## 相关文档

- `README.md` - 详细使用文档
- `docs/MAILFENCE_AUTOMATION_SUMMARY.md` - 项目总结文档
- `.bob/skills/Mailfence_Automation.skill.md` - 技能文档

## 版本信息

- **版本**: 1.0
- **创建日期**: 2026-05-20
- **状态**: 生产就绪
- **作者**: IBM CrazyMail Project

## 未来扩展

此目录结构为未来其他邮件服务的自动化脚本库提供了模板：

```
07_YYYYMMDD_service.com_Automation/
08_YYYYMMDD_another-service.com_Automation/
...
```

每个服务的自动化脚本库都应遵循相同的结构和命名规范。