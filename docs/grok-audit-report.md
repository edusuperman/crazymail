# CrazyMail / tempmails.top 全面流量审计报告

| 项目 | 内容 |
|------|------|
| **审计对象** | https://tempmails.top/（site-01） |
| **审计日期** | 2026-07-14 |
| **数据依据** | GSC 流量报告（2026-06-10 ~ 2026-07-08）、线上 HTML 实测、代码库、STRATEGY / KEYWORD_RESEARCH |
| **阶段对齐** | 阶段二「流量引擎」；验收目标：日均自然搜索 > 100 UV |
| **审计原则** | 只读分析，不修改任何源代码 |

---

## 执行摘要

**结论：流量极低的主因不是「文章写得不够多」，而是「可被搜索引擎抓到的有效页面极少 + 产品页 SSR 失效 + 品牌/语言混乱 + 零外链与几乎零曝光」。**

| 指标 | 现状 | 阶段二目标 | 差距 |
|------|------|------------|------|
| GSC 总点击（约 28 天） | **4** | 日均 100 UV ≈ 月 3000+ | 约 **750×** |
| GSC 总展示 | **25** | 至少数万级 | 几乎未进核心词 SERP |
| 平均排名 | **25.3** | 核心词 Top 10 | 仅边缘词有曝光 |
| 有流量的页面 | **仅首页 `/`** | 首页 + 博客集群 | 博客 0 点击 |
| 本地博客文章 | **50 篇** | 50+ | 数量已达标 |
| **线上可打开文章** | **约 6 篇** | 50+ | **部署/路由严重脱节** |

**一句话诊断：**  
代码仓库里已有约 50 篇博客，但生产环境只稳定渲染早期 6 篇；sitemap 却提交了 50+ URL。Google 抓取大量软 404，同时首页 HTML 正文是 `Loading...`。在这种地基上，继续量产文章对流量几乎无效。

---

## 1. 问题诊断（按优先级）

### P0 — 必须 48 小时内处理（阻塞全部 SEO）

| # | 问题 | 证据 | 影响 |
|---|------|------|------|
| **P0-1** | **生产博客大量软 404** | 实测 `/blog/how-to-create-temporary-email-guide`、`is-temporary-email-safe-guide`、`temporary-email-for-developers-guide`、`disposable-email-for-spam-protection-guide` 返回博客列表 + 文末 `Not Found`；title 仍是「Blog - TempMails.top」。早期 6 篇（如 `best-temporary-email-services-2026`、`6-billion-emails-leaked-2026`、`temp-email-chatgpt-claude-codex`）可打开。 | Google 抓取 sitemap 中 40+ URL → soft 404 → 站点信任度下降；内容工厂产出等于未上线 |
| **P0-2** | **Sitemap 与生产内容严重不一致** | 线上 `sitemap.xml` 含 **54** 个 `<loc>`（含约 50 篇博客），但多数文章不可用 | 浪费抓取预算；GSC 可能出现「已发现未编入索引 / 软 404 / 已抓取未编入索引」 |
| **P0-3** | **首页 SSR 正文几乎为空** | 抓取 HTML：`head` 有完整 meta/JSON-LD，但 `body` 仅旋转 Loading + 「Loading...」；Google 快照级爬虫同样如此 | 主流量入口无可见正文、无 H1 产品文案；Core Web Vitals / 首次内容绘制极差；依赖 JS 水合 + 邮箱 API |
| **P0-4** | **博客布局导致文章页 SEO 污染** | `blog.tsx` 在父路由渲染完整文章列表，子路由通过 `<Outlet />` 挂在列表下方。可打开的文章页同时出现：列表 H1「Blog」+ 文章 H1；**双 canonical**（`/blog` 与文章 URL） | 关键词稀释、重复 H1、canonical 冲突、页面主题不清晰 |

### P1 — 1～2 周内处理（决定能否排上核心词）

