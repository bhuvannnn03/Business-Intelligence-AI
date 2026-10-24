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
    styler = table.style.format(formatters, na_rep="—", precision=2)
    st.dataframe(styler, use_container_width=True, hide_index=True, height=height)


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
    if ignored:
        errors.append(f"Ignored {len(ignored)} unneeded column(s) to reduce data exposure.")
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
    section_heading("WORKSPACE / OVERVIEW", "Business at a glance", "A clear view of sales performance, profitability, and areas to investigate.")
    revenue = float(df["revenue"].sum())
    profit = float(df["gross_profit"].sum())
    margin = profit / revenue * 100 if revenue else 0
    units = float(df["units_sold"].sum())
    cols = st.columns(4)
    cols[0].metric("Total revenue", money(revenue))
    cols[1].metric("Gross profit", money(profit))
    cols[2].metric("Gross margin", f"{margin:.1f}%")
    cols[3].metric("Units sold", number(units))

    left, right = st.columns([1.65, 1])
    with left:
        st.markdown("### Revenue performance")
        st.caption("Daily recorded revenue across the selected period")
        fig = line_figure(daily, "date", "revenue", height=360)
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
    with right:
        st.markdown("### Revenue by product")
        st.caption("Top products ranked by revenue")
        fig = bar_figure(products.head(7).sort_values("revenue"), "revenue", "product", horizontal=True, color=CHART_COLORS[0], height=360)
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
        st.caption("Ranked by recorded revenue.")

    st.markdown("### Business signals")
    signals = []
    if len(daily) >= 14:
        current = float(daily.tail(7)["revenue"].mean())
        previous = float(daily.iloc[-14:-7]["revenue"].mean())
        if previous > 0:
            change = (current - previous) / previous * 100
            if change >= 3:
                signals.append(("Positive", f"Recent average daily revenue is up {change:.1f}% compared with the prior seven recorded days."))
            elif change <= -3:
                signals.append(("Review", f"Recent average daily revenue is down {abs(change):.1f}% compared with the prior seven recorded days. Review product mix, prices, and demand."))
            else:
                signals.append(("Stable", f"Recent average daily revenue is broadly stable ({change:+.1f}%) versus the prior seven recorded days."))
    if not products.empty:
        top = products.iloc[0]
        signals.append(("Top revenue", f"{top['product']} has the highest recorded revenue at {money(top['revenue'])}. Revenue leadership does not necessarily mean the highest margin."))
        low_profit = products.sort_values("gross_profit").iloc[0]
        signals.append(("Profit review", f"{low_profit['product']} has the lowest gross profit in the product summary ({money(low_profit['gross_profit'])}); review its volume, pricing, and cost assumptions."))
    if "stock_on_hand" in df.columns:
        stock = df.dropna(subset=["stock_on_hand"]).groupby("product")["stock_on_hand"].min()
        low_stock = stock[stock <= 10]
        if len(low_stock):
            signals.append(("Inventory", f"{len(low_stock)} product(s) have a minimum recorded stock of 10 or fewer units. Confirm current stock before replenishing."))
    if not signals:
        signals.append(("Data note", "Upload at least 14 daily records for period comparisons and more reliable baseline evaluation."))
    for label, message in signals:
        st.markdown(f'<div class="ic-alert"><b>{label}</b><br>{message}</div>', unsafe_allow_html=True)
    st.caption("Insights are rule-based summaries of the uploaded data, not guarantees or causal explanations.")


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
            "Sales Analytics": "↗   Sales Analytics",
            "Products & Profitability": "◇   Products & Profitability",
            "Inventory": "⬡   Inventory",
            "Forecast & Insights": "⌁   Forecasts",
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
    if uploaded is None and use_demo:
        st.info("Demo mode: the current figures are synthetic examples, not a real business's results.")

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

    elif page == "Sales Analytics":
        section_heading("ANALYTICS / SALES", "Sales analytics", "Explore revenue, sales volume, costs, and profitability over time.")
        a, b, c, d = st.columns(4)
        a.metric("Revenue", money(filtered["revenue"].sum()))
        b.metric("Estimated cost", money(filtered["estimated_cost"].sum()))
        c.metric("Gross profit", money(filtered["gross_profit"].sum()))
        margin = filtered["gross_profit"].sum() / filtered["revenue"].sum() * 100 if filtered["revenue"].sum() else 0
        d.metric("Gross margin", f"{margin:.1f}%")
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

    elif page == "Inventory":
        section_heading("OPERATIONS / STOCK", "Inventory insights", "Use supplied stock counts to flag products for review.")
        if "stock_on_hand" not in filtered.columns:
            st.warning("This dataset has no stock_on_hand column. Upload one to enable inventory insights.")
        else:
            inv_df = filtered.dropna(subset=["stock_on_hand"]).copy()
            inv = inv_df.groupby("product", as_index=False).agg(
                stock_on_hand=("stock_on_hand", "min"),
                units_sold=("units_sold", "sum"),
                revenue=("revenue", "sum"),
            )
            inv["status"] = inv["stock_on_hand"].apply(lambda x: "Out of stock" if x <= 0 else "Low stock" if x <= 10 else "In stock")
            low = inv[inv["status"].isin(["Out of stock", "Low stock"])]
            a, b, c = st.columns(3)
            a.metric("Products monitored", len(inv))
            b.metric("Low / out of stock", len(low))
            c.metric("Minimum stock across products", number(inv["stock_on_hand"].min()) if not inv.empty else "—")
            if not low.empty:
                st.warning(f"{len(low)} product(s) are at or below the 10-unit low-stock threshold. Confirm current stock before ordering.")
            else:
                st.success("No product is at or below the 10-unit low-stock threshold in the selected records.")
            display_table(inv.sort_values("stock_on_hand"), height=380, formats={"stock_on_hand": "{:,.0f}", "units_sold": "{:,.0f}", "revenue": "₹{:,.2f}"})
            st.caption("If stock_on_hand is repeated on each sales row, this view uses the minimum supplied value per product. Confirm the source file's stock semantics.")

    elif page == "Forecast & Insights":
        section_heading("PLANNING / FORECAST", "Forecast & insights", "A transparent baseline forecast, with a historical check when enough daily records are available.")
        a, b, c = st.columns(3)
        a.metric("Next 7-day forecast units", number(forecast["Forecast units"].sum()))
        b.metric("Average daily units", number(avg_units, 1))
        c.metric("Average daily revenue", money(avg_revenue))
        st.markdown("### Next seven days")
        fig = bar_figure(forecast, "Date", "Forecast units", color=CHART_COLORS[3], height=350)
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
        display_table(forecast, height=300, formats={"Forecast units": "{:,.1f}", "Forecast revenue": "₹{:,.2f}"})
        st.markdown("### Historical forecast accuracy")
        if accuracy is None:
            st.info("At least 14 daily records are needed to compare these baseline methods.")
        else:
            display_table(accuracy.round(2), height=180, formats={"Mean absolute error (units)": "{:.2f}"})
            best = accuracy.sort_values("Mean absolute error (units)").iloc[0]
            st.markdown(f'<div class="ic-alert"><b>Lower-error method on this test</b><br>{best["Forecast method"]} (MAE {best['Mean absolute error (units)']:.2f} units).</div>', unsafe_allow_html=True)
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

    elif page == "Team & Settings":
        section_heading("WORKSPACE / CONFIGURATION", "Team & settings", "Configure the local workspace profile and learn what this prototype supports.")
        st.markdown("### Business profile")
        business_name = st.text_input("Business name", value=st.session_state.get("business_name", "My Business"))
        st.session_state["business_name"] = business_name.strip() or "My Business"
        currency = st.selectbox("Display currency", ["INR (₹)", "USD ($)", "EUR (€)", "GBP (£)"], index=0)
        st.session_state["display_currency"] = currency
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

    st.divider()
    st.caption("NURTURA  /  BUSINESS INTELLIGENCE  ·  Prototype analytics · use synthetic/anonymized data until security validation is complete.")


if __name__ == "__main__":
    main()
