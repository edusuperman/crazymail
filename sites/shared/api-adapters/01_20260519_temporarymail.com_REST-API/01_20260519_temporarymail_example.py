#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TemporaryMail.com API 使用示例
展示各种常见使用场景
"""

from temporarymail_client import TemporaryMailClient
import time
import re


def example_1_basic_usage():
    """示例1: 基础使用 - 获取邮箱并等待邮件"""
    print("\n" + "=" * 60)
    print("示例1: 基础使用")
    print("=" * 60)

    client = TemporaryMailClient()

    # 获取随机邮箱
    email = client.get_random_email()
    print(f"\n📧 临时邮箱: {email}")
    print("   请向此地址发送测试邮件\n")

    # 等待邮件（60秒超时）
    emails = client.wait_for_email(timeout=60, check_interval=5)

    if emails:
        print(f"\n✓ 收到 {len(emails)} 封邮件")
        for email in emails:
            print(client.format_email(email))
    else:
        print("\n✗ 未收到邮件")


def example_2_specific_email():
    """示例2: 请求特定的邮箱地址"""
    print("\n" + "=" * 60)
    print("示例2: 请求特定邮箱地址")
    print("=" * 60)

    client = TemporaryMailClient()

    # 尝试获取特定邮箱（可能失败，如果被占用）
    try:
        email = client.request_specific_email("test123@easymailbox.live")
        print(f"\n✓ 成功获取邮箱: {email}")
    except Exception as e:
        print(f"\n✗ 获取失败: {str(e)}")
        print("   尝试获取随机邮箱...")
        email = client.get_random_email()


def example_3_check_multiple_times():
    """示例3: 多次检查收件箱"""
    print("\n" + "=" * 60)
    print("示例3: 多次检查收件箱")
    print("=" * 60)

    client = TemporaryMailClient()
    email = client.get_random_email()

    print(f"\n📧 临时邮箱: {email}")
    print("   将检查收件箱5次，每次间隔10秒\n")

    for i in range(5):
        print(f"[检查 {i+1}/5]", end=" ")
        emails = client.check_inbox()

        if emails:
            print(f"✓ 收到 {len(emails)} 封邮件")
            break
        else:
            print("暂无邮件")

        if i < 4:  # 最后一次不等待
            time.sleep(10)


def example_4_email_details():
    """示例4: 获取邮件详情和附件"""
    print("\n" + "=" * 60)
    print("示例4: 获取邮件详情")
    print("=" * 60)

    client = TemporaryMailClient()
    email = client.get_random_email()

    print(f"\n📧 临时邮箱: {email}")
    print("   等待接收邮件...\n")

    emails = client.wait_for_email(timeout=60)

    if emails:
        for email in emails:
            print(f"\n处理邮件: {email.get('subject', '无主题')}")

            try:
                # 获取详情
                detail = client.get_email_detail(email["id"])
                email_data = detail[email["id"]]

                print(f"  发件人: {email_data.get('from', '未知')}")
                print(f"  主题: {email_data.get('subject', '无主题')}")

                # 检查附件
                if email_data.get("attachments"):
                    print(f"  附件数量: {len(email_data['attachments'])}")
                    for att in email_data["attachments"]:
                        print(f"    - {att['filename']} ({att['size']} bytes)")
                else:
                    print("  无附件")

                # 查看链接
                print(f"  查看链接: https://temporarymail.com/view/?i={email['id']}")

            except Exception as e:
                print(f"  ✗ 获取详情失败: {str(e)}")


def example_5_wait_for_specific_sender():
    """示例5: 等待特定发件人的邮件"""
    print("\n" + "=" * 60)
    print("示例5: 等待特定发件人")
    print("=" * 60)

    client = TemporaryMailClient()
    email = client.get_random_email()

    target_sender = "noreply@example.com"
    print(f"\n📧 临时邮箱: {email}")
    print(f"   等待来自 {target_sender} 的邮件...\n")

    start_time = time.time()
    timeout = 60

    while time.time() - start_time < timeout:
        emails = client.check_inbox()

        for email in emails:
            if target_sender.lower() in email.get("from", "").lower():
                print(f"✓ 收到目标邮件！")
                print(client.format_email(email))
                return

        time.sleep(5)

    print("✗ 超时，未收到目标邮件")


def example_6_extract_verification_code():
    """示例6: 提取验证码（模拟）"""
    print("\n" + "=" * 60)
    print("示例6: 提取验证码")
    print("=" * 60)

    client = TemporaryMailClient()
    email = client.get_random_email()

    print(f"\n📧 临时邮箱: {email}")
    print("   等待包含验证码的邮件...\n")

    emails = client.wait_for_email(timeout=60)

    if emails:
        for email in emails:
            # 从主题中尝试提取验证码
            subject = email.get("subject", "")

            # 匹配常见验证码格式
            patterns = [
                r"\b\d{6}\b",  # 6位数字
                r"\b\d{4}\b",  # 4位数字
                r"\b[A-Z0-9]{6}\b",  # 6位字母数字
            ]

            for pattern in patterns:
                match = re.search(pattern, subject)
                if match:
                    code = match.group(0)
                    print(f"✓ 找到验证码: {code}")
                    print(f"  来源: {email.get('from', '未知')}")
                    print(f"  主题: {subject}")
                    return

        print("✗ 未在邮件主题中找到验证码")
        print("   提示: 实际使用时需要解析邮件HTML内容")


def example_7_batch_check():
    """示例7: 批量检查多个邮箱"""
    print("\n" + "=" * 60)
    print("示例7: 批量检查（演示概念）")
    print("=" * 60)

    print("\n注意: 此示例仅演示概念，实际使用需注意速率限制\n")

    # 创建多个客户端（实际使用时要小心速率限制）
    clients = []

    for i in range(2):  # 只创建2个作为演示
        client = TemporaryMailClient()
        email = client.get_random_email()
        clients.append({"client": client, "email": email, "index": i + 1})
        time.sleep(2)  # 避免请求过快

    print("\n开始检查所有邮箱...")

    for item in clients:
        print(f"\n[邮箱 {item['index']}] {item['email']}")
        try:
            emails = item["client"].check_inbox()
            if emails:
                print(f"  ✓ 收到 {len(emails)} 封邮件")
            else:
                print(f"  - 暂无邮件")
        except Exception as e:
            print(f"  ✗ 检查失败: {str(e)}")


def main():
    """主菜单"""
    examples = {
        "1": ("基础使用", example_1_basic_usage),
        "2": ("请求特定邮箱", example_2_specific_email),
        "3": ("多次检查收件箱", example_3_check_multiple_times),
        "4": ("获取邮件详情", example_4_email_details),
        "5": ("等待特定发件人", example_5_wait_for_specific_sender),
        "6": ("提取验证码", example_6_extract_verification_code),
        "7": ("批量检查", example_7_batch_check),
    }

    print("\n" + "=" * 60)
    print("TemporaryMail.com API 使用示例")
    print("=" * 60)
    print("\n选择要运行的示例:")

    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")

    print("  0. 运行所有示例")
    print("  q. 退出")

    choice = input("\n请选择 (1-7/0/q): ").strip()

    if choice == "q":
        print("\n再见！")
        return

    if choice == "0":
        print("\n将依次运行所有示例...\n")
        for key in sorted(examples.keys()):
            try:
                examples[key][1]()
                time.sleep(2)
            except KeyboardInterrupt:
                print("\n\n✗ 用户中断")
                break
            except Exception as e:
                print(f"\n✗ 示例执行出错: {str(e)}")
    elif choice in examples:
        try:
            examples[choice][1]()
        except KeyboardInterrupt:
            print("\n\n✗ 用户中断")
        except Exception as e:
            print(f"\n✗ 示例执行出错: {str(e)}")
    else:
        print("\n✗ 无效选择")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

# Made with Bob
