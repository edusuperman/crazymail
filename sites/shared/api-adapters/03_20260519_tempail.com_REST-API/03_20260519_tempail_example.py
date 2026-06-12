"""
Tempail.com API 使用示例

演示如何使用 TempailClient 进行各种操作
"""

from tempail_client import TempailClient
import time


def example_basic_usage():
    """基础使用示例"""
    print("=" * 60)
    print("示例 1: 基础使用")
    print("=" * 60)

    # 创建客户端
    client = TempailClient(language="ru")

    # 初始化并获取邮箱
    info = client.initialize()
    print(f"\n✓ 临时邮箱已创建: {info['email']}")
    print(f"✓ 会话ID: {info['oturum']}")

    # 检查收件箱
    print("\n检查收件箱...")
    emails = client.check_inbox()

    if emails:
        print(f"✓ 找到 {len(emails)} 封邮件")
        for i, email in enumerate(emails, 1):
            print(f"\n邮件 {i}:")
            print(f"  发件人: {email['from']}")
            print(f"  主题: {email['subject']}")
            print(f"  时间: {email['time']}")
    else:
        print("✓ 收件箱为空")


def example_wait_for_email():
    """等待邮件示例"""
    print("\n" + "=" * 60)
    print("示例 2: 等待新邮件")
    print("=" * 60)

    client = TempailClient(language="ru")
    info = client.initialize()

    print(f"\n✓ 邮箱地址: {info['email']}")
    print("\n请向此地址发送测试邮件...")
    print("等待新邮件（60秒超时）...\n")

    # 等待新邮件
    new_email = client.wait_for_email(timeout=60, interval=5)

    if new_email:
        print(f"\n✓ 收到新邮件!")
        print(f"  发件人: {new_email['from']}")
        print(f"  主题: {new_email['subject']}")
        print(f"  时间: {new_email['time']}")

        # 读取邮件内容
        print("\n读取邮件内容...")
        content = client.read_email(new_email["id"], new_email["id"])
        print(f"\n邮件正文预览:")
        print(content["body_text"][:300] + "...")
    else:
        print("\n✗ 超时，未收到新邮件")


def example_monitor_inbox():
    """持续监控收件箱示例"""
    print("\n" + "=" * 60)
    print("示例 3: 持续监控收件箱")
    print("=" * 60)

    client = TempailClient(language="ru")
    info = client.initialize()

    print(f"\n✓ 邮箱地址: {info['email']}")
    print("\n开始监控收件箱（按 Ctrl+C 停止）...\n")

    def on_new_email(emails):
        """收到新邮件时的回调函数"""
        print(f"\n[{time.strftime('%H:%M:%S')}] 收到 {len(emails)} 封新邮件:")
        for email in emails:
            print(f"  • {email['from']}: {email['subject']}")

    try:
        # 监控5次（每次间隔10秒）
        client.monitor_inbox(callback=on_new_email, interval=10, max_iterations=5)
    except KeyboardInterrupt:
        print("\n\n✓ 监控已停止")


def example_read_and_delete():
    """读取和删除邮件示例"""
    print("\n" + "=" * 60)
    print("示例 4: 读取和删除邮件")
    print("=" * 60)

    client = TempailClient(language="ru")
    info = client.initialize()

    print(f"\n✓ 邮箱地址: {info['email']}")

    # 检查收件箱
    emails = client.check_inbox()

    if emails:
        first_email = emails[0]
        print(f"\n找到邮件: {first_email['subject']}")

        # 读取邮件
        print("\n读取邮件内容...")
        content = client.read_email(first_email["id"], first_email["id"])
        print(f"✓ 发件人: {content['from']}")
        print(f"✓ 主题: {content['subject']}")
        print(f"✓ 正文: {content['body_text'][:200]}...")

        # 删除邮件
        print("\n删除邮件...")
        if client.delete_email(first_email["id"], first_email["id"]):
            print("✓ 邮件已删除")

        # 再次检查
        emails = client.check_inbox()
        print(f"\n✓ 当前收件箱邮件数: {len(emails)}")
    else:
        print("\n✓ 收件箱为空，无法演示删除功能")


