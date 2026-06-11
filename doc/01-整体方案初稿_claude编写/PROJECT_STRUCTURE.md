# CrazyMail 完整项目目录结构
# AI IDE 按此结构初始化项目，不得随意创建目录

```
crazymail/
│
├── .cursorrules                    ← Cursor AI IDE 规则（从 crazymail_docs/ 复制）
├── .windsurfrules                  ← Windsurf AI IDE 规则（同上）
├── .env.example                    ← 环境变量模板（不含真实密钥）
├── .env                            ← 真实密钥（git忽略）
├── .gitignore
├── docker-compose.yml              ← 本地开发基础设施
├── pyproject.toml                  ← Python 项目配置（uv管理）
├── README.md
│
├── backend/                        ← Python FastAPI 后端
│   ├── main.py                     ← FastAPI 应用入口
│   ├── config.py                   ← 全局配置（从环境变量读取）
│   │
│   ├── routers/                    ← API 路由（每个模块一个文件）
│   │   ├── __init__.py
│   │   ├── content.py              ← /api/v1/content
│   │   ├── sites.py                ← /api/v1/sites
│   │   ├── personas.py             ← /api/v1/personas
│   │   ├── security.py             ← /api/v1/security（皇城司）
│   │   ├── gold_medal.py           ← /api/v1/gold-medal
│   │   └── dashboard.py            ← /api/v1/dashboard
│   │
│   ├── agents/                     ← AI Agent 定义
│   │   ├── __init__.py
│   │   ├── crews/                  ← CrewAI Agent YAML 配置
│   │   │   ├── ligang_researcher.yaml
│   │   │   ├── zhangzeduan_outliner.yaml
│   │   │   ├── zhoubangyan_writer.yaml
│   │   │   ├── liqingzhao_writer.yaml
│   │   │   ├── yuefei_qa.yaml
│   │   │   ├── zhongshidao_seo.yaml
│   │   │   └── hanshizhong_links.yaml
│   │   │
│   │   ├── workflows/              ← LangGraph Workflow 定义
│   │   │   ├── content_pipeline.py ← 7阶段内容流水线
│   │   │   ├── qa_workflow.py      ← 质检子流程
│   │   │   └── persona_action.py   ← 好汉操作流程
│   │   │
│   │   └── tools/                  ← Agent 使用的工具
│   │       ├── keyword_tools.py    ← 关键词研究工具
│   │       ├── serp_tools.py       ← SERP 抓取工具
│   │       ├── qa_tools.py         ← 质检 API 工具
│   │       └── seo_tools.py        ← SEO 分析工具
│   │
│   ├── personas/                   ← 人格档案存储
│   │   ├── officials/              ← 编制内官员（YAML格式）
│   │   │   ├── songhuizong.yaml
│   │   │   ├── ligang.yaml
│   │   │   └── ...
│   │   └── heroes/                 ← 108好汉（每人一个子目录）
│   │       ├── wusong_026/
│   │       │   ├── soul.json
│   │       │   ├── SOUL.md
│   │       │   ├── IDENTITY.md
│   │       │   ├── STYLE.md
│   │       │   ├── MEMORY.md
│   │       │   ├── HEARTBEAT.md
│   │       │   ├── HISTORY.md
│   │       │   ├── GROWTH.md
│   │       │   └── examples/
│   │       └── ...（其余好汉同结构）
│   │
│   ├── models/                     ← Pydantic 数据模型
│   │   ├── content.py
│   │   ├── site.py
│   │   ├── persona.py
│   │   └── security.py
│   │
│   ├── services/                   ← 业务逻辑层
│   │   ├── content_service.py
│   │   ├── persona_service.py
│   │   ├── behavior_engine.py      ← 行为节律引擎
│   │   ├── isolation_checker.py    ← 皇城司扫描器
│   │   ├── proxy_manager.py        ← 代理池管理
│   │   └── gold_medal_service.py
│   │
│   ├── core/                       ← 基础设施
│   │   ├── database.py             ← PostgreSQL 连接
│   │   ├── redis_client.py         ← Redis 连接
│   │   ├── ws_manager.py           ← WebSocket 管理
│   │   └── security.py             ← 认证/授权
│   │
│   └── tests/
│       ├── test_content_pipeline.py
│       ├── test_qa.py
│       └── test_personas.py
│
├── frontend/                       ← Next.js 15 前端
│   ├── src/
│   │   ├── app/                    ← App Router 页面
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx            ← 主 Dashboard（清明上河图）
│   │   │   ├── sites/[id]/         ← 单个驿站详情
│   │   │   ├── heroes/             ← 108好汉管理
│   │   │   └── security/           ← 皇城司控制台
│   │   │
│   │   ├── components/
│   │   │   ├── ui/                 ← Shadcn/ui 组件
│   │   │   ├── dashboard/          ← Dashboard 专用组件
│   │   │   ├── pipeline/           ← 流水线组件
│   │   │   └── personas/           ← 人格管理组件
│   │   │
│   │   ├── pixi/                   ← PixiJS 场景（最重要）
│   │   │   ├── MainScene.ts        ← 主场景（清明上河图）
│   │   │   ├── PigeonSystem.ts     ← 飞鸽系统
│   │   │   ├── CharacterSprites.ts ← 官员/好汉动画
│   │   │   ├── GoldMedalEffect.ts  ← 金牌特效
│   │   │   └── assets/             ← 国风 SVG 素材
│   │   │
│   │   ├── flows/                  ← React Flow 图表
│   │   │   ├── ContentPipelineFlow.tsx
│   │   │   └── SiteOverviewFlow.tsx
│   │   │
│   │   └── lib/
│   │       ├── ws-client.ts        ← WebSocket 客户端
│   │       ├── api-client.ts       ← API 请求封装
│   │       └── store.ts            ← Zustand 状态管理
│   │
│   ├── public/
│   │   └── assets/                 ← 静态资源
│   ├── package.json
│   └── tsconfig.json
│
├── infra/                          ← 基础设施配置
│   ├── docker-compose.yml          ← 本地 PostgreSQL + Redis
│   ├── docker-compose.prod.yml     ← 生产环境
│   └── nginx/
│       └── nginx.conf
│
├── scripts/                        ← 运维脚本
│   ├── init_db.py                  ← 数据库初始化
│   ├── seed_personas.py            ← 初始化108好汉人格
│   ├── daily_isolation_check.py    ← 每日隔离扫描
│   └── backup.sh                   ← 数据备份
│
├── docs/
│   └── manual/                     ← 人工兜底操作手册（底座）
│       ├── content_template/       ← 人工内容模板（Google Docs格式）
│       ├── qa_checklist.md         ← 人工质检清单
│       └── MANUAL_RECOVERY.md      ← 系统恢复手册
│
└── crazymail_docs/                 ← 本目录：AI IDE 上下文文档
    ├── .cursorrules
    ├── .windsurfrules
    ├── README.md
    ├── ARCHITECTURE.md
    ├── TECH_STACK.md
    ├── DATABASE_SCHEMA.md
    ├── API_DESIGN.md
    ├── PROJECT_STRUCTURE.md（本文件）
    ├── HARDWARE_REQUIREMENTS.md
    ├── DEVELOPMENT_ROADMAP.md
    ├── modules/
    │   ├── CONTENT_FACTORY.md
    │   ├── SECURITY_ISOLATION.md
    │   ├── PERSONA_SYSTEM.md
    │   ├── VISUALIZATION.md
    │   └── GOLD_MEDAL.md
    └── personas/
        └── PERSONA_TEMPLATE.md
```
