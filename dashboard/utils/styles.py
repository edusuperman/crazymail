import streamlit as st

COLORS = {
    "ink_black": "#1a1a1a",
    "vermillion": "#c0392b",
    "imperial_gold": "#d4a017",
    "jade_green": "#2e7d5e",
    "parchment": "#f5f0e8",
    "ink_blue": "#2c4a6e",
    "warning_amber": "#e67e22",
    "ash_gray": "#bdc3c7",
}


def inject_global_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700&display=swap');

        .stApp {
            background-color: #f5f0e8;
        }

        section[data-testid="stSidebar"] {
            background-color: #1a1a1a;
        }

        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] .stMarkdown h1,
        section[data-testid="stSidebar"] .stMarkdown h2,
        section[data-testid="stSidebar"] .stMarkdown h3,
        section[data-testid="stSidebar"] label {
            color: #f5f0e8 !important;
        }

        h1, h2, h3 {
            font-family: 'Noto Serif SC', serif !important;
            color: #1a1a1a !important;
        }

        .metric-card {
            background: white;
            border-left: 4px solid #c0392b;
            border-radius: 6px;
            padding: 1rem 1.2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            margin-bottom: 0.5rem;
        }

        .metric-card .label {
            font-size: 0.85rem;
            color: #666;
            margin-bottom: 0.2rem;
        }

        .metric-card .value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #1a1a1a;
            font-family: 'Noto Serif SC', serif;
        }

        .status-pass {
            color: #2e7d5e;
            font-weight: 700;
        }

        .status-fail {
            color: #c0392b;
            font-weight: 700;
        }

        .pipeline-stage {
            display: inline-block;
            background: #2c4a6e;
            color: #f5f0e8;
            padding: 0.4rem 1rem;
            border-radius: 20px;
            margin: 0.2rem;
            font-size: 0.85rem;
        }

        .pipeline-arrow {
            display: inline-block;
            color: #d4a017;
            font-size: 1.2rem;
            margin: 0 0.2rem;
            vertical-align: middle;
        }

        .calendar-day {
            background: white;
            border-radius: 6px;
            padding: 0.8rem;
            margin-bottom: 0.5rem;
            border-left: 3px solid #2e7d5e;
        }

        .calendar-day.today {
            border-left: 3px solid #c0392b;
        }

        .section-divider {
            border-top: 2px solid #d4a017;
            margin: 1.5rem 0 1rem 0;
        }

        div[data-testid="stMetric"] {
            background: white;
            border-left: 4px solid #c0392b;
            border-radius: 6px;
            padding: 0.5rem 1rem;
        }

        div[data-testid="stMetric"] label {
            color: #666 !important;
        }

        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: #1a1a1a !important;
            font-family: 'Noto Serif SC', serif !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_title(title: str, subtitle: str = ""):
    html = f"<h2 style='color:{COLORS['ink_black']}; font-family:Noto Serif SC,serif;'>{title}</h2>"
    if subtitle:
        html += f"<p style='color:#666; margin-top:-0.5rem;'>{subtitle}</p>"
    html += "<div class='section-divider'></div>"
    st.markdown(html, unsafe_allow_html=True)


def render_status_badge(passed: bool) -> str:
    if passed:
        return '<span class="status-pass">PASS</span>'
    return '<span class="status-fail">FAIL</span>'
