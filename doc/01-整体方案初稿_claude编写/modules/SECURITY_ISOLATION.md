# 皇城司：站点网络安全隔离架构

## 设计目标

运营多站点内容网络时，防止各站点之间产生可被识别的关联性特征
（即 SEO 行业通称的"脚印管理"，footprint management），
确保每个站点在技术层面表现为完全独立的个体。

---

## 七层隔离体系

### Layer 1：物理层隔离

```yaml
# 20个站点分配规则
hosting_distribution:
  group_a:  # 站点01-04
    provider: Cloudflare Pages
    region: us-east
  group_b:  # 站点05-08
    provider: Hostinger
    region: eu-west
  group_c:  # 站点09-12
    provider: Vultr
    region: ap-southeast
  group_d:  # 站点13-16
    provider: BunnyCDN
    region: us-west
  group_e:  # 站点17-20
    provider: SiteGround
    region: eu-central

rules:
  - 同一主机商最多管理 4 个站点
  - 任意两个相关 niche 站点不得在同一主机商
  - /24 子网内不得出现超过 2 个项目站点
```

### Layer 2：网络层隔离

```python
# backend/core/proxy_manager.py

PROXY_ASSIGNMENT_RULES = {
    # 内容生产（编制内）：使用数据中心 IP，稳定、用于 API 调用
    "content_production": {
        "proxy_type": "datacenter",
        "rotation": "session",  # 每次会话更换
    },
    # 108好汉推广：住宅代理，按好汉注册地理位置匹配
    "persona_actions": {
        "proxy_type": "residential",
        "rotation": "account",  # 每个账号固定一个 IP 段
        "geo_match": True,      # IP 地理位置必须与好汉档案中的城市匹配
        "provider": "brightdata",  # 或 oxylabs
    },
    # 宋徽宗管理操作：固定 IP + VPN 双跳
    "admin_operations": {
        "proxy_type": "vpn_chain",
        "fixed": True,
    }
}
```

### Layer 3：身份层隔离

```
域名注册规则：
├── 每5个站点使用不同的域名注册商
│   ├── 站点01-04：Namecheap
│   ├── 站点05-08：Cloudflare Registrar
│   ├── 站点09-12：Porkbun
│   ├── 站点13-16：Dynadot
│   └── 站点17-20：GoDaddy（仅用于此分组）
├── 所有域名启用 WHOIS 隐私保护
├── 各分组使用不同的隐私保护服务商
└── 注册邮箱：每站点独立，不同邮件服务商（ProtonMail/Tutanota/Gmail交替使用）

支付隔离：
├── 每5站点独立支付卡（不同银行发卡）
└── 联盟账号：按 Niche 分组注册，同 Niche 多站点共用一个联盟账号（官方允许）
```

### Layer 4：浏览器与指纹隔离

```python
# 每位好汉的浏览器指纹配置（存于 persona_accounts 表）
BROWSER_PROFILE_TEMPLATE = {
    "tool": "dolphin_anty",           # 或 GoLogin
    "canvas_fingerprint": "auto_unique",
    "webgl_renderer": "randomize",
    "screen_resolution": "1366x768",  # 选普通分辨率，不选4K（更像真实用户）
    "timezone": "{persona.timezone}", # 与代理IP地理匹配
    "language": "{persona.language}",
    "fonts": "system_standard",       # 不添加非标字体（降低指纹特异性）
    "user_agent": "Chrome/{recent_stable} on Windows 10",  # 非最新版
    "cookies_scope": "isolated",       # 绝对不跨账号共享 cookies
    "webrtc": "disabled",             # 防 IP 泄露
    "do_not_track": "random",         # 随机（真实用户行为不一致）
}
```

### Layer 5：行为节律隔离

