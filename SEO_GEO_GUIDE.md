# CrazyMail SEO/GEO 技术规范
# 版本：1.0 | 2026-06-11
# 基于 2026 年最新 SEO/GEO 最佳实践

## ════════════════════════════════════════════
## 什么是 GEO？
## ════════════════════════════════════════════

GEO（Generative Engine Optimization）= 生成式引擎优化

目标：让 AI 系统（ChatGPT、Perplexity、Claude、Google AI Mode）
在回答用户问题时，引用或推荐你的品牌/内容。

**关键数据（2026）：**
- ChatGPT 周活跃用户 9 亿+
- LLM 流量预计 2027 年超过传统 Google 搜索
- Google AI Overviews 覆盖 ~16% 的搜索查询
- 近 1/3 美国消费者用 AI 工具完成购物相关任务

## ════════════════════════════════════════════
## SEO + GEO 协同策略
## ════════════════════════════════════════════

**传统 SEO → 进化后的 SEO/GEO：**

| 维度 | 传统 SEO | 2026 SEO/GEO |
|------|---------|--------------|
| 目标 | Google 排名 | 多平台可见性（Search + AI + 社交） |
| 内容 | 关键词导向 | 意图+实体导向，语义结构化 |
| 链接 | 传递 PageRank 的外链 | 外链 + 品牌提及 + 共同引用 |
| KPI | 流量 | 可见性、影响力、转化率 |
| 技术 | 基础技术 SEO | 技术 SEO + JavaScript 兼容性 |

## ════════════════════════════════════════════
## 7 步 GEO 行动计划（适用于 CrazyMail）
## ════════════════════════════════════════════

### Step 1: 打好 SEO 基础（技术层面）

**每个页面必须做到：**
- ✅ SSR（服务端渲染）— AI 爬虫对 JavaScript 页面支持差
- ✅ 可爬取、可索引（robots.txt 允许）
- ✅ 快速加载、移动端友好
- ✅ HTTPS
- ✅ 语义化 HTML（h1, h2, article, nav, section）

### Step 2: 建立信任信号（E-E-A-T）

**AI 系统更倾向引用可信来源：**
- Experience（经验）：展示真实使用案例
- Expertise（专业）：深度技术内容
- Authority（权威）：数据引用、来源说明
- Trust（信任）：隐私政策、联系方式、关于页面

**具体做法：**
- 添加"关于我们"页面（团队介绍、专业背景）
- 文章中引用权威数据源
- 添加作者署名和简介
- 展示用户评价/案例

### Step 3: 建立品牌提及和共同引用

**AI 系统看重品牌在整个网络的存在感：**
- 外链仍然重要，但品牌提及和共同引用同样关键
- 共同引用 = 你的品牌与竞品/行业关键词同时出现

**具体做法：**
- 在 Reddit、LinkedIn、YouTube 建立品牌存在
- 在行业文章中被提及（与竞品并列）
- 在技术论坛中提供有价值的内容

### Step 4: 多平台布局

**AI 平台引用最多的内容来源：**
- Reddit（极高权重）
- LinkedIn（专业内容）
- YouTube（视频教程/评测）
- 播客（文字稿也会被索引）

**CrazyMail 多平台策略：**
- Reddit：在 r/privacy、r/onlinetools 等子版块提供价值
- LinkedIn：发布隐私保护相关的专业内容
- YouTube：制作临时邮箱使用教程
- 博客：深度指南和比较文章

### Step 5: 回答用户问题（意图导向）

**AI 搜索更偏向对话式和问题导向：**

**内容策略：**
- 从"关键词"转向"意图"
- 优化更长、更具体的对话式查询
- 创建 FAQ 格式内容
- 直接回答问题（简洁、权威）

**CrazyMail 内容示例：**
- "What is a temporary email and why should I use one?"
- "How to protect your privacy when signing up for services"
- "Best temporary email services in 2026 (comparison)"
- "Is it safe to use temp email for banking?"

### Step 6: 结构化数据（Schema.org）

**每个页面必须包含 JSON-LD 结构化数据：**

```json
{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "CrazyMail",
  "description": "Free temporary email service for privacy protection",
  "url": "https://crazymail.com",
  "applicationCategory": "UtilitiesApplication",
  "operatingSystem": "Web"
}
```

**推荐的 Schema 类型：**
- WebApplication（首页）
- Article（博客文章）
- FAQPage（FAQ 页面）
- HowTo（教程）
- BreadcrumbList（面包屑导航）

### Step 7: 监测 AI 可见性

**定期测试：**
- 在 ChatGPT/Perplexity 中搜索相关问题
- 检查是否被引用
- 分析竞品的 AI 可见性
- 追踪 LLM 来源流量

## ════════════════════════════════════════════
## 页面级 SEO/GEO 检查清单
## ════════════════════════════════════════════

每个页面上线前必须通过：

**技术层面：**
- [ ] SSR 正常工作
- [ ] Meta title（50-60 字符，含关键词）
- [ ] Meta description（150-160 字符，含关键词）
- [ ] OG tags（og:title, og:description, og:image）
- [ ] JSON-LD 结构化数据
- [ ] 干净的 URL（/blog/best-temp-email，不是 ?id=123）
- [ ] 图片 alt 文本
- [ ] 内部链接
- [ ] 移动端响应式
- [ ] Core Web Vitals 达标

**内容层面：**
- [ ] 直接回答用户问题
- [ ] 包含权威数据/来源
- [ ] E-E-A-T 信号（作者、来源、经验）
- [ ] FAQ 格式内容（如适用）
- [ ] 语义化 HTML 结构

## ════════════════════════════════════════════
## 技术实现要求
## ════════════════════════════════════════════

**Next.js SSR 配置：**
```typescript
// 每个页面必须使用 SSR
export const dynamic = 'force-dynamic'

// 或使用 generateMetadata 动态生成 meta tags
export async function generateMetadata() {
  return {
    title: '...',
    description: '...',
    openGraph: { ... },
  }
}
```

**JSON-LD 组件：**
```typescript
// frontend/src/components/JsonLd.tsx
export function JsonLd({ data }: { data: object }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  )
}
```

**Sitemap 生成：**
```typescript
// frontend/src/app/sitemap.ts
export default function sitemap() {
  return [
    { url: 'https://crazymail.com', lastModified: new Date() },
    { url: 'https://crazymail.com/blog/best-temp-email', lastModified: new Date() },
    // ...
  ]
}
```