| # | 问题 | 证据 | 影响 |
|---|------|------|------|
| **P1-1** | **GSC 查询词与业务核心词完全错位** | 有点击/展示的词几乎全是 `tempmail premium`、`temp mail pro`、`ozsaip.com`；**没有** `temporary email` / `disposable email` / `temp mail` 等核心词 | 流量依赖品牌边缘词与邮箱域名本身，规模天花板极低 |
| **P1-2** | **语言与市场定位混乱** | 首页 title/description/FAQ JSON-LD 为**中文**；`html lang="en"`；hreflang 声明 en/zh/ja… 但实际是同一 URL + `?lang=`；博客全英文 | 英语大盘用户看到中文 snippet；中文用户又进英文博客；Google 难判定主语言 |
| **P1-3** | **品牌命名分裂** | 线上品牌「TempMail Pro」；域名 tempmails.top；config.yaml 仍是 tempmailpro.com；GSC 用户搜「temp mail pro/premium」 | 品牌无法沉淀；与已有竞品/App 名冲突风险 |
| **P1-4** | **内容关键词自相残杀** | 如 `temporary-email-online-privacy-guide` 与 `temporary-email-for-online-privacy`；`disposable-email-for-spam-protection-guide` 与 `disposable-email-spam-protection-guide` 主题高度重叠 | 互相抢排名，谁都难上首页 |
| **P1-5** | **文章页几乎无站内内链体系** | 多数文章仅「← Back to Blog」+ 指向首页的 CTA；无 Related Posts、无主题集群、无面包屑 Schema | 权重无法在内容间传递；新文章难被发现 |
| **P1-6** | **内容质量/可信度风险** | 大量文章正文含裸 Markdown 标题 `<p># Title</p>`；生产版对比文用「Alex Chen」第三方口吻自评第一（历史 GROK 报告已指出）；文中示例邮箱写成 `@tempmails.top`，而 GSC 实际出现的是 `ozsaip.com` 等真实域名 | E-E-A-T 弱；可能被判定为 AI 垃圾/误导内容 |
| **P1-7** | **ads.txt 线上 404** | `public/ads.txt` 本地存在，线上返回 404 HTML 页 | 阻断 AdSense/广告变现准备 |

### P2 — 2～6 周（增长放大器）

| # | 问题 | 证据 | 影响 |
|---|------|------|------|
| **P2-1** | **零反向链接、零目录、零社媒运营闭环** | 增长黑客工具有规格（`GROWTH_HACKER_SPEC.md`），但无可见执行结果；GSC 展示量仅 25 说明几乎无引用流量入口 | 新站无法突破「无外链 → 无排名 → 无流量」死循环 |
| **P2-2** | **域名与信任** | `.top` TLD；新站（约 2026-06 起有 GSC 数据）；无权威背书 | 同类词高竞争下信任分低 |
| **P2-3** | **功能页缺失或 404** | `/pricing`、`/api-docs` 线上 404；Footer 部分链到 `/coming-soon` | 转化路径与开发者 SEO 落地页缺失 |
| **P2-4** | **OG 图为 SVG** | `og-image.svg` 可访问，但部分社交平台对 SVG OG 支持差 | 分享卡片可能空白，影响 CTR |
| **P2-5** | **策略文档过时** | STRATEGY 写「13 篇」；仓库已 50 篇；线上约 6 篇 | 运营决策与真实状态脱节 |

### P3 — 中长期优化

| # | 问题 | 说明 |
|---|------|------|
| **P3-1** | 核心大词竞争极端 | `temporary email` / `temp mail` 被 temp-mail.org（约 4600 万月访）等垄断 |
| **P3-2** | 产品差异化未在 SERP 中体现 | 无广告、实时收信等卖点未转化为可排名的独立落地页 |
| **P3-3** | 矩阵扩张过早 | 当前单站未破流量瓶颈，扩站只会复制低流量模式 |

---

## 2. 分维度详细分析

### 2.1 技术 SEO

#### 已做好的部分（值得保留）

- `robots.txt` 允许爬取，声明 sitemap，禁止 `/api/`、`/admin/`
- 多数路由配置了 `title` / `description` / `og:*` / `canonical`
- 首页有 FAQPage + WebApplication JSON-LD
- 文章有 Article JSON-LD（headline、datePublished、publisher）
- Google Search Console 已验证（`google-site-verification` 存在）
- 部署在 Vercel，HTTPS + HSTS 正常

#### 严重缺陷

**A. 生产路由 / 部署脱节（最高危）**

| 环境 | 博客数量 | 文章可访问性 |
|------|----------|--------------|
| 本地 `src/routes/blog.*.tsx` | 50 | 源码完整 |
| 本地 `blog.tsx` 列表 | 50 | 完整 |
| 线上 sitemap | 54 URL | 声明完整 |
| 线上实际可打开 | **≈6 篇早期文章** | 其余 soft 404 |

