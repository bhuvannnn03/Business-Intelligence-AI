import io
from datetime import date

import numpy as np
import pandas as pd
import streamlit as st

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
# Replace app.py with this file. Dependencies: streamlit, pandas, numpy, reportlab
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="NURTURA | Business Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Premium dark-navy visual system
st.markdown(
    """
    <style>
    :root { color-scheme: dark; }
    .stApp { background: #090e18; color: #e6ebf3; }
    [data-testid="stHeader"] { background: rgba(9,14,24,.94); }
    [data-testid="stToolbar"] { right: 1rem; }
    [data-testid="stSidebar"] { background: #0b1220; border-right: 1px solid #202b3c; }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1.15rem; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #9ba8bb; }
    [data-testid="stSidebar"] hr { margin: .85rem 0; border-color: #202b3c !important; }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1540px; }
    h1, h2, h3 { color: #f4f6fa !important; letter-spacing: -.035em; }
    h1 { font-weight: 650 !important; }
    h2, h3 { font-weight: 600 !important; }
    p, label, .stMarkdown { color: #c2cad7; }
    [data-testid="stMetric"] { background: linear-gradient(145deg,#111b2b,#0e1725); border: 1px solid #253247; padding: 18px 19px; border-radius: 13px; }
    [data-testid="stMetricLabel"] { color: #99a8bc !important; font-size: .82rem; }
    [data-testid="stMetricValue"] { color: #f4f7fb !important; font-weight: 650; letter-spacing: -.035em; }
    [data-testid="stMetricDelta"] { font-size: .8rem; }
    div[data-testid="stDataFrame"] { border: 1px solid #253247; border-radius: 11px; overflow: hidden; }
    div[data-testid="stPlotlyChart"], div[data-testid="stVegaLiteChart"] { background: #0e1725; border: 1px solid #253247; border-radius: 13px; padding: 9px; }
    div.stButton > button, div.stDownloadButton > button { border-radius: 8px; border: 1px solid #5376bd; background: #3156a6; color: #fff; font-weight: 600; padding: .58rem 1rem; transition: all .15s ease; }
    div.stButton > button:hover, div.stDownloadButton > button:hover { background: #3a64bd; border-color: #7695d4; color: #fff; }
    .ic-eyebrow { color: #7f9edb; font-size: .7rem; text-transform: uppercase; letter-spacing: .16em; font-weight: 700; margin-bottom: .45rem; }
    .ic-subtitle { color: #98a6ba; margin-top: -.45rem; margin-bottom: 1.25rem; font-size: .98rem; }
    .ic-panel { background: #0e1725; border: 1px solid #253247; border-radius: 13px; padding: 18px 20px; margin-bottom: 12px; }
    .ic-alert { background: #101b2b; border: 1px solid #25364c; border-left: 3px solid #6b8dca; border-radius: 8px; padding: 12px 15px; margin: 8px 0; color: #cbd4e1; }
    .ic-alert b { color: #eef3fa; font-size: .9rem; }
    .ic-muted { color: #8d9bb0; font-size: .86rem; }
    [data-testid="stSidebar"] div[role="radiogroup"] { gap: 4px; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label { background: transparent; border: 1px solid transparent; border-radius: 8px; padding: 9px 11px; margin: 0; min-height: 38px; transition: background .15s ease, border-color .15s ease; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover { background: #121d2d; border-color: #253247; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) { background: #17253a; border-color: #2c4262; box-shadow: inset 2px 0 0 #8aa6dc; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p { color: #f1f5fb !important; font-weight: 600; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label p { font-size: .88rem; color: #aab6c7; margin: 0; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display: none; }
    [data-testid="stFileUploader"] section { border-color: #2a374b; background: #0e1725; }
    [data-testid="stDateInput"] input, [data-testid="stTextInput"] input, [data-testid="stSelectbox"] [data-baseweb="select"] { background: #0e1725; }
    hr { border-color: #253247 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

REQUIRED_COLUMNS = ["date", "units_sold", "selling_price", "unit_cost"]
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
        st.line_chart(daily.set_index("date")["revenue"], use_container_width=True)
    with right:
        st.markdown("### Revenue by product")
        st.bar_chart(products.head(7).set_index("product")["revenue"], use_container_width=True)
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
    with st.sidebar:
        st.markdown("""
        <div style="padding:4px 2px 17px 2px">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px">
            <div style="width:34px;height:34px;border:1px solid #405477;border-radius:9px;display:flex;align-items:center;justify-content:center;background:linear-gradient(145deg,#1d2b43,#101a2a);color:#dbe6fb;font-size:17px;font-weight:700">N</div>
            <div><div style="font-size:14px;letter-spacing:2.2px;color:#f1f5fb;font-weight:750">NURTURA</div><div style="font-size:10px;letter-spacing:1.1px;color:#8190a7;margin-top:3px;text-transform:uppercase">Business intelligence</div></div>
          </div>
          <div style="font-size:10px;letter-spacing:1.6px;color:#72839c;font-weight:700;text-transform:uppercase;margin-bottom:8px">Workspace</div>
        </div>
        """, unsafe_allow_html=True)
        page = st.radio("Navigate", NAV_ITEMS, label_visibility="collapsed")
        st.divider()
        st.markdown("<div style='font-size:10px;letter-spacing:1.5px;color:#72839c;font-weight:700;text-transform:uppercase;margin:3px 0 9px'>Data source</div>", unsafe_allow_html=True)
        uploaded = st.file_uploader("Sales data · CSV", type=["csv"], help="Required: date, units_sold, selling_price, unit_cost. Optional: product, stock_on_hand, order_id.")
        use_demo = st.toggle("Load sample workspace", value=uploaded is None, help="Uses synthetic demonstration data, not real business records.")
        st.caption("Uploads are processed in this app session. Persistent storage and separate company workspaces are not enabled yet.")

    raw = None
    validation_notes = []
    if uploaded is not None:
        try:
            raw = pd.read_csv(uploaded)
        except Exception as exc:
            st.error(f"Could not read the CSV file: {exc}")
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
        st.markdown("<div style='font-size:10px;letter-spacing:1.5px;color:#72839c;font-weight:700;text-transform:uppercase;margin:8px 0 9px'>Filters</div>", unsafe_allow_html=True)
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
        st.line_chart(daily.set_index("date")[["revenue", "gross_profit"]], use_container_width=True)
        left, right = st.columns(2)
        with left:
            st.markdown("### Daily units sold")
            st.bar_chart(daily.set_index("date")["units_sold"], use_container_width=True)
        with right:
            st.markdown("### Cost and profit mix")
            st.bar_chart(daily.set_index("date")[["estimated_cost", "gross_profit"]], use_container_width=True)
        st.markdown("### Daily performance table")
        st.dataframe(daily, use_container_width=True, hide_index=True)

    elif page == "Products & Profitability":
        section_heading("ANALYTICS / PRODUCTS", "Products & profitability", "Find which products contribute revenue and estimated gross profit.")
        st.dataframe(products, use_container_width=True, hide_index=True)
        left, right = st.columns(2)
        with left:
            st.markdown("### Revenue by product")
            st.bar_chart(products.set_index("product")["revenue"], use_container_width=True)
        with right:
            st.markdown("### Gross profit by product")
            st.bar_chart(products.set_index("product")["gross_profit"], use_container_width=True)
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
            st.dataframe(inv.sort_values("stock_on_hand"), use_container_width=True, hide_index=True)
            st.caption("If stock_on_hand is repeated on each sales row, this view uses the minimum supplied value per product. Confirm the source file's stock semantics.")

    elif page == "Forecast & Insights":
        section_heading("PLANNING / FORECAST", "Forecast & insights", "A transparent baseline forecast, with a historical check when enough daily records are available.")
        a, b, c = st.columns(3)
        a.metric("Next 7-day forecast units", number(forecast["Forecast units"].sum()))
        b.metric("Average daily units", number(avg_units, 1))
        c.metric("Average daily revenue", money(avg_revenue))
        st.markdown("### Next seven days")
        st.bar_chart(forecast.set_index("Date")["Forecast units"], use_container_width=True)
        st.dataframe(forecast, use_container_width=True, hide_index=True)
        st.markdown("### Historical forecast accuracy")
        if accuracy is None:
            st.info("At least 14 daily records are needed to compare these baseline methods.")
        else:
            st.dataframe(accuracy.round(2), use_container_width=True, hide_index=True)
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
        st.line_chart(daily.set_index("date")["revenue"], use_container_width=True)
        st.dataframe(products.head(10), use_container_width=True, hide_index=True)
        pdf_bytes = build_pdf_report(filtered, daily, forecast, accuracy, st.session_state["business_name"])
        st.download_button(
            "Download professional PDF report",
            data=pdf_bytes,
            file_name=f"{(st.session_state['business_name'].strip().lower().replace(' ', '_') or 'business')}_intelligence_report.pdf",
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
        st.write("This prototype processes uploaded data within the active app session. It does not yet offer persistent account-based storage or secure organization separation. Do not upload sensitive customer information until those controls are implemented.")
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
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        st.download_button("Download filtered data as CSV", filtered.to_csv(index=False).encode("utf-8"), "filtered_business_data.csv", "text/csv")
        st.markdown("### Data quality notes")
        st.write(f"- Required columns: {', '.join(REQUIRED_COLUMNS)}")
        st.write(f"- Optional columns detected: {', '.join([c for c in ['product','stock_on_hand','order_id'] if c in filtered.columns]) or 'none'}")
        st.write(f"- Date range represented: {filtered['date'].min().date()} to {filtered['date'].max().date()}")
        st.write("- Financial values are derived from the supplied selling_price and unit_cost fields; they are not independently verified.")

    st.divider()
    st.caption("NURTURA • Business intelligence workspace • Verify source data before making financial or inventory decisions.")


if __name__ == "__main__":
    main()
