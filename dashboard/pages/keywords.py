import streamlit as st
import pandas as pd
from utils.styles import COLORS, render_metric_card, render_section_title
from utils.data_loader import load_keywords


def render():
    render_section_title("李纲研究室", "关键词发现与管理")

    kw_data = load_keywords()

    if not kw_data:
        st.info("暂无关键词数据。请先运行关键词发现工具。")
        return

    latest = kw_data[-1]

    total = latest.get("total_discovered", 0)
    covered = latest.get("already_covered_count", 0)
    new_kw = latest.get("new_keywords_count", 0)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("发现总数", str(total))
    with col2:
        render_metric_card("已覆盖", str(covered))
    with col3:
        render_metric_card("新发现", str(new_kw))
    with col4:
        seeds = latest.get("seed_keywords", [])
        render_metric_card("种子关键词", str(len(seeds)))

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("### 新发现 vs 已覆盖")

    if total > 0:
        chart_data = pd.DataFrame(
            {"状态": ["已覆盖", "新发现"], "数量": [covered, new_kw]}
        )
        st.bar_chart(
            chart_data,
            x="状态",
            y="数量",
            color="状态",
            color_discrete_map={
                "已覆盖": COLORS["jade_green"],
                "新发现": COLORS["imperial_gold"],
            },
        )

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("### 关键词列表")

    keywords = latest.get("keywords", [])
    if keywords:
        rows = []
        for kw in keywords:
            rows.append(
                {
                    "关键词": kw.get("keyword", ""),
                    "类型": kw.get("type", ""),
                    "意图": kw.get("intent", ""),
                    "竞争度": kw.get("competition", ""),
                    "相关性": kw.get("relevance", ""),
                    "内容类型": kw.get("content_type", ""),
                    "已覆盖": "是" if kw.get("already_covered") else "否",
                }
            )
        df = pd.DataFrame(rows)

        def style_covered(val):
            if val == "是":
                return "color: #2e7d5e; font-weight: bold"
            return "color: #d4a017; font-weight: bold"

        st.dataframe(
            df.style.map(style_covered, subset=["已覆盖"]),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("暂无关键词条目。")

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("### 操作")
    st.button("运行关键词发现", disabled=True, help="此按钮仅作展示，MVP版本不执行实际操作。")
    st.caption(f"数据来源：{latest.get('_file', 'N/A')} | 生成时间：{latest.get('generated_at', 'N/A')}")