这是当前流量为 0 的**最大技术根因**。Sitemap 在告诉 Google「这里有 50 篇干货」，Google 打开后得到列表页 + Not Found。

**B. 父路由布局错误**

```text
/blog/:slug 实际渲染结构：
  [Blog 列表页 H1 + 全部卡片]
  [Outlet → 文章正文]
```

正确结构应为：

```text
/blog          → 仅列表
/blog/:slug    → 仅文章（面包屑 + 正文 + 相关推荐）
```

当前导致：双 H1、双 canonical、正文权重被列表稀释。

**C. 首页可索引内容空洞**

`TempMailApp` 在 `mailbox === null` 时整页只渲染 Loading。邮箱创建依赖客户端 `useEffect` + API。SSR HTML 中：

- 有 meta / FAQ JSON-LD（好）
- **没有**可见产品 UI、没有 H1 正文段落（坏）

搜索引擎「能读到结构化数据」，但「读不到用户真正看到的产品页面」。

**D. 语言信号冲突**

| 信号 | 值 |
|------|-----|
| `<html lang>` | `en` |
| 首页 title/description/FAQ | 中文 |
| hreflang en | 指向 `/`（中文 meta） |
| hreflang zh | `/?lang=zh`（客户端切换，非独立页面） |
| 博客 | 英文 |

这不是真正的多语言 SEO，而是「单页 i18n 假装 hreflang」。

**E. 其他技术点**

| 项 | 状态 | 说明 |
|----|------|------|
| Meta robots | 基本 OK | index, follow |
| Canonical | 部分冲突 | 文章页双 canonical |
| Sitemap | 有害 | 含大量 soft 404 URL |
| 内链 | 弱 | 首页→Blog 有；文章间几乎无 |
| ads.txt | 线上失败 | 404 |
| OG image | 弱 | SVG，建议 1200×630 PNG/JPG |

### 2.2 内容质量

#### 数量与覆盖

- 仓库：约 **50** 篇（接近 AdSense/阶段二数量门槛）
- 主题覆盖：验证、隐私、学生、开发者、社媒、AI 工具、dating、法律、对比等，**选题面够广**
- KEYWORD_RESEARCH 中的 P0 长尾多数已有对应 slug

#### 质量问题

1. **模板化 AI 痕迹重**  
   - 开头套路：`Hey there` / `Let's be real` / `Here's the thing`  
   - 多篇几乎相同的「Step 1 打开网站 → Step 2 复制地址 → Step 3 去注册」  
   - 大量残留 `<p># Markdown 标题</p>`（内容工厂 Stage 部署时未剥离 MD 标记）

2. **事实准确性不一致**  
   - 文中写 `@tempmails.top` 邮箱示例  
   - GSC 实际查询出现 `ozsaip.com`  
   - 保留时长：有的写 10 分钟，有的写 24 小时 / 数小时 — 与产品 FAQ 不一致  

3. **E-E-A-T 风险**  
   - 生产早期对比文：虚构「Alex Chen」独立测评、自评 Top Pick（历史已标红）  
   - 较新文改为「TempMails Team」更诚实，但生产可能仍是旧版对比文  

4. **用户价值不足**  
   - 竞品强站提供：即时工具 + 清晰说明 + 多年域名信任 + App  
   - 当前文章多为「通用隐私说教 + 引导回首页」，缺少：  
     - 真实测试数据表格（送达率、被拦域名列表）  
     - 更新的「平台是否屏蔽 temp mail」实测  
     - 截图、流程图、视频  

5. **主题集群未建立**  
   应形成 pillar → cluster，例如：

   ```text
   Pillar: How temporary email works
     ├─ for verification
     ├─ for developers  
     ├─ is it legal / safe
     └─ vs permanent email
   ```

   现状：50 篇并列，互不相链 → 无法形成主题权威。

### 2.3 网站性能与移动端

