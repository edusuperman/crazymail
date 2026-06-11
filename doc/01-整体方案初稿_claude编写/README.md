# CrazyMail（疯邮）项目总览

> 以北宋朝廷为视觉隐喻的 AI 驱动 SEO 内容矩阵自动化系统

---

## 项目定位

CrazyMail 是一套**多站点 Niche 内容生产 + 社媒增长推广**的全自动化运营平台：

- **内容侧**：20个独立 Niche 站点，每站运行完整7阶段 AI 流水线，目标产出 E-E-A-T 合规内容
- **推广侧**：108位真实授权人员的社媒账号矩阵，SoulSpec 标准人格系统，模拟独立人格行为
- **变现侧**：联盟营销（隐私/VPN/开发者工具高CPC品类）+ 数字产品
- **可视化**：动态清明上河图风格 Dashboard，实时展现整套系统运转状态

## 核心特点

| 特点 | 说明 |
|------|------|
| 插座架构 | FastAPI Router 模块化，任意模块可插拔，可退化到人工操作 |
| 双轨 AI | CrewAI 角色层（谁做）+ LangGraph 状态层（怎么流） |
| 人格成长 | SoulSpec 标准，108好汉人格随交互自动积累成长 |
| 安全隔离 | 皇城司七层隔离体系，物理/网络/身份/浏览器/行为/内容/资金 |
| 人工兜底 | 十二道金牌分级熔断，任意模块可随时切换人工模式 |
| 国风可视化 | PixiJS 清明上河图场景，飞鸽传书实时动效 |

## 目录结构

```
crazymail/
├── backend/                    # Python 后端
│   ├── main.py                 # FastAPI 入口
│   ├── routers/                # 模块化 Router（插座）
│   │   ├── content.py          # 内容工厂
│   │   ├── sites.py            # 站点管理
│   │   ├── personas.py         # 人格系统
│   │   ├── security.py         # 皇城司
│   │   └── gold_medal.py       # 金牌熔断
│   ├── agents/
│   │   ├── crews/              # CrewAI Agent 定义（YAML）
│   │   └── workflows/          # LangGraph Workflow 定义
│   ├── personas/               # 108好汉 + 编制内人格文件
│   │   ├── officials/          # 编制内官员（YAML）
│   │   └── heroes/             # 108好汉（JSON + Markdown）
│   ├── models/                 # Pydantic 数据模型
│   ├── services/               # 业务服务层
│   └── core/                   # 配置、数据库、安全
├── frontend/                   # Next.js 15 前端
│   ├── src/
│   │   ├── app/                # App Router 页面
│   │   ├── components/         # React 组件
│   │   ├── pixi/               # PixiJS 场景
│   │   ├── flows/              # React Flow 图表
│   │   └── lib/                # 工具库（ws-client等）
├── infra/                      # 基础设施配置
│   ├── docker-compose.yml
│   ├── nginx/
│   └── supabase/
├── crazymail_docs/             # 本目录：项目文档（AI IDE 上下文）
└── scripts/                    # 运维脚本
```

## 快速开始

```bash
# 1. 克隆项目
git clone <repo> && cd crazymail

# 2. 安装依赖（使用 uv）
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Keys

# 4. 启动基础设施
docker-compose up -d postgres redis

# 5. 运行后端
uv run uvicorn backend.main:app --reload --port 8000

# 6. 运行前端
cd frontend && npm install && npm run dev
```

## 变现目标

第一阶段目标：2-3个站点，联盟营销月收入 $500+
第二阶段目标：10个站点，月收入 $3000+
第三阶段目标：20个站点 + 108好汉全运转，月收入 $10000+

---

详细设计文档见各模块 `crazymail_docs/modules/` 目录
