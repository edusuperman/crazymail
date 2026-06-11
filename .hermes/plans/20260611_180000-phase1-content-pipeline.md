# Phase 1: 单站点内容流水线 实施计划

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** 跑通一个站点的完整 7 阶段 AI 内容流水线，产出一篇通过质检的文章

**Architecture:** 
- CrewAI 定义 7 个官员角色（谁做什么）
- LangGraph 控制流水线状态流转（怎么流）
- FastAPI 提供 API 接口
- Supabase 存储数据

**Tech Stack:** Python 3.12, FastAPI, CrewAI 0.80+, LangGraph 0.2+, Supabase

**完成标准:**
- 对任意英文关键词，24小时内自动产出一篇文章
- AI检测分 < 30，SEO分 > 75
- 宋徽宗审核界面可以通过/打回文章

---

## Week 1: 后端 Agent 骨架（Task 1-12）

### Task 1: 创建数据模型 - ContentTask

**Objective:** 定义内容任务的数据模型

**Files:**
- Create: `backend/models/content.py`

**Step 1: 创建数据模型**

```python
"""
内容工厂数据模型
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    RESEARCHING = "researching"      # 李纲：关键词研究
    ANALYZING = "analyzing"          # 张择端：SERP分析+大纲
    WRITING = "writing"              # 周邦彦/李清照：内容写作
    QA_CHECKING = "qa_checking"      # 岳飞：9重质检
    OPTIMIZING = "optimizing"        # 种师道：SEO优化
    LINK_BUILDING = "link_building"  # 韩世忠：链接建设
    REVIEWING = "reviewing"          # 宋徽宗：人工审核
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"


class ContentTask(BaseModel):
    """内容任务"""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    keyword: str
    site_id: str
    niche: str = ""
    status: TaskStatus = TaskStatus.PENDING
    
    # 各阶段产出
    research_data: Optional[dict] = None      # 李纲产出
    serp_analysis: Optional[dict] = None      # 张择端产出
    outline: Optional[dict] = None            # 张择端产出
    content: Optional[str] = None             # 周邦彦/李清照产出
    qa_report: Optional[dict] = None          # 岳飞产出
    seo_optimization: Optional[dict] = None   # 种师道产出
    link_strategy: Optional[dict] = None      # 韩世忠产出
    
    # 质检分数
    ai_detection_score: Optional[float] = None
    seo_score: Optional[float] = None
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class CreateTaskRequest(BaseModel):
    """创建任务请求"""
    keyword: str
    site_id: str
    niche: str = ""


class TaskResponse(BaseModel):
    """任务响应"""
    task_id: str
    status: TaskStatus
    keyword: str
    site_id: str
    ai_detection_score: Optional[float] = None
    seo_score: Optional[float] = None
    created_at: datetime
```

**Step 2: 验证模型**

Run: `cd backend && uv run python -c "from models.content import ContentTask; print('✅ 数据模型创建成功')"`

**Step 3: 提交**

```bash
git add backend/models/content.py
git commit -m "feat(content): 创建内容任务数据模型"
```

---

### Task 2: 创建 CrewAI Agent 定义 - 李纲（关键词研究）

**Objective:** 定义李纲角色的 CrewAI Agent

**Files:**
- Create: `backend/agents/crews/keyword_researcher.py`

**Step 1: 创建 Agent 定义**

```python
"""
李纲 - 关键词研究 Agent
职责：分析关键词潜力、搜索量、竞争度
"""
from crewai import Agent, Task, Crew


def create_keyword_researcher(llm) -> Agent:
    """创建关键词研究 Agent"""
    return Agent(
        role="关键词研究专家",
        goal="分析关键词的搜索潜力、竞争度和商业价值",
        backstory="""你是李纲，北宋名臣，擅长战略分析。
在 CrazyMail 系统中，你负责关键词研究工作。
你精通 SEO 关键词分析，能够识别高价值、低竞争的关键词机会。
你使用数据驱动的方法，结合搜索量、竞争度、CPC 等指标进行分析。""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )


def create_keyword_research_task(agent: Agent, keyword: str, niche: str) -> Task:
    """创建关键词研究任务"""
    return Task(
        description=f"""分析以下关键词的潜力：

关键词：{keyword}
领域：{niche}

请完成以下分析：
1. 关键词变体和长尾词建议（至少5个）
2. 搜索意图分析（信息型/商业型/交易型）
3. 竞争度评估（低/中/高）
4. 内容角度建议（从哪个切入点写最有机会排名）
5. 推荐的次要关键词（LSI Keywords）

输出格式：JSON""",
        expected_output="包含关键词分析、变体建议、竞争评估的 JSON 报告",
        agent=agent,
    )
```

**Step 2: 验证 Agent**

Run: `cd backend && uv run python -c "from agents.crews.keyword_researcher import create_keyword_researcher; print('✅ 李纲 Agent 定义成功')"`

**Step 3: 提交**

```bash
git add backend/agents/crews/keyword_researcher.py
git commit -m "feat(agent): 定义李纲关键词研究 Agent"
```

---

### Task 3: 创建 CrewAI Agent 定义 - 张择端（SERP分析+大纲）

**Objective:** 定义张择端角色的 CrewAI Agent

**Files:**
- Create: `backend/agents/crews/content_strategist.py`

**Step 1: 创建 Agent 定义**

