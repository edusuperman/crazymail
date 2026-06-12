"""
Guerrilla Mail API 客户端使用示例

演示 GuerrillaMailClient 的各种使用场景。

作者: IBM CrazyMail Project
创建日期: 2026-05-20
"""

from guerrillamail_client import GuerrillaMailClient, GuerrillaMailAPIError
import time


def example_basic_usage():
    """示例1: 基础使用"""
    print("=" * 60)
    print("示例1: 基础使用")
    print("=" * 60)

    # 创建客户端
    client = GuerrillaMailClient()

    # 获取临时邮箱
    info = client.get_email_address()
    print(f"\n临时邮箱: {info['email_addr']}")
    print(f"别名: {info['alias']}")
    print(f"有效期: 60分钟")

    # 检查邮件
    result = client.check_email()
    print(f"\n收件箱: {len(result['list'])} 封邮件")

    # 显示邮件列表
    for i, mail in enumerate(result["list"], 1):
        print(f"\n邮件 {i}:")
        print(f"  发件人: {mail['mail_from']}")
        print(f"  主题: {mail['mail_subject']}")
        print(f"  时间: {mail['mail_date']}")
        print(f"  大小: {mail['size']} 字节")

    # 读取第一封邮件的详细内容
    if result["list"]:
        first_mail = result["list"][0]
        detail = client.fetch_email(first_mail["mail_id"])
        print(f"\n第一封邮件详情:")
        print(f"主题: {detail['mail_subject']}")
        print(f"正文预览: {detail['mail_body'][:200]}...")

    print("\n✓ 示例完成")


def example_custom_username():
    """示例2: 自定义邮箱用户名"""
    print("\n" + "=" * 60)
    print("示例2: 自定义邮箱用户名")
    print("=" * 60)

    client = GuerrillaMailClient()

    # 先获取默认邮箱
    info = client.get_email_address()
    print(f"\n默认邮箱: {info['email_addr']}")

    # 尝试设置自定义用户名
    try:
        custom_name = f"test{int(time.time())}"
        info = client.set_email_user(custom_name)
        print(f"自定义邮箱: {info['email_addr']}")
        print("✓ 自定义用户名设置成功")
    except GuerrillaMailAPIError as e:
        print(f"✗ 自定义用户名失败: {e}")
        print("继续使用默认邮箱")

    print("\n✓ 示例完成")


def example_wait_for_email():
    """示例3: 等待新邮件"""
    print("\n" + "=" * 60)
    print("示例3: 等待新邮件")
    print("=" * 60)

    client = GuerrillaMailClient()
    info = client.get_email_address()

    print(f"\n临时邮箱: {info['email_addr']}")
    print("请向此邮箱发送测试邮件...")
    print("等待新邮件（最多30秒）...\n")

    # 等待新邮件
    mails = client.wait_for_email(timeout=30, check_interval=5)

    if mails:
        print(f"✓ 收到 {len(mails)} 封新邮件:")
        for mail in mails:
            print(f"  - {mail['mail_from']}: {mail['mail_subject']}")
    else:
        print("⚠ 未收到新邮件（超时）")

    print("\n✓ 示例完成")


def example_email_management():
    """示例4: 邮件管理"""
    print("\n" + "=" * 60)
    print("示例4: 邮件管理")
    print("=" * 60)

    client = GuerrillaMailClient()
    client.get_email_address()

    # 获取邮件列表
    result = client.get_email_list(offset=0)
    print(f"\n收件箱: {len(result['list'])} 封邮件")

    if result["list"]:
        # 显示邮件
        for mail in result["list"]:
            status = "已读" if mail["mail_read"] else "未读"
            print(f"  [{status}] {mail['mail_from']}: {mail['mail_subject']}")

        # 删除第一封邮件
        try:
            first_id = result["list"][0]["mail_id"]
            client.del_email([first_id])
            print(f"\n✓ 已删除邮件 ID: {first_id}")
        except GuerrillaMailAPIError as e:
            print(f"\n✗ 删除邮件失败: {e}")
    else:
        print("收件箱为空")

    print("\n✓ 示例完成")


def example_pagination():
    """示例5: 邮件分页"""
    print("\n" + "=" * 60)
    print("示例5: 邮件分页")
    print("=" * 60)

    client = GuerrillaMailClient()
    client.get_email_address()

    # 获取第一页
    page1 = client.get_email_list(offset=0)
    print(f"\n第1页: {len(page1['list'])} 封邮件")

    # 如果有超过20封邮件，获取第二页
    total_count = int(page1.get("count", 0))
    if total_count > 20:
        page2 = client.get_email_list(offset=20)
        print(f"第2页: {len(page2['list'])} 封邮件")

    print(f"邮件总数: {total_count}")
    print("\n✓ 示例完成")


def example_time_management():
    """示例6: 时间管理"""
    print("\n" + "=" * 60)
    print("示例6: 时间管理")
    print("=" * 60)

    client = GuerrillaMailClient()
    info = client.get_email_address()

    print(f"\n邮箱: {info['email_addr']}")
    print(f"创建时间: {info['email_timestamp']}")

    # 获取剩余时间
    remaining = client.get_remaining_time()
    if remaining:
        minutes = remaining // 60
        seconds = remaining % 60
        print(f"剩余时间: {minutes} 分钟 {seconds} 秒")
        print(f"过期状态: {'已过期' if client.is_expired() else '有效'}")

    # 模拟等待
    print("\n等待5秒...")
    time.sleep(5)

    # 再次检查剩余时间
    remaining = client.get_remaining_time()
    if remaining:
        minutes = remaining // 60
        seconds = remaining % 60
        print(f"更新后剩余时间: {minutes} 分钟 {seconds} 秒")

    print("\n✓ 示例完成")


