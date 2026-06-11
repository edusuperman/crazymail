# CrazyMail 数据库 Schema 设计
# PostgreSQL 16 / Supabase

---

## 核心表结构

### 1. 站点管理（sites）

```sql
CREATE TABLE sites (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code            VARCHAR(20) UNIQUE NOT NULL,  -- 驿站代号，如 "yizhan_01"
    name            VARCHAR(100) NOT NULL,         -- 站点名称
    domain          VARCHAR(255) UNIQUE NOT NULL,
    niche           VARCHAR(100) NOT NULL,         -- 垂类，如 "temp-email-privacy"
    niche_tier      INTEGER DEFAULT 1,             -- 批次（1/2/3）
    status          VARCHAR(20) DEFAULT 'active',  -- active/paused/gold_medal
    hosting_provider VARCHAR(100),
    ip_address      VARCHAR(45),
    cdn_provider    VARCHAR(100),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    metadata        JSONB DEFAULT '{}'
);

-- 站点指标（单独表，按日分区）
CREATE TABLE site_metrics (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id     UUID REFERENCES sites(id),
    date        DATE NOT NULL,
    sessions    INTEGER DEFAULT 0,
    pageviews   INTEGER DEFAULT 0,
    revenue_usd DECIMAL(10,2) DEFAULT 0,
    rpm         DECIMAL(10,4) DEFAULT 0,
    articles_published INTEGER DEFAULT 0,
    created_at  TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY RANGE (date);
```

### 2. 内容流水线（content_pipeline）

```sql
-- 内容任务主表
CREATE TABLE content_tasks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id         UUID REFERENCES sites(id),
    keyword         VARCHAR(500) NOT NULL,
    keyword_volume  INTEGER,
    keyword_difficulty INTEGER,
    target_url      VARCHAR(500),
    status          VARCHAR(30) DEFAULT 'pending',
    -- pending / researching / outlining / writing / qa_check
    -- seo_optimize / link_building / human_review / published / failed
    current_stage   INTEGER DEFAULT 1,  -- 1-7
    assigned_agent  VARCHAR(50),        -- 当前负责的官员
    workflow_run_id VARCHAR(255),       -- LangGraph run ID
    priority        INTEGER DEFAULT 5,  -- 1-10，越高越优先
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 内容版本（每个阶段产出单独存储）
CREATE TABLE content_versions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id     UUID REFERENCES content_tasks(id),
    stage       INTEGER NOT NULL,  -- 1-7
    agent_name  VARCHAR(50),
    content     TEXT,
    metadata    JSONB DEFAULT '{}',  -- SEO分数、AI检测分等
    is_approved BOOLEAN DEFAULT NULL,  -- NULL=待审，TRUE=通过，FALSE=打回
    reviewer    VARCHAR(100),
    review_note TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 质检结果（岳飞9重）
CREATE TABLE qa_results (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version_id      UUID REFERENCES content_versions(id),
    ai_detection_score  DECIMAL(5,2),   -- 越低越好，目标 < 30
    seo_score           DECIMAL(5,2),   -- 越高越好，目标 > 75
    eeat_score          DECIMAL(5,2),   -- 目标 > 80
    human_score         DECIMAL(5,2),   -- 目标 > 70
    overall_pass        BOOLEAN,
    failed_checks       JSONB DEFAULT '[]',
    suggestions         TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### 3. 人格系统（personas）

```sql
-- 人格主表
CREATE TABLE personas (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code            VARCHAR(50) UNIQUE NOT NULL,  -- 如 "liangshan_026_wusong"
    display_name    VARCHAR(100) NOT NULL,
    persona_type    VARCHAR(20) NOT NULL,  -- 'official'（编制内）或 'hero'（108好汉）
    level           INTEGER DEFAULT 1,    -- 成长等级 1-4
    xp              INTEGER DEFAULT 0,    -- 经验值
    status          VARCHAR(20) DEFAULT 'active',
    soul_file_path  VARCHAR(500),         -- SOUL.md 文件路径
    config          JSONB DEFAULT '{}',   -- 行为参数（活跃时间/频率等）
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    last_active_at  TIMESTAMPTZ
);

-- 人格平台账号（一个好汉在多个平台）
CREATE TABLE persona_accounts (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    persona_id  UUID REFERENCES personas(id),
    platform    VARCHAR(50) NOT NULL,  -- twitter/reddit/facebook等
    account_id  VARCHAR(255),
    username    VARCHAR(255),
    status      VARCHAR(20) DEFAULT 'active',  -- active/suspended/warning
    proxy_id    UUID,                           -- 对应代理配置
    browser_profile_id VARCHAR(255),           -- Dolphin Anty Profile ID
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 人格成长记录
CREATE TABLE persona_memory (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    persona_id  UUID REFERENCES personas(id),
    event_type  VARCHAR(50),   -- post/comment/like/milestone/learning
    content     TEXT,
    platform    VARCHAR(50),
    sentiment   VARCHAR(20),   -- positive/neutral/negative
    xp_gained   INTEGER DEFAULT 0,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### 4. 金牌系统（gold_medals）

```sql
CREATE TABLE gold_medal_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    medal_level     INTEGER NOT NULL,  -- 1-12
    trigger_type    VARCHAR(50),       -- auto / manual
    trigger_reason  TEXT,
    affected_scope  JSONB,             -- 影响范围（站点/好汉/全局）
    actions_taken   JSONB DEFAULT '[]',
    resolved_at     TIMESTAMPTZ,
    resolved_by     VARCHAR(100),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 系统状态快照（用于人工接管时恢复）
CREATE TABLE system_snapshots (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_type VARCHAR(30),  -- pre_gold_medal / manual / scheduled
    state_data  JSONB NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### 5. 皇城司安全监控

```sql
CREATE TABLE security_events (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type  VARCHAR(50),   -- ip_leak/fingerprint_collision/account_flag
    severity    VARCHAR(20),   -- info/warning/critical
    source      VARCHAR(100),  -- 来源模块/站点/好汉
    details     JSONB DEFAULT '{}',
    resolved    BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 代理池管理
CREATE TABLE proxy_pool (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider    VARCHAR(100),
    ip_address  VARCHAR(45),
    country     VARCHAR(10),
    city        VARCHAR(100),
    status      VARCHAR(20) DEFAULT 'active',
    assigned_to UUID,  -- 分配给哪个 persona_account
    last_used   TIMESTAMPTZ,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 索引策略

```sql
-- 高频查询索引
CREATE INDEX idx_content_tasks_status ON content_tasks(status, priority DESC);
CREATE INDEX idx_content_tasks_site ON content_tasks(site_id, created_at DESC);
CREATE INDEX idx_persona_memory_persona ON persona_memory(persona_id, created_at DESC);
CREATE INDEX idx_security_events_severity ON security_events(severity, resolved, created_at DESC);
CREATE INDEX idx_site_metrics_date ON site_metrics(site_id, date DESC);
```

---

## Redis 键设计

```
# 任务队列（Celery）
crazymail:queue:content_production    # 内容生产队列
crazymail:queue:persona_actions       # 好汉操作队列
crazymail:queue:qa_check             # 质检队列

# 实时状态
crazymail:site:{site_id}:status       # 站点实时状态
crazymail:persona:{persona_id}:state  # 好汉当前状态
crazymail:pipeline:{task_id}:stage    # 任务当前阶段

# Pub/Sub 频道（WebSocket 推送）
crazymail:events:dashboard            # 全局 Dashboard 事件
crazymail:events:gold_medal           # 金牌告警
crazymail:events:pigeon:{task_id}     # 飞鸽动效触发
```