def example_qr_code():
    """获取QR码示例"""
    print("\n" + "=" * 60)
    print("示例 5: 获取QR码")
    print("=" * 60)

    client = TempailClient(language="ru")
    info = client.initialize()

    print(f"\n✓ 邮箱地址: {info['email']}")

    # 获取QR码
    print("\n获取QR码...")
    qr_info = client.get_qr_code()

    print(f"\n✓ QR码图片URL:")
    print(f"  {qr_info['qr_code_url']}")
    print(f"\n✓ 邮箱URL:")
    print(f"  {qr_info['email_url']}")

    print("\n提示: 可以使用这个QR码在移动设备上快速访问邮箱")


def example_destroy_mailbox():
    """销毁邮箱示例"""
    print("\n" + "=" * 60)
    print("示例 6: 销毁邮箱")
    print("=" * 60)

    client = TempailClient(language="ru")
    info = client.initialize()

    print(f"\n✓ 邮箱地址: {info['email']}")

    # 获取会话信息
    session_info = client.get_session_info()
    print("\n当前会话信息:")
    for key, value in session_info.items():
        if value:
            print(f"  {key}: {value}")

    # 销毁邮箱
    print("\n销毁邮箱...")
    if client.destroy_mailbox():
        print("✓ 邮箱已永久销毁")

        # 验证会话已清除
        session_info = client.get_session_info()
        print("\n销毁后的会话信息:")
        for key, value in session_info.items():
            print(f"  {key}: {value}")
    else:
        print("✗ 销毁失败")


def example_multi_language():
    """多语言支持示例"""
    print("\n" + "=" * 60)
    print("示例 7: 多语言支持")
    print("=" * 60)

    languages = ["ru", "en", "de", "fr", "es"]

    print("\n创建不同语言的邮箱:\n")

    for lang in languages:
        try:
            client = TempailClient(language=lang)
            info = client.initialize()
            print(f"✓ {lang.upper()}: {info['email']}")
        except Exception as e:
            print(f"✗ {lang.upper()}: {str(e)}")


def example_error_handling():
    """错误处理示例"""
    print("\n" + "=" * 60)
    print("示例 8: 错误处理")
    print("=" * 60)

    client = TempailClient(language="ru")

    # 尝试在未初始化时检查收件箱
    print("\n测试 1: 未初始化就检查收件箱")
    try:
        emails = client.check_inbox()
        print("✗ 应该抛出异常")
    except Exception as e:
        print(f"✓ 正确捕获异常: {str(e)}")

    # 初始化
    info = client.initialize()
    print(f"\n✓ 邮箱已初始化: {info['email']}")

    # 尝试读取不存在的邮件
    print("\n测试 2: 读取不存在的邮件")
    try:
        content = client.read_email("invalid_id", "999")
        print("✗ 应该抛出异常")
    except Exception as e:
        print(f"✓ 正确捕获异常: {str(e)[:100]}...")


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("Tempail.com API 使用示例集合")
    print("=" * 60)

    examples = [
        ("基础使用", example_basic_usage),
        ("等待新邮件", example_wait_for_email),
        ("持续监控", example_monitor_inbox),
        ("读取和删除", example_read_and_delete),
        ("获取QR码", example_qr_code),
        ("销毁邮箱", example_destroy_mailbox),
        ("多语言支持", example_multi_language),
        ("错误处理", example_error_handling),
    ]

    print("\n可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\n选择要运行的示例（输入数字，或按回车运行所有示例）:")
    choice = input("> ").strip()

    if choice.isdigit() and 1 <= int(choice) <= len(examples):
        # 运行选定的示例
        name, func = examples[int(choice) - 1]
        print(f"\n运行示例: {name}")
        func()
    else:
        # 运行所有示例
        print("\n运行所有示例...\n")
        for name, func in examples:
            try:
                func()
                time.sleep(2)  # 示例之间暂停
            except KeyboardInterrupt:
                print("\n\n✓ 已取消")
                break
            except Exception as e:
                print(f"\n✗ 示例出错: {str(e)}")

    print("\n" + "=" * 60)
    print("示例运行完成")
    print("=" * 60)


if __name__ == "__main__":
    main()

# Made with Bob
