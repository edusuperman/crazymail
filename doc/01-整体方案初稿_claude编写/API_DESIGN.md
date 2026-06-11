# CrazyMail FastAPI 接口设计

## 设计原则
- RESTful 风格，统一 /api/v1/ 前缀
- 每个业务模块独立 Router（插座原则）
- 所有响应统一格式：{ success, data, message, timestamp }
- WebSocket 端点用于实时 Dashboard 推送

---

## 内容工厂模块 /api/v1/content

```
POST   /api/v1/content/tasks              # 创建内容任务（输入关键词）
GET    /api/v1/content/tasks              # 获取任务列表（分页+筛选）
GET    /api/v1/content/tasks/{task_id}    # 获取任务详情+阶段进度
PATCH  /api/v1/content/tasks/{task_id}   # 更新任务（优先级/状态）
DELETE /api/v1/content/tasks/{task_id}   # 取消任务

POST   /api/v1/content/tasks/{task_id}/approve  # 宋徽宗审批通过
POST   /api/v1/content/tasks/{task_id}/reject   # 宋徽宗打回重写
GET    /api/v1/content/review-queue              # 待审核队列

GET    /api/v1/content/versions/{version_id}     # 获取某版本内容
GET    /api/v1/content/tasks/{task_id}/versions  # 获取任务所有版本

POST   /api/v1/content/qa/check         # 手动触发质检（单篇）
GET    /api/v1/content/qa/{version_id}  # 获取质检报告
```

---

## 站点管理模块 /api/v1/sites

```
GET    /api/v1/sites                    # 所有驿站列表
POST   /api/v1/sites                    # 新建驿站
GET    /api/v1/sites/{site_id}          # 驿站详情
PATCH  /api/v1/sites/{site_id}          # 更新驿站配置
GET    /api/v1/sites/{site_id}/metrics  # 驿站指标（流量/收益）
GET    /api/v1/sites/{site_id}/content  # 驿站内容列表
POST   /api/v1/sites/{site_id}/pause    # 暂停驿站
POST   /api/v1/sites/{site_id}/resume  # 恢复驿站
GET    /api/v1/sites/overview           # 20站总览仪表盘数据
```

---

## 人格系统模块 /api/v1/personas

```
GET    /api/v1/personas                          # 所有人格列表
POST   /api/v1/personas                          # 新建人格
GET    /api/v1/personas/{persona_id}             # 人格详情+当前状态
PATCH  /api/v1/personas/{persona_id}             # 更新人格配置

GET    /api/v1/personas/{persona_id}/accounts    # 该人格的平台账号
POST   /api/v1/personas/{persona_id}/accounts    # 添加平台账号
PATCH  /api/v1/personas/{persona_id}/accounts/{account_id}  # 更新账号

GET    /api/v1/personas/{persona_id}/memory      # 人格记忆日志
POST   /api/v1/personas/{persona_id}/memory      # 手动追加记忆事件
GET    /api/v1/personas/{persona_id}/growth      # 成长轨迹+当前等级

POST   /api/v1/personas/{persona_id}/actions/post     # 发布一条内容
POST   /api/v1/personas/{persona_id}/actions/interact # 执行互动（点赞/评论）
GET    /api/v1/personas/{persona_id}/schedule    # 查看排期计划
POST   /api/v1/personas/{persona_id}/schedule    # 创建排期任务

GET    /api/v1/personas/officials                # 仅编制内官员
GET    /api/v1/personas/heroes                   # 仅108好汉
GET    /api/v1/personas/heroes/map               # 好汉全球分布地图数据
```

---

## 皇城司模块 /api/v1/security

```
GET    /api/v1/security/health              # 整体安全状态
GET    /api/v1/security/events              # 安全事件列表
GET    /api/v1/security/events/{event_id}   # 事件详情
POST   /api/v1/security/events/{event_id}/resolve  # 标记已处理

GET    /api/v1/security/isolation/check     # 运行隔离完整性检查
GET    /api/v1/security/isolation/report    # 最新隔离健康报告
POST   /api/v1/security/isolation/scan      # 触发关联性扫描

GET    /api/v1/security/proxies             # 代理池状态
POST   /api/v1/security/proxies/{proxy_id}/rotate  # 轮换代理
GET    /api/v1/security/fingerprints        # 指纹Profile列表
```

---

## 金牌系统模块 /api/v1/gold-medal

```
GET    /api/v1/gold-medal/status            # 当前金牌级别和状态
GET    /api/v1/gold-medal/history           # 历史金牌事件
POST   /api/v1/gold-medal/trigger/{level}  # 手动触发指定级别金牌
POST   /api/v1/gold-medal/release           # 解除金牌状态（恢复正常）
GET    /api/v1/gold-medal/manual-mode       # 获取人工接管模式下的待办
POST   /api/v1/gold-medal/manual-mode/complete  # 完成人工操作，准备恢复自动
```

---

## Dashboard 模块 /api/v1/dashboard

```
GET    /api/v1/dashboard/overview     # 全局大盘数据
GET    /api/v1/dashboard/pipeline     # 当前运转中的所有任务
GET    /api/v1/dashboard/revenue      # 收益数据（按时间/站点）
GET    /api/v1/dashboard/alerts       # 当前告警列表
GET    /api/v1/dashboard/pigeons      # 当前飞鸽状态（动效数据）
```

---

## WebSocket 端点

```
WS  /ws/dashboard         # 全局实时推送（飞鸽动效/金牌告警/状态更新）
WS  /ws/pipeline/{task}   # 单任务流水线实时进度
WS  /ws/persona/{id}      # 单人格实时状态
```

**WebSocket 事件格式**：
```json
{
  "event": "pigeon_fly",
  "data": {
    "from": "liangshan_02_ligang",
    "to": "liangshan_03_zhangzeduan",
    "task_id": "uuid",
    "payload_size": "medium"
  },
  "timestamp": "2026-06-10T12:00:00Z"
}
```

**事件类型**：
- `pigeon_fly` — 飞鸽起飞（任务进入下一阶段）
- `pigeon_shot` — 飞鸽中箭（质检失败）
- `pigeon_land` — 飞鸽落地（任务完成）
- `gold_medal` — 金牌触发
- `site_alert` — 站点异常
- `persona_level_up` — 好汉升级
- `review_needed` — 需要宋徽宗审核
