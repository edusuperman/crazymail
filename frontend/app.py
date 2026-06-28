"""
疯邮 · 大宋宣和驿站 — Dashboard MVP
=====================================
Streamlit 实现的虚拟办公室 + 数据看板
参考 Marvis 等距3D办公室设计，国风主题

启动: streamlit run app.py
"""

import streamlit as st
import time
import random
from datetime import datetime, timedelta

# ════════════════════════════════════════════
# 页面配置
# ════════════════════════════════════════════
st.set_page_config(
    page_title="疯邮 · 大宋宣和驿站",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ════════════════════════════════════════════
# 自定义 CSS（国风暗色主题）
# ════════════════════════════════════════════
st.markdown("""
<style>
    /* 全局字体 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&display=swap');
    
    /* 主色调 */
    :root {
        --bg-dark: #1a1a2e;
        --bg-card: #16213e;
        --bg-sidebar: #0f0f23;
        --accent-gold: #d4a574;
        --accent-red: #e74c3c;
        --accent-green: #2ecc71;
        --accent-blue: #3498db;
        --text-primary: #ecf0f1;
        --text-secondary: #95a5a6;
    }
    
    /* 侧边栏 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 100%);
    }
    [data-testid="stSidebar"] .stMarkdown p {
        color: #ecf0f1;
    }
    
    /* 隐藏默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 卡片样式 */
    .dashboard-card {
        background: linear-gradient(135deg, #16213e 0%, #1a1a2e 100%);
        border: 1px solid #2c3e50;
        border-radius: 12px;
        padding: 20px;
        margin: 8px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* 好汉工位 */
    .hero-desk {
        background: linear-gradient(135deg, #1e3a5f 0%, #16213e 100%);
        border: 2px solid #2c3e50;
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .hero-desk:hover {
        border-color: #d4a574;
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(212, 165, 116, 0.2);
    }
    .hero-desk .hero-avatar {
        font-size: 48px;
        margin-bottom: 8px;
    }
    .hero-desk .hero-name {
        color: #d4a574;
        font-family: 'Noto Serif SC', serif;
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 4px;
    }
    .hero-desk .hero-role {
        color: #95a5a6;
        font-size: 11px;
    }
    .hero-desk .hero-status {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 10px;
        margin-top: 6px;
    }
    .status-working {
        background: rgba(46, 204, 113, 0.2);
        color: #2ecc71;
        border: 1px solid rgba(46, 204, 113, 0.3);
    }
    .status-idle {
        background: rgba(149, 165, 166, 0.2);
        color: #95a5a6;
        border: 1px solid rgba(149, 165, 166, 0.3);
    }
    .status-error {
        background: rgba(231, 76, 60, 0.2);
        color: #e74c3c;
        border: 1px solid rgba(231, 76, 60, 0.3);
    }
    
    /* 流水线阶段 */
    .pipeline-stage {
        background: linear-gradient(135deg, #1e3a5f 0%, #16213e 100%);
        border: 2px solid #2c3e50;
        border-radius: 12px;
        padding: 12px 16px;
        text-align: center;
        position: relative;
    }
    .pipeline-stage.active {
        border-color: #d4a574;
        box-shadow: 0 0 20px rgba(212, 165, 116, 0.3);
    }
    .pipeline-stage.completed {
        border-color: #2ecc71;
    }
    .pipeline-stage .stage-icon {
        font-size: 28px;
        margin-bottom: 6px;
    }
    .pipeline-stage .stage-name {
        color: #ecf0f1;
        font-size: 12px;
        font-weight: 600;
    }
    .pipeline-stage .stage-count {
        color: #d4a574;
        font-size: 20px;
        font-weight: 700;
        margin-top: 4px;
    }
    
    /* 数据指标 */
    .metric-card {
        background: linear-gradient(135deg, #16213e 0%, #1a1a2e 100%);
        border: 1px solid #2c3e50;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .metric-value {
        color: #d4a574;
        font-size: 32px;
        font-weight: 700;
        font-family: 'Noto Serif SC', serif;
    }
    .metric-label {
        color: #95a5a6;
        font-size: 12px;
        margin-top: 4px;
    }
    .metric-change {
        font-size: 11px;
        margin-top: 4px;
    }
    .metric-up { color: #2ecc71; }
    .metric-down { color: #e74c3c; }
    
    /* 事件日志 */
    .event-log {
        background: #0f0f23;
        border: 1px solid #2c3e50;
        border-radius: 8px;
        padding: 12px;
        max-height: 300px;
        overflow-y: auto;
        font-family: monospace;
        font-size: 12px;
    }
    .event-item {
        padding: 6px 0;
        border-bottom: 1px solid #1a1a2e;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .event-time {
        color: #95a5a6;
        min-width: 60px;
    }
    .event-icon {
        font-size: 14px;
    }
    .event-text {
        color: #ecf0f1;
    }
    
    /* 连接线（流水线） */
    .pipeline-connector {
        display: flex;
        align-items: center;
        justify-content: center;
        color: #d4a574;
        font-size: 20px;
        padding: 0 4px;
    }
    
    /* 标题样式 */
    .section-title {
        color: #d4a574;
        font-family: 'Noto Serif SC', serif;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid #2c3e50;
    }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════
# 模拟数据
# ════════════════════════════════════════════

def get_heroes_data():
    """108好汉数据（模拟）"""
    heroes = [
        {"name": "及时雨·宋江", "avatar": "🏹", "role": "内容总监", "status": "working", "task": "审核文章 #42"},
        {"name": "智多星·吴用", "avatar": "📚", "role": "策略顾问", "status": "working", "task": "分析关键词"},
        {"name": "入云龙·公孙胜", "avatar": "☁️", "role": "SEO 专家", "status": "working", "task": "优化 meta tags"},
        {"name": "豹子头·林冲", "avatar": "⚔️", "role": "安全巡检", "status": "idle", "task": "等待任务"},
        {"name": "花和尚·鲁智深", "avatar": "🔨", "role": "部署工程师", "status": "working", "task": "部署 site-03"},
        {"name": "行者·武松", "avatar": "🐯", "role": "质量检测", "status": "working", "task": "QC 文章 #38"},
        {"name": "小李广·花荣", "avatar": "🎯", "role": "精准投放", "status": "idle", "task": "等待任务"},
        {"name": "黑旋风·李逵", "avatar": "⚡", "role": "紧急修复", "status": "error", "task": "API 超时排查"},
    ]
    return heroes


def get_pipeline_data():
    """内容工厂7阶段数据"""
    stages = [
        {"name": "关键词发现", "icon": "🔍", "count": 156, "active": False, "completed": True},
        {"name": "内容生成", "icon": "✍️", "count": 42, "active": True, "completed": False},
        {"name": "质量检测", "icon": "🔬", "count": 38, "active": False, "completed": False},
        {"name": "AI 润色", "icon": "✨", "count": 35, "active": False, "completed": False},
        {"name": "发布上线", "icon": "🚀", "count": 28, "active": False, "completed": False},
        {"name": "流量监控", "icon": "📊", "count": 28, "active": False, "completed": False},
        {"name": "持续优化", "icon": "♻️", "count": 12, "active": False, "completed": False},
    ]
    return stages


def get_metrics():
    """核心指标"""
    return {
        "总邮件数": {"value": "1,247", "change": "+89", "up": True},
        "今日邮件": {"value": "47", "change": "+12", "up": True},
        "活跃站点": {"value": "3", "change": "+1", "up": True},
        "文章总数": {"value": "156", "change": "+8", "up": True},
        "今日流量": {"value": "2,341", "change": "+156", "up": True},
        "月收入": {"value": "$127", "change": "+$23", "up": True},
    }


def get_events():
    """实时事件日志"""
    events = [
        {"time": "15:42", "icon": "✍️", "text": "智多星·吴用 开始撰写「临时邮箱安全性指南」"},
        {"time": "15:38", "icon": "✅", "text": "文章「Best Temp Email 2026」QC 通过 (SEO: 82)"},
        {"time": "15:35", "icon": "📧", "text": "site-01 收到 3 封新邮件"},
        {"time": "15:30", "icon": "🚀", "text": "site-02 部署完成，耗时 23s"},
        {"time": "15:25", "icon": "⚠️", "text": "黑旋风·李逵 发现 API 响应超时 (>5s)"},
        {"time": "15:20", "icon": "🔍", "text": "入云龙·公孙胜 发现新关键词: 'disposable email for github'"},
        {"time": "15:15", "icon": "📊", "text": "今日流量突破 2000 UV"},
        {"time": "15:10", "icon": "💰", "text": "AdSense 收入 +$3.2 (site-01)"},
        {"time": "15:05", "icon": "🔬", "text": "行者·武松 完成文章 #35 质检 (AI检测: 18)"},
        {"time": "15:00", "icon": "🏹", "text": "及时雨·宋江 批准发布 5 篇文章"},
    ]
    return events


# ════════════════════════════════════════════
# 侧边栏
# ════════════════════════════════════════════

with st.sidebar:
    st.markdown("## 🏛️ 宣和总驿")
    st.markdown("---")
    
    # 导航菜单
    menu = st.radio(
        "导航",
        ["📊 总览", "📧 驿件管理", "✍️ 内容工厂", "👥 好汉管理", "🌐 站点矩阵", "⚙️ 系统设置"],
        label_visibility="collapsed",
    )
    
    st.markdown("---")
    st.markdown("### 🏃 驿丞状态")
    
    # 当前活跃的好汉
    heroes = get_heroes_data()
    working_count = sum(1 for h in heroes if h["status"] == "working")
    st.metric("在线好汉", f"{working_count}/{len(heroes)}")
    
    st.markdown("---")
    st.markdown("### 📋 最近对话")
    st.caption("审核文章 #42 质量报告")
    st.caption("site-03 部署确认")
    st.caption("关键词策略讨论")
    
    st.markdown("---")
    st.caption("宣和总驿 v1.0 · 阶段二")


# ════════════════════════════════════════════
# 主界面
# ════════════════════════════════════════════

# 顶部标题
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
    <div>
        <h1 style="color: #d4a574; font-family: 'Noto Serif SC', serif; margin: 0; font-size: 28px;">
            🏛️ 大宋宣和驿站
        </h1>
        <p style="color: #95a5a6; margin: 4px 0 0 0; font-size: 14px;">
            临时邮箱矩阵 · 智能运营中枢
        </p>
    </div>
    <div style="text-align: right;">
        <span style="color: #2ecc71; font-size: 12px;">● 系统正常</span><br>
        <span style="color: #95a5a6; font-size: 11px;">""" + datetime.now().strftime("%Y-%m-%d %H:%M") + """</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════
# 核心指标行
# ════════════════════════════════════════════

metrics = get_metrics()
cols = st.columns(6)
for i, (name, data) in enumerate(metrics.items()):
    with cols[i]:
        change_class = "metric-up" if data["up"] else "metric-down"
        change_arrow = "↑" if data["up"] else "↓"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{data['value']}</div>
            <div class="metric-label">{name}</div>
            <div class="metric-change {change_class}">{change_arrow} {data['change']}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════
# 内容工厂流水线
# ════════════════════════════════════════════

st.markdown('<div class="section-title">🏭 内容工厂 · 七阶段流水线</div>', unsafe_allow_html=True)

pipeline = get_pipeline_data()
pipeline_cols = st.columns(13)  # 7 stages + 6 connectors

for i, stage in enumerate(pipeline):
    col_idx = i * 2
    with pipeline_cols[col_idx]:
        status_class = "active" if stage["active"] else ("completed" if stage["completed"] else "")
        st.markdown(f"""
        <div class="pipeline-stage {status_class}">
            <div class="stage-icon">{stage['icon']}</div>
            <div class="stage-name">{stage['name']}</div>
            <div class="stage-count">{stage['count']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 连接箭头
    if i < len(pipeline) - 1:
        with pipeline_cols[col_idx + 1]:
            st.markdown('<div class="pipeline-connector">→</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════
# 好汉工位（虚拟办公室）
# ════════════════════════════════════════════

st.markdown('<div class="section-title">👥 好汉工位 · 虚拟办公室</div>', unsafe_allow_html=True)

heroes = get_heroes_data()
hero_cols = st.columns(4)

for i, hero in enumerate(heroes):
    with hero_cols[i % 4]:
        status_class = f"status-{hero['status']}"
        status_text = {"working": "工作中", "idle": "待命", "error": "异常"}[hero["status"]]
        st.markdown(f"""
        <div class="hero-desk">
            <div class="hero-avatar">{hero['avatar']}</div>
            <div class="hero-name">{hero['name']}</div>
            <div class="hero-role">{hero['role']}</div>
            <div class="hero-status {status_class}">{status_text}</div>
            <div style="color: #bdc3c7; font-size: 11px; margin-top: 8px; min-height: 16px;">
                {hero['task'] if hero['status'] == 'working' else '&nbsp;'}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════
# 底部：站点状态 + 事件日志
# ════════════════════════════════════════════

col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown('<div class="section-title">🌐 站点矩阵</div>', unsafe_allow_html=True)
    
    sites = [
        {"name": "tempmails.top", "status": "online", "traffic": "1,247", "revenue": "$89"},
        {"name": "tempmails.io", "status": "online", "traffic": "678", "revenue": "$28"},
        {"name": "tempmails.org", "status": "building", "traffic": "—", "revenue": "—"},
    ]
    
    for site in sites:
        status_color = "#2ecc71" if site["status"] == "online" else "#f39c12"
        status_text = "● 在线" if site["status"] == "online" else "◐ 建设中"
        st.markdown(f"""
        <div class="dashboard-card" style="padding: 12px 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="color: #d4a574; font-weight: 600;">{site['name']}</span>
                    <span style="color: {status_color}; font-size: 12px; margin-left: 8px;">{status_text}</span>
                </div>
                <div style="text-align: right;">
                    <span style="color: #ecf0f1; font-size: 14px;">{site['traffic']} UV</span>
                    <span style="color: #2ecc71; font-size: 14px; margin-left: 12px;">{site['revenue']}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="section-title">📋 实时事件日志</div>', unsafe_allow_html=True)
    
    events = get_events()
    events_html = '<div class="event-log">'
    for event in events:
        events_html += f"""
        <div class="event-item">
            <span class="event-time">{event['time']}</span>
            <span class="event-icon">{event['icon']}</span>
            <span class="event-text">{event['text']}</span>
        </div>
        """
    events_html += '</div>'
    
    st.markdown(events_html, unsafe_allow_html=True)


# ════════════════════════════════════════════
# 自动刷新（模拟实时数据）
# ════════════════════════════════════════════

st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🔄 刷新数据", use_container_width=True):
        st.rerun()
