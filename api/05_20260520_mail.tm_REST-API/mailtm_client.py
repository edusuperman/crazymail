"""
Mail.tm API 客户端

这是一个用于与 Mail.tm 临时邮箱服务交互的 Python 客户端。
Mail.tm 提供完全免费的临时邮箱服务，支持 REST API 和 JWT 认证。

作者: IBM CrazyMail Project
创建日期: 2026-05-20
版本: 1.0.0
"""

import requests
import time
import logging
import random
import string
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MailTmAPIError(Exception):
    """API错误基类"""

    pass


class AuthenticationError(MailTmAPIError):
    """认证错误"""

    pass


class RateLimitError(MailTmAPIError):
    """速率限制错误"""

    pass


class AccountCreationError(MailTmAPIError):
    """账户创建错误"""

    pass


class MailTmClient:
    """
    Mail.tm API 客户端

    提供与 Mail.tm 临时邮箱服务交互的完整功能。

    特点：
    - 完全免费，无需 API Key
    - REST API + JWT 认证
    - 速率限制：8 QPS
    - 支持邮件接收、查看、删除

    Attributes:
        base_url (str): API基础URL
        session (requests.Session): HTTP会话对象
        timeout (int): 请求超时时间（秒）
        max_retries (int): 最大重试次数
        retry_delay (int): 重试延迟（秒）

    Example:
        >>> client = MailTmClient()
        >>> email, password = client.create_account()
        >>> print(f"临时邮箱: {email}")
        >>> messages = client.get_messages()
        >>> print(f"收到 {len(messages)} 封邮件")
    """

    def __init__(
        self,
        base_url: str = "https://api.mail.tm",
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
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            }
        )

        # 认证相关
        self.jwt_token: Optional[str] = None
        self.token_time: Optional[float] = None

        # 账户相关
        self.email_address: Optional[str] = None
        self.password: Optional[str] = None
        self.account_id: Optional[str] = None

        logger.info(f"Mail.tm 客户端初始化完成: {base_url}")

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        发送HTTP请求（带重试机制和速率限制）

        Args:
            method: HTTP方法（GET, POST等）
            endpoint: API端点
            **kwargs: 其他请求参数

        Returns:
            requests.Response: 响应对象

        Raises:
            MailTmAPIError: 请求失败时抛出
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    f"请求: {method} {url} (尝试 {attempt + 1}/{self.max_retries})"
                )

                # 速率限制：8 QPS，添加延迟
                time.sleep(0.125)  # 125ms 延迟确保不超过 8 QPS

                response = self.session.request(
                    method=method, url=url, timeout=self.timeout, **kwargs
                )

                # 检查速率限制
                if response.status_code == 429:
                    logger.warning("触发速率限制，等待后重试...")
                    time.sleep(5)
                    continue

                response.raise_for_status()
                logger.debug(f"响应: {response.status_code}")
                return response

            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"请求失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}"
                )

                if attempt == self.max_retries - 1:
                    raise MailTmAPIError(f"请求失败: {str(e)}")

                # 指数退避
                delay = self.retry_delay * (2**attempt)
                logger.info(f"等待 {delay} 秒后重试...")
                time.sleep(delay)

    def get_domains(self) -> List[Dict[str, Any]]:
        """
        获取可用域名列表

        Returns:
            List[Dict]: 域名列表

        Raises:
            MailTmAPIError: 获取失败时抛出
        """
        try:
            logger.info("获取可用域名...")
            response = self._request("GET", "/domains")
            data = response.json()

            # API 可能返回字典或列表
            if isinstance(data, dict):
                domains = data.get("hydra:member", [])
            else:
                domains = data

            logger.info(f"找到 {len(domains)} 个可用域名")

            return domains

        except Exception as e:
            logger.error(f"获取域名失败: {str(e)}")
            raise MailTmAPIError(f"获取域名失败: {str(e)}")

    def create_account(
        self, address: Optional[str] = None, password: Optional[str] = None
    ) -> tuple[str, str]:
        """
        创建新账户

        Args:
            address: 邮箱地址（可选，不提供则自动生成）
            password: 密码（可选，不提供则自动生成）

        Returns:
            tuple: (邮箱地址, 密码)

        Raises:
            AccountCreationError: 创建失败时抛出
        """
        try:
            # 如果未提供地址，自动生成
            if not address:
                domains = self.get_domains()
                if not domains:
                    raise AccountCreationError("无可用域名")

                domain = domains[0]["domain"]
                username = "".join(
                    random.choices(string.ascii_lowercase + string.digits, k=10)
                )
                address = f"{username}@{domain}"

            # 如果未提供密码，自动生成
            if not password:
                password = "".join(
                    random.choices(string.ascii_letters + string.digits, k=12)
                )

            logger.info(f"创建账户: {address}")

            data = {"address": address, "password": password}

            response = self._request("POST", "/accounts", json=data)
            account_data = response.json()

            self.email_address = address
            self.password = password
            self.account_id = account_data.get("id")

            logger.info(f"账户创建成功: {address}")
            return address, password

        except Exception as e:
            logger.error(f"创建账户失败: {str(e)}")
            raise AccountCreationError(f"创建账户失败: {str(e)}")

    def get_token(
        self, address: Optional[str] = None, password: Optional[str] = None
    ) -> str:
        """
        获取 JWT Token

        Args:
            address: 邮箱地址（可选，使用已保存的地址）
            password: 密码（可选，使用已保存的密码）

        Returns:
            str: JWT Token

        Raises:
            AuthenticationError: 认证失败时抛出
        """
        try:
            address = address or self.email_address
            password = password or self.password

            if not address or not password:
                raise AuthenticationError("需要提供邮箱地址和密码")

            logger.info(f"获取 Token: {address}")

            data = {"address": address, "password": password}

            response = self._request("POST", "/token", json=data)
            token_data = response.json()

            self.jwt_token = token_data.get("token")
            self.token_time = time.time()

            if not self.jwt_token:
                raise AuthenticationError("未能获取 JWT Token")

            # 更新会话头部
            self.session.headers.update({"Authorization": f"Bearer {self.jwt_token}"})

            logger.info("Token 获取成功")
            return self.jwt_token

        except Exception as e:
            logger.error(f"获取 Token 失败: {str(e)}")
            raise AuthenticationError(f"获取 Token 失败: {str(e)}")

    def _ensure_authenticated(self):
        """确保已认证，如果未认证或令牌过期则重新认证"""
        if not self.jwt_token:
            if not self.email_address or not self.password:
                raise AuthenticationError("未登录，请先创建账户或提供登录凭证")
            self.get_token()
        elif self.token_time and (time.time() - self.token_time > 3600):
            logger.info("Token 已过期，重新获取...")
            self.get_token()

    def get_account_info(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取账户信息

        Args:
            account_id: 账户ID（可选，使用已保存的ID）

        Returns:
            Dict: 账户信息

        Raises:
            MailTmAPIError: 获取失败时抛出
        """
        self._ensure_authenticated()

        try:
            account_id = account_id or self.account_id
            if not account_id:
                raise MailTmAPIError("需要提供账户ID")

            logger.info(f"获取账户信息: {account_id}")
            response = self._request("GET", f"/accounts/{account_id}")
            data = response.json()

            return data

        except Exception as e:
            logger.error(f"获取账户信息失败: {str(e)}")
            raise MailTmAPIError(f"获取账户信息失败: {str(e)}")

    def get_messages(self, page: int = 1) -> List[Dict[str, Any]]:
        """
        获取邮件列表

        Args:
            page: 页码（默认为1）

        Returns:
            List[Dict]: 邮件列表

        Raises:
            MailTmAPIError: 获取失败时抛出
        """
        self._ensure_authenticated()

        try:
            logger.debug(f"获取邮件列表（第 {page} 页）...")
            response = self._request("GET", f"/messages?page={page}")
            data = response.json()

            # API 可能返回字典或列表
            if isinstance(data, dict):
                messages = data.get("hydra:member", [])
            else:
                messages = data

            logger.info(f"收件箱中有 {len(messages)} 封邮件")
            return messages

        except Exception as e:
            logger.error(f"获取邮件列表失败: {str(e)}")
            raise MailTmAPIError(f"获取邮件列表失败: {str(e)}")

    def get_message(self, message_id: str) -> Dict[str, Any]:
        """
        获取邮件详情

        Args:
            message_id: 邮件ID

        Returns:
            Dict: 邮件详情

        Raises:
            MailTmAPIError: 获取失败时抛出
        """
        self._ensure_authenticated()

        try:
            logger.info(f"获取邮件详情: {message_id}")
            response = self._request("GET", f"/messages/{message_id}")
            data = response.json()

            return data

        except Exception as e:
            logger.error(f"获取邮件详情失败: {str(e)}")
            raise MailTmAPIError(f"获取邮件详情失败: {str(e)}")

    def delete_message(self, message_id: str) -> bool:
        """
        删除邮件

        Args:
            message_id: 邮件ID

        Returns:
            bool: 是否删除成功
        """
        self._ensure_authenticated()

        try:
            logger.info(f"删除邮件: {message_id}")
            self._request("DELETE", f"/messages/{message_id}")

            logger.info("邮件删除成功")
            return True

        except Exception as e:
            logger.error(f"删除邮件失败: {str(e)}")
            return False

    def mark_as_read(self, message_id: str) -> bool:
        """
        标记邮件为已读

        Args:
            message_id: 邮件ID

        Returns:
            bool: 是否标记成功
        """
        self._ensure_authenticated()

        try:
            logger.info(f"标记邮件为已读: {message_id}")
            self._request("PATCH", f"/messages/{message_id}", json={"seen": True})

            logger.info("邮件标记成功")
            return True

        except Exception as e:
            logger.error(f"标记邮件失败: {str(e)}")
            return False

    def wait_for_message(
        self,
        timeout: int = 300,
        check_interval: int = 10,
        callback: Optional[Callable] = None,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        等待接收邮件

        Args:
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）
            callback: 收到邮件时的回调函数

        Returns:
            Optional[List[Dict]]: 邮件列表，超时返回None
        """
        logger.info(f"等待接收邮件（超时: {timeout}秒，间隔: {check_interval}秒）...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                messages = self.get_messages()

                if messages:
                    logger.info(f"收到 {len(messages)} 封邮件")
                    if callback:
                        callback(messages)
                    return messages

                elapsed = int(time.time() - start_time)
                remaining = timeout - elapsed
                logger.debug(
                    f"暂无邮件，继续等待... (已等待: {elapsed}秒, 剩余: {remaining}秒)"
                )

                time.sleep(check_interval)

            except Exception as e:
                logger.error(f"检查邮件时出错: {str(e)}")
                time.sleep(check_interval)

        logger.warning("等待超时，未收到邮件")
        return None

    def delete_account(self, account_id: Optional[str] = None) -> bool:
        """
        删除账户

        Args:
            account_id: 账户ID（可选，使用已保存的ID）

        Returns:
            bool: 是否删除成功
        """
        self._ensure_authenticated()

        try:
            account_id = account_id or self.account_id
            if not account_id:
                raise MailTmAPIError("需要提供账户ID")

            logger.info(f"删除账户: {account_id}")
            self._request("DELETE", f"/accounts/{account_id}")

            # 清除本地状态
            self.email_address = None
            self.password = None
            self.account_id = None
            self.jwt_token = None

            logger.info("账户删除成功")
            return True

        except Exception as e:
            logger.error(f"删除账户失败: {str(e)}")
            return False

    def close(self):
        """关闭客户端，清理资源"""
        logger.info("关闭客户端...")
        self.session.close()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()

    def __repr__(self) -> str:
        """字符串表示"""
        return f"<MailTmClient(email={self.email_address})>"


def main():
    """
    主函数 - 使用示例
    """
    # 使用上下文管理器
    with MailTmClient() as client:
        try:
            # 1. 创建账户
            email, password = client.create_account()
            print(f"\n临时邮箱地址: {email}")
            print(f"密码: {password}")

            # 2. 获取 Token
            client.get_token()

            # 3. 获取账户信息
            account_info = client.get_account_info()
            print(f"\n账户信息:")
            print(f"  配额: {account_info.get('quota')} 字节")
            print(f"  已用: {account_info.get('used')} 字节")
            print(f"  创建时间: {account_info.get('createdAt')}")

            print(f"\n请向 {email} 发送测试邮件")
            print("等待接收邮件...\n")

            # 4. 等待接收邮件
            def on_message_received(messages):
                print(f"\n收到 {len(messages)} 封新邮件!")
                for msg in messages:
                    print(f"  - 发件人: {msg.get('from', {}).get('address')}")
                    print(f"    主题: {msg.get('subject')}")

            messages = client.wait_for_message(
                timeout=60, check_interval=10, callback=on_message_received
            )

            # 5. 获取邮件详情
            if messages:
                for msg in messages:
                    detail = client.get_message(msg["id"])
                    print(f"\n邮件详情:")
                    print(f"  发件人: {detail.get('from', {}).get('address')}")
                    print(f"  主题: {detail.get('subject')}")
                    print(f"  内容预览: {detail.get('intro', '')}")

                    # 标记为已读
                    client.mark_as_read(msg["id"])
            else:
                print("\n未收到邮件")

        except Exception as e:
            logger.error(f"发生错误: {str(e)}")
            raise


if __name__ == "__main__":
    main()

# Made with Bob
