#!/usr/bin/env python3
"""
端到端测试：使用 Mailfence 发送邮件到 temp-mail.io 邮箱
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "sites" / "shared"))
sys.path.insert(0, str(project_root / "sites" / "shared" / "api_adapters" / "06_20260520_mailfence.com_Automation"))

from api_adapters.tempmailio_adapter import TempMailIOAdapter
from mailfence_automation import MailfenceAutomation, MailfenceConfig


async def test_end_to_end():
    """端到端测试"""
    print("=" * 60)
    print("端到端邮件测试")
    print("=" * 60)
    print()

    # 1. 创建 temp-mail.io 邮箱
    print("1️⃣ 创建临时邮箱...")
    adapter = TempMailIOAdapter()
    email = await adapter.create_email()
    print(f"   邮箱地址: {email.address}")
    print()

    # 2. 使用 Mailfence 发送测试邮件
    print("2️⃣ 使用 Mailfence 发送测试邮件...")
    async with MailfenceAutomation() as mf:
        # 登录
        print("   登录 Mailfence...")
        if not await mf.login():
            print("   ❌ 登录失败")
            return False
        print("   ✓ 登录成功")

        # 发送邮件
        print(f"   发送邮件到 {email.address}...")
        success = await mf.compose_email(
            to=email.address,
            subject="E2E Test - TempMail Pro",
            body=(
                f"这是一封端到端测试邮件。\n\n"
                f"测试详情:\n"
                f"- 收件人: {email.address}\n"
                f"- 发件人: Mailfence\n"
                f"- 测试类型: 端到端邮件接收\n\n"
                f"如果你收到这封邮件，说明 temp-mail.io 服务工作正常！\n\n"
                f"---\n"
                f"TempMail Pro 自动化测试"
            ),
            send=True,
        )

        if not success:
            print("   ❌ 邮件发送失败")
            return False
        print("   ✓ 邮件发送成功")

    print()

    # 3. 等待邮件到达
    print("3️⃣ 等待邮件到达（30秒）...")
    for i in range(6):
        await asyncio.sleep(5)
        messages = await adapter.get_messages(email.address)
        print(f"   [{(i+1)*5}秒] 邮件数量: {len(messages)}")
        if messages:
            break

    print()

    # 4. 检查邮件
    print("4️⃣ 检查邮件...")
    messages = await adapter.get_messages(email.address)
    if messages:
        print(f"   ✓ 收到 {len(messages)} 封邮件:")
        for msg in messages:
            print(f"     - 发件人: {msg.from_address}")
            print(f"       主题: {msg.subject}")
            print(f"       时间: {msg.received_at}")
    else:
        print("   ⚠️ 未收到邮件（可能需要更长时间）")

    print()

    # 5. 清理
    await adapter.aclose()

    print("=" * 60)
    if messages:
        print("✅ 端到端测试成功！")
    else:
        print("⚠️ 端到端测试部分成功（邮件可能延迟）")
    print("=" * 60)

    return bool(messages)


if __name__ == "__main__":
    success = asyncio.run(test_end_to_end())
    sys.exit(0 if success else 1)
