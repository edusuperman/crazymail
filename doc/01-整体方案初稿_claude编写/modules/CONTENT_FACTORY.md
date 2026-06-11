# 内容工厂模块设计（编制内7阶段流水线）

## 角色映射

| 官员 | 负责阶段 | CrewAI Role | 主要工具 |
|------|---------|-------------|---------|
| 李纲 | Stage 1: 关键词研究 | Keyword Researcher | Ahrefs API / Semrush API / GSC API |
| 张择端 | Stage 2: SERP分析+大纲 | Content Strategist | Firecrawl / Jina Reader |
| 周邦彦 / 李清照 | Stage 3: 内容写作（并行）| Content Writer | Claude API / DeepSeek API |
| 岳飞 | Stage 4: 9重质检 | QA Inspector | Originality.ai / Surfer SEO API |
| 种师道 | Stage 5: SEO优化 | SEO Optimizer | NeuronWriter API / Schema工具 |
| 韩世忠 | Stage 6: 链接建设策划 | Link Builder | Ahrefs / 自建链接数据库 |
| 宋徽宗 | Stage 7: 最终审核 | 人工节点（你）| Dashboard 审核界面 |

---

## LangGraph Workflow 详细设计

```python
# backend/agents/workflows/content_pipeline.py

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver

class ContentPipelineState(TypedDict):
    task_id: str
    keyword: str
    site_id: str
    stage: int
    research_data: dict
    serp_analysis: dict
    outline: dict
    draft: str
    qa_report: dict
    seo_optimized: str
    link_suggestions: list
    human_approved: Optional[bool]
    error_count: int
    max_retries: int  # 默认 3

# 节点定义
workflow = StateGraph(ContentPipelineState)
workflow.add_node("research",      ligang_research_node)
workflow.add_node("outline",       zhangzeduan_outline_node)
workflow.add_node("write",         writing_node)          # 周邦彦或李清照
workflow.add_node("qa_check",      yufei_qa_node)
workflow.add_node("seo_optimize",  zhongshidao_seo_node)
workflow.add_node("link_strategy", hanshizhong_link_node)
workflow.add_node("human_review",  human_review_node)     # interrupt节点

# 条件边：质检失败→打回重写
workflow.add_conditional_edges(
    "qa_check",
    qa_router,
    {
        "pass": "seo_optimize",
        "retry": "write",          # 分数在阈值附近，重写
        "reject": END              # 低于底线，任务失败
    }
)
# 人工审核节点
workflow.add_node("human_review", human_review_node)
workflow.compile(
    checkpointer=PostgresSaver(conn),
    interrupt_before=["human_review"]  # 在此节点前暂停等待人工
)
```

---

## CrewAI Agent YAML 示例

```yaml
# backend/agents/crews/ligang_researcher.yaml
name: "李纲 - 关键词研究官"
role: "SEO Keyword Research Specialist"
goal: >
  对给定 niche 进行深度关键词研究，识别高价值长尾关键词机会，
  输出结构化的关键词报告，包含搜索量、难度、商业意图分析。
backstory: >
  李纲，北宋名臣，以精准识人、深谋远虑著称。
  在内容工厂中，他凭借敏锐洞察，总能在竞争激烈的关键词战场
  发现被忽视的机会——那些搜索量稳健、竞争度适中的黄金词汇。
tools:
  - ahrefs_api_tool
  - semrush_api_tool
  - google_trends_tool
  - keyword_clustering_tool
llm: "deepseek-v3"   # 批量研究用低成本模型
max_iter: 5
verbose: false
```

---

## 质检9重详细标准（岳飞）

```python
QA_THRESHOLDS = {
    "ai_detection_score": {"max": 30, "weight": 0.20},    # Originality.ai
    "seo_score":          {"min": 75, "weight": 0.20},    # Surfer SEO
    "eeat_score":         {"min": 80, "weight": 0.15},    # 自定义检查
    "human_score":        {"min": 70, "weight": 0.15},    # 人味评分
    "word_count":         {"min": 1500, "max": 4000, "weight": 0.05},
    "heading_structure":  {"min": 0.9, "weight": 0.05},   # H2/H3合规率
    "internal_links":     {"min": 2, "max": 5, "weight": 0.05},
    "image_alt_coverage": {"min": 1.0, "weight": 0.05},   # 100%覆盖
    "schema_complete":    {"min": 1.0, "weight": 0.10},   # Schema必须完整
}

# 分数计算
PASS_SCORE = 85   # 自动发布
REVIEW_SCORE = 65 # 进入宋徽宗审核队列
FAIL_SCORE = 65   # 低于此分，打回重写（最多3次）
```

---

## 去AI味 + 加人味策略（写作阶段注入）

每位虚拟作者有独立的"人味配方"，通过 STYLE.md 注入到写作 Prompt：

```
人味注入维度：
1. 口头禅：每位作者有 2-3 个标志性表达（从 SOUL.md 加载）
2. 轻微错误：偶尔用 em dash——代替逗号，偶尔首字母不大写
3. 个人观点：每篇必须有 1-2 处 "In my testing..." / "I've found that..."
4. 数字随机化："3 ways" vs "three ways" 随机选择
5. 段落节奏变化：偶尔出现单句段落
6. 转折词多样性：不重复使用 "however" / "furthermore"
7. 第一手经验声明：提及亲身测试/使用经历
```

---

## 作者 Bio 系统

每个站点有 2-3 个虚拟作者，配备：
- 作者专属页面（/author/xxx）
- LinkedIn 个人主页（真实账号运营）
- 头像（AI生成但经过处理）
- 专业背景描述（与 Niche 相关）
- Person Schema JSON-LD