| 维度 | 观察 | 风险 |
|------|------|------|
| 首页首屏 | SSR 输出 Loading，再等 API 创建邮箱 | LCP 差；移动弱网更明显 |
| JS 依赖 | TanStack Start + 大包 React 生态 | 工具站应极致轻量；竞品多为服务端直接出邮箱 |
| 移动适配 | viewport 正确；UI 用响应式 Tailwind | 框架层 OK，但 Loading 阻塞同样影响移动 |
| 博客页体积 | 父布局渲染全部列表卡片 + 长文 | 文章页无谓加载大量列表 DOM |
| 缓存 | Vercel `max-age=0, must-revalidate` | 每次 MISS 成本高；静态博客可 CDN 长缓存 |

**性能结论：**  
不是「需要再压 50KB CSS」的问题，而是 **首屏被 API 门闩锁死** + **博客布局错误加重 DOM**。对 SEO 与转化都是硬伤——用户搜 temp mail 的期望是「1 秒内看到可用邮箱」。

### 2.4 竞争对手对比

数据综合自项目 `KEYWORD_RESEARCH.md` 与公开行业信息（2026）：

| 维度 | temp-mail.org | Guerrilla Mail | 10MinuteMail 等 | **tempmails.top** |
|------|---------------|----------------|-----------------|-------------------|
| 月访问量级 | **~4600 万** | 高（老牌） | 百万～千万级 | **≈ 0～个位数/日** |
| 域名年龄/信任 | 高 | 极高（2006+） | 高 | 新 + `.top` |
| 核心词排名 | 垄断级 | 稳固 | 稳固 | 基本未进入 |
| 产品首屏 | 立即出邮箱 | 立即出邮箱 | 立即出邮箱 | **Loading → API** |
| 广告 | 重 | 重 | 有 | 宣称无广告（差异点） |
| 内容 SEO | 中等，靠品牌与外链 | 弱内容、强品牌 | 弱内容 | **有内容但未生效** |
| 多语言 | 强 | 中 | 中 | UI i18n 有，SEO 未落地 |
| 外链/目录 | 海量 | 海量 | 海量 | 几乎无 |

**可差异化切入点（竞品弱点）：**

1. **真正无广告、干净 UI**（多数巨头靠广告变现，体验差）  
2. **开发者向**：API 文档落地页、测试账号场景（需把 `/api-docs` 真正上线）  
3. **场景型长尾**：「ChatGPT 注册」「TikTok 验证」等实测文（已有选题，需保证线上可访问 + 持续更新实测）  
4. **诚实对比**（不装第三方），建立信任  

**不可硬刚：**

- 直接冲 `temporary email` 首页（需数年 + 外链 + 品牌）  
- 仅靠文章数量堆砌  

### 2.5 流量获取策略

| 渠道 | 当前状态 | 评价 |
|------|----------|------|
| **SEO / 内容** | 主战略；GSC 4 点击 | 方向对，**执行被技术事故卡死** |
| **GSC / 监控** | 有 traffic-report | 数据已说明问题，需按周复盘 |
| **社媒** | 有 growth_hacker 规格 | 未见稳定发布节奏与账号矩阵 |
| **目录站** | 规格中列出 Product Hunt / AlternativeTo 等 | 未见完成提交与收录 |
| **反向链接** | 无系统 BD | 新站最缺的资产 |
| **付费获客** | 未做 | 阶段二可暂缓；先修 SEO 地基 |
| **品牌词** | 「TempMail Pro」与域名不一致 | 品牌搜索无法积累 |

**GSC 数据解读（2026-06-10 ~ 07-08）：**

```text
总点击 4 | 展示 25 | CTR 16% | 均位 25.3
全部点击来自首页 /
有点击词：tempmail premium / temp mail premium / temp mail pro plus
有展示但无点击：@ozsaip.com 等（域名本身被搜，位次 7–9）
```

含义：

1. 用户不是通过「临时邮箱」需求词找到你，而是搜 **Pro/Premium 变体** 或 **具体邮箱域名**。  
2. 博客集群对 GSC **零贡献**（与线上大量 404 / 未部署一致）。  
3. `ozsaip.com` 位次 7–9 是少数「已有可见度」的资产，可做品牌/域名相关落地说明，但**不能当增长主引擎**。

---

## 3. 根本原因分析（Root Cause）

按因果链排序：

