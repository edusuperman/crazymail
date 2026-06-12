"""
邮件适配器注册表

集中管理所有已注册的邮件 API 适配器实例。
支持按 provider 名称查找、列出全部、运行时注册/注销。

作者: CrazyMail Project
创建日期: 2026-06-12
版本: 1.0.0
"""

from __future__ import annotations

import logging
from typing import Any

from .base import EmailAdapter

logger = logging.getLogger(__name__)


class EmailAdapterRegistry:
    """邮件适配器注册表

    维护 provider_name → EmailAdapter 的映射关系。
    单例模式：通过 EmailAdapterRegistry.instance() 获取全局唯一实例。

    使用示例::

        registry = EmailAdapterRegistry.instance()
        registry.register(MailTmAdapter())
        adapter = registry.get("mail.tm")

    Attributes:
        _adapters: 已注册的适配器字典
    """

    _global_instance: EmailAdapterRegistry | None = None

    def __init__(self) -> None:
        self._adapters: dict[str, EmailAdapter] = {}

    # ------------------------------------------------------------------ #
    #  单例访问                                                            #
    # ------------------------------------------------------------------ #

    @classmethod
    def instance(cls) -> EmailAdapterRegistry:
        """获取全局单例实例

        Returns:
            EmailAdapterRegistry: 全局唯一注册表
        """
        if cls._global_instance is None:
            cls._global_instance = cls()
        return cls._global_instance

    @classmethod
    def reset(cls) -> None:
        """重置全局单例（主要用于测试）"""
        cls._global_instance = None

    # ------------------------------------------------------------------ #
    #  注册 / 注销                                                         #
    # ------------------------------------------------------------------ #

    def register(self, adapter: EmailAdapter) -> None:
        """注册适配器

        如果同名 provider 已存在，将被覆盖并记录警告日志。

        Args:
            adapter: 要注册的适配器实例

        Raises:
            TypeError: adapter 不是 EmailAdapter 的实例
        """
        if not isinstance(adapter, EmailAdapter):
            raise TypeError(f"期望 EmailAdapter 实例，收到 {type(adapter).__name__}")

        name = adapter.provider_name

        if name in self._adapters:
            logger.warning("适配器 '%s' 已存在，将被覆盖", name)

        self._adapters[name] = adapter
        logger.info("已注册邮件适配器: %s", name)

    def unregister(self, provider_name: str) -> bool:
        """注销适配器

        Args:
            provider_name: 提供商名称

        Returns:
            bool: 是否成功注销（provider 不存在时返回 False）
        """
        if provider_name in self._adapters:
            del self._adapters[provider_name]
            logger.info("已注销邮件适配器: %s", provider_name)
            return True

        logger.warning("尝试注销不存在的适配器: %s", provider_name)
        return False

    # ------------------------------------------------------------------ #
    #  查询                                                                #
    # ------------------------------------------------------------------ #

    def get(self, provider_name: str) -> EmailAdapter:
        """按名称获取适配器

        Args:
            provider_name: 提供商名称（如 "mail.tm"）

        Returns:
            EmailAdapter: 对应的适配器实例

        Raises:
            KeyError: provider 未注册
        """
        adapter = self._adapters.get(provider_name)
        if adapter is None:
            available = ", ".join(self._adapters.keys()) or "(无)"
            raise KeyError(
                f"未找到邮件适配器: '{provider_name}'。已注册: {available}"
            )
        return adapter

    def get_or_none(self, provider_name: str) -> EmailAdapter | None:
        """按名称获取适配器，不存在时返回 None

        Args:
            provider_name: 提供商名称

        Returns:
            EmailAdapter | None: 适配器实例或 None
        """
        return self._adapters.get(provider_name)

    def list_providers(self) -> list[str]:
        """列出所有已注册的提供商名称

        Returns:
            list[str]: 提供商名称列表（无序）
        """
        return list(self._adapters.keys())

    def list_adapters(self) -> list[EmailAdapter]:
        """列出所有已注册的适配器实例

        Returns:
            list[EmailAdapter]: 适配器实例列表（无序）
        """
        return list(self._adapters.values())

    def has(self, provider_name: str) -> bool:
        """检查指定 provider 是否已注册

        Args:
            provider_name: 提供商名称

        Returns:
            bool: 是否已注册
        """
        return provider_name in self._adapters

    # ------------------------------------------------------------------ #
    #  健康检查                                                            #
    # ------------------------------------------------------------------ #

    async def check_all_health(self) -> dict[str, bool]:
        """对所有已注册适配器执行健康检查

        Returns:
            dict[str, bool]: provider_name → 是否健康
        """
        results: dict[str, bool] = {}
        for name, adapter in self._adapters.items():
            try:
                results[name] = await adapter.check_health()
            except Exception:
                logger.exception("健康检查失败: %s", name)
                results[name] = False
        return results

    # ------------------------------------------------------------------ #
    #  魔术方法                                                            #
    # ------------------------------------------------------------------ #

    def __len__(self) -> int:
        return len(self._adapters)

    def __contains__(self, provider_name: str) -> bool:
        return self.has(provider_name)

    def __repr__(self) -> str:
        providers = ", ".join(self._adapters.keys()) or "(空)"
        return f"<EmailAdapterRegistry([{providers}])>"