```python
"""
张择端 - 内容策略 Agent
职责：SERP 分析 + 内容大纲生成
"""
from crewai import Agent, Task, Crew


def create_content_strategist(llm) -> Agent:
    """创建内容策略 Agent"""
    return Agent(
        role="内容策略专家",
        goal="分析 SERP 结果，制定最优内容大纲",
        backstory="""你是张择端，北宋画家，擅长观察和描绘细节。
在 CrazyMail 系统中，你负责 SERP 分析和内容大纲制定。
你能够从搜索结果中识别内容模式、用户需求和排名机会。
你制定的大纲既有逻辑性又有 SEO 友好性。""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )


def create_serp_analysis_task(agent: Agent, keyword: str, research_data: dict) -> Task:
    """创建 SERP 分析任务"""
    return Task(
        description=f"""基于关键词研究结果，进行 SERP 分析并生成内容大纲：

关键词：{keyword}
研究数据：{research_data}

请完成以下工作：
1. SERP 分析：
   - 当前排名前10的内容特征（字数、结构、角度）
   - 内容差距分析（现有内容缺少什么）
   - 用户痛点识别

2. 内容大纲：
   - H1 标题（含关键词，吸引点击）
   - H2/H3 结构（至少3个H2，每个H2下1-2个H3）
   - 每个章节的核心要点
   - 建议的内链锚文本
   - Schema Markup 类型建议

输出格式：JSON""",
        expected_output="包含 SERP 分析和详细内容大纲的 JSON 报告",
        agent=agent,
    )
```

**Step 2: 验证 Agent**

Run: `cd backend && uv run python -c "from agents.crews.content_strategist import create_content_strategist; print('✅ 张择端 Agent 定义成功')"`

**Step 3: 提交**

```bash
git add backend/agents/crews/content_strategist.py
git commit -m "feat(agent): 定义张择端内容策略 Agent"
```

---

### Task 4: 创建 CrewAI Agent 定义 - 李清照（内容写作）

**Objective:** 定义李清照角色的 CrewAI Agent

**Files:**
- Create: `backend/agents/crews/content_writer.py`

**Step 1: 创建 Agent 定义**

```python
"""
李清照 - 内容写作 Agent
职责：根据大纲撰写高质量文章
"""
from crewai import Agent, Task, Crew


def create_content_writer(llm) -> Agent:
    """创建内容写作 Agent"""
    return Agent(
        role="内容写作专家",
        goal="撰写高质量、有深度、人味十足的 SEO 文章",
        backstory="""你是李清照，北宋著名女词人，才华横溢，文笔优美。
在 CrazyMail 系统中，你负责内容写作工作。
你写的文章既有深度又有温度，读起来像真人写的。
你擅长用生动的例子、个人见解和自然的过渡来丰富内容。
你的写作风格：专业但不枯燥，有观点但不偏激，有细节但不啰嗦。""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )


def create_writing_task(agent: Agent, keyword: str, outline: dict, niche: str) -> Task:
    """创建写作任务"""
    return Task(
        description=f"""根据以下大纲撰写一篇完整的 SEO 文章：

关键词：{keyword}
领域：{niche}
大纲：{outline}

写作要求：
1. 字数：1500-3000 词
2. 风格：专业但亲切，像资深从业者在分享经验
3. 结构：严格按照大纲的 H2/H3 结构
4. SEO 要求：
   - 关键词自然出现 3-5 次（不堆砌）
   - 使用 LSI 关键词
   - 包含内链建议锚文本
5. 人味要求（降低 AI 检测分数）：
   - 加入个人观点/经验
   - 使用口语化表达（适当）
   - 包含具体案例/数据
   - 有轻微的不完美（如口语化过渡）
6. 不要使用以下 AI 常用词：
   - "首先/其次/最后"的刻板结构
   - "值得注意的是"
   - "总而言之"
   - "综上所述"

输出格式：Markdown 文章""",
        expected_output="一篇 1500-3000 词的高质量 SEO 文章（Markdown 格式）",
        agent=agent,
    )
```

**Step 2: 验证 Agent**

Run: `cd backend && uv run python -c "from agents.crews.content_writer import create_content_writer; print('✅ 李清照 Agent 定义成功')"`

**Step 3: 提交**

```bash
git add backend/agents/crews/content_writer.py
git commit -m "feat(agent): 定义李清照内容写作 Agent"
```

---

### Task 5: 创建 CrewAI Agent 定义 - 岳飞（质检）

**Objective:** 定义岳飞角色的 CrewAI Agent

**Files:**
- Create: `backend/agents/crews/qa_inspector.py`

**Step 1: 创建 Agent 定义**

```python
"""
岳飞 - 质检 Agent
职责：9重质检，确保内容质量
"""
from crewai import Agent, Task, Crew


def create_qa_inspector(llm) -> Agent:
    """创建质检 Agent"""
    return Agent(
        role="内容质检专家",
        goal="执行 9 重质检，确保内容达到发布标准",
        backstory="""你是岳飞，南宋名将，治军严明，一丝不苟。
在 CrazyMail 系统中，你负责内容质量检查。
你有 9 道检查程序，任何一道不通过都不能放行。
你的标准：AI 检测分 < 30，SEO 分 > 75，E-E-A-T 合规。""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )


def create_qa_task(agent: Agent, content: str, keyword: str) -> Task:
    """创建质检任务"""
    return Task(
        description=f"""对以下内容执行 9 重质检：

关键词：{keyword}
内容：{content}

9 重质检清单：
1. AI 味检测（目标 < 30 分）
   - 检查是否有 AI 常用词/句式
   - 检查句式是否过于规律
   - 检查是否有个人观点/经验

2. SEO 评分（目标 > 75 分）
   - 关键词密度（2-3%）
   - 标题包含关键词
   - Meta Description 质量
   - 内链建议

3. E-E-A-T 信号
   - 经验（Experience）：是否有具体案例
   - 专业（Expertise）：是否有专业术语
   - 权威（Authoritativeness）：是否有数据引用
   - 可信（Trustworthiness）：是否有来源说明

4. 字数/结构检查
   - 字数 1500-3000
   - H2/H3 结构完整
   - 段落长度适中

5. 内链建议
   - 站内相关文章链接建议
   - 锚文本建议

6. 图片 alt 文本建议
   - 至少 3 张图片建议
   - alt 文本包含关键词

7. Schema Markup 建议
   - 推荐的 Schema 类型
   - 关键字段

8. 去重检测
   - 与站内已发内容对比
   - 重复度 < 20%

9. 人味评分
   - 口头禅/个人观点存在
   - 句式变化度
   - 情感表达

输出格式：JSON（每项评分 + 总分 + 修改建议）""",
        expected_output="包含 9 项评分和修改建议的 JSON 质检报告",
        agent=agent,
    )
```

