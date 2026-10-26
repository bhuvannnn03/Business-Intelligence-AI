import io
from datetime import date
import re

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    KeepTogether
)
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF

# -----------------------------------------------------------------------------
# NURTURA — Business Intelligence workspace
# Replace app.py with this file. Dependencies: streamlit, pandas, numpy, plotly, reportlab
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="NURTURA | Business Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# NURTURA premium enterprise visual system
st.markdown(
    """
    <style>
    :root { color-scheme: dark; }
    .stApp { background: radial-gradient(ellipse at 8% 0%, #14233a 0%, #0a101b 34%, #080d16 100%); color: #e8eef8; }
    [data-testid="stHeader"] { background: rgba(8,13,22,.88); backdrop-filter: blur(14px); }
    [data-testid="stToolbar"] { right: 1rem; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg,#0a1424 0%,#08111f 100%); border-right: 1px solid #203149; }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1rem; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #a8b6ca; }
    [data-testid="stSidebar"] hr { margin: .9rem 0; border-color: #24334a !important; }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1600px; }
    h1, h2, h3 { color: #f4f7fc !important; letter-spacing: -.035em; }
    h1 { font-weight: 720 !important; font-size: clamp(2rem, 3vw, 2.75rem) !important; }
    h2, h3 { font-weight: 650 !important; }
    p, label, .stMarkdown { color: #c5d0df; }
    [data-testid="stMetric"] { background: linear-gradient(145deg,rgba(23,38,59,.96),rgba(14,24,39,.96)); border: 1px solid #2a3d58; padding: 20px 21px; border-radius: 16px; box-shadow: 0 8px 24px rgba(0,0,0,.12); min-height: 118px; }
    [data-testid="stMetricLabel"] { color: #a6b5ca !important; font-size: .82rem; font-weight: 550; }
    [data-testid="stMetricValue"] { color: #f7f9fd !important; font-weight: 720; letter-spacing: -.04em; font-size: clamp(1.45rem, 2.1vw, 2.05rem); }
    [data-testid="stMetricDelta"] { font-size: .8rem; }
    div[data-testid="stDataFrame"] { border: 1px solid #2a3b53; border-radius: 13px; overflow: hidden; box-shadow: 0 8px 24px rgba(0,0,0,.10); }
    div[data-testid="stPlotlyChart"] { background: linear-gradient(145deg,rgba(16,27,44,.94),rgba(12,21,35,.94)); border: 1px solid #263951; border-radius: 16px; padding: 8px; box-shadow: 0 10px 28px rgba(0,0,0,.12); }
    div.stButton > button, div.stDownloadButton > button { border-radius: 10px; border: 1px solid #6b91e7; background: linear-gradient(135deg,#4778dc,#315bc0); color: #fff; font-weight: 650; padding: .65rem 1rem; box-shadow: 0 5px 16px rgba(49,91,192,.18); transition: all .18s ease; }
    div.stButton > button:hover, div.stDownloadButton > button:hover { transform: translateY(-1px); background: linear-gradient(135deg,#5688ed,#3a68d2); border-color: #9bb6f3; color: #fff; }
    .ic-eyebrow { color: #8eafff; font-size: .7rem; text-transform: uppercase; letter-spacing: .19em; font-weight: 750; margin-bottom: .55rem; }
    .ic-subtitle { color: #9eafc6; margin-top: -.45rem; margin-bottom: 1.5rem; font-size: 1rem; max-width: 900px; line-height: 1.6; }
    .ic-panel { background: linear-gradient(145deg,rgba(20,34,54,.96),rgba(13,23,38,.96)); border: 1px solid #2a3d58; border-radius: 16px; padding: 20px 22px; margin-bottom: 14px; }
    .ic-alert { background: linear-gradient(100deg,rgba(24,41,64,.95),rgba(15,27,44,.95)); border: 1px solid #2b405c; border-left: 3px solid #83a6f6; border-radius: 11px; padding: 14px 16px; margin: 9px 0; color: #cbd7e8; line-height: 1.55; }
    .ic-alert b { color: #f1f5fc; font-size: .9rem; letter-spacing: .01em; }
    .ic-muted { color: #8d9db4; font-size: .86rem; }
    .ic-brand { display:flex; align-items:center; gap:11px; padding:8px 3px 20px; }
    .ic-brand-mark { width:44px; height:44px; display:flex; align-items:center; justify-content:center; border-radius:13px; background:linear-gradient(145deg,#7ce7c5,#4fd4b0); border:1px solid #8df0d1; color:#09231f; font-size:21px; font-weight:850; box-shadow:0 8px 22px rgba(0,0,0,.18); }
    .ic-brand-name { color:#f6f8fd; font-size:15px; letter-spacing:1.9px; font-weight:850; }
    .ic-brand-sub { color:#8fa8c7; font-size:9px; letter-spacing:1.45px; margin-top:4px; text-transform:uppercase; }
    .ic-section-label { font-size:10px; letter-spacing:1.7px; color:#8295b2; font-weight:800; text-transform:uppercase; margin:5px 0 10px; }
    .ic-status { display:inline-flex; align-items:center; gap:7px; border:1px solid #294a45; border-radius:999px; padding:6px 10px; color:#9fe2c5; background:rgba(25,90,69,.18); font-size:11px; font-weight:650; }
    [data-testid="stSidebar"] div[role="radiogroup"] { gap: 7px; padding-top: 4px; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label { background: transparent; border: 1px solid transparent; border-radius: 11px; padding: 10px 12px; margin: 0; min-height: 43px; transition: background .16s ease, border-color .16s ease; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover { background: rgba(79,212,176,.07); border-color: #253c53; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) { background: rgba(79,212,176,.12); border-color: rgba(79,212,176,.18); box-shadow: inset 3px 0 0 #5ce0b8; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p { color: #68e7c2 !important; font-weight: 750; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label p { font-size: .88rem; color: #aab9ce; margin: 0; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display: none; }
    [data-testid="stFileUploader"] section { border-color: #30445f; background: rgba(17,29,47,.8); border-radius: 12px; }
    [data-testid="stDateInput"] input, [data-testid="stTextInput"] input, [data-testid="stSelectbox"] [data-baseweb="select"], [data-testid="stMultiSelect"] [data-baseweb="select"] { background: #111d2f; border-color:#2e425d; border-radius:9px; }
    [data-testid="stAlert"] { border-radius: 11px; }
    hr { border-color: #26374f !important; }

/* Dashboard spacing and typography */
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { font-size: 19px !important; }
[data-testid="stSidebar"] label { font-size: 18px !important; }
[data-testid="stSidebar"] div[role="radiogroup"] > label [data-testid="stMarkdownContainer"] p { font-size: 21px !important; }
[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { min-width: 42px !important; }

/* Blend Streamlit's top toolbar into the app background without hiding
   its sidebar-collapse/reopen control. */
[data-testid="stHeader"] {
    display: flex !important;
    visibility: visible !important;
    height: 2.35rem !important;
    min-height: 2.35rem !important;
    background: #0a101b !important;
    border-bottom: 0 !important;
    box-shadow: none !important;
}
[data-testid="stToolbar"] { visibility: visible !important; }
[data-testid="stAppViewContainer"] > .main,
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="stAppViewBlockContainer"],
.block-container {
    padding-top: 0 !important;
    margin-top: 0 !important;
}
/* Move the brand closer to the top while keeping the navigation toggle usable. */
[data-testid="stSidebar"] > div:first-child { padding-top: .25rem !important; }
[data-testid="stSidebar"] .ic-brand {
    margin-top: -.55rem !important;
    padding-top: .25rem !important;
    padding-bottom: 14px !important;
}
.block-container {
    max-width: 1800px !important;
    padding-bottom: 2rem !important;
}
[data-testid="stVerticalBlock"] { gap: .65rem !important; }

/* Dark tables consistent with the dashboard */
[data-testid="stTable"] table,
[data-testid="stTable"] th,
[data-testid="stTable"] td {
    background-color: #0d1727 !important;
    color: #e5edf8 !important;
    border-color: #263951 !important;
}
[data-testid="stTable"] tbody tr:nth-child(even) td { background-color: #111f32 !important; }
[data-testid="stDataFrame"] { background: #0d1727 !important; color: #e5edf8 !important; }
[data-testid="stDataFrame"] [data-testid="stDataFrameResizable"],
[data-testid="stDataFrame"] canvas { background-color: #0d1727 !important; }

h1 { font-size: clamp(1.8rem, 2.4vw, 2.25rem) !important; margin-bottom: .25rem !important; }
h2 { font-size: 1.45rem !important; }
h3 { font-size: 1.12rem !important; }
.block-container { padding-top: .35rem !important; padding-bottom: .75rem !important; }
[data-testid="stVerticalBlock"] { gap: .42rem !important; }
[data-testid="stMetric"] { padding: 12px 15px !important; min-height: 88px !important; }
.ic-subtitle { margin-bottom: .7rem !important; }
.ic-panel { padding: 13px 16px !important; margin-bottom: 5px !important; }
.ic-alert { padding: 10px 12px !important; margin: 4px 0 !important; }
h3 { font-size: 27px !important; }
/* Final layout guard: toolbar and content share one continuous dark surface. */
[data-testid="stHeader"], [data-testid="stToolbar"] { background-color: #0a101b !important; }
[data-testid="stAppViewContainer"], [data-testid="stMain"] { background: transparent !important; }
.block-container { padding-top: .15rem !important; }
/* Final spacing adjustment: blend top strip and raise the brand */
[data-testid="stHeader"] {
    height: 1.2rem !important;
    min-height: 1.2rem !important;
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
    visibility: visible !important;
}
[data-testid="stToolbar"] { visibility: visible !important; }
[data-testid="stAppViewContainer"] > .main,
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="stAppViewBlockContainer"],
.block-container {
    margin-top: 0 !important;
    padding-top: 0 !important;
}
[data-testid="stSidebar"] > div:first-child,
[data-testid="stSidebar"] section[data-testid="stSidebarContent"] {
    padding-top: 0 !important;
}
[data-testid="stSidebar"] .ic-brand {
    margin-top: -1.5rem !important;
    padding-top: 0 !important;
    padding-bottom: 8px !important;
    transform: translateY(-10px);
}

/* FINAL: make Streamlit chrome and dashboard one continuous surface */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
}
[data-testid="stHeader"] {
    height: 2rem !important;
    min-height: 2rem !important;
    visibility: visible !important;
}
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stAppViewContainer"] > .main,
[data-testid="stMainBlockContainer"],
[data-testid="stAppViewBlockContainer"],
.block-container {
    background: transparent !important;
    margin-top: 0 !important;
    padding-top: 0 !important;
}
.stApp {
    background: radial-gradient(ellipse at 8% 0%, #14233a 0%, #0a101b 34%, #080d16 100%) !important;
}
/* Keep the sidebar toggle visible and clickable while removing the separate bar look. */
[data-testid="stHeader"] button,
[data-testid="stHeader"] [data-testid="stSidebarCollapsedControl"] {
    visibility: visible !important;
    opacity: 1 !important;
}
[data-testid="stSidebar"] > div:first-child,
[data-testid="stSidebar"] section[data-testid="stSidebarContent"] {
    padding-top: 0 !important;
}
[data-testid="stSidebar"] .ic-brand {
    margin-top: -1rem !important;
    padding-top: 0 !important;
    padding-bottom: 8px !important;
    transform: translateY(-8px) !important;
}

/* FINAL OVERRIDE: remove the thin horizontal seam below Streamlit's top controls */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stAppViewContainer"] > .main,
[data-testid="stMainBlockContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stMainBlockContainer"] > div,
.block-container {
    border-top: 0 !important;
    border-bottom: 0 !important;
    box-shadow: none !important;
    outline: 0 !important;
}
[data-testid="stHeader"]::before,
[data-testid="stHeader"]::after,
[data-testid="stMain"]::before,
[data-testid="stMain"]::after,
[data-testid="stAppViewContainer"]::before,
[data-testid="stAppViewContainer"]::after {
    content: none !important;
    display: none !important;
    border: 0 !important;
    box-shadow: none !important;
}
/* Same continuous background behind the toolbar and page content */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stMain"],
[data-testid="stAppViewContainer"] > .main,
.block-container {
    background: #0a101b !important;
}
[data-testid="stHeader"] {
    height: 2rem !important;
    min-height: 2rem !important;
    border: none !important;
    background: #0a101b !important;
}
.block-container {
    padding-top: 0 !important;
    margin-top: 0 !important;
}

</style>
    """,
    unsafe_allow_html=True,
)

