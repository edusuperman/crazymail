# 内容工厂 MVP 技术规格
# 版本：v1.0 | 2026-06-23
# 此文件供 OpenCode 执行时参考

## ════════════════════════════════════════════
## 目标
## ════════════════════════════════════════════

创建 `tools/content_factory.py` — 轻量级内容生产流水线脚本。

功能：关键词 → 大纲 → 初稿 → 人味润色 → 质检 → 输出 TanStack 路由文件

## ════════════════════════════════════════════
## MiMo API 配置（已从官方文档验证）
## ════════════════════════════════════════════

参考文档：https://platform.xiaomimimo.com/docs/en-US/quick-start/first-api-call

### API 调用方式

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("MIMO_API_KEY"),
    base_url="https://api.xiaomimimo.com/v1"
)

completion = client.chat.completions.create(
    model="mimo-v2.5-pro",
    messages=[
        {"role": "system", "content": "系统提示"},
        {"role": "user", "content": "用户提示"}
    ],
    max_completion_tokens=4096,
    temperature=0.7,
    top_p=0.95,
    stream=False
)
```

### 关键配置

| 项目 | 值 |
|------|-----|
| BASE_URL | `https://api.xiaomimimo.com/v1` |
| Key格式 | `sk-xxxxx`（按量付费） |
| 模型名 | `mimo-v2.5-pro` |
| Header | `api-key: $KEY`（不是 Authorization: Bearer） |
| 参数名 | `max_completion_tokens`（不是 max_tokens） |

### API Key 获取

Key 存储在 OpenCode 配置文件中：
- 路径：`~/.config/opencode/opencode.json`
- 字段：`provider.mimo.options.apiKey`
- 格式：`sk-xxxxx`

**注意**：脚本应从 OpenCode 配置文件读取 Key，不要求用户单独配置。

### 使用 openai SDK

项目已有 `openai` 包（或通过 `uv add openai` 安装）。
使用 SDK 而非 urllib.request，更可靠。

## ════════════════════════════════════════════
## 流水线设计（5个阶段）
## ════════════════════════════════════════════

```
Stage 1: 关键词 → 大纲 (JSON)
Stage 2: 大纲 → 初稿 (Markdown)
Stage 3: 初稿 → 人味润色 (Markdown)
Stage 4: 润色稿 → 质检报告 (JSON)
Stage 5: 润色稿 → TanStack 路由文件 (.tsx)
```

### Stage 1: 关键词 → 大纲

输入：关键词字符串
输出：JSON 大纲文件

```json
{
  "title": "文章标题（含关键词，50-60字符）",
  "subtitle": "副标题",
  "slug": "url-friendly-slug",
  "category": "Guide|Data|Privacy|Industry|AI Tools|Social Media",
  "primary_keyword": "主关键词",
  "secondary_keywords": ["kw2", "kw3"],
  "meta_description": "SEO描述（150-160字符）",
  "sections": [
    {
      "heading": "H2标题",
      "key_points": ["要点1", "要点2"],
      "data_needed": "需要的数据或证据"
    }
  ],
  "faq": [
    {"q": "问题", "a": "简短回答"}
  ],
  "cta": "行动号召文案"
}
```

### Stage 2: 大纲 → 初稿

系统提示要求：
- 像朋友聊天一样自然
- 分享第一手测试经验
- 偶尔用口语化表达（"Look," / "Here's the thing"）
- 段落3-5句话，不超过100字
- 每篇至少1处个人观点
- 禁止使用：Furthermore, Moreover, In conclusion, It's important to note
- 使用列表和表格
- 身份：TempMails Team（tempmails.top 的建设者）
- 诚实态度：可以推荐自己的产品，但要标明是自己的

### Stage 3: 人味润色

润色规则：
- 去掉所有AI味表达
- 增加口头禅
- 变化转折词
- 增加第一手经验感
- 保持结构和信息不变

### Stage 4: 质检

检查项：
1. 字数：1200-3500
2. AI味词：0个（Furthermore, Moreover, In conclusion 等）
3. 人味表达：≥2个（here's the thing, honestly, i've tested 等）
4. H2标题：≥3个
5. 内部链接：≥1个（tempmails.top 或 /）
6. 关键词出现：≥3次