**Step 2: 验证 Agent**

Run: `cd backend && uv run python -c "from agents.crews.qa_inspector import create_qa_inspector; print('✅ 岳飞 Agent 定义成功')"`

**Step 3: 提交**

```bash
git add backend/agents/crews/qa_inspector.py
git commit -m "feat(agent): 定义岳飞质检 Agent"
```

---

### Task 6: 创建 CrewAI Agent 定义 - 种师道（SEO优化）

**Objective:** 定义种师道角色的 CrewAI Agent

**Files:**
- Create: `backend/agents/crews/seo_optimizer.py`

**Step 1: 创建 Agent 定义**

```python
"""
种师道 - SEO 优化 Agent
职责：优化内容的 SEO 元素
"""
from crewai import Agent, Task, Crew


def create_seo_optimizer(llm) -> Agent:
    """创建 SEO 优化 Agent"""
    return Agent(
        role="SEO 优化专家",
        goal="优化内容的 SEO 元素，提升搜索排名潜力",
        backstory="""你是种师道，北宋名将，擅长战略布局。
在 CrazyMail 系统中，你负责 SEO 优化工作。
你精通搜索引擎优化，能够从技术层面提升内容的排名潜力。
你关注：标题优化、Meta 描述、Schema Markup、内链策略。""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )


def create_seo_optimization_task(agent: Agent, content: str, keyword: str, qa_report: dict) -> Task:
    """创建 SEO 优化任务"""
    return Task(
        description=f"""优化以下内容的 SEO 元素：

关键词：{keyword}
内容：{content}
质检报告：{qa_report}

请完成以下优化：
1. 标题优化
   - 确保包含关键词
   - 长度 50-60 字符
   - 吸引点击

2. Meta Description
   - 150-160 字符
   - 包含关键词
   - 有行动号召

3. Schema Markup
   - 生成 JSON-LD 代码
   - 推荐类型：Article/HowTo/FAQ

4. 内链策略
   - 建议 3-5 个内链位置
   - 锚文本建议

5. 图片优化
   - alt 文本建议
   - 文件名建议

6. URL Slug 建议
   - 包含关键词
   - 简洁友好

输出格式：JSON（包含优化后的各元素）""",
        expected_output="包含优化后标题、Meta、Schema 等的 JSON 报告",
        agent=agent,
    )
```

**Step 2: 验证 Agent**

Run: `cd backend && uv run python -c "from agents.crews.seo_optimizer import create_seo_optimizer; print('✅ 种师道 Agent 定义成功')"`

**Step 3: 提交**

```bash
git add backend/agents/crews/seo_optimizer.py
git commit -m "feat(agent): 定义种师道 SEO 优化 Agent"
```

---

### Task 7: 创建 CrewAI Agent 定义 - 韩世忠（链接建设）

**Objective:** 定义韩世忠角色的 CrewAI Agent

**Files:**
- Create: `backend/agents/crews/link_builder.py`

**Step 1: 创建 Agent 定义**

```python
"""
韩世忠 - 链接建设 Agent
职责：制定外链获取策略
"""
from crewai import Agent, Task, Crew


def create_link_builder(llm) -> Agent:
    """创建链接建设 Agent"""
    return Agent(
        role="链接建设专家",
        goal="制定外链获取策略，提升网站权威度",
        backstory="""你是韩世忠，南宋名将，擅长联络和外交。
在 CrazyMail 系统中，你负责链接建设工作。
你精通白帽外链策略，能够找到高质量的外链机会。
你关注：客座博客、资源页链接、broken link building、HARO。""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )


def create_link_building_task(agent: Agent, keyword: str, content_title: str, niche: str) -> Task:
    """创建链接建设任务"""
    return Task(
        description=f"""为以下内容制定外链获取策略：

关键词：{keyword}
内容标题：{content_title}
领域：{niche}

请制定以下策略：
1. 竞品外链分析
   - 识别竞品的高质量外链来源
   - 找出可复制的外链机会

2. 外链获取策略（按优先级排序）
   - 客座博客机会（目标网站 + 投稿指南）
   - 资源页链接机会
   - Broken Link Building 机会
   - HARO/记者请求机会

3. 外展邮件模板
   - 个性化的外展邮件模板
   - 跟进邮件模板

4. 内容资产建议
   - 哪些内容类型更容易获得外链
   - 可创建的链接诱饵内容

输出格式：JSON""",
        expected_output="包含外链策略、目标网站、邮件模板的 JSON 报告",
        agent=agent,
    )
```

**Step 2: 验证 Agent**

Run: `cd backend && uv run python -c "from agents.crews.link_builder import create_link_builder; print('✅ 韩世忠 Agent 定义成功')"`

**Step 3: 提交**

```bash
git add backend/agents/crews/link_builder.py
git commit -m "feat(agent): 定义韩世忠链接建设 Agent"
```

---

### Task 8: 创建 LangGraph Workflow - 前3阶段

**Objective:** 用 LangGraph 串联关键词研究、SERP分析、内容写作前3个阶段

**Files:**
- Create: `backend/agents/workflows/content_pipeline.py`

**Step 1: 创建 Workflow**

