# 十二道金牌系统设计（分级熔断 + 人工接管协议）

## 历史典故

宋高宗绍兴十一年，岳飞正大举北伐、捷报频传之际，
宋高宗一日之内连发十二道金牌，强令岳飞班师。
金牌代表的是：**无可违抗的最高优先级覆盖指令**。

在 CrazyMail 中，十二道金牌是系统最后的防线——
从轻度告警到全面停机，保证在任何灾难场景下，
系统都能有序退出自动模式，转由人工接管。

---

## 十二道金牌定义

| 金牌 | 级别 | 自动触发条件 | 执行动作 | 通知方式 |
|------|------|------------|---------|---------|
| 第一道 | 🟡 轻度 | 某站点流量单日跌幅 > 30% | 暂停该站新内容推送 | Dashboard 黄色角标 |
| 第二道 | 🟡 轻度 | GSC出现手动处罚通知 | 暂停该站外链建设 | Dashboard + 邮件 |
| 第三道 | 🟡 轻度 | 某好汉账号被平台标记警告 | 隔离该好汉，暂停操作48h | Dashboard |
| 第四道 | 🟠 中度 | 质检系统连续失败 > 10次 | 暂停内容生产流水线 | Dashboard + 推送通知 |
| 第五道 | 🟠 中度 | AdSense账号收到违规警告 | 暂停相关站点广告投放 | 邮件 + 推送 |
| 第六道 | 🟠 中度 | 2个以上站点同日异常 | 启动皇城司全面关联扫描 | 推送通知 |
| 第七道 | 🔴 严重 | 主数据库连接失败 > 5min | 切换只读备份模式 | 推送 + 短信 |
| 第八道 | 🔴 严重 | API费用单日超出预算 200% | 熔断所有 LLM 调用 | 推送 + 短信 |
| 第九道 | 🔴 严重 | 检测到大规模爬虫抓取 | Cloudflare 防护升级至 Under Attack | 自动处理 |
| 第十道 | 🔴 严重 | 3个以上好汉账号同日被封 | 108好汉模块全线暂停 | 推送 + 短信 |
| 第十一道 | ⚫ 危急 | 核心域名收到法律通知 | 全站静默，仅保留静态镜像 | 电话告警（如配置）|
| 第十二道 | ⚫ 危急 | 宋徽宗手动触发 | 全系统停机，切换纯人工模式 | 全渠道告警 |

---

## 底座原则：每个模块的人工替代方案

当对应级别金牌触发时，以下人工替代方案立即激活：

```
自动化模块                    人工替代方案（底座）
────────────────────────────────────────────────────
7阶段AI内容流水线    →  Google Docs模板包（/docs/manual/content_template/）
质检自动化          →  人工质检Checklist（/docs/manual/qa_checklist.pdf）
关键词自动研究      →  Ahrefs/Semrush 手动查询指南
SEO优化自动化       →  人工优化SOP文档
108好汉自动发帖     →  Buffer/Hootsuite 手动排期
内链自动建设        →  Excel 内链矩阵管理表
监控自动报警        →  Google Alerts + 每日手动巡检清单
────────────────────────────────────────────────────
```

**底座演练要求**：每个模块每月至少执行一次「人工模式演练」，
确保在AI失效的情况下，能在 2 小时内完成人工接管。

---

## 代码实现骨架

```python
# backend/routers/gold_medal.py

from enum import IntEnum
from fastapi import APIRouter, BackgroundTasks

router = APIRouter(prefix="/api/v1/gold-medal", tags=["gold-medal"])

class MedalLevel(IntEnum):
    L1_SITE_TRAFFIC_DROP = 1
    L2_GSC_PENALTY = 2
    L3_PERSONA_WARNING = 3
    L4_QA_FAILURE = 4
    L5_ADSENSE_WARNING = 5
    L6_MULTI_SITE_ANOMALY = 6
    L7_DATABASE_FAILURE = 7
    L8_API_BUDGET_EXCEEDED = 8
    L9_SCRAPING_ATTACK = 9
    L10_MULTI_PERSONA_BAN = 10
    L11_LEGAL_NOTICE = 11
    L12_MANUAL_FULL_STOP = 12

MEDAL_ACTIONS = {
    MedalLevel.L1_SITE_TRAFFIC_DROP: pause_site_content_push,
    MedalLevel.L2_GSC_PENALTY: pause_link_building,
    MedalLevel.L3_PERSONA_WARNING: isolate_persona,
    MedalLevel.L4_QA_FAILURE: pause_content_pipeline,
    MedalLevel.L8_API_BUDGET_EXCEEDED: circuit_break_llm,
    MedalLevel.L12_MANUAL_FULL_STOP: full_system_shutdown,
}

@router.post("/trigger/{level}")
async def trigger_gold_medal(level: MedalLevel, reason: str,
                              background_tasks: BackgroundTasks):
    """触发金牌（自动或手动）"""
    event = await create_gold_medal_event(level, reason)
    background_tasks.add_task(execute_medal_actions, event)
    background_tasks.add_task(notify_songhuizong, event)
    background_tasks.add_task(create_system_snapshot, event)
    return {"medal_level": level, "event_id": event.id}

@router.post("/release")
async def release_gold_medal(resume_checklist: dict):
    """解除金牌状态（需要通过恢复检查清单）"""
    # 验证所有检查项已完成
    await validate_resume_checklist(resume_checklist)
    await restore_system_from_snapshot()
    return {"status": "resumed"}
```

---

## 系统快照机制

每次触发第7道及以上金牌前，自动保存系统状态快照：

```json
{
  "snapshot_type": "pre_gold_medal",
  "medal_level": 8,
  "timestamp": "2026-06-10T15:30:00Z",
  "active_tasks": [...],
  "pipeline_states": {...},
  "persona_states": {...},
  "site_statuses": {...},
  "restore_instructions": "见 MANUAL_RECOVERY.md"
}
```

快照保留 30 天，支持按时间点恢复。

---

## Dashboard 金牌动效设计

- 第1-3道：站点/好汉图标出现黄色警告角标
- 第4-6道：对应区域图标变橙色，飞鸽停止飞行
- 第7-9道：画面局部变灰（对应模块停运）
- 第10-11道：大范围灰色，宋徽宗从座位站起，走向画面中央
- 第12道：**全图转黑白**，所有角色静止，背景古琴声戛然而止，
           宋徽宗手持金牌，画面中央出现「奉旨停机」字样
