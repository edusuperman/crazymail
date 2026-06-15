"""CrazyMail FastAPI 入口

唯一的 FastAPI 应用实例，所有路由在此注册。
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .config import settings
from .routers import email


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """应用生命周期：启动/关闭时执行"""
    logger.info("CrazyMail 启动: {} v{}", settings.APP_NAME, settings.APP_VERSION)
    yield
    logger.info("CrazyMail 关闭")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="临时邮箱 API 服务",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(email.router, prefix="/api/v1/email", tags=["email"])


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    """全局健康检查"""
    return {"status": "ok", "version": settings.APP_VERSION}
