"""
Temp-Mail.io 邮件适配器

将 Temp-Mail.io REST API 适配到统一 EmailAdapter 接口。
基于已有的 tempmailio_client_v2.py 逻辑，改用 httpx 异步客户端。

特点：
- 完全免费，无需 API Key
- REST API，无需认证创建邮箱
- 支持多域名选择
- 支持邮件接收和详情查看

作者: CrazyMail Project
创建日期: 2026-06-12
版本: 1.0.0
"""

from __future__ import annotations

import logging
import random
import string
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

_DATE_FORMATS: list[str] = [
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%dT%H:%M:%S.%f%z",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%d %H:%M:%S",
]


class TempMailIOAdapter(EmailAdapter):
    """Temp-Mail.io 适配器

    实现 EmailAdapter 接口，封装 Temp-Mail.io REST API。
    使用 httpx.AsyncClient 进行异步 HTTP 请求。

    用法::

        adapter = TempMailIOAdapter()
        domains = await adapter.get_domains()
        email = await adapter.create_email(username="myname", domain="example.com")
        messages = await adapter.get_messages(email.address)
        await adapter.aclose()

    Attributes:
        _base_url:    API 基础地址
        _client:      httpx 异步客户端
        _token:       当前邮箱的认证令牌
        _email:       当前邮箱地址
    """

    def __init__(
        self,
        base_url: str = "https://api.internal.temp-mail.io/api",
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._max_retries = max_retries

        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=timeout,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Application-Name": "web",
                "Application-Version": "4.0.0",
                "x-cors-header": "iaWg3pchvFx48fY",
                "Content-Type": "application/json",
            },
            follow_redirects=True,
        )

        self._token: str | None = None
        self._email: str | None = None

        logger.info("TempMailIOAdapter 初始化: %s", base_url)

    @property
    def provider_name(self) -> str:
        return "tempmailio"

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        json: dict[str, Any] | None = None,
        auth_required: bool = False,
    ) -> httpx.Response:
        headers: dict[str, str] = {}
        if auth_required and self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        last_exc: Exception | None = None

        for attempt in range(self._max_retries):
            try:
                response = await self._client.request(
                    method=method,
                    url=endpoint,
                    json=json,
                    headers=headers if headers else None,
                )

                if response.status_code == 429:
                    logger.warning("触发速率限制，等待 5 秒后重试...")
                    import asyncio
                    await asyncio.sleep(5)
                    continue

                if response.is_success:
                    return response

                self._raise_mapped_error(response)

            except httpx.TimeoutException as exc:
                last_exc = exc
                logger.warning("请求超时 (尝试 %d/%d): %s", attempt + 1, self._max_retries, exc)
                if attempt < self._max_retries - 1:
                    import asyncio
                    await asyncio.sleep(2 ** attempt * 0.5)

            except httpx.NetworkError as exc:
                last_exc = exc
                logger.warning("网络错误 (尝试 %d/%d): %s", attempt + 1, self._max_retries, exc)
                if attempt < self._max_retries - 1:
                    import asyncio
                    await asyncio.sleep(2 ** attempt * 0.5)

            except (AuthenticationError, RateLimitError, EmailAdapterError):
                raise

        if isinstance(last_exc, (httpx.TimeoutException, httpx.NetworkError)):
            raise NetworkError(f"请求失败（已重试 {self._max_retries} 次）: {last_exc}", provider="tempmailio")
        raise EmailAdapterError(f"请求失败: {last_exc}", provider="tempmailio")

    def _raise_mapped_error(self, response: httpx.Response) -> None:
        status = response.status_code
        try:
            body = response.json()
            detail = body.get("message") or body.get("detail") or ""
        except Exception:
            detail = response.text[:300] if response.text else ""

        msg = f"HTTP {status}: {detail}"

        if status in (401, 403):
            raise AuthenticationError(msg, provider="tempmailio")
        if status == 429:
            raise RateLimitError(msg, provider="tempmailio")
        raise EmailAdapterError(msg, provider="tempmailio", details={"status": status})

    @staticmethod
    def _parse_datetime(date_str: str | None) -> datetime | None:
        if not date_str:
            return None
        for fmt in _DATE_FORMATS:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return None

    @staticmethod
    def _to_email_message(raw: dict[str, Any]) -> EmailMessage:
        from_info = raw.get("from") or {}
        if isinstance(from_info, str):
            from_address = from_info
            from_name = ""
        else:
            from_address = from_info.get("address", "")
            from_name = from_info.get("name", "")

        raw_attachments = raw.get("attachments") or []
        attachments = [
            Attachment(
                filename=a.get("filename", "") or a.get("name", ""),
                content_type=a.get("contentType", "") or a.get("content_type", ""),
                size=a.get("size", 0),
                download_url=a.get("downloadUrl", "") or a.get("download_url", ""),
            )
            for a in raw_attachments
        ]

        date_str = raw.get("created_at") or raw.get("createdAt") or raw.get("date")
        received_at = TempMailIOAdapter._parse_datetime(date_str)

        body_text = raw.get("body_text") or raw.get("text") or ""
        body_html = raw.get("body_html") or ""
        if not body_html and isinstance(raw.get("html"), list):
            body_html = "".join(raw["html"])

        return EmailMessage(
            id=raw.get("_id", "") or raw.get("id", ""),
            from_address=from_address,
            from_name=from_name,
            subject=raw.get("subject", ""),
            body_text=body_text,
            body_html=body_html,
            received_at=received_at,
            is_read=raw.get("seen", False) or raw.get("is_read", False),
            has_attachments=bool(attachments),
            attachments=attachments,
            raw=raw,
        )

    async def create_email(
        self,
        username: str | None = None,
        domain: str | None = None,
    ) -> EmailAddress:
        """创建临时邮箱地址

        Temp-Mail.io API 创建端点使用 min/max_name_length 参数。
        当指定 username 时，使用其长度范围；否则默认 10 位随机用户名。

        Args:
            username: 自定义用户名（API 会根据长度范围生成）
            domain:   自定义域名（当前 API 版本不支持指定，使用可用域名）

        Returns:
            EmailAddress: 创建成功的邮箱信息
        """
        min_len = max(len(username), 5) if username else 10
        max_len = max(min_len, 15) if username else 10

        logger.info("创建邮箱 (min_len=%d, max_len=%d)", min_len, max_len)

        response = await self._request(
            "POST",
            "/v3/email/new",
            json={
                "min_name_length": min_len,
                "max_name_length": max_len,
            },
        )
        data = response.json()

        address = data.get("email", "")
        self._token = data.get("token", "")
        self._email = address

        if not address:
            raise EmailAdapterError("未能获取邮箱地址", provider="tempmailio")

        logger.info("邮箱创建成功: %s", address)
        return EmailAddress(
            address=address,
            token=self._token or "",
            provider="tempmailio",
        )

    async def get_messages(self, email_address: str) -> list[EmailMessage]:
        logger.debug("获取邮件列表: %s", email_address)

        response = await self._request("GET", f"/v3/email/{email_address}/messages")
        data = response.json()

        raw_messages: list[dict[str, Any]] = data if isinstance(data, list) else []
        messages = [self._to_email_message(m) for m in raw_messages]
        logger.info("收件箱 %s 有 %d 封邮件", email_address, len(messages))
        return messages

    async def get_message(self, message_id: str) -> EmailMessage:
        logger.info("获取邮件详情: %s", message_id)

        if not self._email:
            raise EmailAdapterError("未创建邮箱，请先调用 create_email", provider="tempmailio")

        messages = await self.get_messages(self._email)
        for msg in messages:
            if msg.id == message_id:
                return msg

        raise EmailAdapterError(f"未找到邮件: {message_id}", provider="tempmailio")

    async def get_domains(self) -> list[str]:
        """获取可用域名列表

        Returns:
            list[str]: 可用域名列表
        """
        logger.info("获取可用域名...")

        response = await self._request("GET", "/v4/domains")
        data = response.json()

        raw_domains: list[dict[str, Any]] = data.get("domains", [])
        domains = [d["name"] for d in raw_domains if d.get("name")]
        logger.info("找到 %d 个可用域名", len(domains))
        return domains

    async def check_health(self) -> bool:
        try:
            domains = await self.get_domains()
            return len(domains) > 0
        except Exception:
            logger.warning("Temp-Mail.io 健康检查失败")
            return False

    async def aclose(self) -> None:
        logger.info("关闭 TempMailIOAdapter...")
        await self._client.aclose()

    def __repr__(self) -> str:
        return f"<TempMailIOAdapter(provider=tempmailio, email={self._email})>"
