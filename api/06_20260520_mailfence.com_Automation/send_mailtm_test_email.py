#!/usr/bin/env python3
"""
使用 Mailfence 自动化工具发送测试邮件到 Mail.tm
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from mailfence_automation import MailfenceAutomation, MailfenceConfig


async def send_test_to_mailtm():
    """发送测试邮件到 Mail.tm 邮箱"""

    # 读取 Mail.tm 测试邮箱信息
    test_info_file = Path(__file__).parent.parent / "mailtm_test_info.json"

    if not test_info_file.exists():
        print("❌ 错误：找不到 mailtm_test_info.json 文件")
        print("请先运行 Mail.tm 测试脚本创建测试邮箱")
        return False

    with open(test_info_file, "r") as f:
        test_info = json.load(f)

    recipient = test_info["email"]
    print(f"📧 目标邮箱: {recipient}")
    print(f"🔧 服务: {test_info['service']}")
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
        print(f"📨 发送测试邮件到 {recipient}...")
        success = await mf.compose_email(
            to=recipient,
            subject="Mail.tm Real Email Test",
            body=(
                "This is a real email test for Mail.tm service.\n\n"
                "Test Details:\n"
                f"- Recipient: {recipient}\n"
                f"- Service: Mail.tm\n"
                f"- Sender: Mailfence (4qvwxanaqn@mailfence.com)\n"
                f"- Test Type: Real Email Reception\n\n"
                "If you receive this email, the Mail.tm service is working correctly!\n\n"
                "---\n"
                "Sent via Mailfence Automation Script\n"
                "IBM CrazyMail Project"
            ),
            send=True,
        )

        if success:
            print("✓ 邮件发送成功！")
            print()
            print("📋 下一步：")
            print("   运行 Mail.tm 邮件检查脚本验证接收：")
            print("   python tests/05_20260520_check_mailtm_email.py")
            return True
        else:
            print("❌ 邮件发送失败")
            return False


if __name__ == "__main__":
    print("=" * 60)
    print("Mail.tm 真实邮件测试 - Mailfence 发送器")
    print("=" * 60)
    print()

    success = asyncio.run(send_test_to_mailtm())

    print()
    print("=" * 60)
    if success:
        print("✓ 测试邮件发送完成")
    else:
        print("✗ 测试邮件发送失败")
    print("=" * 60)

    sys.exit(0 if success else 1)

# Made with Bob
