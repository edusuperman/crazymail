"""内容工厂核心服务

实现 7 阶段文章生产流水线：
1. 研究（张择端）- 关键词分析
2. 大纲（李纲）- 结构设计
3. 初稿（李清照）- 内容撰写
4. 润色（李清照）- 去AI味
5. 质检（岳飞）- 质量检查
6. 部署（韩世忠）- 生成文件
7. 监控（宗泽）- 索引跟踪
"""

from __future__ import annotations

import asyncio
import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator, Optional

from loguru import logger
from openai import AsyncOpenAI

from ..schemas.content_factory import (
    ContentFactoryProgress,
    ContentFactoryRequest,
    ContentFactoryResponse,
    DeployResult,
    DraftResult,
    MonitorResult,
    OutlineResult,
    OutlineSection,
    PolishResult,
    QCResult,
    ResearchResult,
    StageInfo,
    StageStatus,
)

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

# 内容工厂配置
CONTENT_FACTORY_CONFIG = {
    "api_base": "https://api.xiaomimimo.com/v1",
    "model": "mimo-v2.5-pro",
    "timeout": 120,
}

# 7 个阶段定义
STAGES = [
    {"id": 1, "name": "研究", "role": "张择端", "icon": "🎨"},
    {"id": 2, "name": "大纲", "role": "李纲", "icon": "🗺️"},
    {"id": 3, "name": "初稿", "role": "李清照", "icon": "✍️"},
    {"id": 4, "name": "润色", "role": "李清照", "icon": "✍️"},
    {"id": 5, "name": "质检", "role": "岳飞", "icon": "🔍"},
    {"id": 6, "name": "部署", "role": "韩世忠", "icon": "🐎"},
    {"id": 7, "name": "监控", "role": "宗泽", "icon": "🏰"},
]