### Stage 5: 输出 TanStack 路由文件

模板参考现有文章结构（如 `blog.6-billion-emails-leaked-2026.tsx`）：

```tsx
import { createFileRoute, Link } from "@tanstack/react-router";

export const Route = createFileRoute("/blog/{slug}")({
  head: () => ({
    meta: [
      { title: "{title} - TempMails.top" },
      { name: "description", content: "{meta_desc}" },
      { name: "keywords", content: "{keywords}" },
      { name: "author", content: "TempMails Team" },
      { name: "robots", content: "index, follow" },
      { property: "og:type", content: "article" },
      { property: "og:title", content: "{title}" },
      { property: "og:description", content: "{meta_desc}" },
      { property: "og:url", content: "https://tempmails.top/blog/{slug}" },
    ],
    links: [
      { rel: "canonical", href: "https://tempmails.top/blog/{slug}" },
    ],
    scripts: [
      {
        type: "application/ld+json",
        children: JSON.stringify({
          "@context": "https://schema.org",
          "@type": "Article",
          "headline": "{title}",
          "description": "{meta_desc}",
          "author": { "@type": "Organization", "name": "TempMails Team" },
          "datePublished": "{today}",
          "dateModified": "{today}",
          "publisher": { "@type": "Organization", "name": "TempMails.top" },
        }),
      },
    ],
  }),
  component: BlogPostPage,
});

function BlogPostPage() {
  return (
    <article className="mx-auto max-w-3xl px-4 py-16">
      <Link to="/blog" className="...">← Back to Blog</Link>
      <header>...</header>
      <div className="prose prose-gray prose-lg max-w-none">
        {/* 正文 */}
        {/* CTA */}
        {/* Author Bio: TempMails Team */}
      </div>
    </article>
  );
}
```

正文 Markdown → JSX 转换规则：
- `## H2` → `<h2 className="mt-12 text-2xl font-bold">`
- `### H3` → `<h3 className="mt-8 text-xl font-semibold">`
- `- 列表` → `<ul className="my-4 space-y-1"><li>`
- 表格 → `<div className="my-6 overflow-x-auto"><table className="w-full border-collapse text-sm">`
- `**粗体**` → `<strong>`
- `[链接](url)` → `<a href="url" className="text-primary underline">`

## ════════════════════════════════════════════
## CLI 接口
## ════════════════════════════════════════════

```bash
# 基本用法
python tools/content_factory.py "temporary email for verification"

# 指定语言
python tools/content_factory.py -k "temp mail privacy" --lang zh

# 帮助
python tools/content_factory.py --help
```

## ════════════════════════════════════════════
## 输出文件
## ════════════════════════════════════════════

每次运行产出：
1. `docs/outline-{slug}.json` — 大纲
2. `docs/draft-{slug}.md` — 初稿
3. `docs/humanized-{slug}.md` — 润色稿
4. `docs/qc-{slug}.json` — 质检报告
5. `sites/site-01/frontend/src/routes/blog.{slug}.tsx` — 路由文件
6. 自动更新 `blog.tsx` 的文章列表

## ════════════════════════════════════════════
## 测试用例
## ════════════════════════════════════════════

完成开发后，用以下关键词测试全流程：

```
python tools/content_factory.py "temporary email for verification"
```

验证：
1. 5个阶段全部运行成功，无报错
2. 生成的 .tsx 文件语法正确（可用 `node --check` 或构建验证）
3. 质检报告为 PASS
4. blog.tsx 已更新

## ════════════════════════════════════════════
## 禁止事项
## ════════════════════════════════════════════

- 不要修改 .env 文件
- 不要硬编码 API Key
- 不要使用 `Authorization: Bearer` header（用 openai SDK 自动处理）
- 不要使用 `max_tokens` 参数（用 `max_completion_tokens`）
- 不要使用 `tp-` 开头的 URL（那是 Token Plan，我们用按量付费 `sk-`）
