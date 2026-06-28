import streamlit as st
import pandas as pd
from utils.styles import COLORS, render_metric_card, render_section_title
from utils.data_loader import load_growth_content_dirs


PLATFORM_ICONS = {
    "twitter": "Twitter/X",
    "reddit": "Reddit",
    "linkedin": "LinkedIn",
    "hackernews": "Hacker News",
    "directory": "目录站",
    "content-calendar": "内容日历",
}


def _parse_calendar(content: str) -> list[dict]:
    rows = []
    for line in content.splitlines():
        if line.startswith("|") and "---" not in line and "Date" not in line:
            cols = [c.strip().strip("*") for c in line.split("|")[1:-1]]
            if len(cols) >= 5:
                rows.append(
                    {
                        "日期": cols[0],
                        "平台": cols[1],
                        "动作": cols[2],
                        "内容/主题": cols[3],
                        "预估时间": cols[4],
                    }
                )
    return rows


def render():
    render_section_title("108好汉推广厅", "增长黑客内容矩阵")

    growth_dirs = load_growth_content_dirs()

    if not growth_dirs:
        st.info("暂无增长内容数据。请先运行增长黑客工具。")
        return

    total_files = sum(len(d["files"]) for d in growth_dirs)
    total_dirs = len(growth_dirs)

    col1, col2 = st.columns(2)
    with col1:
        render_metric_card("内容批次", str(total_dirs))
    with col2:
        render_metric_card("内容文件总数", str(total_files))

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("### 已生成的社媒内容")

    for gdir in growth_dirs:
        with st.expander(f"批次：{gdir['date']}（{len(gdir['files'])} 个文件）", expanded=False):
            for f in gdir["files"]:
                platform_key = f["stem"]
                display_name = PLATFORM_ICONS.get(platform_key, f["stem"].replace("-", " ").title())

                st.markdown(f"**{display_name}** — `{f['name']}` ({f['size_kb']} KB)")
                if platform_key == "content-calendar":
                    calendar_rows = _parse_calendar(f["content"])
                    if calendar_rows:
                        st.dataframe(pd.DataFrame(calendar_rows), use_container_width=True, hide_index=True)
                    else:
                        st.code(f["content"][:500] + "..." if len(f["content"]) > 500 else f["content"])
                else:
                    preview = f["content"][:800] + "..." if len(f["content"]) > 800 else f["content"]
                    st.text_area(
                        f"内容预览 - {display_name}",
                        value=preview,
                        height=150,
                        disabled=True,
                        key=f"preview_{gdir['date']}_{f['stem']}",
                    )
                st.markdown("---")

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("### 内容日历")

    calendar_files = []
    for gdir in growth_dirs:
        for f in gdir["files"]:
            if f["stem"] == "content-calendar":
                calendar_files.append(f)

    if calendar_files:
        latest_cal = calendar_files[-1]
        rows = _parse_calendar(latest_cal["content"])
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("无法解析内容日历数据。")
    else:
        st.info("暂无内容日历。")

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("### 目录站提交状态")

    dir_files = []
    for gdir in growth_dirs:
        for f in gdir["files"]:
            if f["stem"] == "directory-submissions":
                dir_files.append(f)

    if dir_files:
        for f in dir_files:
            st.markdown(f"**{f['name']}** ({f['size_kb']} KB)")
            preview = f["content"][:600] + "..." if len(f["content"]) > 600 else f["content"]
            st.code(preview)
    else:
        st.info("暂无目录站提交数据。")

    st.caption(f"数据来源：docs/growth-content-*/ 目录")