def example_multilingual():
    """示例7: 多语言支持"""
    print("\n" + "=" * 60)
    print("示例7: 多语言支持")
    print("=" * 60)

    languages = {
        "en": "English",
        "zh": "简体中文",
        "fr": "Français",
        "ru": "Русский",
        "jp": "日本語",
    }

    print("\n支持的语言:")
    for code, name in languages.items():
        client = GuerrillaMailClient(lang=code)
        info = client.get_email_address()
        print(f"  {name} ({code}): {info['email_addr']}")

    print("\n✓ 示例完成")


def example_error_handling():
    """示例8: 错误处理"""
    print("\n" + "=" * 60)
    print("示例8: 错误处理")
    print("=" * 60)

    try:
        # 创建客户端
        client = GuerrillaMailClient(timeout=30, max_retries=3)

        # 获取邮箱
        info = client.get_email_address()
        print(f"\n✓ 邮箱创建成功: {info['email_addr']}")

        # 尝试获取不存在的邮件
        try:
            client.fetch_email(99999)
        except GuerrillaMailAPIError as e:
            print(f"✓ 正确捕获错误: {e}")

    except GuerrillaMailAPIError as e:
        print(f"✗ API错误: {e}")
    except Exception as e:
        print(f"✗ 未知错误: {e}")

    print("\n✓ 示例完成")


def example_monitoring():
    """示例9: 邮箱监控"""
    print("\n" + "=" * 60)
    print("示例9: 邮箱监控（10秒）")
    print("=" * 60)

    client = GuerrillaMailClient()
    info = client.get_email_address()

    print(f"\n监控邮箱: {info['email_addr']}")
    print("监控时间: 10秒")

    start_time = time.time()
    check_count = 0

    while time.time() - start_time < 10:
        check_count += 1
        result = client.check_email()

        print(f"\n检查 #{check_count}:")
        print(f"  邮件数: {len(result['list'])}")

        if result["list"]:
            print("  最新邮件:")
            for mail in result["list"][:3]:  # 只显示前3封
                print(f"    - {mail['mail_from']}: {mail['mail_subject']}")

        # 显示剩余时间
        remaining = client.get_remaining_time()
        if remaining:
            print(f"  邮箱剩余: {remaining // 60} 分钟")

        time.sleep(5)  # 每5秒检查一次

    print("\n✓ 监控完成")


def example_complete_workflow():
    """示例10: 完整工作流"""
    print("\n" + "=" * 60)
    print("示例10: 完整工作流")
    print("=" * 60)

    try:
        # 1. 创建客户端
        print("\n步骤1: 创建客户端")
        client = GuerrillaMailClient()

        # 2. 获取邮箱
        print("步骤2: 获取临时邮箱")
        info = client.get_email_address()
        email = info["email_addr"]
        print(f"  邮箱: {email}")

        # 3. 检查初始邮件
        print("步骤3: 检查初始邮件")
        result = client.check_email()
        print(f"  初始邮件数: {len(result['list'])}")

        # 4. 等待新邮件（可选）
        print("步骤4: 等待新邮件（10秒）")
        mails = client.wait_for_email(timeout=10, check_interval=5)
        if mails:
            print(f"  收到 {len(mails)} 封新邮件")
        else:
            print("  未收到新邮件")

        # 5. 读取所有邮件
        print("步骤5: 读取所有邮件")
        result = client.check_email()
        for mail in result["list"]:
            detail = client.fetch_email(mail["mail_id"])
            print(f"  - {detail['mail_subject']}")

        # 6. 清理（可选）
        print("步骤6: 清理会话")
        try:
            client.forget_me()
            print("  ✓ 会话已清理")
        except:
            print("  ⚠ 清理失败（可忽略）")

        print("\n✓ 完整工作流完成")

    except Exception as e:
        print(f"\n✗ 工作流失败: {e}")


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("Guerrilla Mail API 客户端示例集")
    print("=" * 60)

    examples = [
        ("基础使用", example_basic_usage),
        ("自定义用户名", example_custom_username),
        ("等待新邮件", example_wait_for_email),
        ("邮件管理", example_email_management),
        ("邮件分页", example_pagination),
        ("时间管理", example_time_management),
        ("多语言支持", example_multilingual),
        ("错误处理", example_error_handling),
        ("邮箱监控", example_monitoring),
        ("完整工作流", example_complete_workflow),
    ]

    print("\n可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\n选择示例 (1-10, 0=全部运行, q=退出): ", end="")

    try:
        choice = input().strip()

        if choice.lower() == "q":
            print("退出")
            return

        if choice == "0":
            # 运行所有示例
            for name, func in examples:
                try:
                    func()
                    time.sleep(2)  # 示例间隔
                except KeyboardInterrupt:
                    print("\n\n中断执行")
                    break
                except Exception as e:
                    print(f"\n✗ 示例失败: {e}")
        else:
            # 运行单个示例
            idx = int(choice) - 1
            if 0 <= idx < len(examples):
                name, func = examples[idx]
                func()
            else:
                print("无效选择")

    except KeyboardInterrupt:
        print("\n\n中断执行")
    except Exception as e:
        print(f"\n错误: {e}")

    print("\n" + "=" * 60)
    print("示例集结束")
    print("=" * 60)


if __name__ == "__main__":
    main()

# Made with Bob
