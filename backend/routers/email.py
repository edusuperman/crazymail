"""邮件路由

提供临时邮箱的创建、收件箱查看、邮件详情、删除、标记已读等接口。
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel

# 将 sites/shared 加入 sys.path 以导入适配器
_SHARED = str(Path(__file__).resolve().parents[2] / "sites" / "shared")
if _SHARED not in sys.path:
    sys.path.insert(0, _SHARED)

from api_adapters.base import (  # noqa: E402
    AuthenticationError,
    EmailAdapterError,
    NetworkError,
    RateLimitError,
)
from api_adapters.mailtm_adapter import MailTmAdapter  # noqa: E402
from api_adapters.tempmailio_adapter import TempMailIOAdapter  # noqa: E402

router = APIRouter()

# 使用 Temp-Mail.io 作为主适配器（保留 MailTmAdapter 作为备用）
_adapter: TempMailIOAdapter | None = None
# 当前邮箱地址（用于获取邮件）
_current_email: str | None = None


def _get_adapter() -> TempMailIOAdapter:
    """获取或创建适配器实例"""
    global _adapter
    if _adapter is None:
        _adapter = TempMailIOAdapter()
    return _adapter


# ════════════════════════════════════════════
# 请求/响应模型
# ════════════════════════════════════════════


class CreateEmailRequest(BaseModel):
    username: str | None = None
    domain: str | None = None


class CreateEmailResponse(BaseModel):
    address: str
    username: str
    domain: str
    provider: str


class MessageSummary(BaseModel):
    id: str
    from_address: str
    from_name: str
    subject: str
    received_at: str | None
    is_read: bool
    has_attachments: bool


class MessageDetail(BaseModel):
    id: str
    from_address: str
    from_name: str
    subject: str
    body_text: str
    body_html: str
    received_at: str | None
    is_read: bool
    has_attachments: bool
    attachments: list[dict[str, Any]]


class ActionResponse(BaseModel):
    success: bool
    message: str


# ════════════════════════════════════════════
# 异常处理
# ════════════════════════════════════════════


def _handle_adapter_error(err: EmailAdapterError) -> HTTPException:
    """将适配器异常映射为 HTTP 异常"""
    if isinstance(err, AuthenticationError):
        return HTTPException(status_code=401, detail=str(err))
    if isinstance(err, RateLimitError):
        return HTTPException(status_code=429, detail=str(err))
    if isinstance(err, NetworkError):
        return HTTPException(status_code=502, detail=str(err))
    return HTTPException(status_code=500, detail=str(err))


# ════════════════════════════════════════════
# 接口
# ════════════════════════════════════════════


@router.post("/create", response_model=CreateEmailResponse)
async def create_email(body: CreateEmailRequest | None = None) -> CreateEmailResponse:
    """创建临时邮箱地址"""
    global _current_email
    adapter = _get_adapter()
    try:
        username = body.username if body else None
        domain = body.domain if body else None
        email_addr = await adapter.create_email(username=username, domain=domain)
        _current_email = email_addr.address
        logger.info("创建邮箱成功: {}", email_addr.address)
        return CreateEmailResponse(
            address=email_addr.address,
            username=email_addr.username,
            domain=email_addr.domain,
            provider=email_addr.provider,
        )
    except EmailAdapterError as err:
        raise _handle_adapter_error(err)


@router.get("/domains")
async def get_domains() -> dict[str, list[str]]:
    """获取可用域名列表"""
    adapter = _get_adapter()
    try:
        domains = await adapter.get_domains()
        return {"domains": domains}
    except EmailAdapterError as err:
        raise _handle_adapter_error(err)


@router.get("/messages", response_model=list[MessageSummary])
async def get_messages(email: str | None = None) -> list[MessageSummary]:
    """获取收件箱邮件列表"""
    adapter = _get_adapter()
    target = email or _current_email
    if not target:
        raise HTTPException(status_code=400, detail="请先创建邮箱或提供 email 参数")
    try:
        messages = await adapter.get_messages(target)
        return [
            MessageSummary(
                id=m.id,
                from_address=m.from_address,
                from_name=m.from_name,
                subject=m.subject,
                received_at=m.received_at.isoformat() if m.received_at else None,
                is_read=m.is_read,
                has_attachments=m.has_attachments,
            )
            for m in messages
        ]
    except EmailAdapterError as err:
        raise _handle_adapter_error(err)


@router.get("/messages/{message_id}", response_model=MessageDetail)
async def get_message_detail(message_id: str) -> MessageDetail:
    """获取单封邮件详情"""
    adapter = _get_adapter()
    try:
        m = await adapter.get_message(message_id)
        return MessageDetail(
            id=m.id,
            from_address=m.from_address,
            from_name=m.from_name,
            subject=m.subject,
            body_text=m.body_text,
            body_html=m.body_html,
            received_at=m.received_at.isoformat() if m.received_at else None,
            is_read=m.is_read,
            has_attachments=m.has_attachments,
            attachments=[
                {
                    "filename": a.filename,
                    "content_type": a.content_type,
                    "size": a.size,
                    "download_url": a.download_url,
                }
                for a in m.attachments
            ],
        )
    except EmailAdapterError as err:
        raise _handle_adapter_error(err)


@router.delete("/messages/{message_id}", response_model=ActionResponse)
async def delete_message(message_id: str) -> ActionResponse:
    """删除邮件"""
    adapter = _get_adapter()
    try:
        await adapter.delete_message(message_id)
        return ActionResponse(success=True, message=f"邮件 {message_id} 已删除")
    except EmailAdapterError as err:
        raise _handle_adapter_error(err)


@router.patch("/messages/{message_id}/read", response_model=ActionResponse)
async def mark_as_read(message_id: str) -> ActionResponse:
    """标记邮件为已读"""
    adapter = _get_adapter()
    try:
        await adapter.mark_as_read(message_id)
        return ActionResponse(success=True, message=f"邮件 {message_id} 已标记已读")
    except EmailAdapterError as err:
        raise _handle_adapter_error(err)


@router.get("/health")
async def email_health() -> dict[str, Any]:
    """邮件服务健康检查"""
    adapter = _get_adapter()
    try:
        healthy = await adapter.check_health()
        return {
            "status": "ok" if healthy else "degraded",
            "provider": adapter.provider_name,
        }
    except Exception as err:
        logger.warning("邮件健康检查失败: {}", err)
        return {"status": "error", "provider": "tempmailio", "detail": str(err)}
