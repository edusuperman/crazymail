"""内容工厂 API 路由

提供内容工厂流水线的 REST API 和 SSE 端点。
"""

from __future__ import annotations

import asyncio
from typing import AsyncIterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger

from ..schemas.content_factory import (
    ContentFactoryRequest,
    ContentFactoryResponse,
    ContentFactoryProgress,
)
from ..services.content_factory import content_factory_service

router = APIRouter()


async def run_pipeline_background(request: ContentFactoryRequest, task_id: str):
    """后台运行流水线"""
    async for progress in content_factory_service.run_pipeline(request, task_id):
        # 进度已经保存在 service 中
        pass


@router.post("/run", response_model=dict)
async def run_pipeline(request: ContentFactoryRequest):
    """启动内容工厂流水线

    返回 task_id，可通过 SSE 端点获取实时进度。
    """
    import uuid
    task_id = str(uuid.uuid4())[:8]

    # 先初始化任务（同步操作）
    from ..schemas.content_factory import StageInfo, StageStatus
    stages = [
        StageInfo(id=s["id"], name=s["name"], role=s["role"], icon=s["icon"])
        for s in [
            {"id": 1, "name": "研究", "role": "张择端", "icon": "🎨"},
            {"id": 2, "name": "大纲", "role": "李纲", "icon": "🗺️"},
            {"id": 3, "name": "初稿", "role": "李清照", "icon": "✍️"},
            {"id": 4, "name": "润色", "role": "李清照", "icon": "✍️"},
            {"id": 5, "name": "质检", "role": "岳飞", "icon": "🔍"},
            {"id": 6, "name": "部署", "role": "韩世忠", "icon": "🐎"},
            {"id": 7, "name": "监控", "role": "宗泽", "icon": "🏰"},
        ]
    ]
    content_factory_service.tasks[task_id] = ContentFactoryResponse(
        task_id=task_id,
        keyword=request.keyword,
        status=StageStatus.RUNNING,
        stages=stages,
    )
    logger.info(f"任务已创建: task_id={task_id}, 任务数: {len(content_factory_service.tasks)}")

    # 在后台启动流水线
    asyncio.create_task(run_pipeline_background(request, task_id))

    return {
        "task_id": task_id,
        "keyword": request.keyword,
        "message": "流水线已启动，请通过 SSE 端点获取进度",
        "sse_url": f"/api/v1/content-factory/progress/{task_id}",
    }


@router.get("/progress/{task_id}")
async def get_progress(task_id: str):
    """SSE 端点：获取流水线实时进度

    返回 Server-Sent Events 流。
    """
    # 检查任务是否存在
    task = content_factory_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")

    async def event_stream() -> AsyncIterator[str]:
        """SSE 事件流"""
        import json
        from datetime import datetime

        # 持续监听任务状态
        last_stage_id = 0
        while True:
            task = content_factory_service.get_task(task_id)
            if not task:
                break

            # 发送每个阶段的进度
            for stage in task.stages:
                if stage.id > last_stage_id and stage.status.value != "waiting":
                    progress = ContentFactoryProgress(
                        task_id=task_id,
                        stage_id=stage.id,
                        stage_name=stage.name,
                        status=stage.status,
                        progress=stage.progress,
                        message=f"{stage.name}: {stage.status.value}",
                        output=stage.output,
                        timestamp=datetime.now(),
                    )
                    yield f"data: {progress.model_dump_json()}\n\n"
                    last_stage_id = stage.id

            # 检查是否完成
            if task.status.value in ("done", "error"):
                # 发送完成消息
                progress = ContentFactoryProgress(
                    task_id=task_id,
                    stage_id=0,
                    stage_name="整体",
                    status=task.status,
                    progress=100,
                    message="流水线完成" if task.status.value == "done" else f"流水线失败: {task.error}",
                    timestamp=datetime.now(),
                )
                yield f"data: {progress.model_dump_json()}\n\n"
                break

            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/tasks", response_model=list[ContentFactoryResponse])
async def list_tasks():
    """列出所有任务"""
    return content_factory_service.list_tasks()


@router.get("/tasks/{task_id}", response_model=ContentFactoryResponse)
async def get_task(task_id: str):
    """获取任务详情"""
    task = content_factory_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    return task


@router.post("/run-sync", response_model=ContentFactoryResponse)
async def run_pipeline_sync(request: ContentFactoryRequest):
    """同步运行内容工厂流水线（等待完成）

    注意：此端点会阻塞直到流水线完成，可能需要几分钟。
    """
    from ..services.content_factory import ContentFactoryService

    # 创建新的服务实例（避免并发问题）
    service = ContentFactoryService()

    # 运行流水线并收集最终结果
    async for progress in service.run_pipeline(request):
        pass  # 忽略进度，只关心最终结果

    # 获取任务结果
    tasks = service.list_tasks()
    if tasks:
        return tasks[0]

    raise HTTPException(status_code=500, detail="流水线执行失败")
