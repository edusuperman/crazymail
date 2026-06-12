"""
Temp-Mail.io API 客户端 v2.0

增强版本，在v1基础上添加：
- 完善异常类层次结构（添加NetworkError）
- 便利字段增强（timestamp, datetime, has_attachments, size）
- 客户端过滤功能
- 统一响应格式处理

作者: opencode + Xiaomi mimo
基于: v1 by Bob (AI Assistant)
创建日期: 2026-06-03
版本: 2.0.0
"""

import requests
import time
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# 异常类层次结构
# ============================================================================

class TempMailIOError(Exception):
    """API错误基类"""
    def __init__(self, message: str, code: Optional[int] = None):
        self.message = message
        self.code = code
        super().__init__(f"{message} (code: {code})" if code else message)


class AuthenticationError(TempMailIOError):
    """认证错误"""
    pass


class RateLimitError(TempMailIOError):
    """速率限制错误（429）"""
    pass


class NetworkError(TempMailIOError):
    """网络请求错误"""
    pass


# ============================================================================
# 客户端类
# ============================================================================

class TempMailIOClient:
    """
    Temp-Mail.io API客户端 v2.0

    Attributes:
        base_url (str): API基础URL
        session (requests.Session): HTTP会话对象
        email_address (str): 当前邮箱地址
        token (str): 认证令牌

    Example:
        >>> client = TempMailIOClient()
        >>> email, token = client.create_mailbox()
        >>> messages = client.get_messages()
        >>> enhanced = client.enhance_messages(messages)
        >>> filtered = client.filter_messages(enhanced, sender="test@example.com")
    """

    def __init__(
        self,
        base_url: str = "https://api.internal.temp-mail.io/api",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 2,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Application-Name": "web",
            "Application-Version": "4.0.0",
            "x-cors-header": "iaWg3pchvFx48fY",
            "Content-Type": "application/json",
        })

        self.email_address: Optional[str] = None
        self.token: Optional[str] = None

        logger.info(f"Temp-Mail.io客户端v2初始化完成: {base_url}")

    # ========================================================================
    # 错误处理
    # ========================================================================

    def _handle_error(self, response: requests.Response) -> None:
        """统一错误处理"""
        if response.status_code == 401:
            raise AuthenticationError("认证失败，请检查token")
        elif response.status_code == 429:
            raise RateLimitError("请求过多，请稍后重试")
        elif response.status_code >= 500:
            raise TempMailIOError(f"服务器错误: {response.status_code}", code=response.status_code)

    # ========================================================================
    # 核心请求
    # ========================================================================

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """发送HTTP请求（带重试机制）"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method=method, url=url, timeout=self.timeout, **kwargs
                )
                self._handle_error(response)
                response.raise_for_status()
                return response

            except (RateLimitError, AuthenticationError):
                raise
            except requests.exceptions.ConnectionError as e:
                raise NetworkError(f"网络连接失败: {e}")
            except requests.exceptions.Timeout as e:
                raise NetworkError(f"请求超时: {e}")
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise TempMailIOError(f"请求失败: {e}")
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                time.sleep(self.retry_delay)

        raise TempMailIOError("请求失败：超过最大重试次数")

    # ========================================================================
    # 邮箱操作
    # ========================================================================

    def create_mailbox(
        self, min_name_length: int = 10, max_name_length: int = 10
    ) -> tuple:
        """
        创建新的临时邮箱

        Args:
            min_name_length: 邮箱用户名最小长度
            max_name_length: 邮箱用户名最大长度

        Returns:
            tuple: (邮箱地址, 认证令牌)
        """
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
        self.email_address = data["email"]
        self.token = data["token"]
        logger.info(f"邮箱创建成功: {self.email_address}")
        return self.email_address, self.token

    def get_messages(self, email: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取邮箱中的所有邮件

        Args:
            email: 邮箱地址（如果不提供，使用当前邮箱）

        Returns:
            List[Dict[str, Any]]: 邮件列表
        """
        email_to_check = email or self.email_address
        if not email_to_check:
            raise TempMailIOError("未指定邮箱地址")

        response = self._request("GET", f"/v3/email/{email_to_check}/messages")
        messages = response.json()
        logger.info(f"获取到 {len(messages)} 封邮件")
        return messages

    def get_domains(self) -> List[Dict[str, Any]]:
        """获取所有可用的邮箱域名"""
        response = self._request("GET", "/v4/domains")
        data = response.json()
        domains = data.get("domains", [])
        logger.info(f"获取到 {len(domains)} 个可用域名")
        return domains

    def wait_for_message(
        self,
        email: Optional[str] = None,
        timeout: int = 300,
        poll_interval: int = 5,
        expected_count: int = 1,
    ) -> List[Dict[str, Any]]:
        """等待接收邮件（轮询方式）"""
        email_to_check = email or self.email_address
        if not email_to_check:
            raise TempMailIOError("未指定邮箱地址")

        logger.info(f"等待邮件... (超时: {timeout}秒)")
        start_time = time.time()

        while time.time() - start_time < timeout:
            messages = self.get_messages(email_to_check)
            if len(messages) >= expected_count:
                return messages
            time.sleep(poll_interval)

        raise TempMailIOError(f"等待邮件超时（{timeout}秒）")

    def get_message_content(self, message: Dict[str, Any]) -> str:
        """获取邮件的文本内容"""
        return message.get("body_text") or message.get("body_html", "")

    # ========================================================================
    # v2 增强功能
    # ========================================================================

    def enhance_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        为单条邮件添加便利字段

        添加字段:
            - timestamp: Unix时间戳（从created_at字段解析）
            - has_attachments: 是否有真实附件（排除签名和追踪像素）
            - content_size: 内容大小（字符数）
        """
        # 解析时间戳（temp-mail.io 使用 created_at 字段）
        if "timestamp" not in message:
            time_str = message.get("created_at") or message.get("date") or message.get("timestamp")
            if isinstance(time_str, str) and time_str:
                try:
                    dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                    message["timestamp"] = int(dt.timestamp())
                    message["datetime"] = dt.isoformat()
                except (ValueError, AttributeError):
                    message["timestamp"] = None
            elif isinstance(time_str, (int, float)):
                message["timestamp"] = int(time_str)

        # 附件标记（排除空名称的签名/追踪像素）
        if "has_attachments" not in message:
            attachments = message.get("attachments", [])
            real_attachments = [a for a in attachments if a.get("name", "").strip()]
            message["has_attachments"] = len(real_attachments) > 0
        if "has_attachments" not in message:
            attachments = message.get("attachments", [])
            message["has_attachments"] = len(attachments) > 0

        # 内容大小
        if "content_size" not in message:
            content = message.get("body_text") or message.get("body_html", "")
            message["content_size"] = len(content)

        return message

    def enhance_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """为多条邮件添加便利字段"""
        return [self.enhance_message(msg) for msg in messages]

    def filter_messages(
        self,
        messages: List[Dict[str, Any]],
        sender: Optional[str] = None,
        subject_contains: Optional[str] = None,
        has_attachments: Optional[bool] = None,
        since: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        客户端过滤邮件

        Args:
            messages: 邮件列表
            sender: 发件人邮箱过滤
            subject_contains: 主题包含关键词
            has_attachments: 是否有附件
            since: Unix时间戳，只返回此时间之后的邮件

        Returns:
            List[Dict[str, Any]]: 过滤后的邮件列表
        """
        filtered = []
        for msg in messages:
            if sender and sender.lower() not in msg.get("from", "").lower():
                continue
            if subject_contains and subject_contains.lower() not in msg.get("subject", "").lower():
                continue
            if has_attachments is not None and msg.get("has_attachments") != has_attachments:
                continue
            if since and msg.get("timestamp", 0) < since:
                continue
            filtered.append(msg)
        return filtered

    # ========================================================================
    # 资源管理
    # ========================================================================

    def close(self):
        """关闭客户端会话"""
        if self.session:
            self.session.close()
            logger.info("客户端会话已关闭")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __repr__(self) -> str:
        return f"TempMailIOClient(email={self.email_address})"
