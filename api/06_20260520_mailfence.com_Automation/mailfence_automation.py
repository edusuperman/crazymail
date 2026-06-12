#!/usr/bin/env python3
"""
Mailfence 邮件自动化工具
使用 Playwright 实现 Mailfence 的登录和发送邮件功能
所有选择器使用 XPath 和 CSS，确保高度可复用
"""

import asyncio
import logging
import os
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from dataclasses import dataclass, field

# 尝试加载 .env 文件
try:
    from dotenv import load_dotenv
    # 从项目根目录加载 .env
    _env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    load_dotenv(_env_path)
except ImportError:
    pass  # python-dotenv 未安装时使用默认值

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class MailfenceConfig:
    """Mailfence 配置（优先从环境变量读取）"""

    email: str = field(default_factory=lambda: os.getenv("MAILFENCE_EMAIL", "4qvwxanaqn@mailfence.com"))
    password: str = field(default_factory=lambda: os.getenv("MAILFENCE_PASSWORD", "100%Automann"))
    base_url: str = "https://mailfence.com"
    login_url: str = "https://mailfence.com/sw?type=L&state=0&lf=mailfence"
    timeout: int = field(default_factory=lambda: int(os.getenv("DEFAULT_REQUEST_TIMEOUT", "30")) * 1000)


