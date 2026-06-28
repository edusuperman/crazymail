import streamlit as st
import pandas as pd
from utils.styles import COLORS, render_metric_card, render_section_title, render_status_badge
from utils.data_loader import load_outlines, load_qc_reports, load_keywords


def render():
    render_section_title("宣和总驿大厅", "项目全局一览")

    outlines = load_outlines()
    qc_reports = load_qc_reports()
    kw_data = load_keywords()

    total_articles = len(outlines)
    total_keywords = sum(len(k.get("keywords", [])) for k in kw_data) if kw_data else 0

    pass_count = sum(1 for q in qc_reports if q.get("overall") == "PASS")
    pass_rate = round(pass_count / len(qc_reports) * 100, 1) if qc_reports else 0

    sites_count = 1

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("文章总数", str(total_articles))
    with col2:
        render_metric_card("关键词数", str(total_keywords))
    with col3:
        render_metric_card("质检通过率", f"{pass_rate}%")
    with col4:
        render_metric_card("站点数", str(sites_count))

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("### 最近文章")

    if outlines:
        rows = []
        for o in outlines:
            qc_match = next(
                (q for q in qc_reports if q.get("keyword") == o.get("primary_keyword")),
                None,
            )
            status = qc_match.get("overall", "N/A") if qc_match else "N/A"
            rows.append(
                {
                    "标题": o.get("title", ""),
                    "主关键词": o.get("primary_keyword", ""),
                    "分类": o.get("category", ""),
                    "质检": status,
                }
            )
        df = pd.DataFrame(rows)

        def style_status(val):
            if val == "PASS":
                return "color: #2e7d5e; font-weight: bold"
            elif val == "FAIL":
                return "color: #c0392b; font-weight: bold"
            return ""

        st.dataframe(
            df.style.map(style_status, subset=["质检"]),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("暂无文章数据。请先运行内容工厂生成文章。")

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("### 系统状态")

    tools = [
        ("内容工厂 (content_factory.py)", True),
        ("关键词发现 (keyword_discovery.py)", True),
        ("流量监控 (traffic_monitor.py)", False),
        ("增长黑客 (growth_hacker.py)", True),
    ]
    for name, available in tools:
        badge = render_status_badge(available)
        status_text = "就绪" if available else "待配置"
        st.markdown(f"- {badge} &nbsp; {name} — **{status_text}**", unsafe_allow_html=True)
