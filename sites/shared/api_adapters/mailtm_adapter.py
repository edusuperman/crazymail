"""
Mail.tm 邮件适配器

将 Mail.tm REST API 适配到统一 EmailAdapter 接口。
基于已有的 mailtm_client_v2.py 逻辑，改用 httpx 异步客户端。

特点：
- 完全免费，无需 API Key
- REST API + JWT 认证
- 速率限制：8 QPS
- 自动 token 刷新

作者: CrazyMail Project
创建日期: 2026-06-12
版本: 1.0.0
"""

from __future__ import annotations

import logging
import random
import string
import time
from datetime import datetime
from typing import Any

import httpx

from .base import (
    Attachment,
    AuthenticationError,
    EmailAdapter,
    EmailAdapterError,
    EmailAddress,
    EmailMessage,
    NetworkError,
    RateLimitError,
)

logger = logging.getLogger(__name__)

# Mail.tm API 返回的日期格式列表（按常见程度排序）
_DATE_FORMATS: list[str] = [
    "%Y-%m-%dT%H:%M:%S.%fZ",  # 2026-05-20T12:34:56.789Z
    "%Y-%m-%dT%H:%M:%S.%f%z",  # 带时区偏移
    "%Y-%m-%dT%H:%M:%SZ",  # 无毫秒
    "%Y-%m-%dT%H:%M:%S%z",  # 无毫秒带时区
    "%Y-%m-%d %H:%M:%S",  # 空格分隔
]

# JWT 有效期（秒），超过后自动刷新
_TOKEN_TTL: int = 3600


