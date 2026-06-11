"""
CrazyMail（疯邮）— FastAPI 应用入口
以北宋朝廷为视觉隐喻的 AI 驱动 SEO 内容矩阵自动化系统
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from loguru import logger

# 加载环境变量
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("🏯 汴京总督府启动中...")
    # TODO: 初始化数据库连接
    # TODO: 初始化 Redis 连接
    # TODO: 初始化 Agent 系统
    logger.info("🏯 汴京总督府已就绪")
    yield
    logger.info("🏯 汴京总督府关闭")


app = FastAPI(
    title="CrazyMail API",
    description="以北宋朝廷为视觉隐喻的 AI 驱动 SEO 内容矩阵自动化系统",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js 前端
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "CrazyMail API",
        "version": "0.1.0",
        "status": "running",
        "message": "汴京总督府已就绪",
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "database": "pending",  # TODO: 检查数据库连接
        "redis": "pending",  # TODO: 检查 Redis 连接
    }


# 注册路由（插座原则：每个模块一个 Router）
# TODO: 按需启用
# from routers import content, sites, personas, security, gold_medal, dashboard
# app.include_router(content.router, prefix="/api/v1/content", tags=["内容工厂"])
# app.include_router(sites.router, prefix="/api/v1/sites", tags=["站点管理"])
# app.include_router(personas.router, prefix="/api/v1/personas", tags=["人格系统"])
# app.include_router(security.router, prefix="/api/v1/security", tags=["皇城司"])
# app.include_router(gold_medal.router, prefix="/api/v1/gold-medal", tags=["金牌系统"])
# app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["仪表盘"])
