# Dashboard MVP 技术规格（Streamlit版）
# 版本：v1.0 | 2026-06-24

## 目标

创建 `dashboard/app.py` — Streamlit 国风 Dashboard MVP。
这是原型验证版本，后续会升级为 Next.js 正式版。

## 核心原则

- 纯展示层，不触发任何真实操作
- 国风大宋驿站风格（配色：墨黑/朱红/帝金/玉绿/宣纸色）
- 对接已有 tools/*.py 产出的数据
- 使用模拟数据补充尚未对接的部分

## 页面结构

### 侧边栏（驿政司）
- 项目标题：疯邮 · 大宋宣和驿站
- 页面导航：总览 / 内容工厂 / 关键词 / 流量 / 增长

### 页面1：总览（宣和总驿大厅）
- 今日摘要卡片：文章总数 / 关键词数 / 质检通过率 / 站点数
- 最近文章列表（读取 docs/outline-*.json 和 docs/qc-*.json）
- 系统状态：各工具运行状态

### 页面2：内容工厂（编制内7阶段）
- 流水线示意图（用 st.graphviz_chart 或纯文字流程图）
- 最近生产的文章列表（读取 docs/ 目录下的大纲和质检文件）
- 质检通过率统计
- 运行内容工厂的按钮（调用 tools/content_factory.py）

### 页面3：关键词发现（李纲研究室）
- 读取 docs/keyword-discovery-*.json
- 展示发现的关键词列表（含评分）
- 新发现 vs 已覆盖的比例
- 运行关键词发现的按钮

### 页面4：流量监控（飞鸽状态）
- GSC 凭据状态检查
- 如果有凭据：展示 GSC 数据
- 如果无凭据：展示模拟数据 + 提示用户配置
- 核心指标卡片：点击数 / 展示数 / CTR / 平均排名

### 页面5：增长黑客（108好汉推广厅）
- 读取 docs/growth-content-*/ 目录
- 展示已生成的社媒内容列表
- 内容日历展示
- 目录站提交状态

## 配色方案（国风）

```python
COLORS = {
    "ink_black": "#1a1a1a",
    "vermillion": "#c0392b",
    "imperial_gold": "#d4a017",
    "jade_green": "#2e7d5e",
    "parchment": "#f5f0e8",
    "ink_blue": "#2c4a6e",
    "warning_amber": "#e67e22",
    "ash_gray": "#bdc3c7",
}
```

页面背景用 parchment（宣纸色），标题用 ink_black，强调用 vermillion，正常状态用 jade_green。

## 数据来源

| 数据 | 来源 | 说明 |
|------|------|------|
| 文章列表 | docs/outline-*.json | 大纲文件 |
| 质检结果 | docs/qc-*.json | 质检报告 |
| 关键词 | docs/keyword-discovery-*.json | 关键词发现结果 |
| 增长内容 | docs/growth-content-*/ | 增长黑客生成的内容 |
| 流量数据 | GSC API 或模拟数据 | 需要凭据 |
| 站点信息 | 硬编码（目前只有1个站） | 后续扩展 |

## 文件结构

```
dashboard/
├── app.py              # 主应用
├── pages/
│   ├── overview.py     # 总览页
│   ├── content.py      # 内容工厂页
│   ├── keywords.py     # 关键词页
│   ├── traffic.py      # 流量监控页
│   └── growth.py       # 增长黑客页
├── utils/
│   ├── data_loader.py  # 数据读取工具
│   └── styles.py       # 国风样式定义
└── README.md           # 使用说明
```

## CLI

```bash
# 启动
streamlit run dashboard/app.py --server.port 8501

# 后台启动
streamlit run dashboard/app.py --server.port 8501 --server.headless true
```

## 依赖

- streamlit（已安装）
- pandas（已安装）
- json（标准库）
- pathlib（标准库）

## 参考文件

- tools/content_factory.py — 内容工厂
- tools/keyword_discovery.py — 关键词发现
- tools/traffic_monitor.py — 流量监控
- tools/growth_hacker.py — 增长黑客
- doc/01-整体方案初稿_claude编写/modules/VISUALIZATION.md — 国风可视化设计
- doc/00-头脑风暴/【20260624】.../CrazyMail_Character_Matrix.md.md — 人物矩阵

## 禁止

- 不要修改 .env
- 不要修改 tools/*.py
- 不要修改其他文件
- 不要自动执行任何操作（纯展示）
