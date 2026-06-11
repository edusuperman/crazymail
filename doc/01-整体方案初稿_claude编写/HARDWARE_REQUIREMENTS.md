# CrazyMail 软硬件配置要求

## 运行场景说明

本系统分为三种运行场景，硬件要求差异较大：
- **A. 开发机（本地）**：你的主力工作机，运行 AI IDE、本地 LLM、指纹浏览器
- **B. 生产服务器（云端）**：运行 FastAPI 后端、任务队列、数据库
- **C. 可选本地服务器**：专用于跑大模型（如你有闲置机器）

---

## A. 开发机配置（你的本地机器）

### 最低配置（能跑，但吃力）
| 配件 | 规格 | 说明 |
|------|------|------|
| CPU | Intel Core i7-12700 / AMD Ryzen 7 5800X（8核16线程）| AI IDE + 多任务并发最低要求 |
| 内存 | **32GB DDR4 3200MHz** | 指纹浏览器每个Profile约200-400MB |
| 显卡 | NVIDIA RTX 3060 **12GB** | 运行 Ollama Qwen2.5-7B 本地模型 |
| 固态 | 500GB NVMe SSD（主系统）+ 1TB HDD（数据）| SSD 存代码和模型，HDD 存浏览器Profile |
| 网络 | 100Mbps 对称带宽 | 108好汉并发代理请求需要足够带宽 |
| 操作系统 | Windows 10/11（你当前）或 Ubuntu 22.04 | 两者均可，Linux 运行 Python 更稳定 |

### 推荐配置（流畅运行）
| 配件 | 规格 | 说明 |
|------|------|------|
| CPU | Intel Core i9-13900K / AMD Ryzen 9 7900X（12-16核）| 多 Agent 并行 + 指纹浏览器不卡顿 |
| 内存 | **64GB DDR5 4800MHz** | 同时开 20+ 指纹浏览器Profile |
| 显卡 | NVIDIA RTX 4070 Ti **16GB** | 可跑 Ollama 13B 模型，速度可接受 |
| 固态 | 2TB NVMe SSD（主力）| 模型文件大（7B约4GB，13B约8GB）|
| 网络 | 500Mbps+ 对称带宽 | 推荐有线连接，稳定优先 |

### 旗舰配置（不差钱，一步到位）
| 配件 | 规格 | 说明 |
|------|------|------|
| CPU | AMD Ryzen 9 7950X / Intel Core i9-14900KS（16核）| |
| 内存 | **128GB DDR5** | 未来扩展空间充足 |
| 显卡 | NVIDIA RTX 4090 **24GB** | 可跑 Ollama 34B 模型，媲美 GPT-3.5 |
| 固态 | 4TB NVMe SSD | |
| 第二块显卡 | RTX 3090 24GB（可选）| 双卡运行 70B 量化模型 |

> ⚠️ **Windows 10 特别注意**：
> - Ollama 在 Windows 上运行需要 WSL2 或直接 Windows 原生（0.5版已支持）
> - Dolphin Anty / GoLogin 在 Windows 10 上可正常运行
> - Docker Desktop 需要 WSL2，内存占用额外约 2-4GB

---

## B. 云端生产服务器

### 最低配置（初期省钱方案）
使用 **Hetzner Cloud**（欧洲，性价比最高）或 **DigitalOcean**：

| 服务 | 规格 | 月费用 |
|------|------|--------|
| FastAPI 后端 | 2 vCPU / 4GB RAM（Hetzner CX22）| ~€4/月 |
| PostgreSQL | Supabase 免费层（500MB存储）| 免费 |
| Redis | Upstash 免费层（10K命令/天）| 免费 |
| 前端 | Vercel 免费层 | 免费 |
| **合计** | | **约 $5-10/月** |

> 适用阶段：Phase 1，1-3个站点验证期

### 推荐配置（规模化阶段）
| 服务 | 规格 | 月费用 |
|------|------|--------|
| FastAPI 后端 | 4 vCPU / 8GB RAM（Hetzner CX32）| ~€11/月 |
| 任务队列（Celery Worker）| 2 vCPU / 4GB RAM | ~€4/月 |
| PostgreSQL | Supabase Pro（8GB存储）| $25/月 |
| Redis | Upstash Pro | $10/月 |
| 前端 | Vercel Pro | $20/月 |
| CDN/流量 | Cloudflare（免费层足够）| 免费 |
| **合计** | | **约 $70/月** |

> 适用阶段：Phase 2-3，10-20个站点运营中

