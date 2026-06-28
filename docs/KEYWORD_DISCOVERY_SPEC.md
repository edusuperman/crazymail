# 关键词自动发现工具技术规格
# 版本：v1.0 | 2026-06-23

## 目标

创建 `tools/keyword_discovery.py` — 自动发现和评估关键词，为内容工厂供词。

## 功能

```
种子关键词 → [扩展] → [评分] → [去重] → [输出]
```

### Stage 1: 关键词扩展

输入：种子关键词列表
输出：扩展后的关键词列表（含变体）

扩展方式（用 MiMo LLM）：
- 问题型：how to X, what is X, is X safe, can I use X for Y
- 比较型：X vs Y, X alternative, best X for Y
- 长尾型：X for [use case], X without [limitation]
- 场景型：X for [platform], X for [year]

### Stage 2: 关键词评分

对每个关键词评估：
- 搜索意图（informational / transactional / navigational）
- 竞争度估算（low / medium / high）
- 内容类型匹配（blog / FAQ / landing page）
- 与 tempmails.top 的相关性（1-10）

### Stage 3: 去重和排序

- 与已有文章关键词去重（读取 docs/KEYWORD_RESEARCH.md 和已有文章标题）
- 按综合得分排序
- 输出 Top N 推荐

## 输出格式

JSON 文件：`docs/keyword-discovery-{date}.json`

```json
{
  "generated_at": "2026-06-23T12:00:00",
  "seed_keywords": ["temporary email", "disposable email"],
  "total_discovered": 45,
  "keywords": [
    {
      "keyword": "is temporary email safe",
      "type": "question",
      "intent": "informational",
      "competition": "low",
      "relevance": 8,
      "content_type": "blog",
      "suggested_title": "Is Temporary Email Safe? What You Need to Know",
      "already_covered": false
    }
  ]
}
```

## CLI 接口

```bash
# 用种子关键词发现
python tools/keyword_discovery.py "temporary email" "disposable email"

# 指定输出数量
python tools/keyword_discovery.py -k "temp mail" -n 30

# 与内容工厂联动
python tools/keyword_discovery.py "temporary email" --feed-factory
```

## 与内容工厂联动

`--feed-factory` 参数：
1. 运行关键词发现
2. 取 Top 5 未覆盖的关键词
3. 依次调用 content_factory.py 生成文章

## API 配置

与 content_factory.py 相同：
- 从 ~/.config/opencode/opencode.json 读取 Key
- base_url: https://api.xiaomimimo.com/v1
- model: mimo-v2.5-pro
- 使用 openai SDK

## 已有关键词（去重用）

读取以下文件获取已有关键词：
- docs/KEYWORD_RESEARCH.md — 手动研究的关键词
- sites/site-01/frontend/src/routes/blog.*.tsx — 已有文章的标题
- docs/outline-*.json — 已生成的大纲

## 参考文件

- docs/KEYWORD_RESEARCH.md — 已有关键词研究
- docs/CONTENT_FACTORY_SPEC.md — 内容工厂规格
- tools/content_factory.py — 内容工厂脚本（参考API调用方式）

## 禁止

- 不要修改 .env
- 不要硬编码 API Key
- 不要修改 content_factory.py