REQUIRED_COLUMNS = ["date", "units_sold", "selling_price", "unit_cost"]
# Conservative prototype limits. Increase only after load testing.
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MiB
MAX_UPLOAD_ROWS = 100_000
MAX_UPLOAD_COLUMNS = 50
ALLOWED_INPUT_COLUMNS = {"date", "units_sold", "selling_price", "unit_cost", "product", "stock_on_hand"}


def clear_workspace_state():
    """Reset this Streamlit browser session's app state and invalidate its upload widget."""
    reset_count = int(st.session_state.get("_nurtura_reset_count", 0)) + 1
    for key in list(st.session_state.keys()):
        try:
            del st.session_state[key]
        except Exception:
            # Best-effort cleanup of app-owned state; widget state is reset by changing keys.
            pass
    st.session_state["_nurtura_reset_count"] = reset_count


def safe_csv_bytes(frame):
    """Return CSV bytes with spreadsheet-formula injection neutralized in text cells."""
    safe = frame.copy()
    dangerous = re.compile(r"^[\s\u0000-\u001f]*[=+@\-]")
    for col in safe.select_dtypes(include=["object", "string"]).columns:
        safe[col] = safe[col].map(
            lambda value: "'" + value if isinstance(value, str) and dangerous.match(value) else value
        )
    return safe.to_csv(index=False).encode("utf-8-sig")


def safe_filename(label):
    """Keep download names simple and avoid path/control characters."""
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", str(label)).strip("_-")[:60]
    return cleaned or "business"
NAV_ITEMS = [
    "Home",
    "Sales Analytics",
    "Products & Profitability",
    "Inventory",
    "Forecast & Insights",
    "Profit Tracker",
    "Summary",
    "Reports",
    "Team & Settings",
    "Data Explorer",
]


def money(value):
    try:
        return f"₹{float(value):,.2f}"
    except (TypeError, ValueError):
        return "—"


def number(value, decimals=0):
    try:
        return f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return "—"


CHART_COLORS = ["#7da2ff", "#49d4b4", "#f3bd68", "#b59cff", "#f28d9d", "#6ec6e8"]
CHART_GRID = "#27384f"


def polish_chart(fig, height=360, show_legend=True):
    """Apply NURTURA's shared styling to interactive Plotly charts."""
    fig.update_layout(
        template="plotly_dark",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, ui-sans-serif, system-ui, sans-serif", color="#c6d2e3", size=12),
        margin=dict(l=18, r=18, t=28, b=18),
        hoverlabel=dict(bgcolor="#15243a", bordercolor="#3b5272", font=dict(color="#f4f7fc", size=12)),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#b9c7da")
        ) if show_legend else dict(visible=False),
        xaxis=dict(showgrid=False, zeroline=False, linecolor=CHART_GRID, tickfont=dict(color="#9eafc5")),
        yaxis=dict(showgrid=True, gridcolor=CHART_GRID, zeroline=False, linecolor=CHART_GRID, tickfont=dict(color="#9eafc5")),
    )
    return fig


def line_figure(data, x, y, labels=None, height=360):
    """Create a polished line chart; y may be one column or a list of columns."""
    columns = [y] if isinstance(y, str) else list(y)
    fig = go.Figure()
    for i, col in enumerate(columns):
        label = (labels or {}).get(col, col.replace("_", " ").title())
        fig.add_trace(go.Scatter(
            x=data[x], y=data[col], name=label, mode="lines+markers",
            line=dict(color=CHART_COLORS[i % len(CHART_COLORS)], width=2.8, shape="spline"),
            marker=dict(size=5, color=CHART_COLORS[i % len(CHART_COLORS)], line=dict(width=1, color="#101b2b")),
            hovertemplate="%{x|%d %b %Y}<br><b>%{y:,.2f}</b><extra>" + label + "</extra>",
        ))
    fig.update_xaxes(showgrid=False, tickformat="%d %b")
    fig.update_yaxes(tickformat=",.0f", title=None)
    return polish_chart(fig, height=height, show_legend=len(columns) > 1)


def bar_figure(data, x, y, horizontal=False, color=None, height=360, labels=None):
    """Create a consistently styled interactive bar chart."""
    color = color or CHART_COLORS[0]
    if horizontal:
        fig = px.bar(data, x=x, y=y, orientation="h", text=x)
        fig.update_traces(marker_color=color, texttemplate="%{x:,.0f}", textposition="outside",
                          cliponaxis=False, marker_line_width=0,
                          hovertemplate="%{y}<br><b>%{x:,.2f}</b><extra></extra>")
        fig.update_yaxes(categoryorder="total ascending", title=None, showgrid=False)
        fig.update_xaxes(title=None, tickformat=",.0f", showgrid=True, gridcolor=CHART_GRID)
    else:
        fig = px.bar(data, x=x, y=y, text=y)
        fig.update_traces(marker_color=color, texttemplate="%{y:,.0f}", textposition="outside",
                          cliponaxis=False, marker_line_width=0,
                          hovertemplate="%{x}<br><b>%{y:,.2f}</b><extra></extra>")
        fig.update_xaxes(title=None, showgrid=False, tickangle=-25)
        fig.update_yaxes(title=None, tickformat=",.0f", gridcolor=CHART_GRID)
    if labels:
        fig.update_layout(xaxis_title=labels.get("x"), yaxis_title=labels.get("y"))
    return polish_chart(fig, height=height, show_legend=False)


def display_table(data, height=360, formats=None):
    """Render a clean, readable table with consistent number formatting."""
    table = data.copy()
    formatters = formats or {}
    # Style the actual Pandas Styler passed into Streamlit. CSS targeting the
    # surrounding Streamlit DOM alone does not reliably recolor dataframe cells.
    styler = (
        table.style
        .format(formatters, na_rep="—", precision=2)
        .set_properties(**{
            "background-color": "#0d1727",
            "color": "#e5edf8",
            "border-color": "#263a52",
            "font-size": "13px",
        })
        .set_table_styles([
            {
                "selector": "thead th",
                "props": [
                    ("background-color", "#172a42"),
                    ("color", "#eaf2ff"),
                    ("font-weight", "700"),
                    ("border-bottom", "1px solid #35506e"),
                    ("padding", "12px 14px"),
                ],
            },
            {
                "selector": "tbody td",
                "props": [
                    ("background-color", "#0d1727"),
                    ("color", "#e5edf8"),
                    ("border-bottom", "1px solid #22344a"),
                    ("padding", "10px 14px"),
                ],
            },
            {
                "selector": "tbody tr:nth-child(even) td",
                "props": [("background-color", "#111f32")],
            },
            {
                "selector": "tbody tr:hover td",
                "props": [("background-color", "#173044")],
            },
            {
                "selector": "table",
                "props": [
                    ("border-collapse", "separate"),
                    ("border-spacing", "0"),
                    ("border", "1px solid #263a52"),
                    ("border-radius", "10px"),
                    ("overflow", "hidden"),
                ],
            },
        ], overwrite=False)
    )
    # Use the styled static table instead of Streamlit's virtualized dataframe grid.
    # The grid can keep white header/footer strips that CSS cannot consistently override.
    st.table(styler)


def make_demo_data():
    """Generate repeatable illustrative data. This is not real business data."""
    rng = np.random.default_rng(18)
    dates = pd.date_range(end=pd.Timestamp.today().normalize() - pd.Timedelta(days=1), periods=90)
    products = [
        ("Everyday Mug", 399.0, 175.0),
        ("Canvas Tote", 549.0, 240.0),
        ("Desk Bottle", 799.0, 360.0),
        ("Notebook Set", 299.0, 110.0),
        ("Wireless Lamp", 1499.0, 860.0),
        ("Travel Pouch", 649.0, 270.0),
    ]
    rows = []
    for i, day in enumerate(dates):
        for j, (product, price, cost) in enumerate(products):
            base = [10, 8, 6, 13, 4, 7][j]
            trend = i * (0.025 if j in (0, 2, 4) else 0.008)
            weekday = 1.2 if day.dayofweek in (4, 5) else 1.0
            units = max(0, int(rng.normal(base + trend, max(1.2, base * .25)) * weekday))
            rows.append({
                "date": day,
                "product": product,
                "units_sold": units,
                "selling_price": price,
                "unit_cost": cost,
                "stock_on_hand": max(0, int(rng.normal(48 - units * .35, 12))),
                "order_id": f"DEMO-{day:%Y%m%d}-{j+1}",
            })
    return pd.DataFrame(rows)


