"""内容工厂数据模型

定义内容工厂流水线的输入、输出和状态模型。
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class StageStatus(str, Enum):
    """阶段状态"""
    WAITING = "waiting"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


class StageInfo(BaseModel):
    """阶段信息"""
    id: int = Field(..., description="阶段编号 1-7")
    name: str = Field(..., description="阶段名称")
    role: str = Field(..., description="执行角色")
    icon: str = Field(..., description="图标")
    status: StageStatus = Field(default=StageStatus.WAITING, description="状态")
    progress: float = Field(default=0, ge=0, le=100, description="进度 0-100")
    output: Optional[str] = Field(default=None, description="输出摘要")
    error: Optional[str] = Field(default=None, description="错误信息")


class ContentFactoryRequest(BaseModel):
    """内容工厂请求"""
    keyword: str = Field(..., min_length=2, max_length=100, description="目标关键词")
    language: str = Field(default="en", description="语言代码")
    word_count_min: int = Field(default=1500, ge=500, description="最小字数")
    word_count_max: int = Field(default=3000, le=5000, description="最大字数")
    auto_deploy: bool = Field(default=False, description="质检通过后自动部署")


class ContentFactoryResponse(BaseModel):
    """内容工厂响应"""
    task_id: str = Field(..., description="任务ID")
    keyword: str = Field(..., description="目标关键词")
    status: StageStatus = Field(..., description="整体状态")
    stages: list[StageInfo] = Field(default_factory=list, description="各阶段状态")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    output_file: Optional[str] = Field(default=None, description="输出文件路径")
    error: Optional[str] = Field(default=None, description="错误信息")


class ContentFactoryProgress(BaseModel):
    """SSE 进度推送"""
    task_id: str
    stage_id: int
    stage_name: str
    status: StageStatus
    progress: float
    message: str
    output: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# 各阶段的内部数据模型

class ResearchResult(BaseModel):
    """Stage 1: 研究结果"""
    keyword: str
    search_intent: str = Field(description="搜索意图: informational/transactional/navigational")
    competition: str = Field(description="竞争度: low/medium/high")
    related_keywords: list[str] = Field(default_factory=list, description="相关关键词")
    suggested_angles: list[str] = Field(default_factory=list, description="建议角度")
    top_competitors: list[str] = Field(default_factory=list, description="竞品文章标题")


class OutlineSection(BaseModel):
    """大纲章节"""
    level: int = Field(default=2, description="标题级别 2 or 3")
    title: str
    key_points: list[str] = Field(default_factory=list, description="要点")
    word_count_target: int = Field(default=250, description="目标字数")


class OutlineResult(BaseModel):
    """Stage 2: 大纲结果"""
    title: str = Field(description="文章标题")
    meta_description: str = Field(description="Meta描述")
    sections: list[OutlineSection] = Field(default_factory=list, description="章节列表")
    faq_count: int = Field(default=3, description="FAQ数量")
    total_word_count: int = Field(default=2000, description="总目标字数")


class DraftResult(BaseModel):
    """Stage 3: 初稿结果"""
    title: str
    content: str = Field(description="Markdown 格式文章内容")
    word_count: int
    sections_written: int


class PolishResult(BaseModel):
    """Stage 4: 润色结果"""
    title: str
    content: str = Field(description="润色后的 Markdown 内容")
    word_count: int
    ai_score_estimate: float = Field(description="预估 AI 检测分")
    human_score_estimate: float = Field(description="预估人味评分")


class QCResult(BaseModel):
    """Stage 5: 质检结果"""
    passed: bool
    score: float = Field(description="综合评分 0-100")
    checks: dict[str, bool] = Field(default_factory=dict, description="各项检查结果")
    failures: list[str] = Field(default_factory=list, description="失败项")
    warnings: list[str] = Field(default_factory=list, description="警告项")


class DeployResult(BaseModel):
    """Stage 6: 部署结果"""
    success: bool
    file_path: str = Field(description="生成的文件路径")
    route: str = Field(description="路由路径")
    url: Optional[str] = Field(default=None, description="访问URL")


class MonitorResult(BaseModel):
    """Stage 7: 监控结果"""
    indexed: bool = Field(default=False, description="是否已索引")
    sitemap_submitted: bool = Field(default=False, description="是否已提交站点地图")
    gsc_url: Optional[str] = Field(default=None, description="Google Search Console URL")
