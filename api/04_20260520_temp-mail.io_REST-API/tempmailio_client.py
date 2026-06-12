"""
Temp-Mail.io API 客户端

这是一个用于与Temp-Mail.io临时邮箱服务交互的Python客户端。

作者: Bob (AI Assistant)
创建日期: 2026-05-20
版本: 1.0.0
"""

import requests
import time
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TempMailIOError(Exception):
    """API错误基类"""

    pass


class AuthenticationError(TempMailIOError):
    """认证错误"""

    pass


class RateLimitError(TempMailIOError):
    """速率限制错误"""

    pass


class TempMailIOClient:
    """
    Temp-Mail.io API客户端

    提供与Temp-Mail.io临时邮箱服务交互的完整功能。

    Attributes:
        base_url (str): API基础URL
        session (requests.Session): HTTP会话对象
        timeout (int): 请求超时时间（秒）
        max_retries (int): 最大重试次数
        retry_delay (int): 重试延迟（秒）

    Example:
        >>> client = TempMailIOClient()
        >>> email, token = client.create_mailbox()
        >>> print(f"临时邮箱: {email}")
        >>> messages = client.get_messages(email)
        >>> print(f"收到 {len(messages)} 封邮件")
    """

    def __init__(
        self,
        base_url: str = "https://api.internal.temp-mail.io/api",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 2,
    ):
        """
        初始化客户端

        Args:
            base_url: API基础URL
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # 初始化会话
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Application-Name": "web",
                "Application-Version": "4.0.0",
                "x-cors-header": "iaWg3pchvFx48fY",
                "Content-Type": "application/json",
            }
        )

        # 邮箱相关
        self.email_address: Optional[str] = None
        self.token: Optional[str] = None

        logger.info(f"Temp-Mail.io客户端初始化完成: {base_url}")

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        发送HTTP请求（带重试机制）

        Args:
            method: HTTP方法（GET, POST等）
            endpoint: API端点
            **kwargs: 其他请求参数

        Returns:
            requests.Response: 响应对象

        Raises:
            TempMailIOError: 请求失败时抛出
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    f"请求: {method} {url} (尝试 {attempt + 1}/{self.max_retries})"
                )

                response = self.session.request(
                    method=method, url=url, timeout=self.timeout, **kwargs
                )

                # 检查速率限制
                if response.status_code == 429:
                    raise RateLimitError("请求过多，请稍后重试")

                response.raise_for_status()
                logger.debug(f"响应: {response.status_code}")
                return response

            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"请求失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}"
                )

                if attempt == self.max_retries - 1:
                    raise TempMailIOError(f"请求失败: {str(e)}")

                time.sleep(self.retry_delay)

        raise TempMailIOError("请求失败：超过最大重试次数")

    def create_mailbox(
        self, min_name_length: int = 10, max_name_length: int = 10
    ) -> tuple[str, str]:
        """
        创建新的临时邮箱

        Args:
            min_name_length: 邮箱用户名最小长度
            max_name_length: 邮箱用户名最大长度

        Returns:
            tuple[str, str]: (邮箱地址, 认证令牌)

        Raises:
            TempMailIOError: 创建失败时抛出

        Example:
            >>> client = TempMailIOClient()
            >>> email, token = client.create_mailbox()
            >>> print(f"邮箱: {email}, Token: {token}")
        """
        try:
            logger.info("正在创建新邮箱...")

            response = self._request(
                "POST",
                "/v3/email/new",
                json={
                    "min_name_length": min_name_length,
                    "max_name_length": max_name_length,
                },
            )

            data = response.json()
            email = data["email"]
            token = data["token"]

            self.email_address = email
            self.token = token

            logger.info(f"邮箱创建成功: {email}")
            return email, token

        except Exception as e:
            logger.error(f"创建邮箱失败: {str(e)}")
            raise TempMailIOError(f"创建邮箱失败: {str(e)}")

    def get_messages(self, email: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取邮箱中的所有邮件

        Args:
            email: 邮箱地址（如果不提供，使用当前邮箱）

        Returns:
            List[Dict[str, Any]]: 邮件列表

        Raises:
            TempMailIOError: 获取失败时抛出

        Example:
            >>> messages = client.get_messages()
            >>> for msg in messages:
            ...     print(f"From: {msg['from']}, Subject: {msg['subject']}")
        """
        email_to_check = email or self.email_address

        if not email_to_check:
            raise TempMailIOError("未指定邮箱地址")

        try:
            logger.debug(f"正在获取邮箱 {email_to_check} 的邮件...")

            response = self._request("GET", f"/v3/email/{email_to_check}/messages")

            messages = response.json()
            logger.info(f"获取到 {len(messages)} 封邮件")
            return messages

        except Exception as e:
            logger.error(f"获取邮件失败: {str(e)}")
            raise TempMailIOError(f"获取邮件失败: {str(e)}")

    def get_domains(self) -> List[Dict[str, Any]]:
        """
        获取所有可用的邮箱域名

        Returns:
            List[Dict[str, Any]]: 域名列表

        Raises:
            TempMailIOError: 获取失败时抛出

        Example:
            >>> domains = client.get_domains()
            >>> for domain in domains:
            ...     print(f"域名: {domain['name']}, 类型: {domain['type']}")
        """
        try:
            logger.info("正在获取可用域名列表...")

            response = self._request("GET", "/v4/domains")
            data = response.json()
            domains = data.get("domains", [])

            logger.info(f"获取到 {len(domains)} 个可用域名")
            return domains

        except Exception as e:
            logger.error(f"获取域名列表失败: {str(e)}")
            raise TempMailIOError(f"获取域名列表失败: {str(e)}")

    def wait_for_message(
        self,
        email: Optional[str] = None,
        timeout: int = 300,
        poll_interval: int = 5,
        expected_count: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        等待接收邮件（轮询方式）

        Args:
            email: 邮箱地址（如果不提供，使用当前邮箱）
            timeout: 最大等待时间（秒）
            poll_interval: 轮询间隔（秒）
            expected_count: 期望接收的邮件数量

        Returns:
            List[Dict[str, Any]]: 接收到的邮件列表

        Raises:
            TempMailIOError: 超时或获取失败时抛出

        Example:
            >>> messages = client.wait_for_message(timeout=60, expected_count=1)
            >>> print(f"收到邮件: {messages[0]['subject']}")
        """
        email_to_check = email or self.email_address

        if not email_to_check:
            raise TempMailIOError("未指定邮箱地址")

        logger.info(f"等待邮件... (超时: {timeout}秒, 轮询间隔: {poll_interval}秒)")

        start_time = time.time()
        attempt = 0

        while time.time() - start_time < timeout:
            attempt += 1
            try:
                messages = self.get_messages(email_to_check)

                if len(messages) >= expected_count:
                    logger.info(f"收到 {len(messages)} 封邮件（第 {attempt} 次检查）")
                    return messages

                logger.debug(
                    f"第 {attempt} 次检查: 暂无邮件，{poll_interval}秒后重试..."
                )
                time.sleep(poll_interval)

            except Exception as e:
                logger.warning(f"检查邮件时出错: {str(e)}")
                time.sleep(poll_interval)

        raise TempMailIOError(f"等待邮件超时（{timeout}秒）")

    def get_message_content(self, message: Dict[str, Any]) -> str:
        """
        获取邮件的文本内容

        Args:
            message: 邮件对象

        Returns:
            str: 邮件文本内容

        Example:
            >>> messages = client.get_messages()
            >>> if messages:
            ...     content = client.get_message_content(messages[0])
            ...     print(content)
        """
        # 优先返回纯文本内容，如果没有则返回HTML内容
        return message.get("body_text") or message.get("body_html", "")

    def close(self):
        """
        关闭客户端会话

        Example:
            >>> client.close()
        """
        if self.session:
            self.session.close()
            logger.info("客户端会话已关闭")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()

    def __repr__(self) -> str:
        """字符串表示"""
        return f"TempMailIOClient(email={self.email_address})"


def main():
    """
    示例用法
    """
    # 使用上下文管理器
    with TempMailIOClient() as client:
        # 创建邮箱
        email, token = client.create_mailbox()
        print(f"\n✅ 邮箱创建成功!")
        print(f"📧 邮箱地址: {email}")
        print(f"🔑 Token: {token}")

        # 获取可用域名
        print("\n📋 获取可用域名...")
        domains = client.get_domains()
        print(f"✅ 找到 {len(domains)} 个可用域名:")
        for domain in domains[:3]:  # 只显示前3个
            print(f"  - {domain['name']} ({domain['type']})")

        # 等待邮件
        print(f"\n⏳ 等待接收邮件... (60秒超时)")
        print(f"💡 请向 {email} 发送测试邮件")

        try:
            messages = client.wait_for_message(timeout=60, poll_interval=5)

            print(f"\n✅ 收到 {len(messages)} 封邮件:")
            for i, msg in enumerate(messages, 1):
                print(f"\n📨 邮件 {i}:")
                print(f"  发件人: {msg.get('from', 'N/A')}")
                print(f"  主题: {msg.get('subject', 'N/A')}")
                print(f"  时间: {msg.get('date', 'N/A')}")

                content = client.get_message_content(msg)
                if content:
                    preview = content[:100] + "..." if len(content) > 100 else content
                    print(f"  内容预览: {preview}")

        except TempMailIOError as e:
            print(f"\n⚠️  {str(e)}")
            print("💡 可以稍后使用 get_messages() 手动检查邮件")


if __name__ == "__main__":
    main()

# Made with Bob