```text
① 生产部署与路由架构缺陷
   → 50 篇内容「写了但搜不到 / 打开是 Not Found」
   → Sitemap 毒化抓取
   → 博客 GSC 零流量

② 首页依赖客户端 API，SSR 只有 Loading
   → 核心落地页对爬虫/首屏不友好
   → 即使用户从边缘词进来，体验与竞品差距大

③ 语言/品牌/定位信号混乱
   → 无法在英语大盘或中文市场建立清晰实体
   → 排名与品牌词双输

④ 内容工厂「量优先」未配套「索引健康 + 内链 + 去重 + 事实校验」
   → 主题重复、MD 残留、E-E-A-T 风险
   → 即使全部上线，也难快速获得高质量排名

⑤ 零外链 / 零分发
   → 新站权威度 ≈ 0
   → 仅靠「发文章等收录」在 2026 年临时邮箱赛道不可行

⑥ 阶段目标与现实脱节
   → 以为「50 篇 = 流量」
   → 实际「可索引有效页 ≈ 1 首页 + 6 博客」且首页正文空洞
```

**一句话：**  
流量低不是市场没需求（竞品千万～千万级 UV），而是 **tempmails.top 尚未成为一个「可被稳定抓取、主题清晰、有权威外链的英文（或中文）工具站」**。

---

## 4. 具体修复建议（可执行步骤）

> 以下为建议动作清单；**本审计不改代码**。按「先止血、再增长」排序。

### 阶段 A：止血（第 1～3 天）— 预期解锁现有内容库存

| 步骤 | 动作 | 验收标准 |
|------|------|----------|
| A1 | **全量重新部署** site-01，确认 50 个 `blog.*` 路由进入生产 build | 随机抽 10 个 sitemap 中的博客 URL，全部 200 且正文含文章 H1（无 `Not Found`） |
| A2 | **修复 blog 父路由**：`/blog` 只渲染列表；`/blog/*` 使用 pathless layout 或独立布局，**禁止**文章页套完整列表 | 文章页仅 1 个 H1、1 个 canonical |
| A3 | **同步 sitemap**：仅包含真实 200 的 URL；部署后用脚本校验 | `sitemap URL 数 == 线上 200 数` |
| A4 | **GSC**：重新提交 sitemap；对软 404 URL 请求重新抓取 | GSC「网页索引」中软 404 下降 |
| A5 | **ads.txt** 确认 static 文件可访问 | `https://tempmails.top/ads.txt` 返回纯文本，非 404 HTML |

### 阶段 B：产品页 SEO 基建（第 3～7 天）

| 步骤 | 动作 | 验收标准 |
|------|------|----------|
| B1 | **首页 SSR 先出静态壳**：Header + H1（英文主市场）+ 功能说明 + FAQ 可见文本；邮箱控件可随后水合 | 无 JS 时 curl HTML 可见 H1 与 ≥300 词说明 |
| B2 | **统一主语言为英文**（建议：临时邮箱全球需求以 EN 为主） | title/description/FAQ JSON-LD/lang 一致为 en；中文作为二期 `/zh` 或子域 |
| B3 | **统一品牌名**：对外只用 **TempMails.top**（或彻底改用 TempMail Pro 并换域——二选一） | 页头、Footer、meta、邮件联系一致 |
| B4 | **修正 hreflang**：无独立翻译页则删除虚假 hreflang，只留 x-default | 无「伪多语言」信号 |
| B5 | OG 图改为 **1200×630 PNG/JPG** | 社交调试工具显示正常卡片 |

### 阶段 C：内容质量与结构（第 1～3 周）

| 步骤 | 动作 | 验收标准 |
|------|------|----------|
| C1 | **批量清洗**：去掉 `<p># ...</p>`；统一产品事实（域名、保留时长、能否发送） | 抽检 0 处 MD 残留；FAQ 与正文一致 |
| C2 | **合并重复主题**：隐私/反垃圾等重复文 301 到一篇权威文 | 每核心意图仅 1 个主 URL |
| C3 | **建立 3 个主题集群 + 内链** | 每文至少 3 条相关文内链 + 回链 pillar |
| C4 | **重写 5 篇「流量钩子」文**（优先）：`how-to-create-temporary-email`、`is-temporary-email-safe`、`is-temporary-email-legal`、`best-temporary-email-services-2026`、`temp-email-chatgpt-claude-codex` | 含真实步骤截图/数据表；对比文去掉虚假独立评测人设 |
| C5 | **首页与文章 CTA** 统一「Get free temp email」指向 `/#app` 或稳定锚点 | 从博客到工具转化路径清晰 |

### 阶段 D：分发与外链（与 C 并行，第 2～6 周）

