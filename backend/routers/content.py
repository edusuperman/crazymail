"""
内容工厂模块路由
7阶段流水线：关键词研究 → SERP分析 → 内容写作 → 质检 → SEO优化 → 链接建设 → 人工审核
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/tasks")
async def list_tasks():
    """获取内容任务列表"""
    return {"tasks": [], "total": 0}


@router.post("/tasks")
async def create_task(keyword: str, site_id: str):
    """创建内容任务"""
    return {"task_id": "pending", "keyword": keyword, "site_id": site_id}


@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """获取任务详情"""
    return {"task_id": task_id, "stage": 0, "status": "pending"}


@router.post("/tasks/{task_id}/approve")
async def approve_task(task_id: str):
    """宋徽宗审批通过"""
    return {"task_id": task_id, "action": "approved"}


@router.post("/tasks/{task_id}/reject")
async def reject_task(task_id: str):
    """宋徽宗打回重写"""
    return {"task_id": task_id, "action": "rejected"}


@router.get("/review-queue")
async def review_queue():
    """待审核队列"""
    return {"queue": [], "total": 0}
