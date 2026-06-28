import streamlit as st
import time
from PIL import Image
import random

st.set_page_config(page_title="CrazyMail · 疯邮·大宋驿站", layout="wide", page_icon="🕊️")

st.title("🐦‍🔥 疯邮 · 大宋宣和驿站")
st.markdown("**AI内容工厂 Dashboard** | 纯展示层 | 前端强分离")

# 侧边栏
st.sidebar.title("驿政司")
st.sidebar.selectbox("选择驿丞模型", ["MiMo 2.5 Pro", "DeepSeek V4 Flash", "本地Ollama", "Claude"])

# 主大厅
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("🏯 宣和总驿大厅")
    st.image("https://via.placeholder.com/800x400?text=清明上河图风格驿站", use_column_width=True)
    
    # 飞鸽状态
    st.subheader("🕊️ 飞鸽传书实时监控")
    status = st.select_slider("模拟状态", ["正常投递", "飞得缓慢", "遭遇风控"])
    
    if status == "正常投递":
        st.success("🕊️ 20只飞鸽正在快速投递内容...")
    elif status == "飞得缓慢":
        st.warning("🕊️ 飞鸽疲惫，流量增长缓慢...")
    else:
        st.error("🏹 部分飞鸽被箭射落！风控预警！")

with col2:
    st.subheader("📜 编制内7阶段")
    officials = ["宋徽宗(总管)", "李纲(研究)", "张择端(大纲)", "李清照(写作)", "岳飞(质检)", "韩世忠(链接)", "宗泽(GEO)"]
    for o in officials:
        st.button(o, key=o)

st.subheader("🌍 108好汉全球分舵（增长黑客 - 纯展示）")
st.info("108位江湖义士分散全球，点击查看推广记录（实际执行走独立集群）")
if st.button("模拟108好汉放飞鸽群"):
    st.balloons()

# 20站概览
st.subheader("驿站网络（20个独立站点）")
cols = st.columns(5)
for i in range(20):
    with cols[i % 5]:
        st.metric(f"驿站{i+1}", "流量正常", "↑12%")

st.caption("CrazyMail 项目 | 严格遵守前端分离 & AdSense合规 | 纯可视化展示")