```python
"""
内容流水线 Workflow
LangGraph 状态图：关键词研究 → SERP分析 → 内容写作
"""
from typing import TypedDict, Optional, Literal
from langgraph.graph import StateGraph, END
from loguru import logger


class PipelineState(TypedDict):
    """流水线状态"""
    task_id: str
    keyword: str
    site_id: str
    niche: str
    
    # 各阶段产出
    research_data: Optional[dict]
    serp_analysis: Optional[dict]
    outline: Optional[dict]
    content: Optional[str]
    
    # 控制
    current_stage: str
    error: Optional[str]


def research_node(state: PipelineState) -> PipelineState:
    """李纲：关键词研究节点"""
    logger.info(f"[李纲] 开始关键词研究: {state['keyword']}")
    
    # TODO: 调用 CrewAI Agent
    # agent = create_keyword_researcher(llm)
    # task = create_keyword_research_task(agent, state['keyword'], state['niche'])
    # result = Crew(agents=[agent], tasks=[task]).kickoff()
    
    # 模拟产出（实际实现时替换为真实调用）
    state['research_data'] = {
        'keyword': state['keyword'],
        'variations': [f"{state['keyword']} guide", f"best {state['keyword']}"],
        'search_intent': 'informational',
        'competition': 'medium',
        'lsi_keywords': ['example1', 'example2'],
    }
    state['current_stage'] = 'analyzing'
    
    logger.info(f"[李纲] 关键词研究完成")
    return state


def analysis_node(state: PipelineState) -> PipelineState:
    """张择端：SERP分析+大纲节点"""
    logger.info(f"[张择端] 开始 SERP 分析: {state['keyword']}")
    
    # TODO: 调用 CrewAI Agent
    
    # 模拟产出
    state['serp_analysis'] = {
        'top_results': [],
        'content_gaps': [],
        'user_pain_points': [],
    }
    state['outline'] = {
        'h1': f"The Ultimate Guide to {state['keyword']}",
        'h2s': [
            {'title': f"What is {state['keyword']}?", 'h3s': ['Definition', 'History']},
            {'title': f"How to Use {state['keyword']}", 'h3s': ['Step 1', 'Step 2']},
            {'title': f"Best Practices for {state['keyword']}", 'h3s': ['Tip 1', 'Tip 2']},
        ],
        'schema_type': 'Article',
    }
    state['current_stage'] = 'writing'
    
    logger.info(f"[张择端] SERP 分析和大纲完成")
    return state


def writing_node(state: PipelineState) -> PipelineState:
    """李清照：内容写作节点"""
    logger.info(f"[李清照] 开始内容写作: {state['keyword']}")
    
    # TODO: 调用 CrewAI Agent
    
    # 模拟产出
    state['content'] = f"# {state['outline']['h1']}\n\nThis is a sample article about {state['keyword']}..."
    state['current_stage'] = 'qa_checking'
    
    logger.info(f"[李清照] 内容写作完成")
    return state


def build_content_pipeline() -> StateGraph:
    """构建内容流水线"""
    workflow = StateGraph(PipelineState)
    
    # 添加节点
    workflow.add_node("research", research_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("writing", writing_node)
    
    # 定义边
    workflow.set_entry_point("research")
    workflow.add_edge("research", "analysis")
    workflow.add_edge("analysis", "writing")
    workflow.add_edge("writing", END)
    
    return workflow.compile()


# 创建流水线实例
content_pipeline = build_content_pipeline()
```

**Step 2: 验证 Workflow**

Run: `cd backend && uv run python -c "from agents.workflows.content_pipeline import content_pipeline; print('✅ 内容流水线创建成功')"`

**Step 3: 提交**

```bash
git add backend/agents/workflows/content_pipeline.py
git commit -m "feat(workflow): 创建内容流水线 LangGraph Workflow（前3阶段）"
```

---

### Task 9: 更新 FastAPI Router - 内容任务接口

**Objective:** 实现内容任务的 CRUD 接口

**Files:**
- Modify: `backend/routers/content.py`

**Step 1: 更新 Router**

```python
"""
内容工厂模块路由
7阶段流水线：关键词研究 → SERP分析 → 内容写作 → 质检 → SEO优化 → 链接建设 → 人工审核
"""
from fastapi import APIRouter, HTTPException
from models.content import ContentTask, CreateTaskRequest, TaskResponse, TaskStatus
from agents.workflows.content_pipeline import content_pipeline
from loguru import logger
from datetime import datetime

router = APIRouter()

# 内存存储（生产环境替换为 Supabase）
tasks_db: dict[str, ContentTask] = {}


@router.get("/tasks")
async def list_tasks():
    """获取内容任务列表"""
    tasks = list(tasks_db.values())
    return {"tasks": [t.model_dump() for t in tasks], "total": len(tasks)}


@router.post("/tasks")
async def create_task(request: CreateTaskRequest):
    """创建内容任务"""
    task = ContentTask(
        keyword=request.keyword,
        site_id=request.site_id,
        niche=request.niche,
    )
    tasks_db[task.task_id] = task
    
    logger.info(f"创建任务: {task.task_id} - {task.keyword}")
    
    return {"task_id": task.task_id, "status": task.status, "message": "任务创建成功"}


@router.post("/tasks/{task_id}/run")
async def run_task(task_id: str):
    """运行内容流水线"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks_db[task_id]
    
    # 构建初始状态
    initial_state = {
        "task_id": task.task_id,
        "keyword": task.keyword,
        "site_id": task.site_id,
        "niche": task.niche,
        "research_data": None,
        "serp_analysis": None,
        "outline": None,
        "content": None,
        "current_stage": "researching",
        "error": None,
    }
    
    try:
        # 运行流水线
        result = content_pipeline.invoke(initial_state)
        
        # 更新任务状态
        task.research_data = result.get('research_data')
        task.serp_analysis = result.get('serp_analysis')
        task.outline = result.get('outline')
        task.content = result.get('content')
        task.status = TaskStatus(result.get('current_stage', 'pending'))
        task.updated_at = datetime.now()
        
        return {"task_id": task_id, "status": task.status, "message": "流水线执行完成"}
    except Exception as e:
        logger.error(f"流水线执行失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """获取任务详情"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks_db[task_id]
    return task.model_dump()


@router.post("/tasks/{task_id}/approve")
async def approve_task(task_id: str):
    """宋徽宗审批通过"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks_db[task_id]
    task.status = TaskStatus.APPROVED
    task.completed_at = datetime.now()
    
    return {"task_id": task_id, "action": "approved", "message": "文章已批准"}


@router.post("/tasks/{task_id}/reject")
async def reject_task(task_id: str):
    """宋徽宗打回重写"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks_db[task_id]
    task.status = TaskStatus.REJECTED
    
    return {"task_id": task_id, "action": "rejected", "message": "文章已打回"}


@router.get("/review-queue")
async def review_queue():
    """待审核队列"""
    queue = [t for t in tasks_db.values() if t.status == TaskStatus.REVIEWING]
    return {"queue": [t.model_dump() for t in queue], "total": len(queue)}
```