| 步骤 | 动作 | 验收标准 |
|------|------|----------|
| D1 | 执行 growth_hacker：**每周 3 次** Reddit/隐私社区有价值回复（非硬广） | 可追踪 UTM 或可统计推荐流量 |
| D2 | 提交 **AlternativeTo、SaaSHub、相关 awesome-list、隐私工具目录** | 至少 5 个有效外链 |
| D3 | 开发者向：上线 `/api-docs`，投递到 API 目录 / Dev 社区 | 开发者关键词有展示 |
| D4 | 内容交换：与隐私/安全独立站换客座或工具列表收录 | 1～2 条 DR 中等外链 |
| D5 | **不要**买垃圾外链、不要 PBN | 避免整站惩罚 |

### 阶段 E：关键词与变现节奏（第 4～8 周）

| 步骤 | 动作 |
|------|------|
| E1 | 放弃短期冲击 `temporary email` 首页；主攻长尾：`temporary email for verification`、`disposable email for free trial`、`is temporary email legal`、`temp email for chatgpt` |
| E2 | 监控 GSC：每周导出；目标「博客页开始有展示」而非只看首页 |
| E3 | 索引健康稳定 + 有效内容 50+ 后再申请 AdSense（ads.txt 必须先好） |
| E4 | 联盟（VPN/密码管理器）可在隐私类文章底部试点，但需用户确认（属 AGENTS 需确认项） |

### 不建议做的事

- 在修复 soft 404 前继续狂产第 51～100 篇  
- 同时开第二个矩阵站「复制同一套」  
- 用中文首页硬吃英文搜索，或反过来不做选择  
- 继续「Alex Chen 独立测评自己」类内容  
- 为冲排名购买批量外链  

---

## 5. 预期效果估算

> 估算基于同类工具站冷启动经验 + 当前缺陷严重程度，**非承诺**。假设严格执行阶段 A～D。

### 5.1 分阶段流量预期（自然搜索为主）

| 时间点 | 前提 | 日均 UV（自然搜索） | GSC 日均点击（约） | 说明 |
|--------|------|---------------------|--------------------|------|
| 当前 | — | **≪ 1** | ~0.1 | 仅 4 次/月级 |
| **A 完成后 2～4 周** | 50 文真索引、sitemap 干净 | **5～20** | 5～15 | 长尾开始有展示；排名仍靠后 |
| **A+B+C 完成后 6～8 周** | 首页可抓取 + 5 篇钩子文强化 + 内链 | **30～80** | 30～70 | 接近阶段二目标下沿 |
| **A～D 完成后 3～4 月** | 有基础外链 + 稳定更新 | **100～300** | 100～250 | **可能达到阶段二日均 100 UV** |
| **6～12 月** | 持续内容 + 外链 + 产品口碑 | **500～3000+** | — | 仍远低于巨头；足够支撑 AdSense 试水 |

### 5.2 各修复项的贡献粗估

| 修复项 | 对 3 个月内流量的相对贡献 |
|--------|---------------------------|
| 修复生产 404 + sitemap（A） | **35～40%**（没有它其他都无效） |
| 首页 SSR 可见内容（B1） | **15～20%** |
| 语言/品牌统一（B2–B3） | **10%** |
| 钩子文重写 + 去重 + 内链（C） | **20～25%** |
| 外链与目录（D） | **15～20%** |
| 继续堆 50 篇新文（在 A 未完成时） | **~0%** |

### 5.3 收入侧（阶段二末～阶段三初）

| 条件 | 粗算 |
|------|------|
| 日均 100 UV，ARPU 极低（未开广告） | ≈ $0 |
| 日均 100 UV + AdSense（RPM $5～15，工具站波动大） | 月约 **$15～$45** |
| 日均 500 UV + 优化广告位 + 少量联盟 | 月约 **$100～$400** |
| 阶段二「月入 $500+」 | 通常需要 **更高 UV 或更高 RPM 联盟**，单靠 100 UV AdSense 不够 |

因此：**阶段二验收应坚持「先 100 UV」，变现目标放到流量起来之后**，与 STRATEGY 一致；但需承认 100 UV 只是门槛不是终点。

### 5.4 风险与置信度

