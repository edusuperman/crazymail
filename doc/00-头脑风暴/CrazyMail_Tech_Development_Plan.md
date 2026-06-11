# CrazyMail（疯邮）技术开发详细方案

## 1. 项目技术架构总览

**整体架构**：前后端分离 + Agentic Workflow 可控系统 + 国风可视化 Dashboard

- **前端**：国风卡通 Dashboard (Web)
- **后端**：Python-based Agent Orchestration
- **数据层**：本地/云端混合存储
- **部署**：免费/低成本优先

**核心原则回顾**（简要）：
- 前端强分离（20站）
- AI辅助 + 人工把关
- 纯展示层卡通角色
- 增长黑客子模块特殊处理

## 2. 技术栈详细清单（2026年推荐版本）

### 前端技术栈
- **框架**：Next.js 15 (App Router) + TypeScript
- **UI组件**：Shadcn/ui + Tailwind CSS
- **可视化**：
  - PixiJS 8.x 或 Three.js r168 (轻3D飞鸽 + 驿站场景)
  - React Flow (LangGraph流程图)
  - Recharts / Chart.js (收入、流量图)
  - Konva.js (2D卡通动画)
- **国风资源**：Grok Imagine / Midjourney 生成SVG/PNG卡通资产
- **部署**：Vercel / Cloudflare Pages (免费)

### 后端 / Agent 技术栈
- **主要框架**：CrewAI 0.51+ + LangGraph 0.2+
- **LLM**：Claude 3.5/4 (主力) + Grok + DeepSeek (本地Ollama)
- **本地运行**：Ollama 0.3+ + SEO Intel
- **Workflow编排**：n8n (可选可视化) 或纯LangGraph
- **数据**：SQLite + JSON 文件存储 (低成本)

### 其他工具
- 指纹浏览器：GoLogin / Incogniton (免费版)
- 代理：住宅代理池 (低成本)
- 监控：Google Search Console API + AdSense API

## 3. 业务板块与矩阵

### 主业务板块（模块化）

1. **内容工厂模块** (编制内核心)
   - 对应7阶段流水线
   - 人物：宋徽宗、李纲、周邦彦、李清照、岳飞等 (一对多：一个名人可负责多个阶段)

2. **站点管理模块**
   - 20个独立站点
   - 每个站点一对一或一对多驿丞 (编制内名人)

3. **增长黑客模块** (编外特殊)
   - 108好汉全球分舵
   - 一对多：一个好汉可视化代表多个虚拟身份

4. **监控与风险模块**
   - 风险雷达、飞鸽状态

**矩阵关系**：
- **编制内**：业务板块与历史名人 → 多对多（一个名人可跨多个站点/阶段）
- **编外**：108好汉 → 主要服务增长黑客模块，一对多（一个好汉代表多个推广身份）
- **隔离要求**：站点内容生产隔离（不同niche），推广身份严格4-5集群隔离

## 4. 人物矩阵详细设计

**编制内（朝廷官员组）**：
- 核心7人（可复用）
  - 总管：宋徽宗
  - 研究/大纲：李纲、张择端
  - 写作：周邦彦、李清照
  - 质检：岳飞
  - 优化/链接：韩世忠、种师道

**编外（108好汉）**：
- 仅用于增长黑客可视化
- 分组：按地区/平台分组展示

**关系**：
- 编制内：混合使用（一人多岗）
- 编外：纯展示，一对多

## 5. 详细技术实现路径

### Phase 1: MVP Dashboard (Week 1-2)
- 使用 Streamlit 1.38+ 快速原型国风界面 + PixiJS 集成飞鸽动画

### Phase 2: Agent Workflow
- CrewAI 定义角色 + LangGraph 实现7阶段有条件流转 + 人工节点

### Phase 3: 国风资产集成
- 生成SVG飞鸽动画 + 108好汉卡通图

### Phase 4: 部署与安全
- Vercel + Cloudflare Tunnel (本地服务暴露)

## 6. 软件版本与来源推荐

- Next.js: 官网 latest
- Ollama: ollama.com
- CrewAI: pip install crewai
- PixiJS: pixijs.com
- GoLogin: gologin.app (免费阶梯)

**注意**：所有工具优先开源/免费版本，严格合规。

---

这个文件是技术开发的超详细部分。如果你需要再拆分成更多文件（如单独的《人物矩阵.md》、《前端实现.md》等），告诉我，我立刻继续生成。 

文件已保存：**CrazyMail_Tech_Development_Plan.md**