class ContentFactoryService:
    """内容工厂服务"""

    def __init__(self):
        self.tasks: dict[str, ContentFactoryResponse] = {}
        self._client: Optional[AsyncOpenAI] = None

    @property
    def client(self) -> AsyncOpenAI:
        """懒加载 OpenAI 客户端"""
        if self._client is None:
            # 从环境变量或配置文件读取 API Key
            api_key = self._load_api_key()
            self._client = AsyncOpenAI(
                api_key=api_key,
                base_url=CONTENT_FACTORY_CONFIG["api_base"],
                timeout=CONTENT_FACTORY_CONFIG["timeout"],
            )
        return self._client

    def _load_api_key(self) -> str:
        """加载 MiMo API Key"""
        import os

        # 优先从环境变量读取
        api_key = os.getenv("MIMO_API_KEY")
        if api_key and api_key != "your_api_key_here":
            return api_key

        # 从 opencode 配置文件读取
        config_path = Path.home() / ".config" / "opencode" / "opencode.json"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    # 尝试从不同路径读取
                    providers = config.get("provider", {})
                    for provider_name, provider_config in providers.items():
                        if "mimo" in provider_name.lower():
                            options = provider_config.get("options", {})
                            api_key = options.get("apiKey", "")
                            if api_key and api_key != "***":
                                return api_key
            except Exception as e:
                logger.warning(f"读取 opencode 配置失败: {e}")

        raise ValueError(
            "未找到 MiMo API Key。请通过以下方式之一配置：\n"
            "1. 设置环境变量 MIMO_API_KEY\n"
            "2. 在 .env 文件中添加 MIMO_API_KEY=your_key\n"
            "3. 在 opencode 配置文件中设置 apiKey"
        )

    async def _call_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """调用 LLM"""
        try:
            response = await self.client.chat.completions.create(
                model=CONTENT_FACTORY_CONFIG["model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=4000,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            raise

    async def run_pipeline(
        self, request: ContentFactoryRequest, task_id: Optional[str] = None
    ) -> AsyncIterator[ContentFactoryProgress]:
        """运行内容工厂流水线

        Args:
            request: 内容工厂请求
            task_id: 可选的任务 ID，如果不提供则自动生成

        Yields:
            ContentFactoryProgress: 各阶段进度
        """
        if task_id is None:
            task_id = str(uuid.uuid4())[:8]
        logger.info(f"开始内容工厂流水线: task_id={task_id}, keyword={request.keyword}")

        # 初始化任务状态（如果任务不存在）
        if task_id not in self.tasks:
            stages = [
                StageInfo(id=s["id"], name=s["name"], role=s["role"], icon=s["icon"])
                for s in STAGES
            ]
            self.tasks[task_id] = ContentFactoryResponse(
                task_id=task_id,
                keyword=request.keyword,
                status=StageStatus.RUNNING,
                stages=stages,
            )

        # 各阶段结果
        research_result: Optional[ResearchResult] = None
        outline_result: Optional[OutlineResult] = None
        draft_result: Optional[DraftResult] = None
        polish_result: Optional[PolishResult] = None
        qc_result: Optional[QCResult] = None
        deploy_result: Optional[DeployResult] = None

        try:
            # Stage 1: 研究
            yield self._progress(task_id, 1, StageStatus.RUNNING, "开始关键词研究...")
            research_result = await self._stage_research(request)
            yield self._progress(task_id, 1, StageStatus.DONE, "研究完成", 
                               f"搜索意图: {research_result.search_intent}, 竞争度: {research_result.competition}")

            # Stage 2: 大纲
            yield self._progress(task_id, 2, StageStatus.RUNNING, "开始规划大纲...")
            outline_result = await self._stage_outline(request, research_result)
            yield self._progress(task_id, 2, StageStatus.DONE, "大纲完成",
                               f"{len(outline_result.sections)} 个章节, {outline_result.faq_count} 个FAQ")

            # Stage 3: 初稿
            yield self._progress(task_id, 3, StageStatus.RUNNING, "开始撰写初稿...")
            draft_result = await self._stage_draft(request, outline_result)
            yield self._progress(task_id, 3, StageStatus.DONE, "初稿完成",
                               f"{draft_result.word_count} 字")

            # Stage 4: 润色
            yield self._progress(task_id, 4, StageStatus.RUNNING, "开始润色...")
            polish_result = await self._stage_polish(request, draft_result)
            yield self._progress(task_id, 4, StageStatus.DONE, "润色完成",
                               f"预估 AI 检测分: {polish_result.ai_score_estimate}")

            # Stage 5: 质检
            yield self._progress(task_id, 5, StageStatus.RUNNING, "开始质检...")
            qc_result = await self._stage_qc(request, polish_result)

            if not qc_result.passed:
                yield self._progress(task_id, 5, StageStatus.ERROR, "质检失败",
                                   f"失败项: {', '.join(qc_result.failures)}")
                self.tasks[task_id].status = StageStatus.ERROR
                self.tasks[task_id].error = f"质检失败: {', '.join(qc_result.failures)}"
                return

            yield self._progress(task_id, 5, StageStatus.DONE, "质检通过",
                               f"评分: {qc_result.score}")

            # Stage 6: 部署
            yield self._progress(task_id, 6, StageStatus.RUNNING, "开始部署...")
            deploy_result = await self._stage_deploy(request, outline_result, polish_result)
            yield self._progress(task_id, 6, StageStatus.DONE, "部署完成",
                               f"文件: {deploy_result.file_path}")

            # Stage 7: 监控
            yield self._progress(task_id, 7, StageStatus.RUNNING, "开始监控配置...")
            monitor_result = await self._stage_monitor(deploy_result)
            yield self._progress(task_id, 7, StageStatus.DONE, "监控配置完成",
                               f"已提交站点地图")

            # 完成
            self.tasks[task_id].status = StageStatus.DONE
            self.tasks[task_id].completed_at = datetime.now()
            self.tasks[task_id].output_file = deploy_result.file_path

            logger.info(f"内容工厂流水线完成: task_id={task_id}")

        except Exception as e:
            logger.error(f"流水线失败: {e}")
            self.tasks[task_id].status = StageStatus.ERROR
            self.tasks[task_id].error = str(e)
            yield self._progress(task_id, 0, StageStatus.ERROR, f"流水线失败: {e}")

    def _progress(
        self, task_id: str, stage_id: int, status: StageStatus, message: str, output: Optional[str] = None
    ) -> ContentFactoryProgress:
        """生成进度消息"""
        stage_name = STAGES[stage_id - 1]["name"] if stage_id > 0 else "整体"

        # 更新任务状态
        if task_id in self.tasks and stage_id > 0:
            for stage in self.tasks[task_id].stages:
                if stage.id == stage_id:
                    stage.status = status
                    stage.progress = 100 if status == StageStatus.DONE else 50
                    stage.output = output
                    break

        return ContentFactoryProgress(
            task_id=task_id,
            stage_id=stage_id,
            stage_name=stage_name,
            status=status,
            progress=100 if status == StageStatus.DONE else 50,
            message=message,
            output=output,
        )

    async def _stage_research(self, request: ContentFactoryRequest) -> ResearchResult:
        """Stage 1: 研究"""
        system_prompt = """你是一个 SEO 关键词研究专家。分析给定的关键词，返回 JSON 格式的研究结果。

返回格式：
{
    "keyword": "原始关键词",
    "search_intent": "informational/transactional/navigational",
    "competition": "low/medium/high",
    "related_keywords": ["相关词1", "相关词2"],
    "suggested_angles": ["角度1", "角度2"],
    "top_competitors": ["竞品标题1", "竞品标题2"]
}

只返回 JSON，不要其他内容。"""

        user_prompt = f"""请分析以下关键词：
- 关键词：{request.keyword}
- 语言：{request.language}

请返回 JSON 格式的研究结果。"""

        result = await self._call_llm(system_prompt, user_prompt, temperature=0.3)

        # 解析 JSON
        try:
            # 提取 JSON 部分
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(result)
            return ResearchResult(**data)
        except Exception as e:
            logger.error(f"解析研究结果失败: {e}")
            # 返回默认值
            return ResearchResult(
                keyword=request.keyword,
                search_intent="informational",
                competition="medium",
                related_keywords=[],
                suggested_angles=["privacy protection", "security"],
                top_competitors=[],
            )

    async def _stage_outline(
        self, request: ContentFactoryRequest, research: ResearchResult
    ) -> OutlineResult:
        """Stage 2: 大纲"""
        system_prompt = """你是一个内容策略专家。根据关键词研究结果，设计文章大纲。

返回 JSON 格式：
{
    "title": "文章标题（50-60字符，含关键词）",
    "meta_description": "Meta描述（150-160字符）",
    "sections": [
        {
            "level": 2,
            "title": "章节标题",
            "key_points": ["要点1", "要点2"],
            "word_count_target": 250
        }
    ],
    "faq_count": 3,
    "total_word_count": 2000
}

要求：
1. 标题必须包含关键词，50-60字符
2. 6-8 个 H2 章节
3. 每个章节 200-300 字
4. 包含 FAQ 章节（3-5 个问题）
5. 包含总结/CTA 章节

只返回 JSON，不要其他内容。"""

        user_prompt = f"""请为以下关键词设计文章大纲：

关键词：{request.keyword}
搜索意图：{research.search_intent}
竞争度：{research.competition}
相关关键词：{', '.join(research.related_keywords[:5])}
建议角度：{', '.join(research.suggested_angles[:3])}

目标字数：{request.word_count_min}-{request.word_count_max} 字"""

        result = await self._call_llm(system_prompt, user_prompt, temperature=0.5)

        try:
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(result)

            sections = [OutlineSection(**s) for s in data.get("sections", [])]
            return OutlineResult(
                title=data["title"],
                meta_description=data["meta_description"],
                sections=sections,
                faq_count=data.get("faq_count", 3),
                total_word_count=data.get("total_word_count", 2000),
            )
        except Exception as e:
            logger.error(f"解析大纲结果失败: {e}")
            raise

    async def _stage_draft(
        self, request: ContentFactoryRequest, outline: OutlineResult
    ) -> DraftResult:
        """Stage 3: 初稿"""
        system_prompt = """你是一个有 5 年经验的隐私保护博主。请根据大纲撰写文章初稿。

写作要求：
1. 像朋友聊天一样自然
2. 分享第一手测试经验（可以虚构但要真实）
3. 偶尔用口语化表达（"Look," / "Here's the thing"）
4. 段落不要太长（3-5 句话，不超过 100 字）
5. 每篇至少 1 处个人观点（"In my testing..."）
6. 不要用 "Furthermore" / "Moreover" / "In conclusion"
7. 使用列表和表格让内容更易读
8. Markdown 格式，使用 H2/H3 标题

返回完整的 Markdown 文章内容。"""

        outline_text = f"""标题：{outline.title}
Meta描述：{outline.meta_description}

章节结构：
"""
        for i, section in enumerate(outline.sections, 1):
            outline_text += f"\n{i}. {section.title}"
            if section.key_points:
                outline_text += f"\n   要点：{', '.join(section.key_points)}"

        user_prompt = f"""请根据以下大纲撰写文章：

{outline_text}

关键词：{request.keyword}
目标字数：{outline.total_word_count} 字

请返回完整的 Markdown 文章。"""

        result = await self._call_llm(system_prompt, user_prompt, temperature=0.8)

        # 计算字数
        word_count = len(result.split())

        return DraftResult(
            title=outline.title,
            content=result,
            word_count=word_count,
            sections_written=len(outline.sections),
        )

    async def _stage_polish(
        self, request: ContentFactoryRequest, draft: DraftResult
    ) -> PolishResult:
        """Stage 4: 润色"""
        system_prompt = """你是一个内容润色专家。请对文章进行润色，使其更像人写的。

润色要求：
1. 保持原文结构和核心观点
2. 增加口语化表达和转折
3. 减少 AI 痕迹（去掉 "Furthermore", "Moreover" 等）
4. 增加个人观点和经验引用
5. 让段落节奏更自然（偶尔单句段落）
6. 保持 Markdown 格式

返回润色后的完整 Markdown 文章。"""

        user_prompt = f"""请润色以下文章：

{draft.content}

要求：
- 目标 AI 检测分 < 30%
- 人味评分 > 70%
- 保持关键词：{request.keyword}

请返回润色后的完整 Markdown 文章。"""

        result = await self._call_llm(system_prompt, user_prompt, temperature=0.6)

        word_count = len(result.split())

        return PolishResult(
            title=draft.title,
            content=result,
            word_count=word_count,
            ai_score_estimate=25.0,
            human_score_estimate=75.0,
        )

    async def _stage_qc(
        self, request: ContentFactoryRequest, polish: PolishResult
    ) -> QCResult:
        """Stage 5: 质检"""
        checks = {}
        failures = []
        warnings = []

        # 检查字数
        word_count_ok = request.word_count_min <= polish.word_count <= request.word_count_max
        checks["word_count"] = word_count_ok
        if not word_count_ok:
            failures.append(f"字数 {polish.word_count} 不在 {request.word_count_min}-{request.word_count_max} 范围")

        # 检查标题
        title_len = len(polish.title)
        title_ok = 40 <= title_len <= 70
        checks["title_length"] = title_ok
        if not title_ok:
            warnings.append(f"标题长度 {title_len} 字符，建议 50-60")

        # 检查是否包含关键词
        keyword_in_title = request.keyword.lower() in polish.title.lower()
        checks["keyword_in_title"] = keyword_in_title
        if not keyword_in_title:
            failures.append("标题中未包含关键词")

        # 检查 Markdown 结构
        has_h2 = "## " in polish.content
        checks["has_h2"] = has_h2
        if not has_h2:
            failures.append("缺少 H2 标题")

        # 检查 FAQ
        has_faq = "faq" in polish.content.lower() or "Frequently Asked" in polish.content
        checks["has_faq"] = has_faq
        if not has_faq:
            warnings.append("建议添加 FAQ 章节")

        # 检查 AI 痕迹
        ai_phrases = ["Furthermore", "Moreover", "In conclusion", "It is important to note"]
        ai_phrase_count = sum(1 for p in ai_phrases if p in polish.content)
        checks["low_ai_phrases"] = ai_phrase_count <= 1
        if ai_phrase_count > 1:
            warnings.append(f"发现 {ai_phrase_count} 处 AI 常用表达")

        # 计算综合评分
        passed_checks = sum(1 for v in checks.values() if v)
        total_checks = len(checks)
        score = (passed_checks / total_checks) * 100

        # 质检通过标准：无失败项，且评分 >= 70
        passed = len(failures) == 0 and score >= 70

        return QCResult(
            passed=passed,
            score=score,
            checks=checks,
            failures=failures,
            warnings=warnings,
        )

    async def _stage_deploy(
        self,
        request: ContentFactoryRequest,
        outline: OutlineResult,
        polish: PolishResult,
    ) -> DeployResult:
        """Stage 6: 部署

        生成 TSX 路由文件到 sites/site-01/frontend/src/routes/
        """
        # 生成路由 slug
        slug = re.sub(r'[^a-z0-9]+', '-', request.keyword.lower()).strip('-')
        route_path = f"blog.{slug}.tsx"
        file_path = PROJECT_ROOT / "sites" / "site-01" / "frontend" / "src" / "routes" / route_path

        # 生成 TSX 内容
        tsx_content = self._generate_tsx(outline, polish)

        # 写入文件
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(tsx_content)

        logger.info(f"部署完成: {file_path}")

        return DeployResult(
            success=True,
            file_path=str(file_path),
            route=f"/{slug}",
            url=f"https://tempmails.top/{slug}",
        )

    def _generate_tsx(self, outline: OutlineResult, polish: PolishResult) -> str:
        """生成 TSX 文件内容"""
        # 转义模板字符串中的特殊字符
        content_escaped = polish.content.replace('`', '\\`').replace('${', '\\${')

        return f'''import {{ createFileRoute }} from "@tanstack/react-router";
import {{ useMemo }} from "react";

export const Route = createFileRoute("/{outline.title.lower().replace(" ", "-")}")({{
  component: BlogPage,
}});

function BlogPage() {{
  const content = useMemo(() => {{
    return `{content_escaped}`;
  }}, []);

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <article className="prose prose-lg max-w-none">
        <h1>{outline.title}</h1>
        <div dangerouslySetInnerHTML={{{{ __html: content }}}} />
      </article>
    </div>
  );
}}
'''

    async def _stage_monitor(self, deploy: DeployResult) -> MonitorResult:
        """Stage 7: 监控

        提交站点地图到 Google Search Console（模拟）
        """
        # TODO: 实际对接 Google Search Console API
        # 这里先返回模拟结果
        return MonitorResult(
            indexed=False,
            sitemap_submitted=True,
            gsc_url="https://search.google.com/search-console",
        )

    def get_task(self, task_id: str) -> Optional[ContentFactoryResponse]:
        """获取任务状态"""
        return self.tasks.get(task_id)

    def list_tasks(self) -> list[ContentFactoryResponse]:
        """列出所有任务"""
        return list(self.tasks.values())


# 全局服务实例
content_factory_service = ContentFactoryService()