**Step 2: 验证 Router**

Run: `cd backend && uv run python -c "from routers.content import router; print('✅ 内容路由更新成功')"`

**Step 3: 提交**

```bash
git add backend/routers/content.py
git commit -m "feat(content): 实现内容任务 CRUD 接口"
```

---

### Task 10: 更新 main.py - 注册内容路由

**Objective:** 在 FastAPI 应用中注册内容路由

**Files:**
- Modify: `backend/main.py`

**Step 1: 更新 main.py**

在 `main.py` 中取消注释内容路由：

```python
# 注册路由（插座原则：每个模块一个 Router）
from routers import content
app.include_router(content.router, prefix="/api/v1/content", tags=["内容工厂"])
# TODO: 按需启用
# from routers import sites, personas, security, gold_medal, dashboard
```

**Step 2: 验证应用启动**

Run: `cd backend && uv run uvicorn backend.main:app --host 127.0.0.1 --port 8001 &`
Run: `curl http://127.0.0.1:8001/docs` (应返回 Swagger UI)

**Step 3: 提交**

```bash
git add backend/main.py
git commit -m "feat(api): 注册内容工厂路由"
```

---

### Task 11: 端到端测试 - 创建并运行任务

**Objective:** 测试完整的任务创建和运行流程

**Files:**
- Create: `tests/test_content_pipeline.py`

**Step 1: 创建测试**

```python
"""
内容流水线端到端测试
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_create_task():
    """测试创建任务"""
    response = client.post("/api/v1/content/tasks", json={
        "keyword": "best email marketing tools",
        "site_id": "site_001",
        "niche": "digital marketing",
    })
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "pending"
    return data["task_id"]


def test_list_tasks():
    """测试获取任务列表"""
    response = client.get("/api/v1/content/tasks")
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert "total" in data


def test_run_pipeline():
    """测试运行流水线"""
    # 先创建任务
    create_response = client.post("/api/v1/content/tasks", json={
        "keyword": "best email marketing tools",
        "site_id": "site_001",
        "niche": "digital marketing",
    })
    task_id = create_response.json()["task_id"]
    
    # 运行流水线
    run_response = client.post(f"/api/v1/content/tasks/{task_id}/run")
    assert run_response.status_code == 200
    
    # 获取任务详情
    get_response = client.get(f"/api/v1/content/tasks/{task_id}")
    assert get_response.status_code == 200
    task = get_response.json()
    assert task["research_data"] is not None
    assert task["content"] is not None
```

**Step 2: 运行测试**

Run: `cd backend && uv run pytest tests/test_content_pipeline.py -v`

**Step 3: 提交**

```bash
git add tests/test_content_pipeline.py
git commit -m "test(content): 添加内容流水线端到端测试"
```

---

### Task 12: 阶段性验证 - 完整流程测试

**Objective:** 验证 Week 1 的所有功能

**验证清单:**
- [ ] 所有 Agent 定义文件可正常导入
- [ ] LangGraph Workflow 可正常创建
- [ ] FastAPI 应用可正常启动
- [ ] POST /api/v1/content/tasks 可创建任务
- [ ] POST /api/v1/content/tasks/{id}/run 可运行流水线
- [ ] GET /api/v1/content/tasks/{id} 可获取任务详情
- [ ] 测试通过

**验证命令:**
```bash
cd backend
uv run python -c "from agents.crews.keyword_researcher import create_keyword_researcher; print('✅ 李纲')"
uv run python -c "from agents.crews.content_strategist import create_content_strategist; print('✅ 张择端')"
uv run python -c "from agents.crews.content_writer import create_content_writer; print('✅ 李清照')"
uv run python -c "from agents.workflows.content_pipeline import content_pipeline; print('✅ 流水线')"
uv run pytest tests/test_content_pipeline.py -v
```

---

## Week 2: 质检 + 完整流水线（Task 13-20）

### Task 13: 扩展 LangGraph Workflow - 添加质检节点

**Objective:** 在流水线中添加岳飞质检节点

**Files:**
- Modify: `backend/agents/workflows/content_pipeline.py`

**Step 1: 添加质检节点**

```python
def qa_node(state: PipelineState) -> PipelineState:
    """岳飞：质检节点"""
    logger.info(f"[岳飞] 开始 9 重质检")
    
    # TODO: 调用 CrewAI Agent
    # agent = create_qa_inspector(llm)
    # task = create_qa_task(agent, state['content'], state['keyword'])
    # result = Crew(agents=[agent], tasks=[task]).kickoff()
    
    # 模拟质检报告
    state['qa_report'] = {
        'ai_detection_score': 25,  # < 30 通过
        'seo_score': 80,           # > 75 通过
        'eeat_score': 70,
        'word_count': 2000,
        'structure_score': 85,
        'internal_links': 3,
        'image_alts': 4,
        'schema_markup': 'Article',
        'uniqueness_score': 90,
        'human_feel_score': 75,
        'overall_score': 78,
        'passed': True,
        'suggestions': [],
    }
    state['ai_detection_score'] = 25
    state['seo_score'] = 80
    state['current_stage'] = 'optimizing'
    
    logger.info(f"[岳飞] 质检完成: AI检测={25}, SEO={80}")
    return state
```