### 各站点托管成本（20个站点）
| 方案 | 说明 | 单站成本 |
|------|------|---------|
| Cloudflare Pages | 静态/SSG 站点，无服务器 | 免费（每月100GB流量）|
| Hostinger VPS | WordPress/动态站 | ~$4/月/站 |
| Vercel（备用）| Next.js 前端站点 | 免费基础版 |

---

## C. 关键软件版本速查表

### 必装软件（开发机）

| 软件 | 版本 | 下载地址 |
|------|------|---------|
| Git | 2.47+ | git-scm.com |
| Python | **3.12.4** | python.org 或 pyenv |
| uv（包管理）| **0.4.x** | astral.sh/uv |
| Node.js | **22.11 LTS** | nodejs.org 或 nvm |
| pnpm | **9.x** | pnpm.io |
| Docker Desktop | **27.x** | docker.com |
| Ollama | **0.5.x** | ollama.com |
| Dolphin Anty | 最新版 | dolphin.ru.com |
| Cursor | 最新版（v0.44+）| cursor.com |
| Windsurf | 最新版 | windsurf.ai |
| VS Code | 1.95+（备用）| code.visualstudio.com |

### Ollama 本地模型推荐

| 模型 | 大小 | 显存要求 | 适用任务 |
|------|------|---------|---------|
| qwen2.5:7b | 4.7GB | 8GB VRAM | 日常任务、关键词研究 |
| qwen2.5:14b | 9.0GB | 12GB VRAM | 内容写作辅助 |
| deepseek-r1:8b | 5.2GB | 8GB VRAM | 推理、质检逻辑 |
| llama3.1:8b | 4.7GB | 8GB VRAM | 英文内容写作 |

```bash
# 安装推荐模型
ollama pull qwen2.5:7b
ollama pull deepseek-r1:8b
ollama pull llama3.1:8b
```

---

## D. 网络带宽估算

| 场景 | 峰值带宽需求 | 说明 |
|------|------------|------|
| 20站点 + API调用 | 20 Mbps | Claude/DeepSeek API 调用并发 |
| 108好汉代理操作 | 50 Mbps | 通过住宅代理的并发请求 |
| 本地 Ollama | 本地不耗带宽 | 纯本机 GPU 计算 |
| 指纹浏览器（10个并发）| 30 Mbps | 每个浏览器会话约3Mbps |
| **推荐宽带** | **100Mbps 对称** | 家庭宽带基本满足，建议有线 |

---

## E. 开发工具选型建议

### Cursor vs Windsurf（2026年6月现状）

基于最新评测：

| 维度 | Cursor | Windsurf |
|------|--------|---------|
| 规则文件系统 | .cursorrules（生态最成熟）| .windsurfrules（格式相同）|
| Agent 控制粒度 | 高（每步确认）| 低（自动执行）|
| 上下文管理 | 手动选文件 | 自动 RAG 分析整库 |
| 价格 | $20/月 Pro | $20/月 Pro |
| 适合本项目 | ✅ 推荐（大项目，需精细控制）| ✅ 可选（自动上下文省心）|

**推荐**：主力用 **Cursor**（.cursorrules 生态 + 精细控制），
同步维护 .windsurfrules（两文件格式相同，复制一份即可）。

> 本项目的 .cursorrules 和 .windsurfrules 文件已在 `crazymail_docs/` 目录中生成，
> 将其复制到项目根目录即可生效。

---

## F. 费用汇总估算

### 初期月费（Phase 1，验证期）

| 项目 | 费用 |
|------|------|
| 云服务器（Hetzner）| ~$10 |
| Claude API（内容生产）| ~$30-50 |
| DeepSeek API（批量研究）| ~$5-10 |
| Supabase（免费层）| $0 |
| 住宅代理（最小量）| ~$30 |
| 域名（2-3个）| ~$10 |
| **Phase 1 月合计** | **~$85-110/月** |

### 规模化月费（Phase 3，20站点全运转）

| 项目 | 费用 |
|------|------|
| 云服务器（多台）| ~$70 |
| Claude API | ~$150-300 |
| DeepSeek API | ~$30-50 |
| Supabase Pro | $25 |
| Redis Pro | $10 |
| 住宅代理（108好汉规模）| ~$200-400 |
| Dolphin Anty Pro | ~$50 |
| 各站点托管（20站）| ~$80 |
| **Phase 3 月合计** | **~$615-985/月** |

> 对应 Phase 3 的目标月收益 $10,000+，成本约占 10%，ROI 可观。
