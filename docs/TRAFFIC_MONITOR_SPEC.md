# 流量监控工具技术规格
# 版本：v1.0 | 2026-06-23

## 目标

创建 `tools/traffic_monitor.py` — 自动化 GSC 数据分析，输出可操作的洞察。

## 功能概览

```
GSC API → [拉取数据] → [分析趋势] → [发现问题] → [输出报告]
```

## 两种模式

### 模式1：API 模式（推荐）

需要 Google OAuth2 认证。首次使用需要用户授权。

### 模式2：CSV 导入模式（备选）

用户从 GSC 手动导出 CSV，脚本分析。

## 核心功能

### 1. 搜索表现分析

- 总点击数、总展示数、平均CTR、平均排名
- 按日期的趋势（最近7天/28天/3个月）
- Top 10 表现最好的查询词
- Top 10 表现最好的页面
- 高展示低CTR的查询词（优化机会）

### 2. 索引状态检查

- 已索引页面数
- 未索引页面及原因
- 站点地图提交状态

### 3. 机会发现

- 排名 5-20 的关键词（有提升空间）
- CTR 低于平均值的页面（需要优化 title/description）
- 新出现的查询词（最近才有排名的）

### 4. 报告输出

JSON 报告：`docs/traffic-report-{date}.json`
Markdown 摘要：`docs/traffic-report-{date}.md`

## GSC API 配置

### 前置条件

1. Google Cloud 项目已启用 Search Console API
2. OAuth2 客户端凭据已下载
3. 用户已授权访问 tempmails.top 的 GSC 数据

### API 端点

```
POST https://www.googleapis.com/webmasters/v3/sites/https%3A%2F%2Ftempmails.top%2F/searchAnalytics/query
```

请求体：
```json
{
  "startDate": "2026-06-01",
  "endDate": "2026-06-23",
  "dimensions": ["query", "page"],
  "rowLimit": 100,
  "startRow": 0
}
```

### 认证方式

使用 Google 客户端库：
```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('tools/gsc_credentials.json')
service = build('searchconsole', 'v1', credentials=creds)
```

### 凭据文件

- 位置：`tools/gsc_credentials.json`（已在 .gitignore 中）
- 首次授权：运行脚本时如果无凭据，输出授权 URL 让用户操作
- Token 刷新：自动处理

## CLI 接口

```bash
# API 模式（默认）
python tools/traffic_monitor.py

# CSV 导入模式
python tools/traffic_monitor.py --csv path/to/gsc_export.csv

# 指定时间范围
python tools/traffic_monitor.py --days 28

# 只看机会发现
python tools/traffic_monitor.py --opportunities
```

## 输出格式

### JSON 报告

```json
{
  "generated_at": "2026-06-23T12:00:00",
  "site": "https://tempmails.top/",
  "period": "2026-06-01 to 2026-06-23",
  "summary": {
    "total_clicks": 150,
    "total_impressions": 5000,
    "avg_ctr": 0.03,
    "avg_position": 12.5
  },
  "top_queries": [...],
  "top_pages": [...],
  "opportunities": {
    "low_ctr_high_impressions": [...],
    "ranking_5_to_20": [...],
    "new_queries": [...]
  },
  "indexing": {
    "submitted": 10,
    "indexed": 8,
    "not_indexed": [...]
  }
}
```

### Markdown 摘要

```markdown
# 流量监控报告 - 2026-06-23

## 概览
- 总点击: 150
- 总展示: 5,000
- 平均CTR: 3.0%
- 平均排名: 12.5

## Top 查询词
| 查询词 | 点击 | 展示 | CTR | 排名 |
|--------|------|------|-----|------|

## 优化机会
### 高展示低CTR（优化 title/description）
### 排名5-20的关键词（有提升空间）
```

## 参考文件

- tools/content_factory.py — API 调用模式参考
- docs/KEYWORD_RESEARCH.md — 已有关键词

## 禁止

- 不要修改 .env
- 不要硬编码凭据
- 不要修改其他文件