**Step 2: 更新 Workflow 图**

```python
def build_content_pipeline() -> StateGraph:
    """构建内容流水线"""
    workflow = StateGraph(PipelineState)
    
    # 添加节点
    workflow.add_node("research", research_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("writing", writing_node)
    workflow.add_node("qa", qa_node)  # 新增
    
    # 定义边
    workflow.set_entry_point("research")
    workflow.add_edge("research", "analysis")
    workflow.add_edge("analysis", "writing")
    workflow.add_edge("writing", "qa")
    workflow.add_edge("qa", END)
    
    return workflow.compile()
```

**Step 3: 提交**

```bash
git add backend/agents/workflows/content_pipeline.py
git commit -m "feat(workflow): 添加岳飞质检节点"
```

---

### Task 14: 扩展 LangGraph Workflow - 添加SEO优化节点

**Objective:** 在流水线中添加种师道 SEO 优化节点

**Files:**
- Modify: `backend/agents/workflows/content_pipeline.py`

**Step 1: 添加 SEO 优化节点**

```python
def seo_optimization_node(state: PipelineState) -> PipelineState:
    """种师道：SEO 优化节点"""
    logger.info(f"[种师道] 开始 SEO 优化")
    
    # TODO: 调用 CrewAI Agent
    
    # 模拟优化结果
    state['seo_optimization'] = {
        'optimized_title': f"Best {state['keyword']} - Complete Guide 2026",
        'meta_description': f"Discover the best {state['keyword']}. Expert reviews, comparisons, and recommendations.",
        'url_slug': f"best-{state['keyword'].replace(' ', '-')}",
        'schema_markup': {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": f"Best {state['keyword']}",
        },
        'internal_links': [
            {"anchor": "email marketing tips", "url": "/blog/email-marketing-tips"},
            {"anchor": "marketing tools comparison", "url": "/blog/tools-comparison"},
        ],
        'image_alts': [
            f"{state['keyword']} comparison chart",
            f"top {state['keyword']} features",
        ],
    }
    state['current_stage'] = 'link_building'
    
    logger.info(f"[种师道] SEO 优化完成")
    return state
```

**Step 2: 更新 Workflow 图**

在 `build_content_pipeline` 中添加：
```python
workflow.add_node("seo_optimization", seo_optimization_node)
workflow.add_edge("qa", "seo_optimization")
workflow.add_edge("seo_optimization", END)
```

**Step 3: 提交**

```bash
git add backend/agents/workflows/content_pipeline.py
git commit -m "feat(workflow): 添加种师道 SEO 优化节点"
```

---

### Task 15: 扩展 LangGraph Workflow - 添加链接建设节点

**Objective:** 在流水线中添加韩世忠链接建设节点

**Files:**
- Modify: `backend/agents/workflows/content_pipeline.py`

**Step 1: 添加链接建设节点**

```python
def link_building_node(state: PipelineState) -> PipelineState:
    """韩世忠：链接建设节点"""
    logger.info(f"[韩世忠] 开始链接建设策略")
    
    # TODO: 调用 CrewAI Agent
    
    # 模拟策略
    state['link_strategy'] = {
        'competitor_backlinks': [],
        'guest_post_opportunities': [
            {"site": "marketingprofs.com", "da": 85, "contact": "editor@marketingprofs.com"},
            {"site": "neilpatel.com", "da": 90, "contact": "team@neilpatel.com"},
        ],
        'resource_page_opportunities': [],
        'broken_link_opportunities': [],
        'outreach_template': f"Hi,\n\nI noticed you have a great article about {state['keyword']}...",
    }
    state['current_stage'] = 'reviewing'
    
    logger.info(f"[韩世忠] 链接建设策略完成")
    return state
```

**Step 2: 更新 Workflow 图**

```python
workflow.add_node("link_building", link_building_node)
workflow.add_edge("seo_optimization", "link_building")
workflow.add_edge("link_building", END)
```

**Step 3: 提交**

```bash
git add backend/agents/workflows/content_pipeline.py
git commit -m "feat(workflow): 添加韩世忠链接建设节点"
```

---

### Task 16: 实现 Human-in-the-Loop - 宋徽宗审核节点

**Objective:** 实现人工审核节点，支持中断和恢复

**Files:**
- Modify: `backend/agents/workflows/content_pipeline.py`

**Step 1: 添加审核节点**

```python
def review_node(state: PipelineState) -> PipelineState:
    """宋徽宗：人工审核节点（中断点）"""
    logger.info(f"[宋徽宗] 进入人工审核队列")
    state['current_stage'] = 'reviewing'
    # 注意：这个节点会被 interrupt_before 中断
    # 人工审核通过后，会继续执行
    return state
```

**Step 2: 更新 Workflow 图（使用 interrupt_before）**

```python
from langgraph.checkpoint.memory import MemorySaver

def build_content_pipeline() -> StateGraph:
    """构建内容流水线"""
    workflow = StateGraph(PipelineState)
    
    # 添加所有节点
    workflow.add_node("research", research_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("writing", writing_node)
    workflow.add_node("qa", qa_node)
    workflow.add_node("seo_optimization", seo_optimization_node)
    workflow.add_node("link_building", link_building_node)
    workflow.add_node("review", review_node)
    
    # 定义边
    workflow.set_entry_point("research")
    workflow.add_edge("research", "analysis")
    workflow.add_edge("analysis", "writing")
    workflow.add_edge("writing", "qa")
    workflow.add_edge("qa", "seo_optimization")
    workflow.add_edge("seo_optimization", "link_building")
    workflow.add_edge("link_building", "review")
    workflow.add_edge("review", END)
    
    # 编译时设置 interrupt_before
    memory = MemorySaver()
    return workflow.compile(
        checkpointer=memory,
        interrupt_before=["review"],  # 在审核节点前中断
    )
```

**Step 3: 提交**

```bash
git add backend/agents/workflows/content_pipeline.py
git commit -m "feat(workflow): 实现宋徽宗 Human-in-the-Loop 审核节点"
```

