"""
统一邮件适配器层

提供邮件 API 的统一抽象接口，屏蔽各 provider 实现差异。

公共接口：
    数据类:    EmailAddress, EmailMessage, Attachment
    抽象基类:  EmailAdapter
    注册表:    EmailAdapterRegistry
    异常类:    EmailAdapterError, AuthenticationError, RateLimitError, NetworkError

使用示例::

    from sites.shared.api_adapters import EmailAdapterRegistry, EmailAdapter, EmailAddress

    registry = EmailAdapterRegistry.instance()
    # registry.register(MyAdapter())
    # adapter = registry.get("mail.tm")
"""

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
from .registry import EmailAdapterRegistry

__all__ = [
    # 数据类
    "EmailAddress",
    "EmailMessage",
    "Attachment",
    # 抽象基类
    "EmailAdapter",
    # 注册表
    "EmailAdapterRegistry",
    # 异常类
    "EmailAdapterError",
    "AuthenticationError",
    "RateLimitError",
    "NetworkError",
]