class MailfenceAutomation:
    """Mailfence 自动化操作类"""

    # CSS 选择器定义（稳定的选择器）
    SELECTORS = {
        # 登录页面
        "login_button_home": 'button:has-text("Log in")',
        "username_input": 'input[placeholder*="Username"], input[placeholder*="Email"]',
        "password_input": 'input[type="password"]',
        "login_submit": 'button:has-text("Enter")',
        # 邮件界面
        "new_email_button": '[title="New"]',
        "send_button": "#mailSend",  # Send 按钮，使用 ID 选择器（最可靠）
        # 等待加载完成的标志
        "inbox_loaded": '[role="treeitem"]:has-text("Inbox")',  # 更灵活的选择器
        "compose_window": "text=Send",  # 撰写窗口的标志是 Send 按钮
    }

    def __init__(self, config: Optional[MailfenceConfig] = None):
        """
        初始化自动化工具

        Args:
            config: Mailfence 配置，如果为 None 则使用默认配置
        """
        self.config = config or MailfenceConfig()
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()

    async def start(self, headless: bool = False):
        """
        启动浏览器

        Args:
            headless: 是否使用无头模式
        """
        logger.info("启动浏览器...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        logger.info("浏览器启动成功")

    async def close(self):
        """关闭浏览器"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("浏览器已关闭")

    async def login(self) -> bool:
        """
        登录 Mailfence

        Returns:
            bool: 登录是否成功
        """
        try:
            logger.info(f"访问 Mailfence 登录页面: {self.config.login_url}")
            await self.page.goto(self.config.login_url, wait_until="networkidle")

            # 等待登录表单加载
            logger.info("等待登录表单加载...")
            await self.page.wait_for_selector(
                self.SELECTORS["username_input"], timeout=self.config.timeout
            )

            # 填写用户名
            logger.info(f"填写用户名: {self.config.email}")
            await self.page.fill(self.SELECTORS["username_input"], self.config.email)
            await self.page.wait_for_timeout(500)  # 等待输入完成

            # 填写密码
            logger.info("填写密码")
            await self.page.fill(self.SELECTORS["password_input"], self.config.password)
            await self.page.wait_for_timeout(1000)  # 等待密码输入完成

            # 点击登录按钮
            logger.info("点击登录按钮")
            # 使用更可靠的 getByRole 选择器
            await self.page.get_by_role("button", name="Enter").click()
            await self.page.wait_for_timeout(1000)  # 等待点击生效

            # 等待登录成功（URL 变化或页面加载）
            logger.info("等待登录成功...")
            try:
                # 策略1: 等待 URL 变化（登录成功后会跳转）
                await self.page.wait_for_url("**/flatx/**", timeout=self.config.timeout)
                logger.info("✓ 登录成功（URL 已变化）")
            except Exception as e:
                logger.warning(f"URL 等待失败: {e}")
                # 策略2: 直接等待 New 按钮（更可靠）
                try:
                    await self.page.wait_for_selector(
                        self.SELECTORS["new_email_button"], timeout=60000  # 60秒超时
                    )
                    logger.info("✓ 登录成功（找到 New 按钮）")
                except Exception as e2:
                    logger.error(f"登录验证失败: {e2}")
                    # 保存截图用于调试
                    await self.page.screenshot(path="login_failed.png")
                    logger.info("登录失败截图已保存: login_failed.png")
                    return False

            # 等待邮箱界面完全加载（等待 New 按钮出现）
            logger.info("等待邮箱界面加载...")
            try:
                await self.page.wait_for_selector(
                    self.SELECTORS["new_email_button"],
                    timeout=60000,  # 增加到60秒，因为邮箱加载可能较慢
                )
                logger.info("✓ 邮箱界面加载完成")
            except Exception as e:
                logger.error(f"邮箱界面加载超时: {e}")
                await self.page.screenshot(path="inbox_load_failed.png")
                return False

            # 额外等待确保页面完全稳定
            await self.page.wait_for_timeout(2000)
            logger.info("✓ 登录成功")
            return True

        except Exception as e:
            logger.error(f"✗ 登录失败: {str(e)}")
            return False

    async def compose_email(
        self, to: str, subject: str, body: str, send: bool = True
    ) -> bool:
        """
        撰写并发送邮件

        Args:
            to: 收件人邮箱地址
            subject: 邮件主题
            body: 邮件正文
            send: 是否立即发送（False 则保存为草稿）

        Returns:
            bool: 操作是否成功
        """
        try:
            # 点击新建邮件按钮
            logger.info("点击新建邮件按钮")
            await self.page.click(self.SELECTORS["new_email_button"])

            # 等待撰写窗口加载（等待 Send 按钮出现）
            logger.info("等待撰写窗口加载...")
            await self.page.wait_for_selector(
                self.SELECTORS["compose_window"], timeout=self.config.timeout
            )
            # 增加等待时间，确保撰写窗口完全加载
            logger.info("等待撰写窗口完全加载...")
            await self.page.wait_for_timeout(3000)  # 等待3秒确保表单完全加载

            # 填写收件人 - 使用特定的类名选择器
            logger.info(f"填写收件人: {to}")
            try:
                # 使用 GCSDBRWBPL 类名选择器（这是 To/Cc/Bcc 字段的类名）
                # 第一个就是 To 字段
                to_input = await self.page.query_selector("input.GCSDBRWBPL")

                if to_input:
                    # 确保输入框可见且可交互
                    await to_input.wait_for_element_state("visible")
                    await to_input.wait_for_element_state("editable")

                    # 先点击输入框获得焦点
                    await to_input.click()
                    await self.page.wait_for_timeout(500)

                    # 填写邮箱地址
                    await to_input.fill(to, force=True)
                    await self.page.wait_for_timeout(1000)  # 增加等待时间

                    # 按两次 Tab 键：第一次确认邮箱（变灰色），第二次跳转到 Subject
                    await to_input.press("Tab")
                    await self.page.wait_for_timeout(500)
                    await self.page.keyboard.press("Tab")
                    await self.page.wait_for_timeout(500)

                    logger.info("✓ 收件人填写成功")
                else:
                    raise Exception("未找到收件人输入框")

            except Exception as e:
                logger.error(f"收件人填写失败: {e}")
                raise

            # 等待一下，确保收件人已填写并确认
            await self.page.wait_for_timeout(1500)

            # 填写主题 - 使用 ID 选择器（根据 MCP 分析发现 id="mailSubject"）
            logger.info(f"填写主题: {subject}")
            try:
                subject_locator = self.page.locator("#mailSubject")
                await subject_locator.wait_for(state="visible", timeout=5000)
                await subject_locator.fill(subject, force=True)
                logger.info("✓ 主题填写成功")
            except Exception as e:
                logger.error(f"主题填写失败: {e}")
                raise

            # 等待一下，确保主题已填写
            await self.page.wait_for_timeout(500)

            # 填写正文 - 使用键盘输入（最可靠）
            logger.info("填写邮件正文")
            try:
                # Subject 后只需按一次 Tab 就能跳转到正文
                await self.page.keyboard.press("Tab")
                await self.page.wait_for_timeout(500)
                await self.page.keyboard.type(body)
                logger.info("✓ 正文填写成功")
            except Exception as e:
                logger.error(f"正文填写失败: {e}")
                raise

            if send:
                # 发送邮件 - 使用和 New 按钮相同的逻辑
                logger.info("发送邮件...")
                try:
                    logger.info("等待 Send 按钮出现...")

                    # 等待 Send 按钮出现（使用 ID 选择器 #mailSend）
                    await self.page.wait_for_selector(
                        self.SELECTORS["send_button"], state="visible", timeout=10000
                    )
                    logger.info("✓ Send 按钮已出现 (id=mailSend)")

                    # 点击 Send 按钮
                    logger.info("点击 Send 按钮 (#mailSend)...")
                    await self.page.click(self.SELECTORS["send_button"])
                    logger.info("✓ 已点击 Send 按钮")

                    # 等待发送完成
                    await self.page.wait_for_timeout(3000)

                    # 检查撰写窗口是否关闭
                    compose_window = await self.page.query_selector("#mailSubject")
                    if compose_window:
                        logger.warning("撰写窗口仍然打开，邮件可能未发送")
                    else:
                        logger.info("✓ 撰写窗口已关闭，邮件已发送")

                    logger.info("✓ 邮件发送流程完成")
                except Exception as e:
                    logger.error(f"发送失败: {e}")
                    await self.page.screenshot(path="send_failed.png")
                    raise
            else:
                logger.info("✓ 邮件已保存为草稿")

            return True

        except Exception as e:
            logger.error(f"✗ 撰写/发送邮件失败: {str(e)}")
            # 保存截图用于调试
            try:
                await self.page.screenshot(path="mailfence_error.png")
                logger.info("错误截图已保存: mailfence_error.png")
            except:
                pass
            return False

    async def send_test_email(self, recipient: str) -> bool:
        """
        发送测试邮件（便捷方法）

        Args:
            recipient: 收件人邮箱地址

        Returns:
            bool: 是否成功
        """
        return await self.compose_email(
            to=recipient,
            subject="Mail.tm Real Email Test",
            body="This is a real email test for Mail.tm service.\n\n"
            "Sent via Mailfence automation script.\n"
            "Timestamp: " + str(asyncio.get_event_loop().time()),
        )


async def main():
    """主函数 - 演示用法"""
    # 示例1：使用上下文管理器
    async with MailfenceAutomation() as mf:
        # 登录
        if await mf.login():
            # 发送测试邮件
            await mf.send_test_email("qr2z24d94b@wshu.net")

    # 示例2：手动管理生命周期
    # mf = MailfenceAutomation()
    # await mf.start(headless=False)
    # await mf.login()
    # await mf.compose_email(
    #     to="test@example.com",
    #     subject="Test Subject",
    #     body="Test Body",
    #     send=False  # 保存为草稿
    # )
    # await mf.close()


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
