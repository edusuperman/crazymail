import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.styles import inject_global_css

st.set_page_config(
    page_title="疯邮 · 大宋宣和驿站",
    page_icon="🐎",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_css()

PAGES = {
    "总览": "overview",
    "内容工厂": "content",
    "关键词": "keywords",
    "流量": "traffic",
    "增长": "growth",
}

with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding:1rem 0;">
            <h1 style="color:#f5f0e8; font-size:1.6rem; font-family:Noto Serif SC,serif; margin-bottom:0.2rem;">
                疯邮 · 大宋宣和驿站
            </h1>
            <p style="color:#d4a017; font-size:0.85rem; margin-top:0;">驿政司 Dashboard</p>
        </div>
        <hr style="border-color:#d4a017; opacity:0.3;">
        """,
        unsafe_allow_html=True,
    )

    selected = st.radio(
        "导航",
        list(PAGES.keys()),
        label_visibility="collapsed",
    )

    st.markdown(
        """
        <hr style="border-color:#d4a017; opacity:0.3; margin-top:2rem;">
        <p style="color:#bdc3c7; font-size:0.75rem; text-align:center;">
            CrazyMail Dashboard MVP v1.0<br>
            Streamlit 原型验证版
        </p>
        """,
        unsafe_allow_html=True,
    )

page_key = PAGES[selected]

if page_key == "overview":
    from pages.overview import render
    render()
elif page_key == "content":
    from pages.content import render
    render()
elif page_key == "keywords":
    from pages.keywords import render
    render()
elif page_key == "traffic":
    from pages.traffic import render
    render()
elif page_key == "growth":
    from pages.growth import render
    render()
