"""
站点管理模块路由
管理20个驿站（Niche站点）的配置和状态
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_sites():
    """获取所有站点列表"""
    return {"sites": [], "total": 0}


@router.post("/")
async def create_site(name: str, domain: str, niche: str):
    """创建新站点"""
    return {"site_id": "pending", "name": name, "domain": domain}


@router.get("/{site_id}")
async def get_site(site_id: str):
    """获取站点详情"""
    return {"site_id": site_id, "status": "pending"}


@router.get("/{site_id}/metrics")
async def get_site_metrics(site_id: str):
    """获取站点指标"""
    return {"site_id": site_id, "metrics": {}}
