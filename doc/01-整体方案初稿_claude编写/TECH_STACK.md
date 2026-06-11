# CrazyMail 技术栈版本清单（2026年6月定稿）

## 原则：稳定优先，不追最新 RC/Beta

---

## 后端（Python 生态）

| 组件 | 版本 | 用途 | 安装命令 |
|------|------|------|---------|
| Python | **3.12.4** | 运行环境 | pyenv install 3.12.4 |
| uv | **0.4.x** | 包管理器（替代pip/poetry） | curl -LsSf https://astral.sh/uv/install.sh \| sh |
| FastAPI | **0.115.5** | API 网关 | uv add fastapi |
| Uvicorn | **0.32.0** | ASGI 服务器 | uv add "uvicorn[standard]" |
| Pydantic | **2.9.x** | 数据校验 | uv add pydantic |
| CrewAI | **0.80.0** | Agent 角色层 | uv add crewai |
| LangGraph | **0.2.55** | Agent 状态层 | uv add langgraph |
| LangChain | **0.3.x** | LLM 集成基础 | uv add langchain |
| Anthropic SDK | **0.40.x** | Claude API | uv add anthropic |
| DeepSeek SDK | **latest** | DeepSeek API | uv add openai（兼容接口）|
| Ollama Python | **0.3.x** | 本地 LLM | uv add ollama |
| SQLAlchemy | **2.0.x** | ORM | uv add sqlalchemy |
| Alembic | **1.14.x** | DB 迁移 | uv add alembic |
| asyncpg | **0.30.x** | PostgreSQL 异步驱动 | uv add asyncpg |
| redis-py | **5.2.x** | Redis 客户端 | uv add "redis[hiredis]" |
| Celery | **5.4.x** | 任务队列 | uv add celery |
| httpx | **0.28.x** | HTTP 客户端（async） | uv add httpx |
| playwright | **1.48.x** | 浏览器自动化 | uv add playwright |
| supabase-py | **2.9.x** | Supabase 客户端 | uv add supabase |
| python-dotenv | **1.0.x** | 环境变量 | uv add python-dotenv |
| loguru | **0.7.x** | 日志 | uv add loguru |
| pytest | **8.3.x** | 测试 | uv add --dev pytest |
| ruff | **0.7.x** | Lint + Format | uv add --dev ruff |

---

## 前端（Node.js 生态）

| 组件 | 版本 | 用途 | 安装 |
|------|------|------|------|
| Node.js | **22.11 LTS** | 运行环境 | nvm install 22 |
| pnpm | **9.x** | 包管理器（替代npm/yarn） | npm i -g pnpm |
| Next.js | **15.1.x** | 前端框架（App Router） | pnpm create next-app |
| TypeScript | **5.7.x** | 类型系统 | 随 Next.js 安装 |
| React | **19.x** | UI 库 | 随 Next.js 安装 |
| PixiJS | **8.6.x** | 2D 渲染引擎（飞鸽/场景） | pnpm add pixi.js |
| React Flow | **12.3.x** | 流程图（流水线可视化） | pnpm add @xyflow/react |
| Recharts | **2.13.x** | 数据图表 | pnpm add recharts |
| Konva.js | **9.3.x** | 2D 卡通动画补充 | pnpm add konva react-konva |
| Shadcn/ui | **latest** | UI 组件库 | npx shadcn@latest init |
| Tailwind CSS | **3.4.x** | 样式 | 随 Shadcn 安装 |
| Zustand | **5.0.x** | 前端状态管理 | pnpm add zustand |
| TanStack Query | **5.x** | 服务端数据获取 | pnpm add @tanstack/react-query |
| socket.io-client | **4.8.x** | WebSocket 客户端 | pnpm add socket.io-client |
| Framer Motion | **11.x** | 动效补充 | pnpm add framer-motion |
| Zod | **3.23.x** | 前端数据校验 | pnpm add zod |

---

## 基础设施

| 组件 | 版本 | 用途 |
|------|------|------|
| PostgreSQL | **16.4** | 主数据库（Supabase 托管）|
| Redis | **7.4.x** | 缓存 + 任务队列 + Pub/Sub |
| Docker | **27.x** | 容器化 |
| Docker Compose | **2.29.x** | 本地开发编排 |
| Nginx | **1.26.x** | 反向代理 |
| Supabase | **latest cloud** | PostgreSQL托管 + Auth + Storage |

---

## AI / LLM 服务

| 服务 | 用途 | 优先级 |
|------|------|--------|
| Claude 3.5/4 API | 内容写作主力 + 质检 | 最高 |
| DeepSeek V3 API | 关键词研究 + 大纲（低成本批量）| 高 |
| Grok API | SERP 分析 + 图像生成 | 中 |
| Ollama + Qwen2.5-7B | 本地离线运行 + 隐私敏感任务 | 备用 |
| Ollama + DeepSeek-R1-8B | 本地推理 | 备用 |

---

## 自动化 / 运营工具

| 工具 | 版本 | 用途 |
|------|------|------|
| Dolphin Anty | 最新版 | 指纹浏览器（108好汉专用）|
| GoLogin | 最新版 | 指纹浏览器（备用）|
| Bright Data / Oxylabs | 最新版 | 住宅代理池 |
| n8n | **1.x self-hosted** | 可选可视化工作流 |
| Google Search Console API | v1 | 流量监控 |

---

## 开发工具（推荐AI IDE）

| 工具 | 版本 | 推荐理由 |
|------|------|---------|
| **Cursor** | 最新版（v0.44+）| .cursorrules 生态最成熟，Agent 控制粒度最高 |
| **Windsurf** | 最新版 | Cascade 自动上下文，多IDE支持 |
| 说明 | - | .cursorrules 与 .windsurfrules 格式兼容，两者均可直接使用本项目配置 |

---

## 版本兼容性注意事项

1. **CrewAI 0.80+** 引入了新的 Flow API，与旧版 API 有破坏性变更，务必锁定版本
2. **LangGraph 0.2.x** 的 StateGraph API 稳定，但 0.3.x（预期Q3 2026发布）可能有变更，暂不升级
3. **Next.js 15** 的 App Router 与 Pages Router 不混用，本项目全部使用 App Router
4. **React 19** 需要注意 Concurrent Features 的使用，PixiJS 集成需要注意 StrictMode 双调用问题
5. **Python 3.12** 已移除部分旧 API，不向下兼容 3.10