def prepare_data(uploaded_df):
    if uploaded_df is None or uploaded_df.empty:
        return None, ["The uploaded CSV is empty."]

    df = uploaded_df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    errors = []
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        return None, ["Missing required columns: " + ", ".join(missing)]

    # Minimize exposure: ignore every field not required for these analytics.
    ignored = [c for c in df.columns if c not in ALLOWED_INPUT_COLUMNS]
    
    df = df[[c for c in df.columns if c in ALLOWED_INPUT_COLUMNS]].copy()

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in ["units_sold", "selling_price", "unit_cost"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if "stock_on_hand" in df.columns:
        df["stock_on_hand"] = pd.to_numeric(df["stock_on_hand"], errors="coerce")
    if "product" not in df.columns:
        df["product"] = "Unspecified product"
    df["product"] = df["product"].fillna("Unspecified product").astype(str).str.strip()

    before = len(df)
    df = df.dropna(subset=REQUIRED_COLUMNS)
    removed = before - len(df)
    if removed:
        errors.append(f"{removed} row(s) were excluded because required values were missing or invalid.")
    if df.empty:
        return None, errors + ["No valid rows remain after data validation."]
    if (df["units_sold"] < 0).any():
        errors.append("Negative units_sold values were found. Check whether returns are represented correctly.")
    if (df["selling_price"] < 0).any() or (df["unit_cost"] < 0).any():
        errors.append("Negative price or cost values were found. Review those records.")

    df["revenue"] = df["units_sold"] * df["selling_price"]
    df["estimated_cost"] = df["units_sold"] * df["unit_cost"]
    df["gross_profit"] = df["revenue"] - df["estimated_cost"]
    df["gross_margin_pct"] = np.where(df["revenue"] != 0, df["gross_profit"] / df["revenue"] * 100, np.nan)
    df["date"] = df["date"].dt.normalize()
    return df.sort_values("date").reset_index(drop=True), errors


def daily_summary(df):
    daily = df.groupby("date", as_index=False).agg(
        units_sold=("units_sold", "sum"),
        revenue=("revenue", "sum"),
        estimated_cost=("estimated_cost", "sum"),
        gross_profit=("gross_profit", "sum"),
    )
    daily["gross_margin_pct"] = np.where(daily["revenue"] != 0, daily["gross_profit"] / daily["revenue"] * 100, np.nan)
    return daily.sort_values("date").reset_index(drop=True)


def product_summary(df):
    summary = df.groupby("product", dropna=False, as_index=False).agg(
        units_sold=("units_sold", "sum"),
        revenue=("revenue", "sum"),
        estimated_cost=("estimated_cost", "sum"),
        gross_profit=("gross_profit", "sum"),
    )
    summary["gross_margin_pct"] = np.where(summary["revenue"] != 0, summary["gross_profit"] / summary["revenue"] * 100, np.nan)
    return summary.sort_values("revenue", ascending=False).reset_index(drop=True)


def historical_forecast_test(daily, horizon=7):
    """Hold out the last horizon daily records and compare two simple baselines."""
    if len(daily) < max(14, horizon * 2):
        return None
    units = daily["units_sold"].to_numpy(dtype=float)
    start = len(units) - horizon
    actual = units[start:]
    moving_preds, weekly_preds = [], []
    for i in range(horizon):
        history = units[:start + i]
        moving_preds.append(float(np.mean(history[-7:])))
        weekly_index = start + i - 7
        weekly_preds.append(float(units[weekly_index]) if weekly_index >= 0 else float(np.mean(history)))
    moving_mae = float(np.mean(np.abs(actual - np.array(moving_preds))))
    weekly_mae = float(np.mean(np.abs(actual - np.array(weekly_preds))))
    return pd.DataFrame({
        "Forecast method": ["7-day moving average", "Same weekday last week"],
        "Mean absolute error (units)": [moving_mae, weekly_mae],
    })


def forecast_next_week(daily, periods=7):
    last_date = daily["date"].max()
    recent = daily.tail(min(7, len(daily)))
    avg_units = float(recent["units_sold"].mean())
    avg_revenue = float(recent["revenue"].mean())
    future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=periods)
    return pd.DataFrame({
        "Date": future_dates,
        "Forecast units": [avg_units] * periods,
        "Forecast revenue": [avg_revenue] * periods,
    }), avg_units, avg_revenue


