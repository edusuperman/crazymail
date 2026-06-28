import streamlit as st
import pandas as pd
from utils.styles import COLORS, render_metric_card, render_section_title, render_status_badge
from utils.data_loader import load_outlines, load_qc_reports


STAGES = [
    "关键词发现",
    "大纲生成",
    "内容撰写",
    "人性化处理",
    "内链注入",
    "SEO优化",
    "质检发布",
]


def _render_pipeline():
    st.markdown("#### 7阶段流水线")
    parts = []
    for i, stage in enumerate(STAGES):
        parts.append(f'<span class="pipeline-stage">{stage}</span>')
        if i < len(STAGES) - 1:
            parts.append('<span class="pipeline-arrow">→</span>')
    st.markdown("".join(parts), unsafe_allow_html=True)


def render():
    render_section_title("编制内7阶段", "内容工厂流水线总览")

    _render_pipeline()

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    outlines = load_outlines()
    qc_reports = load_qc_reports()

    col1, col2, col3 = st.columns(3)
    with col1:
        render_metric_card("已生产文章", str(len(outlines)))
    with col2:
        pass_count = sum(1 for q in qc_reports if q.get("overall") == "PASS")
        render_metric_card("质检通过", str(pass_count))
    with col3:
        fail_count = sum(1 for q in qc_reports if q.get("overall") == "FAIL")
        render_metric_card("质检未通过", str(fail_count))

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("### 最近生产的文章")

    if outlines:
        rows = []
        for o in outlines:
            qc_match = next(
                (q for q in qc_reports if q.get("keyword") == o.get("primary_keyword")),
                None,
            )
            status = qc_match.get("overall", "N/A") if qc_match else "N/A"
            word_count = "N/A"
            if qc_match and "checks" in qc_match:
                wc = qc_match["checks"].get("word_count", {})
                word_count = str(wc.get("value", "N/A"))
            sections_count = len(o.get("sections", []))
            rows.append(
                {
                    "标题": o.get("title", ""),
                    "主关键词": o.get("primary_keyword", ""),
                    "章节数": sections_count,
                    "字数": word_count,
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
        st.info("暂无文章数据。")

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("### 质检通过率统计")

    if qc_reports:
        pass_c = sum(1 for q in qc_reports if q.get("overall") == "PASS")
        fail_c = len(qc_reports) - pass_c
        chart_data = pd.DataFrame(
            {"状态": ["通过", "未通过"], "数量": [pass_c, fail_c]}
        )
        st.bar_chart(chart_data, x="状态", y="数量", color="状态", color_discrete_map={"通过": COLORS["jade_green"], "未通过": COLORS["vermillion"]})
    else:
        st.info("暂无质检数据。")

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("### 操作")
    st.button("运行内容工厂", disabled=True, help="此按钮仅作展示，MVP版本不执行实际操作。")
    st.caption("提示：MVP 纯展示层，不触发任何真实操作。")