```python
# 行为随机化引擎（backend/services/behavior_engine.py）

class BehaviorEngine:
    """确保同一时间段内，不同好汉的行为模式不产生可识别的同步性"""

    def schedule_action(self, persona_id: str, action_type: str) -> datetime:
        profile = load_heartbeat_profile(persona_id)
        
        # 基础时间 + 随机偏移（±15分钟）
        base_time = get_next_active_slot(profile)
        jitter = random.randint(-900, 900)  # 秒
        
        # 确保同一平台上，相邻好汉的操作间隔 > 8分钟
        while conflicts_with_recent_actions(persona_id, base_time + jitter):
            jitter += random.randint(300, 600)
        
        return base_time + jitter
    
    def simulate_session(self, persona_id: str) -> List[Action]:
        """模拟一次完整的在线会话（包含非推广行为）"""
        # 每次推广操作前，先执行 2-5 个自然行为（浏览/点赞/阅读）
        natural_actions = generate_natural_browsing(persona_id, count=random.randint(2,5))
        promo_action = generate_promotion_action(persona_id)
        cooldown = random.randint(120, 600)  # 推广后冷却期
        return natural_actions + [promo_action, Wait(cooldown)]
```

### Layer 6：内容层隔离

```yaml
content_isolation_rules:
  cross_site_linking: FORBIDDEN          # 站点间绝对禁止相互内链
  shared_analytics_id: FORBIDDEN         # 禁止多站共享 GA/GSC ID
  shared_image_cdn_path: FORBIDDEN       # 图片不共享 CDN 路径
  
  template_uniqueness:
    - 每站点独立 CSS 主题（不同颜色/字体/间距组合）
    - 不同 WordPress/CMS 主题或不同自定义程度
    - 不同 Schema markup 实现方式（手写 vs 插件）
    
  author_bio_requirements:
    - 每站点有 2-3 个独立虚拟作者
    - 每位作者有独立的 LinkedIn 主页（真实运营）
    - 作者头像经过元数据清除处理
    - Person Schema JSON-LD 必须包含 sameAs 字段（指向 LinkedIn）
    
  publish_time_pattern:
    - 不同站点的发布时间表错开
    - 避免所有站点在同一小时内集中发布
    - 加入随机延迟（±2小时）
```

### Layer 7：资金层隔离

```
AdSense 账号分组（官方允许一个账号管理多个站点，但按 Niche 分组更安全）：

AdSense Account A → 站点01-05（隐私工具 Niche）
AdSense Account B → 站点06-10（开发者工具 Niche）
AdSense Account C → 站点11-15（邮件安全 Niche）
AdSense Account D → 站点16-20（综合/其他 Niche）

收款路由：
├── 每组 AdSense 对应独立收款账户
└── 不将多组收益归集到同一账户（防关联）
```

---

## 皇城司自动化工具

### 1. 关联性扫描器（每日自动运行）

```python
# backend/services/isolation_checker.py

class IsolationChecker:
    checks = [
        check_ip_overlap,           # 检查是否有IP重叠
        check_nameserver_overlap,   # 检查NS记录是否重叠
        check_analytics_id_leak,    # 检查GA/GSC ID是否错用
        check_internal_link_leak,   # 检查是否有跨站内链
        check_cdn_path_overlap,     # 检查CDN路径是否重叠
        check_publish_time_sync,    # 检查发布时间是否异常同步
        check_author_cross_site,    # 检查作者是否跨站出现
    ]
    
    async def run_daily_scan(self) -> IsolationReport:
        results = await asyncio.gather(*[c() for c in self.checks])
        report = compile_report(results)
        if report.has_critical_issues:
            await trigger_gold_medal(level=6, reason=report.summary)
        return report
```

### 2. 风险雷达 Dashboard

实时显示：
- 各站点隔离健康分（0-100）
- 最近7天安全事件时间轴
- 代理池健康状态（活跃/故障/过期）
- 指纹Profile使用状态

---

## 皇城司在 Dashboard 中的存在感

- 位于主画布右下角，一扇半掩的**古朴木门**
- 门缝中偶尔有人影闪过（随机触发，每5-10分钟一次）
- 当有安全事件时，门缝透出红光
- 点击木门，展开皇城司控制台（独立侧边栏）
- 控制台风格：深色背景，红色告警，像密室情报厅