| 风险 | 影响 |
|------|------|
| 生产长期不修 404 | 流量维持近零 |
| Google 对 AI 批量内容降权 | 即使上线，排名爬升慢 → 必须重写钩子文 |
| `.top` + 新域 | 外链成本更高 |
| 邮箱域名进黑名单 | 产品可用性下降 → 跳出率升 → SEO 二次伤害 |

**本报告置信度：**  
- 技术问题（404、Loading、双 canonical）：**高**（线上 HTML 实测）  
- 流量预测区间：**中**（依赖执行力度与算法波动）  
- 竞品月活数字：**中**（来自公开/历史研究，可能有浮动）

---

## 6. 90 天行动路线图（摘要）

```text
Week 1     止血：部署全量文章、修 blog 布局、修 sitemap、ads.txt、GSC 重提交
Week 2     首页 SSR 壳 + 语言/品牌统一 + OG 图
Week 3–4   清洗 50 文 + 合并重复 + 内链集群 + 重写 5 钩子文
Week 5–8   外链/目录/社媒节奏；上线 api-docs；每周 GSC 复盘
Week 9–12  按展示数据加码有效长尾；准备 AdSense 材料
```

**每周唯一北极星指标：**  
`GSC 有效点击` + `有展示的页面数（Page 维度）`  
**否决指标：**  
sitemap 中 404/软 404 比例、首页无 JS 是否仍只有 Loading。

---

## 7. 审计证据附录

### 7.1 GSC 摘要（docs/traffic-report-2026-07-11.md）

- 周期：2026-06-10 ~ 2026-07-08  
- Clicks: 4｜Impressions: 25｜CTR: 16%｜Position: 25.3  
- 唯一有点击页面：`/`  
- Top queries：tempmail premium、temp mail premium、temp mail pro plus、ozsaip.com 相关  

### 7.2 线上抽检（2026-07-14）

| URL | 结果 |
|-----|------|
| `/` | 200；meta 中文完整；body = Loading... |
| `/blog` | 200；仅约 6 篇文章卡片（与本地 50 不一致） |
| `/blog/best-temporary-email-services-2026` | 200；有正文；同时渲染列表；双 canonical |
| `/blog/how-to-create-temporary-email-guide` | 软 404（列表 + Not Found） |
| `/blog/is-temporary-email-safe-guide` | 软 404 |
| `/blog/temporary-email-for-developers-guide` | 软 404 |
| `/blog/temp-email-chatgpt-claude-codex` | 200 |
| `/sitemap.xml` | 54 URLs |
| `/robots.txt` | 正常 |
| `/ads.txt` | **404** |
| `/pricing`、`/api-docs` | **404** |

### 7.3 代码库关键路径

| 路径 | 用途 |
|------|------|
| `sites/site-01/frontend/src/routes/__root.tsx` | 全局 meta / lang |
| `sites/site-01/frontend/src/routes/index.tsx` | 首页 SEO（中文） |
| `sites/site-01/frontend/src/routes/blog.tsx` | 博客列表 + Outlet（布局问题） |
| `sites/site-01/frontend/src/routes/blog.*.tsx` | 50 篇文章 |
| `sites/site-01/frontend/src/components/tempmail/TempMailApp.tsx` | Loading 门闩（!mailbox） |
| `sites/site-01/frontend/public/sitemap.xml` | 站点地图 |
| `sites/site-01/frontend/public/robots.txt` | 爬虫规则 |
| `sites/site-01/config.yaml` | 仍写 tempmailpro.com |
| `docs/traffic-report-2026-07-11.md` | GSC 数据 |
| `docs/KEYWORD_RESEARCH.md` | 关键词与竞品 |

---

## 8. 最终结论

1. **tempmails.top 流量低，首先是技术与发布事故，其次才是内容与外链。**  
2. 内容工厂已接近数量目标，但 **生产环境未让 Google 与用户真正读到这些文章**。  
3. 首页作为唯一有点击的页面，却以 **Loading...** 作为 SSR 正文，严重不符合「临时邮箱」类查询的即时满足预期。  
4. 修好 A（可索引）+ B（可理解）后，再谈 C（内容质量）和 D（外链），才有机会在 3 个月内逼近阶段二「日均 100 UV」。  
5. **在地基修复完成前，继续扩写文章或开新站，投入产出比接近于零。**

---

*报告生成：Grok 审计｜CrazyMail 阶段二｜仅文档输出，未修改任何源代码。*
)
