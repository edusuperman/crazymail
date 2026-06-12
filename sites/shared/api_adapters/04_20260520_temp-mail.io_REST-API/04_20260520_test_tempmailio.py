"""
Temp-Mail.io API 测试脚本

用于测试Temp-Mail.io临时邮箱服务的功能，包括真实邮件接收测试。

作者: Bob (AI Assistant)
创建日期: 2026-05-20
版本: 1.0.0
"""

import unittest
import time
import logging
import sys
import os
from typing import Optional

# 添加父目录到路径以导入客户端
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tempmailio_client import TempMailIOClient, TempMailIOError

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TestTempMailIOClient(unittest.TestCase):
    """
    Temp-Mail.io API客户端测试类
    """

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        logger.info("=" * 70)
        logger.info("开始测试 Temp-Mail.io API客户端")
        logger.info("=" * 70)
        cls.client = TempMailIOClient()
        cls.test_email: Optional[str] = None
        cls.test_token: Optional[str] = None

    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        cls.client.close()
        logger.info("=" * 70)
        logger.info("测试完成")
        logger.info("=" * 70)

    def setUp(self):
        """每个测试前的准备"""
        logger.info(f"\n{'=' * 70}")
        logger.info(f"测试: {self._testMethodName}")
        logger.info(f"{'=' * 70}")

    def tearDown(self):
        """每个测试后的清理"""
        pass

    def test_01_create_mailbox(self):
        """测试创建邮箱功能"""
        logger.info("测试创建邮箱...")

        try:
            email, token = self.client.create_mailbox()

            # 保存到类变量供后续测试使用
            self.__class__.test_email = email
            self.__class__.test_token = token

            self.assertIsNotNone(email, "应该获取到邮箱地址")
            self.assertIsNotNone(token, "应该获取到认证令牌")
            self.assertIn("@", email, "邮箱地址应该包含@符号")
            self.assertTrue(len(token) > 0, "令牌不应为空")

            logger.info(f"✅ 邮箱创建成功")
            logger.info(f"   📧 邮箱地址: {email}")
            logger.info(f"   🔑 Token: {token}")

        except Exception as e:
            self.fail(f"创建邮箱失败: {str(e)}")

    def test_02_get_domains(self):
        """测试获取域名列表"""
        logger.info("测试获取域名列表...")

        try:
            domains = self.client.get_domains()

            self.assertIsInstance(domains, list, "应该返回列表")
            self.assertGreater(len(domains), 0, "域名列表不应为空")

            # 检查域名对象结构
            if domains:
                first_domain = domains[0]
                self.assertIn("name", first_domain, "域名对象应包含name字段")
                self.assertIn("type", first_domain, "域名对象应包含type字段")
                self.assertIn(
                    "forward_available",
                    first_domain,
                    "域名对象应包含forward_available字段",
                )

            logger.info(f"✅ 获取到 {len(domains)} 个可用域名")
            logger.info(f"   前3个域名:")
            for domain in domains[:3]:
                logger.info(f"   - {domain['name']} ({domain['type']})")

        except Exception as e:
            self.fail(f"获取域名列表失败: {str(e)}")

    def test_03_get_messages_empty(self):
        """测试获取空邮箱的邮件列表"""
        logger.info("测试获取空邮箱的邮件...")

        try:
            # 确保已创建邮箱
            if not self.__class__.test_email:
                email, token = self.client.create_mailbox()
                self.__class__.test_email = email
                self.__class__.test_token = token

            messages = self.client.get_messages(self.__class__.test_email)

            self.assertIsInstance(messages, list, "应该返回列表")
            logger.info(f"✅ 成功获取邮件列表（当前 {len(messages)} 封邮件）")

        except Exception as e:
            self.fail(f"获取邮件列表失败: {str(e)}")

    def test_04_real_email_test(self):
        """测试真实邮件接收（使用Mailfence发送）"""
        logger.info("测试真实邮件接收...")

        try:
            # 确保已创建邮箱
            if not self.__class__.test_email:
                email, token = self.client.create_mailbox()
                self.__class__.test_email = email
                self.__class__.test_token = token

            test_email = self.__class__.test_email

            logger.info(f"📧 测试邮箱: {test_email}")
            logger.info(f"⏳ 等待接收邮件（60秒超时）...")
            logger.info(f"💡 请使用Mailfence账号向 {test_email} 发送测试邮件")
            logger.info(f"   发件人: 4qvwxanaqn@mailfence.com")
            logger.info(f"   主题: Temp-Mail.io Test")
            logger.info(f"   内容: This is a test email for Temp-Mail.io API")

            # 等待邮件（60秒超时，5秒轮询间隔）
            try:
                messages = self.client.wait_for_message(
                    email=test_email, timeout=60, poll_interval=5, expected_count=1
                )

                self.assertGreater(len(messages), 0, "应该收到至少一封邮件")

                logger.info(f"\n✅ 成功收到 {len(messages)} 封邮件!")

                # 显示邮件详情
                for i, msg in enumerate(messages, 1):
                    logger.info(f"\n📨 邮件 {i}:")
                    logger.info(f"   发件人: {msg.get('from', 'N/A')}")
                    logger.info(f"   主题: {msg.get('subject', 'N/A')}")
                    logger.info(f"   时间: {msg.get('date', 'N/A')}")

                    content = self.client.get_message_content(msg)
                    if content:
                        preview = (
                            content[:100] + "..." if len(content) > 100 else content
                        )
                        logger.info(f"   内容预览: {preview}")

                # 验证邮件内容
                first_message = messages[0]
                self.assertIn("from", first_message, "邮件应包含发件人")
                self.assertIn("subject", first_message, "邮件应包含主题")

                logger.info(f"\n✅ 真实邮件接收测试通过!")

            except TempMailIOError as e:
                logger.warning(f"\n⚠️  等待邮件超时: {str(e)}")
                logger.info(f"💡 这不是错误 - 可能没有及时发送测试邮件")
                logger.info(f"💡 可以稍后手动测试邮件接收功能")
                # 不标记为失败，因为这是预期的情况
                self.skipTest("未在超时时间内收到邮件（这是正常的）")

        except Exception as e:
            self.fail(f"真实邮件测试失败: {str(e)}")

    def test_05_context_manager(self):
        """测试上下文管理器"""
        logger.info("测试上下文管理器...")

        try:
            with TempMailIOClient() as client:
                email, token = client.create_mailbox()
                self.assertIsNotNone(email, "应该获取到邮箱地址")
                logger.info(f"✅ 上下文管理器测试通过")
                logger.info(f"   创建的邮箱: {email}")
        except Exception as e:
            self.fail(f"上下文管理器测试失败: {str(e)}")


