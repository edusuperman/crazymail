#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用测试邮件发送器
支持任意临时邮箱服务的真实邮件测试
"""

import asyncio
import json
import sys
import os
import random
import codecs
from pathlib import Path
from datetime import datetime

# 修复 Windows 控制台编码
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from mailfence_automation import MailfenceAutomation, MailfenceConfig

# 邮件主题模板（随机选择，增加自然度）
SUBJECT_TEMPLATES = [
    "{service} Email Reception Test - {date}",
    "Testing {service} Service on {date}",
    "{service} Real Email Verification {date}",
    "Email Test for {service} - {date}",
    "{service} Service Validation {date}",
]

# 邮件正文模板（随机选择）
BODY_TEMPLATES = [
    """Hello,

This is a real email test for the {service} service.

Test Information:
- Target Service: {service}
- Test Date: {date}
- Test Time: {time}
- Recipient: {recipient}
- Sender: Mailfence (4qvwxanaqn@mailfence.com)
- Test ID: {test_id}

If you receive this email, the {service} service is working correctly!

This test is part of the IBM CrazyMail project for temporary email service analysis.

Best regards,
Automated Testing System
""",
    """Greetings,

You are receiving this message as part of our {service} service testing.

Details:
• Service Under Test: {service}
• Test Timestamp: {date} {time}
• Destination: {recipient}
• Test Reference: {test_id}

Successful receipt of this email confirms that {service} is operational.

---
IBM CrazyMail Project
Automated Email Testing
""",
    """Hi there!

This is an automated test email for {service}.

Test Parameters:
→ Service: {service}
→ Date: {date}
→ Time: {time}
→ To: {recipient}
→ Test Code: {test_id}

If you're reading this, {service} successfully received and delivered this email!

Thank you for being part of our testing process.

Cheers,
The Testing Team
""",
]


def generate_test_id():
    """生成唯一的测试ID"""
    return (
        f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
    )


def extract_service_name(email: str) -> str:
    """从邮箱地址提取服务名称"""
    domain = email.split("@")[1] if "@" in email else email
    # 移除 .com, .org, .io 等后缀
    service = domain.split(".")[0]
    # 首字母大写
    return service.capitalize()


async def send_test_email(
    recipient: str, service_name: str = None, subject: str = None, body: str = None
):
    """
    发送测试邮件

    Args:
        recipient: 收件人邮箱地址
        service_name: 服务名称（如果为None，从邮箱地址自动提取）
        subject: 自定义主题（如果为None，使用随机模板）
        body: 自定义正文（如果为None，使用随机模板）

    Returns:
        bool: 是否成功
    """
    # 自动提取服务名称
    if service_name is None:
        service_name = extract_service_name(recipient)

    # 生成测试信息
    test_id = generate_test_id()
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")

    # 生成主题（如果未提供）
    if subject is None:
        subject_template = random.choice(SUBJECT_TEMPLATES)
        subject = subject_template.format(service=service_name, date=current_date)

    # 生成正文（如果未提供）
    if body is None:
        body_template = random.choice(BODY_TEMPLATES)
        body = body_template.format(
            service=service_name,
            date=current_date,
            time=current_time,
            recipient=recipient,
            test_id=test_id,
        )

    print("=" * 70)
    print(f"📧 通用测试邮件发送器")
    print("=" * 70)
    print()
    print(f"🎯 目标服务: {service_name}")
    print(f"📮 收件人: {recipient}")
    print(f"📋 主题: {subject}")
    print(f"🔖 测试ID: {test_id}")
    print()

    # 创建自动化实例
    print("🚀 启动 Mailfence 自动化...")
    async with MailfenceAutomation() as mf:
        # 登录
        print("🔐 登录 Mailfence...")
        if not await mf.login():
            print("❌ 登录失败")
            return False

        print("✓ 登录成功")
        print()

        # 发送测试邮件
        print(f"📨 发送测试邮件...")
        success = await mf.compose_email(
            to=recipient, subject=subject, body=body, send=True
        )

        if success:
            print("✓ 邮件发送成功！")
            print()
            print("📋 测试信息已保存")

            # 保存测试记录
            test_record = {
                "test_id": test_id,
                "service": service_name,
                "recipient": recipient,
                "subject": subject,
                "timestamp": datetime.now().isoformat(),
                "status": "sent",
            }

            # 保存到文件
            record_file = Path(__file__).parent.parent / "test_email_records.json"
            records = []
            if record_file.exists():
                with open(record_file, "r", encoding="utf-8") as f:
                    records = json.load(f)
            records.append(test_record)
            with open(record_file, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2, ensure_ascii=False)

            print(f"📝 测试记录: {record_file}")
            return True
        else:
            print("❌ 邮件发送失败")
            return False


async def send_test_from_file(test_info_file: str):
    """
    从测试信息文件读取邮箱地址并发送测试邮件

    Args:
        test_info_file: 测试信息文件路径（如 mailtm_test_info.json）

    Returns:
        bool: 是否成功
    """
    test_file = Path(test_info_file)

    if not test_file.exists():
        print(f"❌ 错误：找不到测试信息文件: {test_info_file}")
        return False

    with open(test_file, "r", encoding="utf-8") as f:
        test_info = json.load(f)

    recipient = test_info.get("email")
    service = test_info.get("service", extract_service_name(recipient))

    if not recipient:
        print("❌ 错误：测试信息文件中没有 email 字段")
        return False

    return await send_test_email(recipient, service)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="通用测试邮件发送器 - 支持任意临时邮箱服务"
    )
    parser.add_argument(
        "recipient", nargs="?", help="收件人邮箱地址（或测试信息文件路径）"
    )
    parser.add_argument(
        "--service", "-s", help="服务名称（如果不提供，从邮箱地址自动提取）"
    )
    parser.add_argument("--subject", help="自定义邮件主题")
    parser.add_argument("--body", help="自定义邮件正文")
    parser.add_argument(
        "--file", "-f", help="从测试信息文件读取（如 mailtm_test_info.json）"
    )

    args = parser.parse_args()

    # 如果没有提供任何参数，尝试使用默认的测试信息文件
    if not args.recipient and not args.file:
        default_file = Path(__file__).parent.parent / "mailtm_test_info.json"
        if default_file.exists():
            print(f"📁 使用默认测试信息文件: {default_file}")
            success = asyncio.run(send_test_from_file(str(default_file)))
        else:
            parser.print_help()
            print("\n❌ 错误：请提供收件人邮箱地址或测试信息文件")
            sys.exit(1)
    elif args.file:
        # 从文件读取
        success = asyncio.run(send_test_from_file(args.file))
    elif args.recipient:
        # 检查是否是文件路径
        if Path(args.recipient).exists() and args.recipient.endswith(".json"):
            success = asyncio.run(send_test_from_file(args.recipient))
        else:
            # 直接发送到指定邮箱
            success = asyncio.run(
                send_test_email(
                    recipient=args.recipient,
                    service_name=args.service,
                    subject=args.subject,
                    body=args.body,
                )
            )

    print()
    print("=" * 70)
    if success:
        print("✓ 测试邮件发送完成")
    else:
        print("✗ 测试邮件发送失败")
    print("=" * 70)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

# Made with Bob