---

### Task 17: 更新 FastAPI - 支持审核流程

**Objective:** 更新 API 支持审核中断和恢复

**Files:**
- Modify: `backend/routers/content.py`

**Step 1: 更新运行接口**

```python
@router.post("/tasks/{task_id}/run")
async def run_task(task_id: str):
    """运行内容流水线"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks_db[task_id]
    
    initial_state = {
        "task_id": task.task_id,
        "keyword": task.keyword,
        "site_id": task.site_id,
        "niche": task.niche,
        "research_data": None,
        "serp_analysis": None,
        "outline": None,
        "content": None,
        "qa_report": None,
        "seo_optimization": None,
        "link_strategy": None,
        "ai_detection_score": None,
        "seo_score": None,
        "current_stage": "researching",
        "error": None,
    }
    
    try:
        # 使用 thread_id 支持中断恢复
        config = {"configurable": {"thread_id": task_id}}
        result = content_pipeline.invoke(initial_state, config)
        
        # 更新任务
        task.research_data = result.get('research_data')
        task.serp_analysis = result.get('serp_analysis')
        task.outline = result.get('outline')
        task.content = result.get('content')
        task.qa_report = result.get('qa_report')
        task.seo_optimization = result.get('seo_optimization')
        task.link_strategy = result.get('link_strategy')
        task.ai_detection_score = result.get('ai_detection_score')
        task.seo_score = result.get('seo_score')
        task.status = TaskStatus.REVIEWING
        task.updated_at = datetime.now()
        
        return {
            "task_id": task_id,
            "status": "reviewing",
            "message": "流水线执行完成，等待人工审核",
            "content_preview": task.content[:200] if task.content else None,
        }
    except Exception as e:
        logger.error(f"流水线执行失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

**Step 2: 提交**

```bash
git add backend/routers/content.py
git commit -m "feat(content): 支持审核中断和恢复流程"
```

---

### Task 18: 创建基础审核界面

**Objective:** 创建简单的 HTML 审核界面

**Files:**
- Create: `backend/templates/review.html`

**Step 1: 创建审核页面**

```html
<!DOCTYPE html>
<html>
<head>
    <title>CrazyMail 审核界面 - 汴京总督府</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: #1a1a2e; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .task-card { border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 8px; }
        .score { display: inline-block; padding: 5px 15px; border-radius: 20px; margin: 5px; }
        .score.pass { background: #4CAF50; color: white; }
        .score.fail { background: #f44336; color: white; }
        .content-preview { background: #f5f5f5; padding: 15px; border-radius: 4px; white-space: pre-wrap; max-height: 400px; overflow-y: auto; }
        .actions { margin-top: 20px; }
        .btn { padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
        .btn-approve { background: #4CAF50; color: white; }
        .btn-reject { background: #f44336; color: white; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏯 汴京总督府 - 宋徽宗审核台</h1>
        <p>内容流水线人工审核界面</p>
    </div>
    
    <div id="task-list">
        <h2>待审核队列</h2>
        <div id="queue"></div>
    </div>
    
    <div id="task-detail" style="display:none;">
        <h2>审核详情</h2>
        <div class="task-card">
            <h3 id="task-keyword"></h3>
            <div>
                <span class="score" id="ai-score">AI检测: --</span>
                <span class="score" id="seo-score">SEO: --</span>
            </div>
            <h4>内容预览：</h4>
            <div class="content-preview" id="content-preview"></div>
            <div class="actions">
                <button class="btn btn-approve" onclick="approveTask()">✅ 批准发布</button>
                <button class="btn btn-reject" onclick="rejectTask()">❌ 打回重写</button>
            </div>
        </div>
    </div>
    
    <script>
        let currentTaskId = null;
        
        async function loadQueue() {
            const response = await fetch('/api/v1/content/review-queue');
            const data = await response.json();
            const queueDiv = document.getElementById('queue');
            queueDiv.innerHTML = data.queue.map(task => `
                <div class="task-card" onclick="loadTask('${task.task_id}')">
                    <h3>${task.keyword}</h3>
                    <p>状态: ${task.status} | 创建: ${new Date(task.created_at).toLocaleString()}</p>
                </div>
            `).join('');
        }
        
        async function loadTask(taskId) {
            currentTaskId = taskId;
            const response = await fetch(`/api/v1/content/tasks/${taskId}`);
            const task = await response.json();
            
            document.getElementById('task-keyword').textContent = task.keyword;
            document.getElementById('ai-score').textContent = `AI检测: ${task.ai_detection_score || '--'}`;
            document.getElementById('seo-score').textContent = `SEO: ${task.seo_score || '--'}`;
            document.getElementById('content-preview').textContent = task.content || '无内容';
            document.getElementById('task-detail').style.display = 'block';
        }
        
        async function approveTask() {
            if (!currentTaskId) return;
            await fetch(`/api/v1/content/tasks/${currentTaskId}/approve`, {method: 'POST'});
            alert('文章已批准！');
            loadQueue();
        }
        
        async function rejectTask() {
            if (!currentTaskId) return;
            await fetch(`/api/v1/content/tasks/${currentTaskId}/reject`, {method: 'POST'});
            alert('文章已打回！');
            loadQueue();
        }
        
        loadQueue();
    </script>
</body>
</html>
```

**Step 2: 添加静态文件服务**

在 `main.py` 中添加：
```python
from fastapi.responses import HTMLResponse
from pathlib import Path

@app.get("/review", response_class=HTMLResponse)
async def review_page():
    """审核界面"""
    html_path = Path(__file__).parent / "templates" / "review.html"
    return html_path.read_text(encoding='utf-8')
```

**Step 3: 提交**

```bash
git add backend/templates/review.html backend/main.py
git commit -m "feat(review): 创建宋徽宗审核界面"
```

---

### Task 19: 集成真实 LLM - MiMo v2.5 Pro

**Objective:** 将模拟 Agent 替换为真实 LLM 调用

**Files:**
- Create: `backend/services/llm_service.py`
- Modify: Agent 定义文件

**Step 1: 创建 LLM 服务**

```python
"""
LLM 服务
统一管理 LLM 调用（MiMo v2.5 Pro + Agnes AI）
"""
import os
from langchain_openai import ChatOpenAI
from loguru import logger


def get_mimo_llm() -> ChatOpenAI:
    """获取 MiMo v2.5 Pro LLM"""
    return ChatOpenAI(
        model="mimo-v2.5-pro",
        api_key=os.getenv("MIMO_API_KEY"),
        base_url="https://token-plan-sgp.xiaomimimo.com/v1",
        temperature=0.7,
        max_tokens=4096,
    )


def get_agnes_llm() -> ChatOpenAI:
    """获取 Agnes AI LLM（低成本批量任务）"""
    return ChatOpenAI(
        model="agnes-2.0-flash",
        api_key=os.getenv("AGNES_API_KEY"),
        base_url="https://apihub.agnes-ai.com/v1",
        temperature=0.7,
        max_tokens=4096,
    )


def get_writing_llm() -> ChatOpenAI:
    """获取写作 LLM（主力）"""
    primary = os.getenv("WRITING_MODEL_PRIMARY", "mimo-v2.5-pro")
    if primary == "mimo-v2.5-pro":
        return get_mimo_llm()
    else:
        return get_agnes_llm()


def get_research_llm() -> ChatOpenAI:
    """获取研究 LLM（低成本）"""
    model = os.getenv("RESEARCH_MODEL", "agnes-2.0-flash")
    if model == "agnes-2.0-flash":
        return get_agnes_llm()
    else:
        return get_mimo_llm()
```

**Step 2: 更新 Agent 使用真实 LLM**

在各 Agent 定义中，将 `llm` 参数替换为真实 LLM：

```python
from services.llm_service import get_writing_llm, get_research_llm

# 关键词研究用低成本模型
agent = create_keyword_researcher(get_research_llm())

# 写作用主力模型
agent = create_content_writer(get_writing_llm())
```

**Step 3: 提交**

```bash
git add backend/services/llm_service.py
git commit -m "feat(llm): 创建 LLM 服务，集成 MiMo + Agnes AI"
```

---

### Task 20: Week 2 验证 - 完整 7 阶段流水线

**Objective:** 验证完整的 7 阶段流水线

**验证清单:**
- [ ] 所有 7 个 Agent 定义可正常导入
- [ ] LangGraph Workflow 包含所有 7 个节点
- [ ] Human-in-the-Loop 在审核节点前正确中断
- [ ] 审核界面可正常加载
- [ ] LLM 服务可正常调用
- [ ] 端到端测试通过

**验证命令:**
```bash
cd backend
uv run python -c "
from agents.workflows.content_pipeline import content_pipeline
print('✅ 完整 7 阶段流水线')
print(f'节点: {list(content_pipeline.get_graph().nodes.keys())}')
"
```

---

## Week 3: 调试 + 验证（Task 21-25）

### Task 21: 质检分数校准

**Objective:** 调整质检阈值，确保输出质量

**步骤:**
1. 运行 10 个不同关键词的流水线
2. 收集 AI 检测分数和 SEO 分数
3. 调整阈值参数
4. 记录最优配置

---

### Task 22: 去 AI 味策略优化

**Objective:** 优化写作 Agent 的 Prompt，降低 AI 检测分数

**步骤:**
1. 分析 AI 检测工具的检测逻辑
2. 优化写作 Prompt（增加人味要求）
3. 测试不同 Prompt 版本
4. 选择效果最好的版本

---

### Task 23: 端到端集成测试

**Objective:** 测试完整的任务生命周期

**测试场景:**
1. 创建任务 → 运行流水线 → 审核通过 → 发布
2. 创建任务 → 运行流水线 → 审核打回 → 重新运行
3. 并发运行多个任务

---

### Task 24: 性能测试

**Objective:** 测试流水线的执行时间和资源消耗

**测试指标:**
- 单任务执行时间（目标 < 30 分钟）
- 内存使用
- API 调用次数和成本

---

### Task 25: Phase 1 完成验收

**Objective:** 最终验收，确保达到 Phase 1 完成标准

**验收标准:**
- [ ] 对任意英文关键词，24小时内自动产出一篇文章
- [ ] AI检测分 < 30
- [ ] SEO分 > 75
- [ ] 宋徽宗审核界面可以通过/打回文章
- [ ] 所有测试通过
- [ ] 代码已提交

---

## 风险和注意事项

1. **LLM API 限流**: MiMo 和 Agnes AI 可能有调用频率限制，需要实现重试机制
2. **AI 检测工具**: Originality.ai 可能需要付费 API，考虑使用免费替代方案
3. **CrewAI 版本兼容**: CrewAI 0.80+ 有 API 变更，注意文档
4. **LangGraph 状态持久化**: 需要配置 checkpoint 存储（内存或数据库）

---

## 文件清单

### 新建文件
- `backend/models/content.py` - 数据模型
- `backend/agents/crews/keyword_researcher.py` - 李纲 Agent
- `backend/agents/crews/content_strategist.py` - 张择端 Agent
- `backend/agents/crews/content_writer.py` - 李清照 Agent
- `backend/agents/crews/qa_inspector.py` - 岳飞 Agent
- `backend/agents/crews/seo_optimizer.py` - 种师道 Agent
- `backend/agents/crews/link_builder.py` - 韩世忠 Agent
- `backend/agents/workflows/content_pipeline.py` - LangGraph 流水线
- `backend/services/llm_service.py` - LLM 服务
- `backend/templates/review.html` - 审核界面
- `tests/test_content_pipeline.py` - 测试

### 修改文件
- `backend/main.py` - 注册路由
- `backend/routers/content.py` - 实现接口
