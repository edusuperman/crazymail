# 增长黑客工具技术规格
# 版本：v1.0 | 2026-06-23

## 目标

创建 `tools/growth_hacker.py` — 为各平台生成推广内容，辅助手动发布。

## 设计思路

不依赖任何社交平台API（审批复杂、易失效）。
而是：输入文章/关键词 → 生成多平台内容 → 用户手动发布。

## 功能

### 1. 文章改写为社交帖子

输入：博客文章URL或Markdown文件
输出：多平台格式的帖子

支持平台：
- **Reddit** — 适合 r/privacy, r/cybersecurity, r/privacytoolsIO
  - 标题：问题型或数据型，不带推销语气
  - 正文：分享经验/数据，末尾自然提到工具
  - 避免：直接广告、重复发帖

- **Hacker News** — 技术向
  - 标题：简洁、数据驱动
  - Show HN 格式：展示产品，说明技术细节

- **Twitter/X** — 短文本+线程
  - 推文：280字符内的hook
  - 线程：5-8条推文展开话题

- **LinkedIn** — 专业向
  - 长文格式，带专业洞察

### 2. 目录站提交模板

为以下站点生成提交内容：
- Product Hunt（需要真实发布）
- AlternativeTo
- SaaSHub
- ToolFinder
- 各类临时邮箱目录站

### 3. 外链机会发现

基于关键词搜索潜在外链机会：
- "best temporary email" 相关博客评论
- "temp mail" 相关论坛帖子
- 竞品的外链来源

### 4. 内容日历

生成未来2周的推广计划：
- 每天1-2个推广动作
- 平台轮换
- 内容类型轮换（帖子/评论/目录提交）

## CLI 接口

```bash
# 从博客文章生成多平台内容
python tools/growth_hacker.py --article "temporary email for verification"

# 从关键词生成内容
python tools/growth_hacker.py --keyword "is temporary email safe"

# 生成目录站提交模板
python tools/growth_hacker.py --directories

# 生成内容日历
python tools/growth_hacker.py --calendar 14

# 生成所有
python tools/growth_hacker.py --all
```

## 输出

文件：`docs/growth-content-{date}/`
```
docs/growth-content-20260623/
  reddit-post.md
  hackernews-post.md
  twitter-thread.md
  linkedin-post.md
  directory-submissions.md
  content-calendar.md
```

## API 配置

与 content_factory.py 相同：
- 从 ~/.config/opencode/opencode.json 读取 Key
- base_url: https://api.xiaomimimo.com/v1
- model: mimo-v2.5-pro
- 使用 openai SDK

## 参考文件

- tools/content_factory.py — API 调用参考
- docs/KEYWORD_RESEARCH.md — 关键词
- sites/site-01/frontend/src/routes/blog.*.tsx — 已有文章

## 禁止

- 不要修改 .env
- 不要硬编码 API Key
- 不要修改其他文件
- 不要自动发布到任何平台（只生成内容）
