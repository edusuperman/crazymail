"""
统一邮件适配器接口

定义所有邮件 API 适配器必须遵循的抽象基类、数据类和异常类。
各 provider 的具体适配器继承 EmailAdapter 并实现抽象方法。

作者: CrazyMail Project
创建日期: 2026-06-12
版本: 1.0.0
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


# ════════════════════════════════════════════
# 异常类
# ════════════════════════════════════════════


class EmailAdapterError(Exception):
    """邮件适配器通用错误基类"""

    def __init__(self, message: str, provider: str = "", details: dict[str, Any] | None = None) -> None:
        self.provider = provider
        self.details = details or {}
        super().__init__(message)


class AuthenticationError(EmailAdapterError):
    """认证失败（Token 过期、凭证无效等）"""


class RateLimitError(EmailAdapterError):
    """速率限制（请求过于频繁）"""


class NetworkError(EmailAdapterError):
    """网络层错误（连接超时、DNS 解析失败等）"""


# ════════════════════════════════════════════
# 数据类
# ════════════════════════════════════════════


@dataclass
class EmailAddress:
    """临时邮箱地址

    Attributes:
        address:    完整邮箱地址，如 user@domain.com
        username:   @ 前的用户名部分
        domain:     @ 后的域名部分
        token:      认证令牌（JWT 或 API Key），部分 provider 可能为空
        expires_at: 邮箱过期时间，None 表示永不过期或未知
        provider:   提供商标识，如 "mail.tm"、"tempmailio"
    """

    address: str
    username: str = ""
    domain: str = ""
    token: str = ""
    expires_at: datetime | None = None
    provider: str = ""

    def __post_init__(self) -> None:
        """自动从 address 拆分 username 和 domain（如果未显式提供）"""
        if not self.username or not self.domain:
            parts = self.address.split("@", 1)
            if len(parts) == 2:
                self.username = self.username or parts[0]
                self.domain = self.domain or parts[1]


@dataclass
class Attachment:
    """邮件附件

    Attributes:
        filename:    文件名
        content_type: MIME 类型
        size:        文件大小（字节），未知时为 0
        download_url: 附件下载地址，部分 provider 提供
    """

    filename: str
    content_type: str = ""
    size: int = 0
    download_url: str = ""


@dataclass
class EmailMessage:
    """邮件消息

    Attributes:
        id:              邮件唯一标识（provider 内部 ID）
        from_address:    发件人地址
        from_name:       发件人显示名称
        subject:         邮件主题
        body_text:       纯文本正文
        body_html:       HTML 正文
        received_at:     接收时间
        is_read:         是否已读
        has_attachments: 是否包含附件
        attachments:     附件列表
        raw:             原始 API 返回数据（调试用，不参与业务逻辑）
    """

    id: str
    from_address: str = ""
    from_name: str = ""
    subject: str = ""
    body_text: str = ""
    body_html: str = ""
    received_at: datetime | None = None
    is_read: bool = False
    has_attachments: bool = False
    attachments: list[Attachment] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


# ════════════════════════════════════════════
# 抽象基类
# ════════════════════════════════════════════


class EmailAdapter(abc.ABC):
    """邮件 API 适配器抽象基类

    所有 provider 适配器必须继承此类并实现标记为 @abstractmethod 的方法。

    必须实现：
        provider_name — 提供商标识
        create_email  — 创建临时邮箱
        get_messages   — 获取邮件列表
        get_message    — 获取单封邮件详情

    可选实现（有默认实现，子类可覆盖）：
        delete_message  — 删除邮件
        mark_as_read    — 标记已读
        get_domains     — 获取可用域名列表
        check_health    — 健康检查
    """

    # ------------------------------------------------------------------ #
    #  抽象属性                                                            #
    # ------------------------------------------------------------------ #

    @property
    @abc.abstractmethod
    def provider_name(self) -> str:
        """提供商标识（如 "mail.tm"、"tempmailio"）

        Returns:
            str: 提供商名称，用于日志和注册表
        """
        ...

    # ------------------------------------------------------------------ #
    #  抽象方法（必须实现）                                                 #
    # ------------------------------------------------------------------ #

    @abc.abstractmethod
    async def create_email(self, username: str | None = None, domain: str | None = None) -> EmailAddress:
        """创建临时邮箱地址

        Args:
            username: 自定义用户名，None 则自动生成
            domain:   自定义域名，None 则使用 provider 默认域名

        Returns:
            EmailAddress: 创建成功的邮箱信息

        Raises:
            EmailAdapterError: 创建失败
            RateLimitError:    请求过于频繁
            NetworkError:      网络错误
        """
        ...

    @abc.abstractmethod
    async def get_messages(self, email_address: str) -> list[EmailMessage]:
        """获取指定邮箱的邮件列表

        Args:
            email_address: 邮箱地址

        Returns:
            list[EmailMessage]: 邮件列表，按接收时间倒序

        Raises:
            AuthenticationError: 认证失败
            EmailAdapterError:   获取失败
            NetworkError:        网络错误
        """
        ...

    @abc.abstractmethod
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
        ...

    # ------------------------------------------------------------------ #
    #  可选方法（有默认实现，子类可覆盖）                                      #
    # ------------------------------------------------------------------ #

    async def delete_message(self, message_id: str) -> bool:
        """删除邮件（默认不支持，子类覆盖实现）

        Args:
            message_id: 邮件 ID

        Returns:
            bool: 是否删除成功

        Raises:
            EmailAdapterError: 删除失败
        """
        raise NotImplementedError(f"{self.provider_name} 不支持删除邮件")

    async def mark_as_read(self, message_id: str) -> bool:
        """标记邮件为已读（默认不支持，子类覆盖实现）

        Args:
            message_id: 邮件 ID

        Returns:
            bool: 是否标记成功

        Raises:
            EmailAdapterError: 标记失败
        """
        raise NotImplementedError(f"{self.provider_name} 不支持标记已读")

    async def get_domains(self) -> list[str]:
        """获取可用域名列表（默认不支持，子类覆盖实现）

        Returns:
            list[str]: 可用域名列表

        Raises:
            EmailAdapterError: 获取失败
        """
        raise NotImplementedError(f"{self.provider_name} 不支持获取域名列表")

    async def check_health(self) -> bool:
        """健康检查 — 验证 API 是否可达（默认返回 True，子类覆盖实现）

        Returns:
            bool: API 是否健康
        """
        return True

    # ------------------------------------------------------------------ #
    #  魔术方法                                                            #
    # ------------------------------------------------------------------ #

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(provider={self.provider_name})>"