class MailTmAdapter(EmailAdapter):
    """Mail.tm 适配器

    实现 EmailAdapter 接口，封装 Mail.tm REST API。
    使用 httpx.AsyncClient 进行异步 HTTP 请求。

    用法::

        adapter = MailTmAdapter()
        email = await adapter.create_email()
        messages = await adapter.get_messages(email.address)
        detail = await adapter.get_message(messages[0].id)
        await adapter.aclose()

    Attributes:
        _base_url:    API 基础地址
        _client:      httpx 异步客户端
        _jwt_token:   当前 JWT token
        _token_time:  token 获取时间戳
        _email:       当前登录的邮箱地址
        _password:    当前登录的密码
    """

    def __init__(
        self,
        base_url: str = "https://api.mail.tm",
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        """初始化适配器

        Args:
            base_url:    Mail.tm API 地址
            timeout:     请求超时（秒）
            max_retries: 最大重试次数
        """
        self._base_url = base_url.rstrip("/")
        self._max_retries = max_retries

        # 创建异步 HTTP 客户端
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=timeout,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
            },
            follow_redirects=True,
        )

        # 认证状态
        self._jwt_token: str | None = None
        self._token_time: float | None = None

        # 账户信息
        self._email: str | None = None
        self._password: str | None = None

        logger.info("MailTmAdapter 初始化: %s", base_url)

    # ================================================================== #
    #  抽象属性                                                            #
    # ================================================================== #

    @property
    def provider_name(self) -> str:
        """提供商标识"""
        return "mail.tm"

    # ================================================================== #
    #  内部工具方法                                                        #
    # ================================================================== #

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        json: dict[str, Any] | None = None,
        auth_required: bool = False,
    ) -> httpx.Response:
        """发送 HTTP 请求（带重试和错误映射）

        Args:
            method:        HTTP 方法
            endpoint:      API 路径（如 "/domains"）
            json:          请求体（POST/PATCH/PUT）
            auth_required: 是否需要认证（自动注入 Bearer token）

        Returns:
            httpx.Response: HTTP 响应

        Raises:
            AuthenticationError: 401/403
            RateLimitError:      429
            NetworkError:        网络层错误
            EmailAdapterError:   其他 API 错误
        """
        # 确保 token 有效
        if auth_required:
            await self._ensure_authenticated()

        headers: dict[str, str] = {}
        if auth_required and self._jwt_token:
            headers["Authorization"] = f"Bearer {self._jwt_token}"

        last_exc: Exception | None = None

        for attempt in range(self._max_retries):
            try:
                logger.debug("请求: %s %s (尝试 %d/%d)", method, endpoint, attempt + 1, self._max_retries)

                # 速率限制保护：8 QPS → 每次请求间隔至少 125ms
                if attempt > 0:
                    await _async_sleep(0.125)

                response = await self._client.request(
                    method=method,
                    url=endpoint,
                    json=json,
                    headers=headers if headers else None,
                )

                # 429 速率限制 → 等待后重试
                if response.status_code == 429:
                    logger.warning("触发速率限制，等待 5 秒后重试...")
                    await _async_sleep(5)
                    continue

                # 成功响应直接返回
                if response.is_success:
                    return response

                # 非成功响应 → 映射到统一异常
                self._raise_mapped_error(response)

            except httpx.TimeoutException as exc:
                last_exc = exc
                logger.warning("请求超时 (尝试 %d/%d): %s", attempt + 1, self._max_retries, exc)
                if attempt < self._max_retries - 1:
                    delay = 2 ** attempt * 0.5
                    await _async_sleep(delay)

            except httpx.NetworkError as exc:
                last_exc = exc
                logger.warning("网络错误 (尝试 %d/%d): %s", attempt + 1, self._max_retries, exc)
                if attempt < self._max_retries - 1:
                    delay = 2 ** attempt * 0.5
                    await _async_sleep(delay)

            except (AuthenticationError, RateLimitError, EmailAdapterError):
                # 已映射的异常直接抛出，不重试
                raise

        # 所有重试用尽
        if isinstance(last_exc, (httpx.TimeoutException, httpx.NetworkError)):
            raise NetworkError(f"请求失败（已重试 {self._max_retries} 次）: {last_exc}", provider="mail.tm")
        raise EmailAdapterError(f"请求失败: {last_exc}", provider="mail.tm")

    def _raise_mapped_error(self, response: httpx.Response) -> None:
        """将 HTTP 错误映射到统一异常类

        Args:
            response: 非成功状态码的 HTTP 响应

        Raises:
            AuthenticationError: 401/403
            RateLimitError:      429
            EmailAdapterError:   其他
        """
        status = response.status_code

        # 提取错误详情
        try:
            body = response.json()
            detail = (
                body.get("detail")
                or body.get("message")
                or body.get("hydra:description", "")
            )
        except Exception:
            detail = response.text[:300] if response.text else ""

        msg = f"HTTP {status}: {detail}"

        if status in (401, 403):
            raise AuthenticationError(msg, provider="mail.tm")
        if status == 429:
            raise RateLimitError(msg, provider="mail.tm")
        raise EmailAdapterError(msg, provider="mail.tm", details={"status": status})

    async def _ensure_authenticated(self) -> None:
        """确保 JWT token 有效（过期自动刷新）"""
        if not self._jwt_token:
            if not self._email or not self._password:
                raise AuthenticationError("未登录，请先调用 create_email 或提供凭证", provider="mail.tm")
            await self._fetch_token()
            return

        # 检查 token 是否过期
        if self._token_time and (time.time() - self._token_time > _TOKEN_TTL):
            logger.info("Token 已过期，自动刷新...")
            await self._fetch_token()

    async def _fetch_token(self) -> None:
        """获取/刷新 JWT token

        Raises:
            AuthenticationError: 认证失败
        """
        if not self._email or not self._password:
            raise AuthenticationError("缺少邮箱地址或密码", provider="mail.tm")

        logger.info("获取 Token: %s", self._email)

        response = await self._request(
            "POST",
            "/token",
            json={"address": self._email, "password": self._password},
        )
        data = response.json()

        token = data.get("token")
        if not token:
            raise AuthenticationError("未能获取 JWT Token", provider="mail.tm")

        self._jwt_token = token
        self._token_time = time.time()
        logger.info("Token 获取成功")

    @staticmethod
    def _parse_datetime(date_str: str | None) -> datetime | None:
        """解析 Mail.tm 返回的日期字符串

        Args:
            date_str: ISO-8601 风格日期字符串

        Returns:
            datetime | None: 解析成功返回 datetime，失败返回 None
        """
        if not date_str:
            return None
        for fmt in _DATE_FORMATS:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        # 最后尝试 fromisoformat（Python 3.11+ 支持更多变体）
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return None

    def _to_email_address(self, address: str, password: str) -> EmailAddress:
        """将地址和密码转为 EmailAddress 数据类

        Args:
            address:  完整邮箱地址
            password: 账户密码

        Returns:
            EmailAddress: 标准化数据类
        """
        return EmailAddress(
            address=address,
            token=self._jwt_token or "",
            provider="mail.tm",
        )

    @staticmethod
    def _to_email_message(raw: dict[str, Any]) -> EmailMessage:
        """将 API 原始数据转为 EmailMessage 数据类

        Args:
            raw: Mail.tm API 返回的消息字典

        Returns:
            EmailMessage: 标准化数据类
        """
        # 解析发件人
        from_info = raw.get("from") or {}
        from_address = from_info.get("address", "")
        from_name = from_info.get("name", "")

        # 解析附件
        raw_attachments = raw.get("attachments") or []
        attachments = [
            Attachment(
                filename=a.get("filename", ""),
                content_type=a.get("contentType", ""),
                size=a.get("size", 0),
                download_url=a.get("downloadUrl", ""),
            )
            for a in raw_attachments
        ]

        # 解析时间
        date_str = raw.get("createdAt") or raw.get("updatedAt")
        received_at = MailTmAdapter._parse_datetime(date_str)

        return EmailMessage(
            id=raw.get("id", ""),
            from_address=from_address,
            from_name=from_name,
            subject=raw.get("subject", ""),
            body_text=raw.get("text", ""),
            body_html="".join(raw.get("html") or []),
            received_at=received_at,
            is_read=raw.get("seen", False),
            has_attachments=bool(attachments),
            attachments=attachments,
            raw=raw,
        )

    # ================================================================== #
    #  必须实现的抽象方法                                                   #
    # ================================================================== #

    async def create_email(
        self,
        username: str | None = None,
        domain: str | None = None,
    ) -> EmailAddress:
        """创建临时邮箱地址

        流程：
        1. 获取可用域名（如果未指定）
        2. 生成随机用户名（如果未指定）
        3. POST /accounts 创建账户
        4. 自动获取 JWT token

        Args:
            username: 自定义用户名，None 则自动生成 10 位随机字符串
            domain:   自定义域名，None 则使用第一个可用域名

        Returns:
            EmailAddress: 创建成功的邮箱信息

        Raises:
            EmailAdapterError: 创建失败
            RateLimitError:    请求过于频繁
            NetworkError:      网络错误
        """
        # 获取域名
        if not domain:
            domains = await self.get_domains()
            if not domains:
                raise EmailAdapterError("无可用域名", provider="mail.tm")
            domain = domains[0]

        # 生成用户名
        if not username:
            username = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))

        address = f"{username}@{domain}"
        password = "".join(random.choices(string.ascii_letters + string.digits, k=12))

        logger.info("创建账户: %s", address)

        response = await self._request(
            "POST",
            "/accounts",
            json={"address": address, "password": password},
        )
        account_data = response.json()

        # 保存凭证（后续认证需要）
        self._email = address
        self._password = password

        # 自动获取 token
        await self._fetch_token()

        logger.info("账户创建成功: %s", address)
        return self._to_email_address(address, password)

    async def get_messages(self, email_address: str) -> list[EmailMessage]:
        """获取指定邮箱的邮件列表

        注意：Mail.tm API 基于 JWT token 认证，email_address 参数仅用于日志标识，
        实际请求使用已保存的 token。

        Args:
            email_address: 邮箱地址（用于日志标识）

        Returns:
            list[EmailMessage]: 邮件列表，按接收时间倒序

        Raises:
            AuthenticationError: 认证失败
            EmailAdapterError:   获取失败
            NetworkError:        网络错误
        """
        logger.debug("获取邮件列表: %s", email_address)

        response = await self._request("GET", "/messages", auth_required=True)
        data = response.json()

        # API 可能返回 {"hydra:member": [...]} 或直接返回列表
        if isinstance(data, dict):
            raw_messages: list[dict[str, Any]] = data.get("hydra:member", [])
        else:
            raw_messages = data

        messages = [self._to_email_message(m) for m in raw_messages]
        logger.info("收件箱 %s 有 %d 封邮件", email_address, len(messages))
        return messages

    async def get_message(self, message_id: str) -> EmailMessage:
        """获取单封邮件详情

        Args:
            message_id: 邮件 ID

        Returns:
            EmailMessage: 邮件详情

        Raises:
            EmailAdapterError: 获取失败
            NetworkError:      网络错误
        """
        logger.info("获取邮件详情: %s", message_id)

        response = await self._request(
            "GET",
            f"/messages/{message_id}",
            auth_required=True,
        )
        raw = response.json()
        return self._to_email_message(raw)

    # ================================================================== #
    #  可选方法实现                                                         #
    # ================================================================== #

    async def delete_message(self, message_id: str) -> bool:
        """删除邮件

        Args:
            message_id: 邮件 ID

        Returns:
            bool: 是否删除成功

        Raises:
            EmailAdapterError: 删除失败
        """
        logger.info("删除邮件: %s", message_id)
        await self._request(
            "DELETE",
            f"/messages/{message_id}",
            auth_required=True,
        )
        logger.info("邮件删除成功: %s", message_id)
        return True

    async def mark_as_read(self, message_id: str) -> bool:
        """标记邮件为已读

        Args:
            message_id: 邮件 ID

        Returns:
            bool: 是否标记成功

        Raises:
            EmailAdapterError: 标记失败
        """
        logger.info("标记已读: %s", message_id)
        await self._request(
            "PATCH",
            f"/messages/{message_id}",
            json={"seen": True},
            auth_required=True,
        )
        logger.info("邮件标记成功: %s", message_id)
        return True

    async def get_domains(self) -> list[str]:
        """获取可用域名列表

        Returns:
            list[str]: 可用域名列表（如 ["mail.tm"]）

        Raises:
            EmailAdapterError: 获取失败
        """
        logger.info("获取可用域名...")

        response = await self._request("GET", "/domains")
        data = response.json()

        # API 返回 {"hydra:member": [...]} 或直接返回列表
        if isinstance(data, dict):
            raw_domains: list[dict[str, Any]] = data.get("hydra:member", [])
        else:
            raw_domains = data

        domains = [d["domain"] for d in raw_domains if "domain" in d]
        logger.info("找到 %d 个可用域名", len(domains))
        return domains

    async def check_health(self) -> bool:
        """健康检查 — 尝试获取域名列表

        Returns:
            bool: API 是否健康
        """
        try:
            await self.get_domains()
            return True
        except Exception:
            logger.warning("Mail.tm 健康检查失败")
            return False

    # ================================================================== #
    #  资源清理                                                            #
    # ================================================================== #

    async def aclose(self) -> None:
        """关闭异步 HTTP 客户端，释放连接池"""
        logger.info("关闭 MailTmAdapter...")
        await self._client.aclose()

    def __repr__(self) -> str:
        return f"<MailTmAdapter(provider=mail.tm, email={self._email})>"


# ════════════════════════════════════════════
# 辅助函数
# ════════════════════════════════════════════


async def _async_sleep(seconds: float) -> None:
    """异步等待（避免阻塞事件循环）

    Args:
        seconds: 等待秒数
    """
    import asyncio

    await asyncio.sleep(seconds)