def build_pdf_report(df, daily, forecast, accuracy, business_name):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=landscape(A4), rightMargin=34, leftMargin=34,
        topMargin=32, bottomMargin=34,
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ICBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.5, leading=12, textColor=colors.HexColor("#334155"), alignment=TA_LEFT))
    styles.add(ParagraphStyle(name="ICSmall", parent=styles["BodyText"], fontSize=7, leading=9, textColor=colors.HexColor("#64748b")))
    story = []
    total_revenue = float(df["revenue"].sum())
    total_profit = float(df["gross_profit"].sum())
    total_units = float(df["units_sold"].sum())
    total_cost = float(df["estimated_cost"].sum())
    margin = total_profit / total_revenue * 100 if total_revenue else 0
    start_date, end_date = df["date"].min().strftime("%d %b %Y"), df["date"].max().strftime("%d %b %Y")

    story.append(Paragraph("NURTURA | BUSINESS INTELLIGENCE REPORT", styles["Title"]))
    story.append(Spacer(1, 5))
    story.append(Paragraph(f"{business_name} &nbsp; • &nbsp; {start_date} – {end_date}", styles["ICBody"]))
    story.append(Spacer(1, 16))
    story.append(Paragraph("Executive summary", styles["Heading2"]))
    story.append(Paragraph(
        f"Across {len(df):,} valid records, the dataset shows {money(total_revenue)} in recorded revenue, "
        f"{money(total_profit)} in estimated gross profit, and {number(total_units)} units sold. "
        f"The calculated gross margin is {margin:.1f}%. These are calculated from the uploaded data and are not audited financial statements.",
        styles["ICBody"],
    ))
    story.append(Spacer(1, 12))
    kpis = [
        ["Revenue", "Estimated cost", "Gross profit", "Gross margin", "Units sold"],
        [money(total_revenue), money(total_cost), money(total_profit), f"{margin:.1f}%", number(total_units)],
    ]
    kpi_table = Table(kpis, colWidths=[145] * 5)
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#172b4d")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#eef4ff")),
        ("TEXTCOLOR", (0, 1), (-1, 1), colors.HexColor("#172b4d")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#cbd5e1")),
        ("PADDING", (0, 0), (-1, -1), 9),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 18))

    # Vector chart of recent daily revenue
    recent = daily.tail(30)
    if not recent.empty:
        story.append(Paragraph("Daily revenue — most recent 30 recorded days", styles["Heading2"]))
        drawing = Drawing(720, 190)
        chart = VerticalBarChart()
        chart.x = 42
        chart.y = 30
        chart.height = 125
        chart.width = 650
        chart.data = [tuple(float(x) for x in recent["revenue"].tolist())]
        chart.categoryAxis.categoryNames = [d.strftime("%d %b") for d in recent["date"]]
        chart.categoryAxis.labels.angle = 45
        chart.categoryAxis.labels.fontSize = 6
        chart.valueAxis.labels.fontSize = 7
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = max(1, float(recent["revenue"].max()) * 1.15)
        chart.valueAxis.valueStep = max(1, chart.valueAxis.valueMax / 4)
        chart.bars[0].fillColor = colors.HexColor("#3478f6")
        chart.strokeColor = colors.HexColor("#cbd5e1")
        drawing.add(chart)
        story.append(drawing)
        story.append(Spacer(1, 10))

    products = product_summary(df)
    story.append(Paragraph("Product performance", styles["Heading2"]))
    product_data = [["Product", "Units sold", "Revenue", "Estimated cost", "Gross profit", "Margin"]]
    for _, row in products.head(15).iterrows():
        product_data.append([
            str(row["product"])[:38], number(row["units_sold"]), money(row["revenue"]),
            money(row["estimated_cost"]), money(row["gross_profit"]),
            f"{row['gross_margin_pct']:.1f}%" if pd.notna(row["gross_margin_pct"]) else "—",
        ])
    ptable = Table(product_data, repeatRows=1, colWidths=[180, 70, 100, 100, 100, 65])
    ptable.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#172b4d")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f8fc")]),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(ptable)
    story.append(Spacer(1, 15))

    if not forecast.empty:
        story.append(Paragraph("Next seven days — baseline forecast", styles["Heading2"]))
        story.append(Paragraph(
            "This forecast repeats the recent average daily units and revenue. It is a simple baseline, not a guarantee and not a trained machine-learning prediction.", styles["ICBody"]
        ))
        story.append(Spacer(1, 6))
        fdata = [["Date", "Forecast units", "Forecast revenue"]]
        for _, row in forecast.iterrows():
            fdata.append([row["Date"].strftime("%d %b %Y"), number(row["Forecast units"], 1), money(row["Forecast revenue"])])
        ftable = Table(fdata, repeatRows=1, colWidths=[170, 170, 170])
        ftable.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#172b4d")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#cbd5e1")),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(ftable)
        story.append(Spacer(1, 12))

    if accuracy is not None:
        story.append(Paragraph("Historical forecast evaluation", styles["Heading2"]))
        story.append(Paragraph("Lower mean absolute error (MAE) indicates a smaller average absolute error on the tested historical period. This comparison alone does not establish which method will perform best in the future.", styles["ICBody"]))
        story.append(Spacer(1, 6))
        adata = [["Method", "Mean absolute error (units)"]]
        for _, row in accuracy.iterrows():
            adata.append([row["Forecast method"], f"{row['Mean absolute error (units)']:.2f}"])
        atable = Table(adata, colWidths=[280, 220])
        atable.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#172b4d")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#cbd5e1")),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(atable)

    if "stock_on_hand" in df.columns:
        stock = df.dropna(subset=["stock_on_hand"])
        if not stock.empty:
            story.append(Spacer(1, 14))
            story.append(Paragraph("Inventory review", styles["Heading2"]))
            inv = stock.groupby("product", as_index=False).agg(stock_on_hand=("stock_on_hand", "min"))
            inv["status"] = inv["stock_on_hand"].apply(lambda x: "Out of stock" if x <= 0 else "Low stock" if x <= 10 else "In stock")
            low = inv[inv["status"].isin(["Out of stock", "Low stock"])].sort_values("stock_on_hand")
            if low.empty:
                story.append(Paragraph("No product falls at or below the low-stock threshold of 10 units in the supplied records.", styles["ICBody"]))
            else:
                idata = [["Product", "Lowest recorded stock", "Status"]]
                for _, row in low.head(15).iterrows():
                    idata.append([str(row["product"])[:38], number(row["stock_on_hand"]), row["status"]])
                itable = Table(idata, repeatRows=1, colWidths=[250, 160, 180])
                itable.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#172b4d")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#cbd5e1")),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]))
                story.append(itable)

    story.append(Spacer(1, 20))
    story.append(Paragraph("Methodology and limitations", styles["Heading2"]))
    story.append(Paragraph(
        "Revenue is calculated as units sold × selling price. Estimated cost is units sold × unit cost. Gross profit is revenue minus estimated cost; it excludes operating expenses, taxes, returns not represented in the data, and other accounting adjustments. Stock status uses the lowest supplied stock_on_hand value per product and a configurable illustrative threshold of 10. Verify all inputs before using this report for operational or financial decisions.",
        styles["ICSmall"],
    ))
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def section_heading(eyebrow, title, subtitle=None):
    st.markdown(f'<div class="ic-eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.title(title)
    if subtitle:
        st.markdown(f'<div class="ic-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def render_home(df, daily, products, forecast, avg_units, avg_revenue):
    """Compact executive overview: aligned sections, reduced whitespace, fast scan."""
    section_heading(
        "EXECUTIVE WORKSPACE / OVERVIEW",
        "Executive overview",
        "Sales, profitability, product contribution, and business signals in one workspace."
    )
    revenue = float(df["revenue"].sum())
    cost = float(df["estimated_cost"].sum())
    profit = float(df["gross_profit"].sum())
    margin = profit / revenue * 100 if revenue else 0.0
    units = float(df["units_sold"].sum())
    product_count = int(df["product"].nunique())
    recorded_days = int(df["date"].nunique())

    kpis = st.columns(4)
    kpis[0].metric("Recorded revenue", money(revenue))
    kpis[1].metric("Estimated gross profit", money(profit))
    kpis[2].metric("Gross margin", f"{margin:.1f}%")
    kpis[3].metric("Units sold", number(units))

    st.markdown("### Executive summary")
    st.markdown(
        '<div class="ic-panel"><div class="ic-muted" style="text-transform:uppercase;letter-spacing:.12em;font-weight:750;margin-bottom:5px">Performance snapshot</div>'
        f'<div style="font-size:.93rem;line-height:1.55;color:#dce6f5">Across <b style="color:#fff">{recorded_days:,} recorded days</b> and '
        f'<b style="color:#fff">{product_count:,} products</b>, the selected data records <b style="color:#fff">{money(revenue)}</b> revenue and '
        f'<b style="color:#fff">{money(profit)}</b> estimated gross profit from <b style="color:#fff">{money(cost)}</b> estimated product costs. '
        f'Gross margin is <b style="color:#7ce7c5">{margin:.1f}%</b>. Gross profit excludes operating expenses and taxes.</div></div>',
        unsafe_allow_html=True
    )

    # First row: two core views, kept at equal compact heights.
    top_left, top_right = st.columns([1.35, 1])
    with top_left:
        st.markdown("### Revenue performance")
        st.caption("Daily recorded revenue")
        trend = line_figure(daily, "date", "revenue", height=250)
        trend.update_traces(line=dict(color=CHART_COLORS[0], width=2.5), marker=dict(size=3))
        st.plotly_chart(trend, use_container_width=True, config={"displaylogo": False})
    with top_right:
        st.markdown("### Revenue by product")
        st.caption("Top products by recorded revenue")
        top_products = products.head(6).sort_values("revenue", ascending=True)
        fig = px.bar(top_products, x="revenue", y="product", orientation="h", text="revenue",
                     color="revenue", color_continuous_scale=[[0, "#4269b2"], [1, "#7da2ff"]])
        fig.update_traces(texttemplate="₹%{x:,.0f}", textposition="outside", cliponaxis=False,
                          hovertemplate="%{y}<br>Revenue: ₹%{x:,.2f}<extra></extra>")
        fig.update_layout(coloraxis_showscale=False, margin=dict(l=5, r=30, t=5, b=5))
        fig.update_xaxes(title=None, showgrid=True, gridcolor=CHART_GRID, tickformat="~s")
        fig.update_yaxes(title=None, showgrid=False)
        st.plotly_chart(polish_chart(fig, height=250, show_legend=False), use_container_width=True,
                        config={"displaylogo": False})

    # Second row: three visual summaries only. Pulse is moved below this row to remove
    # the large empty area created when a tall insight column shared a row with charts.
    bottom_left, bottom_mid, bottom_right = st.columns(3)
    with bottom_left:
        st.markdown("### Cost vs. profit")
        mix = pd.DataFrame({"Metric": ["Estimated cost", "Gross profit"], "Amount": [cost, profit]})
        fig = px.pie(mix, names="Metric", values="Amount", hole=.58, color="Metric",
                     color_discrete_map={"Estimated cost": CHART_COLORS[2], "Gross profit": CHART_COLORS[1]})
        fig.update_traces(textposition="inside", textinfo="label+percent",
                          hovertemplate="%{label}<br>₹%{value:,.2f}<extra></extra>",
                          marker=dict(line=dict(color="#0a101b", width=3)))
        fig.update_layout(margin=dict(l=2, r=2, t=3, b=3), showlegend=False)
        st.plotly_chart(polish_chart(fig, height=220, show_legend=False), use_container_width=True,
                        config={"displaylogo": False})
    with bottom_mid:
        st.markdown("### Gross profit by product")
        profit_products = products.sort_values("gross_profit", ascending=True).tail(5)
        fig = px.bar(profit_products, x="gross_profit", y="product", orientation="h", text="gross_profit")
        fig.update_traces(marker_color=CHART_COLORS[1], texttemplate="₹%{x:,.0f}", textposition="outside",
                          cliponaxis=False, hovertemplate="%{y}<br>Gross profit: ₹%{x:,.2f}<extra></extra>")
        fig.update_layout(margin=dict(l=2, r=28, t=3, b=5))
        fig.update_xaxes(title=None, tickformat="~s", gridcolor=CHART_GRID)
        fig.update_yaxes(title=None, showgrid=False)
        st.plotly_chart(polish_chart(fig, height=220, show_legend=False), use_container_width=True,
                        config={"displaylogo": False})
    with bottom_right:
        st.markdown("### Sales mix")
        # Show the top five products' revenue share as a compact complementary view.
        mix_products = products.sort_values("revenue", ascending=False).head(5)
        fig = px.pie(mix_products, names="product", values="revenue", hole=.48,
                     color_discrete_sequence=CHART_COLORS)
        fig.update_traces(textposition="inside", textinfo="percent",
                          hovertemplate="%{label}<br>Revenue: ₹%{value:,.2f}<extra></extra>",
                          marker=dict(line=dict(color="#0a101b", width=2)))
        fig.update_layout(margin=dict(l=2, r=2, t=3, b=3), showlegend=True,
                          legend=dict(font=dict(size=9), orientation="h", yanchor="bottom", y=-.12))
        st.plotly_chart(polish_chart(fig, height=220, show_legend=True), use_container_width=True,
                        config={"displaylogo": False})

    # Compact horizontal insight strip; no tall sidebar to create a blank column below charts.
    st.markdown("### NURTURA Pulse")
    signals = []
    if len(daily) >= 14:
        current = float(daily.tail(7)["revenue"].mean())
        previous = float(daily.iloc[-14:-7]["revenue"].mean())
        if previous > 0:
            change = (current - previous) / previous * 100
            if change >= 3:
                signals.append(("Revenue momentum", f"Daily average up {change:.1f}% vs prior 7 days."))
            elif change <= -3:
                signals.append(("Revenue to review", f"Daily average down {abs(change):.1f}%; review demand and pricing."))
            else:
                signals.append(("Revenue trend", f"Broadly stable ({change:+.1f}%) vs prior 7 days."))
    if not products.empty:
        leader = products.sort_values("revenue", ascending=False).iloc[0]
        profit_leader = products.sort_values("gross_profit", ascending=False).iloc[0]
        signals.append(("Revenue leader", f"{leader['product']}: {money(leader['revenue'])}."))
        signals.append(("Profit leader", f"{profit_leader['product']}: {money(profit_leader['gross_profit'])}."))
    if "stock_on_hand" in df.columns:
        stock = df.dropna(subset=["stock_on_hand"]).groupby("product")["stock_on_hand"].min()
        low_stock = stock[stock <= 10]
        if len(low_stock):
            signals.append(("Inventory check", f"{len(low_stock)} product(s) have minimum stock ≤ 10."))
    if not signals:
        signals.append(("Data note", "Add more daily records to compare revenue momentum."))
    pulse_cols = st.columns(min(4, len(signals)))
    for i, (label, message) in enumerate(signals[:4]):
        with pulse_cols[i]:
            st.markdown(f'<div class="ic-alert"><b>{label}</b><br><span style="font-size:.88rem">{message}</span></div>',
                        unsafe_allow_html=True)
    st.caption("Signals are descriptive, not causal predictions. Check source data before acting.")

    st.markdown("### Recent daily performance")
    recent = daily.tail(7).sort_values("date", ascending=False).copy()
    recent["date"] = recent["date"].dt.strftime("%d %b %Y")
    display_table(recent.rename(columns={
        "date": "Date", "units_sold": "Units sold", "revenue": "Revenue",
        "estimated_cost": "Estimated cost", "gross_profit": "Gross profit",
        "gross_margin_pct": "Gross margin (%)"
    }), height=230, formats={
        "Units sold": "{:,.0f}", "Revenue": "₹{:,.2f}",
        "Estimated cost": "₹{:,.2f}", "Gross profit": "₹{:,.2f}",
        "Gross margin (%)": "{:.1f}%"
    })
    st.caption("Filtered records only · Revenue = units × selling price · Gross profit excludes operating expenses and taxes.")


def main():
    # Streamlit sessions are isolated by the server's session context. This app does not
    # use shared caches or write uploaded business data to application files.
    st.session_state.setdefault("_nurtura_reset_count", 0)
    upload_key = f"sales_upload_{st.session_state['_nurtura_reset_count']}"

    with st.sidebar:
        st.markdown("""
        <div class="ic-brand">
          <div class="ic-brand-mark">N</div>
          <div><div class="ic-brand-name">NURTURA</div><div class="ic-brand-sub">Business Intelligence</div></div>
        </div>
        <div style="margin-bottom:14px"><span class="ic-status">● Workspace ready</span></div>
        <div class="ic-section-label">Workspace</div>
        """, unsafe_allow_html=True)
        nav_labels = {
            "Home": "▦   Overview",
            "Summary": "✦   Summary",
            "Sales Analytics": "↗   Sales Analytics",
            "Products & Profitability": "◇   Products & Profitability",
            "Inventory": "⬡   Inventory",
            "Forecast & Insights": "⌁   Forecasts",
            "Profit Tracker": "◷  Profit Tracker",
            "Reports": "▤   Reports",
            "Team & Settings": "⚙   Settings",
            "Data Explorer": "⌕   Data Explorer",
        }
        page = st.radio("Navigate", NAV_ITEMS, format_func=lambda item: nav_labels[item], label_visibility="collapsed")
        st.divider()
        st.markdown("<div class='ic-section-label'>Data source</div>", unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Sales data · CSV", type=["csv"], key=upload_key,
            help="Required: date, units_sold, selling_price, unit_cost. Optional: product, stock_on_hand. Max 10 MiB / 100,000 rows."
        )
        use_demo = st.toggle("Load sample workspace", value=uploaded is None, key="use_demo_workspace", help="Uses synthetic demonstration data, not real business records.")
        st.button(
            "End session & clear app data", key="clear_workspace_button",
            on_click=clear_workspace_state, use_container_width=True,
            help="Clears app session state and resets the upload widget for this browser session."
        )
        st.caption("Privacy mode · do not upload customer names, emails, phone numbers, payment details, or other unnecessary personal data.")

    raw = None
    validation_notes = []
    if uploaded is not None:
        if uploaded.size > MAX_UPLOAD_BYTES:
            st.error("Upload rejected: the CSV exceeds the 10 MiB limit. Export a smaller, aggregated file and try again.")
            st.stop()
        try:
            uploaded.seek(0)
            raw = pd.read_csv(uploaded, nrows=MAX_UPLOAD_ROWS + 1, low_memory=False)
        except Exception:
            # Avoid showing parser details that may contain data fragments or local paths.
            st.error("Could not safely read this CSV. Check that it is a valid UTF-8/standard CSV file with a header row, then try again.")
            st.stop()
        if len(raw) > MAX_UPLOAD_ROWS:
            st.error("Upload rejected: the CSV exceeds 100,000 rows. Use a smaller or aggregated file.")
            st.stop()
        if len(raw.columns) > MAX_UPLOAD_COLUMNS:
            st.error("Upload rejected: the CSV has more than 50 columns. Keep only the fields needed for sales analysis.")
            st.stop()
    elif use_demo:
        raw = make_demo_data()
    else:
        st.markdown("# Welcome to NURTURA")
        st.write("Upload a sales CSV from the sidebar to start analyzing your business.")
        st.info("Required columns: date, units_sold, selling_price, unit_cost. Optional columns: product, stock_on_hand, order_id.")
        st.stop()

    df, validation_notes = prepare_data(raw)
    if df is None:
        st.error("The data could not be prepared.")
        for note in validation_notes:
            st.warning(note)
        st.stop()
    for note in validation_notes:
        st.warning(note)
   
    daily = daily_summary(df)
    products = product_summary(df)
    forecast, avg_units, avg_revenue = forecast_next_week(daily)
    accuracy = historical_forecast_test(daily)
    business_name = st.session_state.get("business_name", "My Business")

    # Global filters affect analytics/reporting consistently.
    with st.sidebar:
        st.markdown("<div class='ic-section-label'>Global filters</div>", unsafe_allow_html=True)
        min_date = daily["date"].min().date()
        max_date = daily["date"].max().date()
        date_range = st.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        if "product" in df.columns:
            product_options = sorted(df["product"].dropna().astype(str).unique().tolist())
            selected_products = st.multiselect("Products", product_options, default=product_options)
        else:
            selected_products = []

    filtered = df.copy()
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        filtered = filtered[(filtered["date"].dt.date >= date_range[0]) & (filtered["date"].dt.date <= date_range[1])]
    if selected_products:
        filtered = filtered[filtered["product"].isin(selected_products)]
    if filtered.empty:
        st.warning("No records match these filters. Change the date range or product selection.")
        st.stop()
    daily = daily_summary(filtered)
    products = product_summary(filtered)
    forecast, avg_units, avg_revenue = forecast_next_week(daily)
    accuracy = historical_forecast_test(daily)

    if page == "Home":
        render_home(filtered, daily, products, forecast, avg_units, avg_revenue)

    elif page == "Summary":
        section_heading("DECISIONS / SUMMARY", "Business summary", "A decision-focused briefing based on the selected records.")
        total_revenue = float(filtered["revenue"].sum())
        total_profit = float(filtered["gross_profit"].sum())
        total_cost = float(filtered["estimated_cost"].sum())
        total_units = float(filtered["units_sold"].sum())
        margin = total_profit / total_revenue * 100 if total_revenue else 0
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Revenue", money(total_revenue))
        m2.metric("Estimated gross profit", money(total_profit))
        m3.metric("Gross margin", f"{margin:.1f}%")
        m4.metric("Units sold", number(total_units))
        st.markdown("### Executive readout")
        st.markdown(f'<div class="ic-panel"><b>Performance snapshot</b><br>Across <b>{filtered["date"].nunique():,}</b> recorded days and <b>{filtered["product"].nunique():,}</b> products, the selected records show <b>{money(total_revenue)}</b> revenue and <b>{money(total_profit)}</b> estimated gross profit. Estimated product costs are <b>{money(total_cost)}</b>. Gross profit excludes operating expenses and taxes.</div>', unsafe_allow_html=True)
        if len(daily) >= 14:
            recent_rev = float(daily.tail(7)["revenue"].mean())
            previous_rev = float(daily.iloc[-14:-7]["revenue"].mean())
            recent_profit = float(daily.tail(7)["gross_profit"].mean())
            previous_profit = float(daily.iloc[-14:-7]["gross_profit"].mean())
            rev_change = ((recent_rev - previous_rev) / previous_rev * 100) if previous_rev else 0
            profit_change = ((recent_profit - previous_profit) / abs(previous_profit) * 100) if previous_profit else 0
            c1, c2 = st.columns(2)
            c1.metric("Average daily revenue · latest 7 days", money(recent_rev), f"{rev_change:+.1f}% vs prior 7 days")
            c2.metric("Average daily gross profit · latest 7 days", money(recent_profit), f"{profit_change:+.1f}% vs prior 7 days")
            st.markdown("### Signals to review")
            if rev_change < -5:
                st.warning(f"Revenue momentum: recent average daily revenue is down {abs(rev_change):.1f}%. Check product mix, sales volume and data completeness.")
            elif rev_change > 5:
                st.success(f"Revenue momentum: recent average daily revenue is up {rev_change:.1f}%. Check that stock can support demand.")
            else:
                st.info(f"Revenue momentum is relatively stable ({rev_change:+.1f}%). Consider product-level changes before making broad decisions.")
        else:
            st.info("Trend comparisons need at least 14 recorded daily observations. Current totals are still available.")
        if not products.empty:
            best_rev = products.sort_values("revenue", ascending=False).iloc[0]
            best_profit = products.sort_values("gross_profit", ascending=False).iloc[0]
            lowest_margin = products[products["revenue"] > 0].sort_values("gross_margin_pct").head(1)
            x1, x2, x3 = st.columns(3)
            x1.metric("Revenue leader", str(best_rev["product"]), money(best_rev["revenue"]))
            x2.metric("Gross-profit leader", str(best_profit["product"]), money(best_profit["gross_profit"]))
            if not lowest_margin.empty:
                x3.metric("Lowest-margin product", str(lowest_margin.iloc[0]["product"]), f"{lowest_margin.iloc[0]["gross_margin_pct"]:.1f}%")
        st.markdown("### Suggested review checklist")
        for item in [
            "Check products with falling revenue or margin before changing prices.",
            "Verify unit costs and selling prices are current and use a consistent currency.",
            "Review stock availability before increasing promotion or demand generation.",
            "Use the Forecasts page as a baseline estimate, not a guarantee.",
            "Upload expense records before treating gross profit as an expense-adjusted result.",
        ]:
            st.markdown(f"- {item}")
        st.markdown("### What-if scenario planner")
        st.caption("Explore hypothetical changes using current units and unit economics. This is a scenario, not a prediction of customer response.")
        sc1, sc2 = st.columns(2)
        with sc1:
            price_change_pct = st.slider("Hypothetical selling-price change (%)", min_value=-20, max_value=20, value=0, step=1)
        with sc2:
            cost_change_pct = st.slider("Hypothetical unit-cost change (%)", min_value=-20, max_value=20, value=0, step=1)
        scenario_revenue = float(filtered["revenue"].sum()) * (1 + price_change_pct / 100)
        scenario_cost = float(filtered["estimated_cost"].sum()) * (1 + cost_change_pct / 100)
        scenario_profit = scenario_revenue - scenario_cost
        q1, q2, q3 = st.columns(3)
        q1.metric("Scenario revenue", money(scenario_revenue), f"{price_change_pct:+d}% price assumption")
        q2.metric("Scenario cost", money(scenario_cost), f"{cost_change_pct:+d}% cost assumption")
        q3.metric("Scenario gross profit", money(scenario_profit), money(scenario_profit - total_profit) + " vs current")
        st.caption("This simple scenario holds sales volume constant. It does not model price elasticity, competitor responses, taxes, operating expenses or changes in demand.")
        st.caption("Recommendations are descriptive prompts based on the uploaded records, not causal conclusions or financial advice.")

    elif page == "Sales Analytics":
        section_heading("ANALYTICS / SALES", "Sales analytics", "Explore revenue, sales volume, costs, and profitability over time.")
        a, b, c, d = st.columns(4)
        a.metric("Revenue", money(filtered["revenue"].sum()))
        b.metric("Estimated cost", money(filtered["estimated_cost"].sum()))
        c.metric("Gross profit", money(filtered["gross_profit"].sum()))
        margin = filtered["gross_profit"].sum() / filtered["revenue"].sum() * 100 if filtered["revenue"].sum() else 0
        d.metric("Gross margin", f"{margin:.1f}%")
        if len(daily) >= 14:
            latest = daily.tail(7)
            previous = daily.iloc[-14:-7]
            r0, r1, r2 = st.columns(3)
            prev_rev = float(previous["revenue"].sum())
            change_rev = ((float(latest["revenue"].sum()) - prev_rev) / prev_rev * 100) if prev_rev else 0
            prev_profit = float(previous["gross_profit"].sum())
            change_profit = ((float(latest["gross_profit"].sum()) - prev_profit) / abs(prev_profit) * 100) if prev_profit else 0
            r0.metric("Revenue · latest 7 days", money(latest["revenue"].sum()), f"{change_rev:+.1f}% vs prior 7 days")
            r1.metric("Gross profit · latest 7 days", money(latest["gross_profit"].sum()), f"{change_profit:+.1f}% vs prior 7 days")
            r2.metric("Recorded days", f"{len(daily):,}")
        st.markdown("### Revenue and gross profit over time")
        fig = line_figure(daily, "date", ["revenue", "gross_profit"], labels={"revenue": "Revenue", "gross_profit": "Gross profit"}, height=390)
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
        left, right = st.columns(2)
        with left:
            st.markdown("### Daily units sold")
            fig = bar_figure(daily, "date", "units_sold", color=CHART_COLORS[1], height=340)
            st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
        with right:
            st.markdown("### Cost and profit mix")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=daily["date"], y=daily["estimated_cost"], name="Estimated cost", marker_color=CHART_COLORS[2]))
            fig.add_trace(go.Bar(x=daily["date"], y=daily["gross_profit"], name="Gross profit", marker_color=CHART_COLORS[1]))
            fig.update_layout(barmode="group")
            fig.update_xaxes(tickformat="%d %b", tickangle=-25, showgrid=False)
            fig.update_yaxes(tickformat=",.0f", gridcolor=CHART_GRID)
            st.plotly_chart(polish_chart(fig, height=340), use_container_width=True, config={"displaylogo": False})
        st.markdown("### Daily performance table")
        display_table(daily, height=390, formats={"revenue": "₹{:,.2f}", "estimated_cost": "₹{:,.2f}", "gross_profit": "₹{:,.2f}", "gross_margin_pct": "{:.1f}%", "units_sold": "{:,.0f}"})
        st.markdown("### Weekday and weekend pattern")
        weekday_df = filtered.assign(day_type=np.where(filtered["date"].dt.dayofweek >= 5, "Weekend", "Weekday"))
        weekday_summary = weekday_df.groupby("day_type", as_index=False).agg(revenue=("revenue", "sum"), units_sold=("units_sold", "sum"), gross_profit=("gross_profit", "sum"), recorded_days=("date", "nunique"))
        if not weekday_summary.empty:
            weekday_summary["revenue_per_recorded_day"] = weekday_summary["revenue"] / weekday_summary["recorded_days"].replace(0, np.nan)
            display_table(weekday_summary, height=180, formats={"revenue": "₹{:,.2f}", "gross_profit": "₹{:,.2f}", "revenue_per_recorded_day": "₹{:,.2f}", "units_sold": "{:,.0f}"})
        st.caption("Weekday/weekend comparisons use the dates in the selected records. Interpret carefully if some dates are missing.")
        st.markdown("### Unusual daily movements")
        if len(daily) >= 14:
            baseline = daily.iloc[:-7]["revenue"]
            base_mean = float(baseline.mean())
            base_std = float(baseline.std(ddof=0))
            recent = daily.tail(7).copy()
            if base_std > 0:
                recent["baseline_z_score"] = (recent["revenue"] - base_mean) / base_std
                unusual = recent[recent["baseline_z_score"].abs() >= 2].copy()
            else:
                unusual = pd.DataFrame()
            if unusual.empty:
                st.info("No recent days crossed the simple two-standard-deviation review threshold.")
            else:
                display_table(unusual[["date", "revenue", "gross_profit", "baseline_z_score"]], height=220, formats={"revenue": "₹{:,.2f}", "gross_profit": "₹{:,.2f}", "baseline_z_score": "{:.2f}"})
            st.caption("This is a simple statistical flag, not proof of an error or cause. Seasonality and promotions may explain unusual values.")
        else:
            st.info("At least 14 recorded days are needed for a basic unusual-movement check.")

    elif page == "Products & Profitability":
        section_heading("ANALYTICS / PRODUCTS", "Products & profitability", "Find which products contribute revenue and estimated gross profit.")
        display_table(products, height=390, formats={"revenue": "₹{:,.2f}", "estimated_cost": "₹{:,.2f}", "gross_profit": "₹{:,.2f}", "gross_margin_pct": "{:.1f}%", "units_sold": "{:,.0f}"})
        left, right = st.columns(2)
        with left:
            st.markdown("### Revenue by product")
            fig = bar_figure(products.sort_values("revenue"), "revenue", "product", horizontal=True, color=CHART_COLORS[0], height=390)
            st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
        with right:
            st.markdown("### Gross profit by product")
            fig = bar_figure(products.sort_values("gross_profit"), "gross_profit", "product", horizontal=True, color=CHART_COLORS[1], height=390)
            st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
        if not products.empty:
            top = products.iloc[0]
            best_profit = products.sort_values("gross_profit", ascending=False).iloc[0]
            st.markdown("### Product takeaways")
            st.markdown(f'<div class="ic-alert"><b>Revenue leader</b><br>{top["product"]} — {money(top["revenue"])} revenue.</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ic-alert"><b>Gross-profit leader</b><br>{best_profit["product"]} — {money(best_profit["gross_profit"])} gross profit.</div>', unsafe_allow_html=True)
            st.markdown("### Product action matrix")
            matrix = products.copy()
            median_rev = matrix["revenue"].median()
            median_margin = matrix["gross_margin_pct"].median()
            matrix["Revenue tier"] = np.where(matrix["revenue"] >= median_rev, "Higher revenue", "Lower revenue")
            matrix["Margin tier"] = np.where(matrix["gross_margin_pct"] >= median_margin, "Higher margin", "Lower margin")
            matrix["Review prompt"] = np.select(
                [(matrix["revenue"] >= median_rev) & (matrix["gross_margin_pct"] >= median_margin),
                 (matrix["revenue"] >= median_rev) & (matrix["gross_margin_pct"] < median_margin),
                 (matrix["revenue"] < median_rev) & (matrix["gross_margin_pct"] >= median_margin)],
                ["Protect availability", "Review cost and pricing", "Review visibility and demand"],
                default="Review demand and unit economics"
            )
            display_table(matrix[["product", "revenue", "gross_profit", "gross_margin_pct", "Revenue tier", "Margin tier", "Review prompt"]], height=320, formats={"revenue": "₹{:,.2f}", "gross_profit": "₹{:,.2f}", "gross_margin_pct": "{:.1f}%"})
            st.caption("Tiers use medians within the current selection. They are prompts for investigation, not automatic pricing or discontinuation decisions.")

    elif page == "Inventory":
        section_heading("OPERATIONS / STOCK", "Inventory intelligence", "Understand stock health, reorder priorities and slow-moving products using supplied stock data.")
        if "stock_on_hand" not in filtered.columns:
            st.warning("This dataset has no stock_on_hand column. Upload a CSV with current stock counts to enable inventory insights.")
            st.markdown("### Recommended inventory fields")
            display_table(pd.DataFrame({"Field": ["product", "stock_on_hand", "date", "units_sold", "unit_cost"], "Purpose": ["Identify products", "Current units available", "Measure demand history", "Calculate sales velocity", "Estimate stock value at cost"]}), height=230)
            st.info("Advanced reorder planning also benefits from reorder_level, lead_time_days, supplier and minimum_order_qty. These fields are not currently consumed by the upload validator.")
        else:
            threshold = st.slider("Low-stock alert threshold (units)", min_value=1, max_value=100, value=10, step=1)
            lead_days = st.slider("Planning lead time (days)", min_value=1, max_value=45, value=7, step=1)
            safety_days = st.slider("Safety-stock buffer (days)", min_value=0, max_value=30, value=3, step=1)
            inv_source = filtered.dropna(subset=["stock_on_hand"]).copy()
            inv = inv_source.groupby("product", as_index=False).agg(
                stock_on_hand=("stock_on_hand", "min"),
                units_sold=("units_sold", "sum"),
                revenue=("revenue", "sum"),
                estimated_cost=("estimated_cost", "sum"),
                unit_cost=("unit_cost", "mean"),
                active_days=("date", "nunique"),
                last_sale_date=("date", "max"),
            )
            inv["avg_daily_units"] = inv["units_sold"] / inv["active_days"].replace(0, np.nan)
            inv["days_of_stock"] = np.where(inv["avg_daily_units"] > 0, inv["stock_on_hand"] / inv["avg_daily_units"], np.nan)
            inv["inventory_value_at_cost"] = inv["stock_on_hand"] * inv["unit_cost"]
            inv["reorder_point_estimate"] = inv["avg_daily_units"].fillna(0) * (lead_days + safety_days)
            inv["suggested_reorder_units_estimate"] = np.maximum(0, np.ceil(inv["reorder_point_estimate"] - inv["stock_on_hand"]))
            inv["status"] = np.select(
                [inv["stock_on_hand"] <= 0, inv["stock_on_hand"] <= threshold, inv["days_of_stock"].notna() & (inv["days_of_stock"] < lead_days)],
                ["Out of stock", "Low stock", "Stockout risk"], default="Review stock"
            )
            inv["ABC class"] = "C"
            inv_abc = inv.sort_values("revenue", ascending=False).copy()
            if inv_abc["revenue"].sum() > 0:
                inv_abc["revenue_share_cum"] = inv_abc["revenue"].cumsum() / inv_abc["revenue"].sum()
                inv_abc["ABC class"] = np.select([inv_abc["revenue_share_cum"] <= .80, inv_abc["revenue_share_cum"] <= .95], ["A", "B"], default="C")
                inv["ABC class"] = inv["product"].map(inv_abc.set_index("product")["ABC class"])
            low = inv[inv["status"].isin(["Out of stock", "Low stock", "Stockout risk"])]
            a, b, c, d = st.columns(4)
            a.metric("Products monitored", f"{len(inv):,}")
            b.metric("Low / out / risk", f"{len(low):,}")
            c.metric("Inventory value at cost · estimate", money(inv["inventory_value_at_cost"].sum()))
            d.metric("Units in stock", number(inv["stock_on_hand"].sum()))
            tabs = st.tabs(["Inventory overview", "Reorder planner", "Demand & stockout", "Slow-moving stock", "ABC priority"])
            with tabs[0]:
                st.markdown("#### Stock health")
                if not low.empty:
                    st.warning(f"{len(low)} product(s) need review. Confirm current counts before placing orders.")
                else:
                    st.success("No products crossed the current stock thresholds in the selected records.")
                display_table(inv.sort_values(["stock_on_hand", "product"])[["product", "stock_on_hand", "status", "units_sold", "avg_daily_units", "days_of_stock", "inventory_value_at_cost"]], height=360, formats={"stock_on_hand": "{:,.0f}", "units_sold": "{:,.0f}", "avg_daily_units": "{:,.2f}", "days_of_stock": "{:,.1f}", "inventory_value_at_cost": "₹{:,.2f}"})
                fig = px.pie(inv, names="status", values="stock_on_hand", hole=.48, color_discrete_sequence=CHART_COLORS, title="Units by stock status")
                fig.update_traces(textposition="inside", textinfo="label+percent", marker=dict(line=dict(color="#0d1727", width=2)))
                st.plotly_chart(polish_chart(fig, height=320), use_container_width=True)
            with tabs[1]:
                st.markdown("#### Estimated reorder recommendations")
                st.caption("These are planning estimates from recent average sales, current stock and the lead-time assumptions above. They are not purchase orders.")
                reorder = inv[inv["suggested_reorder_units_estimate"] > 0].sort_values("suggested_reorder_units_estimate", ascending=False).copy()
                reorder["estimated_reorder_cost"] = reorder["suggested_reorder_units_estimate"] * reorder["unit_cost"]
                if reorder.empty:
                    st.success("No estimated replenishment gap under the current assumptions.")
                else:
                    display_table(reorder[["product", "stock_on_hand", "avg_daily_units", "reorder_point_estimate", "suggested_reorder_units_estimate", "estimated_reorder_cost", "status"]], height=350, formats={"stock_on_hand": "{:,.0f}", "avg_daily_units": "{:,.2f}", "reorder_point_estimate": "{:,.1f}", "suggested_reorder_units_estimate": "{:,.0f}", "estimated_reorder_cost": "₹{:,.2f}"})
                    st.metric("Estimated replenishment cost", money(reorder["estimated_reorder_cost"].sum()))
            with tabs[2]:
                st.markdown("#### Demand and stockout risk")
                risk = inv.sort_values("days_of_stock", na_position="last")
                display_table(risk[["product", "stock_on_hand", "avg_daily_units", "days_of_stock", "status"]], height=340, formats={"stock_on_hand": "{:,.0f}", "avg_daily_units": "{:,.2f}", "days_of_stock": "{:,.1f}"})
                st.caption("Days-of-stock is only an estimate; sales velocity may be distorted by missing dates, promotions, seasonality or historical stockouts.")
            with tabs[3]:
                st.markdown("#### Slow-moving products")
                slow = inv[(inv["stock_on_hand"] > 0) & ((inv["avg_daily_units"].fillna(0) <= 0) | (inv["days_of_stock"].fillna(999999) > 60))].copy()
                slow["capital_tied_up_estimate"] = slow["inventory_value_at_cost"]
                if slow.empty:
                    st.info("No product met the current slow-moving heuristic. This does not prove all inventory is selling efficiently.")
                else:
                    display_table(slow[["product", "stock_on_hand", "units_sold", "days_of_stock", "capital_tied_up_estimate", "last_sale_date"]], height=320, formats={"stock_on_hand": "{:,.0f}", "units_sold": "{:,.0f}", "days_of_stock": "{:,.1f}", "capital_tied_up_estimate": "₹{:,.2f}"})
                    st.metric("Estimated capital in flagged stock", money(slow["capital_tied_up_estimate"].sum()))
            with tabs[4]:
                st.markdown("#### ABC classification by revenue contribution")
                st.caption("A = roughly first 80% of cumulative revenue, B = next 15%, C = remaining contribution. Classification is calculated from this filtered period.")
                display_table(inv.sort_values("revenue", ascending=False)[["product", "revenue", "gross_profit" if "gross_profit" in inv.columns else "estimated_cost", "ABC class", "stock_on_hand"]], height=320, formats={"revenue": "₹{:,.2f}", "gross_profit": "₹{:,.2f}", "estimated_cost": "₹{:,.2f}", "stock_on_hand": "{:,.0f}"})
            st.caption("Stock on hand is treated as the minimum supplied value per product because it may be repeated on sales rows. Validate this interpretation against your source system before making purchasing decisions.")

    elif page == "Forecast & Insights":
        section_heading("PLANNING / FORECAST", "Forecast & insights", "A transparent baseline forecast, with a historical check when enough daily records are available.")
        horizon = st.slider("Forecast horizon (days)", min_value=7, max_value=30, value=7, step=1)
        forecast, avg_units, avg_revenue = forecast_next_week(daily, periods=horizon)
        a, b, c, d = st.columns(4)
        a.metric(f"Forecast units · {horizon} days", number(forecast["Forecast units"].sum()))
        b.metric(f"Forecast revenue · {horizon} days", money(forecast["Forecast revenue"].sum()))
        c.metric("Average daily units", number(avg_units, 1))
        d.metric("Average daily revenue", money(avg_revenue))
        st.markdown(f"### Next {horizon} days")
        fig = px.line(
            forecast,
            x="Date",
            y="Forecast units",
            markers=True,
            title=None,
        )
        fig.update_traces(
            line=dict(color=CHART_COLORS[3], width=3),
            marker=dict(size=9, color=CHART_COLORS[3]),
            hovertemplate="%{x|%d %b %Y}<br>Forecast units: %{y:.1f}<extra></extra>",
        )
        fig.update_layout(
            height=320,
            margin=dict(l=16, r=18, t=18, b=16),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#c6d2e3"),
            showlegend=False,
        )
        fig.update_xaxes(title=None, showgrid=False, tickformat="%d %b")
        fig.update_yaxes(title=None, gridcolor=CHART_GRID, rangemode="tozero")
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
        display_table(forecast, height=300, formats={"Forecast units": "{:,.1f}", "Forecast revenue": "₹{:,.2f}"})
        st.markdown("### Historical forecast accuracy")
        if accuracy is None:
            st.info("At least 14 daily records are needed to compare these baseline methods.")
        else:
            display_table(accuracy.round(2), height=180, formats={"Mean absolute error (units)": "{:.2f}"})
            best = accuracy.sort_values("Mean absolute error (units)").iloc[0]
            best_method = best["Forecast method"]
            best_mae = best["Mean absolute error (units)"]
            st.markdown(f'<div class="ic-alert"><b>Lower-error method on this test</b><br>{best_method} (MAE {best_mae:.2f} units).</div>', unsafe_allow_html=True)
        st.markdown("### Business insights")
        if len(daily) >= 14:
            current = daily.tail(7)["revenue"].mean()
            previous = daily.iloc[-14:-7]["revenue"].mean()
            if previous > 0:
                change = (current - previous) / previous * 100
                if change > 2:
                    st.success(f"Recent average daily revenue is up {change:.1f}% versus the previous seven recorded days.")
                elif change < -2:
                    st.warning(f"Recent average daily revenue is down {abs(change):.1f}% versus the previous seven recorded days.")
                else:
                    st.info(f"Recent average daily revenue is broadly stable ({change:+.1f}%) versus the previous seven recorded days.")
        if len(daily) >= 2:
            last, prior = daily.iloc[-1], daily.iloc[-2]
            direction = "higher" if last["revenue"] > prior["revenue"] else "lower" if last["revenue"] < prior["revenue"] else "unchanged"
            st.write(f"Latest recorded daily revenue is **{direction}** than the previous recorded day.")
        st.caption("Forecast limitation: this is a recent-average baseline. It does not account for holidays, promotions, seasonality, stockouts, or external factors unless those patterns are reflected in the recent history.")

    elif page == "Profit Tracker":
        section_heading(
        "WORKSPACE / PROFIT TRACKER",
        "Daily & monthly profit",
        "Track sales, costs, and operating expenses."
    )
    
        st.markdown("### Upload operating expenses")
        expense_file = st.file_uploader(
            "Upload expense CSV",
            type=["csv"],
            key="profit_tracker_expenses"
        )
        budget_file = st.file_uploader(
            "Optional monthly budget CSV (month,budget_amount)",
            type=["csv"],
            key="profit_tracker_budget",
            help="Use month values like 2026-10 and budget_amount as a numeric amount."
        )
    
        expenses = pd.DataFrame(
            columns=["date", "category", "amount"]
        )
    
        if expense_file is not None:
            try:
                expenses = pd.read_csv(expense_file)
                expenses.columns = [
                    str(c).strip().lower() for c in expenses.columns
                ]
    
                if not {"date", "category", "amount"}.issubset(
                    expenses.columns
                ):
                    st.error(
                        "CSV needs date, category, amount columns."
                    )
                    expenses = pd.DataFrame(
                        columns=["date", "category", "amount"]
                    )
                else:
                    expenses["date"] = pd.to_datetime(
                        expenses["date"], errors="coerce"
                    )
                    expenses["amount"] = pd.to_numeric(
                        expenses["amount"], errors="coerce"
                    )
                    expenses["category"] = (
                        expenses["category"].astype(str).str.strip()
                    )
                    expenses = expenses.dropna(
                        subset=["date", "amount"]
                    )
                    expenses = expenses[
                        (expenses["amount"] >= 0)
                        & (expenses["category"] != "")
                    ]
    
            except Exception:
                st.error("Could not read the expense CSV.")
                expenses = pd.DataFrame(
                    columns=["date", "category", "amount"]
                )
    
        tracker = daily.copy()
        tracker["date"] = pd.to_datetime(
            tracker["date"], errors="coerce"
        )
        tracker = tracker.dropna(subset=["date"])
    
        if expenses.empty:
            expense_daily = pd.DataFrame(
                columns=["date", "operating_expenses"]
            )
        else:
            expense_daily = (
                expenses.groupby("date", as_index=False)["amount"]
                .sum()
                .rename(columns={"amount": "operating_expenses"})
            )
    
        tracker = tracker.merge(
            expense_daily, on="date", how="left"
        )
        tracker["operating_expenses"] = (
            tracker["operating_expenses"].fillna(0)
        )
        tracker["profit_after_expenses"] = (
            tracker["gross_profit"] - tracker["operating_expenses"]
        )
        tracker["month"] = tracker["date"].dt.to_period("M").astype(str)
    
        st.caption(
            "Profit after expenses = existing gross profit minus "
            "uploaded operating expenses. Taxes and unprovided costs "
            "are excluded."
        )
    
        a, b, c, d = st.columns(4)
        a.metric("Revenue", money(tracker["revenue"].sum()))
        b.metric("Gross profit", money(tracker["gross_profit"].sum()))
        c.metric(
            "Operating expenses",
            money(tracker["operating_expenses"].sum())
        )
        d.metric(
            "Profit after expenses",
            money(tracker["profit_after_expenses"].sum())
        )
    
        st.markdown("### Daily profit & loss")
        display_table(
            tracker[
                [
                    "date", "revenue", "estimated_cost",
                    "gross_profit", "operating_expenses",
                    "profit_after_expenses"
                ]
            ].rename(columns={
                "date": "Date",
                "revenue": "Revenue",
                "estimated_cost": "Estimated cost",
                "gross_profit": "Gross profit",
                "operating_expenses": "Operating expenses",
                "profit_after_expenses": "Profit after expenses",
            }),
            height=360,
            formats={
                "Revenue": "₹{:,.2f}",
                "Estimated cost": "₹{:,.2f}",
                "Gross profit": "₹{:,.2f}",
                "Operating expenses": "₹{:,.2f}",
                "Profit after expenses": "₹{:,.2f}",
            },
        )
    
        st.markdown("### Monthly P&L")
        monthly = tracker.groupby("month", as_index=False).agg(
            revenue=("revenue", "sum"),
            gross_profit=("gross_profit", "sum"),
            operating_expenses=("operating_expenses", "sum"),
            profit_after_expenses=("profit_after_expenses", "sum")
        )
    
        display_table(
            monthly.rename(columns={
                "month": "Month",
                "revenue": "Revenue",
                "gross_profit": "Gross profit",
                "operating_expenses": "Operating expenses",
                "profit_after_expenses": "Profit after expenses",
            }),
            height=260,
            formats={
                "Revenue": "₹{:,.2f}",
                "Gross profit": "₹{:,.2f}",
                "Operating expenses": "₹{:,.2f}",
                "Profit after expenses": "₹{:,.2f}",
            },
        )
    
        if not monthly.empty:
            chart_data = monthly.melt(
                id_vars="month",
                value_vars=["revenue", "gross_profit", "profit_after_expenses"],
                var_name="metric",
                value_name="amount"
            )
            fig = px.line(
                chart_data,
                x="month",
                y="amount",
                color="metric",
                markers=True,
                color_discrete_sequence=CHART_COLORS,
            )
            fig.update_layout(
                paper_bgcolor="#0d1727",
                plot_bgcolor="#0d1727",
                font=dict(color="#c6d2e3"),
                margin=dict(t=24, l=18, r=18, b=18),
                legend=dict(font=dict(color="#c6d2e3")),
            )
            st.plotly_chart(polish_chart(fig, height=380), use_container_width=True)
    
        st.markdown("### Budget vs actual expenses")
        if budget_file is None:
            st.info("Upload a budget CSV with month and budget_amount columns to compare planned monthly spending with uploaded expenses.")
        else:
            try:
                budget = pd.read_csv(budget_file)
                budget.columns = [str(c).strip().lower() for c in budget.columns]
                if not {"month", "budget_amount"}.issubset(budget.columns):
                    st.error("Budget CSV needs month and budget_amount columns.")
                else:
                    budget["month"] = pd.to_datetime(budget["month"].astype(str), errors="coerce").dt.to_period("M").astype(str)
                    budget["budget_amount"] = pd.to_numeric(budget["budget_amount"], errors="coerce")
                    budget = budget.dropna(subset=["budget_amount"])
                    actual_expense = tracker.groupby("month", as_index=False)["operating_expenses"].sum()
                    budget_monthly = budget.groupby("month", as_index=False)["budget_amount"].sum().merge(actual_expense, on="month", how="outer").fillna(0)
                    budget_monthly["variance"] = budget_monthly["budget_amount"] - budget_monthly["operating_expenses"]
                    budget_monthly["status"] = np.where(budget_monthly["variance"] < 0, "Over budget", "Within budget")
                    display_table(budget_monthly.rename(columns={"month": "Month", "budget_amount": "Budget", "operating_expenses": "Actual expenses", "variance": "Budget remaining", "status": "Status"}), height=260, formats={"Budget": "₹{:,.2f}", "Actual expenses": "₹{:,.2f}", "Budget remaining": "₹{:,.2f}"})
                    st.caption("Budget comparison is only as complete as the expense records uploaded for the same months.")
            except Exception:
                st.error("Could not read the budget CSV. Check the month and budget_amount columns.")

        st.markdown("### Expense breakdown")
        if not expenses.empty:
            category_totals = expenses.groupby(
                "category", as_index=False
            )["amount"].sum()
    
            pie = px.pie(
                category_totals,
                names="category",
                values="amount",
                hole=0.45,
                color_discrete_sequence=CHART_COLORS,
            )
            pie.update_traces(
                textposition="inside",
                textinfo="label+percent",
                insidetextfont=dict(color="#ffffff", size=12),
                marker=dict(line=dict(color="#0d1727", width=3)),
                hovertemplate="<b>%{label}</b><br>Amount: ₹%{value:,.2f}<br>Share: %{percent}<extra></extra>",
            )
            pie.update_layout(
                paper_bgcolor="#0d1727",
                plot_bgcolor="#0d1727",
                font=dict(color="#c6d2e3"),
                legend=dict(font=dict(color="#c6d2e3")),
                margin=dict(t=24, l=18, r=18, b=18),
            )
            st.plotly_chart(polish_chart(pie, height=420), use_container_width=True)
        else:
            st.caption("Illustrative preview only — upload your own expense CSV to replace these example values.")
            example_categories = pd.DataFrame({
                "category": ["Rent", "Utilities", "Supplies", "Transport", "Other"],
                "amount": [12000, 2800, 4500, 1600, 2100],
            })
            pie = px.pie(
                example_categories,
                names="category",
                values="amount",
                hole=0.45,
                color_discrete_sequence=CHART_COLORS,
            )
            pie.update_traces(
                textposition="inside",
                textinfo="label+percent",
                insidetextfont=dict(color="#ffffff", size=12),
                marker=dict(line=dict(color="#0d1727", width=3)),
                hovertemplate="<b>%{label}</b><br>Amount: ₹%{value:,.2f}<br>Share: %{percent}<extra></extra>",
            )
            pie.update_layout(
                paper_bgcolor="#0d1727",
                plot_bgcolor="#0d1727",
                font=dict(color="#c6d2e3"),
                legend=dict(font=dict(color="#c6d2e3")),
                margin=dict(t=24, l=18, r=18, b=18),
            )
            st.plotly_chart(polish_chart(pie, height=420), use_container_width=True)
    elif page == "Reports":
        section_heading("WORKSPACE / REPORTS", "Reports & exports", "Generate a business report from the current filtered data.")
        revenue = filtered["revenue"].sum()
        profit = filtered["gross_profit"].sum()
        margin = profit / revenue * 100 if revenue else 0
        a, b, c = st.columns(3)
        a.metric("Report revenue", money(revenue))
        b.metric("Report gross profit", money(profit))
        c.metric("Report gross margin", f"{margin:.1f}%")
        business_name = st.text_input("Business / report name", value=st.session_state.get("business_name", "My Business"))
        st.session_state["business_name"] = business_name.strip() or "My Business"
        st.markdown("### Report preview")
        fig = line_figure(daily, "date", "revenue", height=330)
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
        display_table(products.head(10), height=340, formats={"revenue": "₹{:,.2f}", "estimated_cost": "₹{:,.2f}", "gross_profit": "₹{:,.2f}", "gross_margin_pct": "{:.1f}%", "units_sold": "{:,.0f}"})
        pdf_bytes = build_pdf_report(filtered, daily, forecast, accuracy, st.session_state["business_name"])
        st.download_button(
            "Download professional PDF report",
            data=pdf_bytes,
            file_name=f"{safe_filename(st.session_state['business_name'].strip().lower())}_intelligence_report.pdf",
            mime="application/pdf",
            key="download_full_pdf_report",
        )
        st.caption("The report contains a revenue chart, executive summary, product table, baseline forecast, and forecast evaluation when enough history is available.")
        st.download_button("Download filtered sales records (CSV)", data=safe_csv_bytes(filtered), file_name=f"{safe_filename(st.session_state['business_name'].strip().lower())}_filtered_records.csv", mime="text/csv", key="report_filtered_csv")
        st.download_button("Download product performance (CSV)", data=safe_csv_bytes(products), file_name=f"{safe_filename(st.session_state['business_name'].strip().lower())}_product_performance.csv", mime="text/csv", key="report_products_csv")

    elif page == "Team & Settings":
        section_heading("WORKSPACE / CONFIGURATION", "Team & settings", "Configure the local workspace profile and learn what this prototype supports.")
        st.markdown("### Business profile")
        business_name = st.text_input("Business name", value=st.session_state.get("business_name", "My Business"))
        st.session_state["business_name"] = business_name.strip() or "My Business"
        currency = st.selectbox("Display currency", ["INR (₹)", "USD ($)", "EUR (€)", "GBP (£)"], index=0)
        st.session_state["display_currency"] = currency
        st.markdown("### Optional performance targets")
        target_revenue = st.number_input("Target revenue for selected period (₹)", min_value=0.0, value=float(st.session_state.get("target_revenue", 0.0)), step=1000.0)
        target_margin = st.number_input("Target gross margin (%)", min_value=0.0, max_value=100.0, value=float(st.session_state.get("target_margin", 40.0)), step=1.0)
        st.session_state["target_revenue"] = target_revenue
        st.session_state["target_margin"] = target_margin
        current_revenue = float(filtered["revenue"].sum())
        current_margin = float(filtered["gross_profit"].sum() / current_revenue * 100) if current_revenue else 0.0
        t1, t2 = st.columns(2)
        t1.metric("Revenue target progress", f"{(current_revenue / target_revenue * 100):.1f}%" if target_revenue else "Set a target", money(current_revenue - target_revenue) + " vs target" if target_revenue else "No target set")
        t2.metric("Gross margin target", f"{current_margin:.1f}%", f"{current_margin - target_margin:+.1f} pp vs target")
        st.markdown("### Team workspace")
        st.info("Team page is a planning placeholder. Email login, invitations, user roles, and shared multi-user data are not enabled in this version.")
        st.markdown("### Data and privacy")
        st.write("This prototype is designed to process uploaded data in the active Streamlit session and does not intentionally write uploaded datasets or reports to application files or a database. It has no account login, role-based access, or shared organization workspace. Hosting-provider logs, runtime behavior, browser downloads, and platform retention are outside this code's control and must be checked separately. Do not upload confidential, customer-identifiable, payment, or regulated data until an independent security review is complete.")
        st.markdown("### Current prototype safeguards")
        st.write("- Upload limits: 10 MiB, 100,000 rows, and 50 columns.")
        st.write("- Unneeded columns are discarded before analytics; accepted fields are date, units_sold, selling_price, unit_cost, product, and stock_on_hand.")
        st.write("- No application-level data cache is used for uploaded datasets.")
        st.write("- PDF and CSV exports are generated in memory; CSV text cells beginning with spreadsheet formula characters are neutralized.")
        st.write("- The clear button resets this session's app state and invalidates the upload widget. It cannot erase downloaded files, screenshots, browser caches, or provider logs.")
        st.warning("Security status: prototype safeguards are not a certification. Session-isolation, deployment, logs, cache, and data-clear behavior still require live tests before confidential data is used.")
        st.markdown("### Metric definitions")
        st.write("- **Revenue:** units sold × selling price")
        st.write("- **Estimated cost:** units sold × unit cost")
        st.write("- **Gross profit:** revenue − estimated cost")
        st.write("- **Gross margin:** gross profit ÷ revenue × 100")

    elif page == "Data Explorer":
        section_heading("DATA / EXPLORER", "Data explorer", "Review validated records and check the shape of your uploaded data.")
        a, b, c = st.columns(3)
        a.metric("Valid rows", len(filtered))
        b.metric("Unique products", filtered["product"].nunique())
        c.metric("Date span", f"{filtered['date'].min():%d %b} – {filtered['date'].max():%d %b %Y}")
        st.markdown("### Validated data")
        display_table(filtered, height=460, formats={"revenue": "₹{:,.2f}", "estimated_cost": "₹{:,.2f}", "gross_profit": "₹{:,.2f}", "gross_margin_pct": "{:.1f}%", "units_sold": "{:,.0f}", "selling_price": "₹{:,.2f}", "unit_cost": "₹{:,.2f}", "stock_on_hand": "{:,.0f}"})
        st.download_button("Download filtered data as CSV", safe_csv_bytes(filtered), "filtered_business_data.csv", "text/csv")
        st.markdown("### Data quality notes")
        st.write(f"- Required columns: {', '.join(REQUIRED_COLUMNS)}")
        st.write(f"- Optional columns detected: {', '.join([c for c in ['product','stock_on_hand','order_id'] if c in filtered.columns]) or 'none'}")
        st.write(f"- Date range represented: {filtered['date'].min().date()} to {filtered['date'].max().date()}")
        st.write("- Financial values are derived from the supplied selling_price and unit_cost fields; they are not independently verified.")
        st.markdown("### Data quality checks")
        base_cols = [c for c in ["date", "product", "units_sold", "selling_price", "unit_cost"] if c in filtered.columns]
        duplicate_count = int(filtered.duplicated(subset=base_cols).sum()) if base_cols else 0
        st.metric("Potential duplicate rows", f"{duplicate_count:,}")
        quality_rows = []
        for col in ["date", "product", "units_sold", "selling_price", "unit_cost", "stock_on_hand"]:
            if col in filtered.columns:
                quality_rows.append({"Field": col, "Missing values": int(filtered[col].isna().sum()), "Unique values": int(filtered[col].nunique(dropna=True))})
        if quality_rows:
            display_table(pd.DataFrame(quality_rows), height=260)
        st.caption("Duplicate checks are heuristic: two legitimate transactions can share the same values. Review flagged records before deleting anything.")
        st.download_button("Download data-quality summary", safe_csv_bytes(pd.DataFrame(quality_rows)), "nurtura_data_quality_summary.csv", "text/csv")

    st.divider()
    st.caption("NURTURA  /  BUSINESS INTELLIGENCE  ·  Prototype analytics · estimates depend on uploaded data quality; use synthetic/anonymized data until security validation is complete.")


if __name__ == "__main__":
    main()
