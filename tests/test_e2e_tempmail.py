#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端到端测试：验证 CrazyMail 前后端能正确接收邮件

流程：
1. 通过后端 API 创建临时邮箱
2. 通过 Mailfence 自动化发送测试邮件到该地址
3. 轮询后端 API 检查是否收到邮件
"""

import asyncio
import json
import sys
import codecs
import time
from pathlib import Path

# 修复 Windows 控制台编码
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "sites" / "shared" / "api_adapters" / "06_20260520_mailfence.com_Automation"))
sys.path.insert(0, str(PROJECT_ROOT / "sites" / "shared" / "api_adapters"))

import httpx
from mailfence_automation import MailfenceAutomation

BACKEND_URL = "http://127.0.0.1:8000"


async def step1_create_mailbox():
    """步骤1：通过后端 API 创建临时邮箱"""
    print("\n" + "=" * 60)
    print("步骤1：创建临时邮箱")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{BACKEND_URL}/api/v1/email/create", json={})
        resp.raise_for_status()
        data = resp.json()

    email = data["address"]
    print(f"✅ 邮箱创建成功: {email}")
    print(f"   用户名: {data['username']}")
    print(f"   域名: {data['domain']}")
    return email


async def step2_send_email(recipient: str):
    """步骤2：通过 Mailfence 自动化发送测试邮件"""
    print("\n" + "=" * 60)
    print("步骤2：发送测试邮件")
    print("=" * 60)

    from datetime import datetime
    import random

    test_id = f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
    subject = f"CrazyMail E2E Test - {test_id}"
    body = f"""Hello,

This is an automated end-to-end test email for CrazyMail.

Test Details:
- Recipient: {recipient}
- Test ID: {test_id}
- Timestamp: {datetime.now().isoformat()}
- Purpose: Verify CrazyMail backend can receive and display emails

If you see this email in the CrazyMail frontend, the system is working correctly!

Best regards,
CrazyMail Automated Testing
"""

    print(f"📮 收件人: {recipient}")
    print(f"📋 主题: {subject}")
    print(f"🔖 测试ID: {test_id}")

    print("\n🚀 启动 Mailfence 自动化...")
    async with MailfenceAutomation() as mf:
        print("🔐 登录 Mailfence...")
        if not await mf.login():
            print("❌ 登录失败")
            return None
        print("✅ 登录成功")

        print(f"📨 发送邮件...")
        success = await mf.compose_email(
            to=recipient, subject=subject, body=body, send=True
        )

        if success:
            print("✅ 邮件发送成功！")
            return {"test_id": test_id, "subject": subject}
        else:
            print("❌ 邮件发送失败")
            return None


async def step3_check_messages(email: str, max_wait: int = 60):
    """步骤3：轮询后端 API 检查是否收到邮件"""
    print("\n" + "=" * 60)
    print("步骤3：检查邮件接收")
    print("=" * 60)

    print(f"🔍 监控邮箱: {email}")
    print(f"⏱️ 最大等待: {max_wait} 秒")
    print()

    async with httpx.AsyncClient() as client:
        for i in range(max_wait // 5):
            await asyncio.sleep(5)

            resp = await client.get(
                f"{BACKEND_URL}/api/v1/email/messages",
                params={"email": email},
            )

            if resp.status_code == 200:
                data = resp.json()
                messages = data.get("messages", [])
                total = data.get("total", 0)

                elapsed = (i + 1) * 5
                print(f"  [{elapsed:3d}s] 邮件数: {total}", end="")

                if total > 0:
                    print(f" ✅ 收到邮件！")
                    print()
                    print("📧 邮件详情:")
                    for msg in messages:
                        print(f"   发件人: {msg.get('from_address', 'N/A')}")
                        print(f"   主题: {msg.get('subject', 'N/A')}")
                        print(f"   时间: {msg.get('received_at', 'N/A')}")
                    return messages
                else:
                    print(" ⏳ 等待中...")
            else:
                print(f"  [error] API 返回 {resp.status_code}")

    print(f"\n❌ {max_wait} 秒内未收到邮件")
    return []


async def main():
    """主测试流程"""
    print("=" * 60)
    print("CrazyMail 端到端邮件接收测试")
    print("=" * 60)

    # 检查后端是否运行
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BACKEND_URL}/health")
            resp.raise_for_status()
            print(f"✅ 后端运行正常")
    except Exception as e:
        print(f"❌ 后端未运行: {e}")
        print("请先启动后端: uvicorn backend.main:app --port 8000")
        sys.exit(1)

    # 步骤1：创建邮箱
    email = await step1_create_mailbox()

    # 步骤2：发送测试邮件
    result = await step2_send_email(email)
    if not result:
        print("\n❌ 测试终止：邮件发送失败")
        sys.exit(1)

    # 步骤3：检查邮件
    messages = await step3_check_messages(email, max_wait=60)

    # 结果总结
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)

    if messages:
        print(f"✅ 测试通过！成功收到 {len(messages)} 封邮件")
        print(f"   邮箱: {email}")
        print(f"   测试ID: {result['test_id']}")
    else:
        print(f"❌ 测试失败！未能收到邮件")
        print(f"   邮箱: {email}")
        print(f"   可能原因:")
        print(f"   1. temp-mail.io API 需要 token 认证才能获取邮件")
        print(f"   2. Mailfence 发送的邮件未被 temp-mail.io 接收")
        print(f"   3. 后端 adapter 的 get_messages 方法有问题")

    sys.exit(0 if messages else 1)


if __name__ == "__main__":
    asyncio.run(main())
