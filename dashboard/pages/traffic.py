import os
import streamlit as st
import pandas as pd
from utils.styles import COLORS, render_metric_card, render_section_title
from utils.data_loader import get_simulation_traffic_data


def _check_gsc_credentials() -> bool:
    creds_path = os.environ.get("GSC_CREDENTIALS_PATH", "")
    if creds_path and os.path.exists(creds_path):
        return True
    return False


def render():
    render_section_title("飞鸽状态", "流量监控中心")

    has_gsc = _check_gsc_credentials()

    if has_gsc:
        st.success("GSC 凭据已配置，正在获取真实数据...")
        st.info("GSC API 对接尚未实现，以下展示模拟数据。")
        data = get_simulation_traffic_data()
    else:
        st.warning("GSC 凭据未配置。以下展示模拟数据，请配置 GSC 凭据后查看真实流量。")
        st.markdown(
            """
            **配置方法：**
            1. 在 [Google Search Console](https://search.google.com/search-console) 创建 API 凭据
            2. 设置环境变量 `GSC_CREDENTIALS_PATH` 指向凭据文件
            3. 重启 Dashboard
            """
        )
        data = get_simulation_traffic_data()

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("### 核心指标")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("总点击数", str(data["total_clicks"]))
    with col2:
        render_metric_card("总展示数", str(data["total_impressions"]))
    with col3:
        render_metric_card("平均 CTR", f"{data['avg_ctr']}%")
    with col4:
        render_metric_card("平均排名", str(data["avg_position"]))

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("### 流量趋势（近30天）")

    days = data["days"]
    df = pd.DataFrame(days)
    df["date"] = pd.to_datetime(df["date"])

    tab1, tab2, tab3, tab4 = st.tabs(["点击数", "展示数", "CTR", "排名"])

    with tab1:
        st.line_chart(df, x="date", y="clicks", color=COLORS["vermillion"])

    with tab2:
        st.line_chart(df, x="date", y="impressions", color=COLORS["ink_blue"])

    with tab3:
        st.line_chart(df, x="date", y="ctr", color=COLORS["jade_green"])

    with tab4:
        st.line_chart(df, x="date", y="position", color=COLORS["imperial_gold"])

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("### 每日明细")
    display_df = df.copy()
    display_df.columns = ["日期", "点击", "展示", "CTR(%)", "平均排名"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.caption("数据来源：模拟数据（种子=42，可复现）")