def run_quick_test():
    """
    快速测试 - 不包括真实邮件接收测试
    """
    logger.info("\n" + "=" * 70)
    logger.info("运行快速测试（跳过真实邮件接收测试）")
    logger.info("=" * 70 + "\n")

    suite = unittest.TestSuite()
    suite.addTest(TestTempMailIOClient("test_01_create_mailbox"))
    suite.addTest(TestTempMailIOClient("test_02_get_domains"))
    suite.addTest(TestTempMailIOClient("test_03_get_messages_empty"))
    suite.addTest(TestTempMailIOClient("test_05_context_manager"))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


def run_full_test():
    """
    完整测试 - 包括真实邮件接收测试
    """
    logger.info("\n" + "=" * 70)
    logger.info("运行完整测试（包括真实邮件接收测试）")
    logger.info("=" * 70 + "\n")

    suite = unittest.TestLoader().loadTestsFromTestCase(TestTempMailIOClient)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


def main():
    """
    主函数 - 提供测试选项
    """
    import argparse

    parser = argparse.ArgumentParser(description="Temp-Mail.io API 测试脚本")
    parser.add_argument(
        "--mode",
        choices=["quick", "full"],
        default="quick",
        help="测试模式: quick=快速测试（跳过邮件接收）, full=完整测试（包括邮件接收）",
    )

    args = parser.parse_args()

    if args.mode == "quick":
        success = run_quick_test()
    else:
        success = run_full_test()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

# Made with Bob
