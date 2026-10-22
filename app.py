 
import streamlit as st
import pandas as pd
import numpy as np

def validate_sales_data(df):
    """Validate and prepare an uploaded sales dataset."""
    df = df.copy()

    required = ["date", "units_sold", "selling_price", "unit_cost"]
    missing_columns = [col for col in required if col not in df.columns]

    if missing_columns:
        return None, [
            f"Missing required column: {col}"
            for col in missing_columns
        ]

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    numeric_columns = [
        "units_sold", "selling_price", "unit_cost"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    issues = []

    if df["date"].isna().any():
        issues.append(
            f"{df['date'].isna().sum()} rows have invalid dates."
        )

    invalid_numbers = df[numeric_columns].isna().any(axis=1)
    if invalid_numbers.any():
        issues.append(
            f"{invalid_numbers.sum()} rows have missing or invalid numbers."
        )

    negative_values = (
        (df["units_sold"] < 0)
        | (df["selling_price"] < 0)
        | (df["unit_cost"] < 0)
    ).fillna(False)

    if negative_values.any():
        issues.append(
            f"{negative_values.sum()} rows contain negative values; "
            "check returns or data-entry errors."
        )

    duplicate_count = int(df.duplicated().sum())
    if duplicate_count:
        issues.append(
            f"{duplicate_count} exact duplicate rows found. "
            "Review them before removing anything."
        )

    # Keep the original rows for review; don't silently delete data.
    return df, issues


def calculate_business_metrics(df):
    """Calculate core sales and estimated gross-profit metrics."""
    df = df.copy()

    df["revenue"] = df["units_sold"] * df["selling_price"]
    df["estimated_cost"] = df["units_sold"] * df["unit_cost"]
    df["estimated_gross_profit"] = (
        df["revenue"] - df["estimated_cost"]
    )

    total_revenue = df["revenue"].sum()
    total_profit = df["estimated_gross_profit"].sum()

    metrics = {
        "total_revenue": float(total_revenue),
        "estimated_gross_profit": float(total_profit),
        "units_sold": float(df["units_sold"].sum()),
        "gross_margin_pct": (
            float(total_profit / total_revenue * 100)
            if total_revenue > 0 else 0.0
        ),
    }

    return df, metrics


def generate_business_warnings(df, metrics):
    """Generate transparent, rule-based business warnings."""
    warnings = []

    if metrics["total_revenue"] <= 0:
        warnings.append(
            "Revenue is zero or negative. Check the uploaded data."
        )

    if metrics["estimated_gross_profit"] < 0:
        warnings.append(
            "Estimated gross profit is negative. Review prices and costs."
        )

    if 0 < metrics["gross_margin_pct"] < 10:
        warnings.append(
            "Gross margin is below 10%. Review product costs and pricing."
        )

    if "stock_on_hand" in df.columns:
        stock = pd.to_numeric(
            df["stock_on_hand"], errors="coerce"
        )

        if (stock < 0).any():
            warnings.append(
                "Negative stock values detected. Check inventory records."
            )

        if (stock == 0).any():
            warnings.append(
                "Some records show zero stock. Check for potential stockouts."
            )

    if "product" in df.columns:
        product_count = df["product"].nunique(dropna=True)
        if product_count == 0:
            warnings.append(
                "No identifiable products were found in the dataset."
            )

    if not warnings:
        warnings.append(
            "No basic rule-based warnings were triggered. "
            "This does not guarantee that the data or business is healthy."
        )

    return warnings


st.set_page_config(
    page_title="Business Intelligence AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- PREMIUM DARK THEME ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg: #07111f;
    --panel: #0c1b2d;
    --border: #203651;
    --text: #e7f0ff;
    --muted: #91a7c2;
    --blue: #3984ff;
    --green: #26d7a0;
}

.stApp {
    background: radial-gradient(ellipse at top right, #10234b 0%, #07111f 48%);
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stSidebar"] {
    background: #091526;
    border-right: 1px solid var(--border);
}

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--text) !important;
}

p, label, span {
    letter-spacing: 0.1px;
}

.hero {
    padding: 16px 0 22px 0;
}

.eyebrow {
    color: #70a9ff;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(2rem, 4vw, 3.1rem);
    font-weight: 700;
    line-height: 1.1;
    color: #f0f6ff;
    margin: 10px 0;
}

.hero-title span {
    color: #6b9cff;
}

.subtext {
    color: #9bb0ca;
    font-size: 1rem;
}

.kpi {
    background: linear-gradient(145deg, #102541, #0b192a);
    border: 1px solid #244263;
    border-radius: 16px;
    padding: 20px;
    min-height: 137px;
    box-shadow: 0 8px 28px #00000018;
}

.kpi-label {
    color: #a8bdd6;
    font-size: 0.88rem;
    margin-bottom: 12px;
}

.kpi-value {
    color: #f0f6ff;
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(1.35rem, 2vw, 2rem);
    font-weight: 700;
    overflow-wrap: anywhere;
}

.kpi-note {
    color: #8ca5c2;
    font-size: 0.78rem;
    margin-top: 9px;
}

.panel {
    background: #0b192a;
    border: 1px solid #203651;
    border-radius: 16px;
    padding: 18px 20px;
    margin: 8px 0 18px 0;
}

div[data-testid="stMetric"] {
    background: #0d2035;
    border: 1px solid #203651;
    padding: 15px;
    border-radius: 12px;
}

div[data-testid="stMetricLabel"] {
    color: #a8bdd6;
}

.stButton > button {
    background: linear-gradient(90deg, #246bfa, #478eff);
    color: white;
    border: 0;
    border-radius: 9px;
    font-weight: 600;
}

.stButton > button:hover {
    border: 1px solid #83b3ff;
    color: white;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #203651;
    border-radius: 10px;
}

footer {visibility: hidden;}
#MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------- DATA INPUT ----------
st.sidebar.markdown("## 📊 BI INTELLIGENCE")
st.sidebar.caption("RETAIL ANALYTICS PLATFORM")
st.sidebar.divider()

page = st.sidebar.radio(
    "WORKSPACE",
    ["Executive Overview", "Sales Analysis", "Forecast & Insights", "Data Explorer"]
)

st.sidebar.divider()
st.sidebar.markdown("### Upload sales data")
uploaded_file = st.sidebar.file_uploader(
    "Choose a CSV file",
    type=["csv"],
    help="Required columns: date, units_sold, selling_price, unit_cost"
)

st.sidebar.caption(
    "Expected columns: date, units_sold, selling_price, unit_cost"
)

# ---------- DEMO DATA ----------
rng = np.random.default_rng(42)
dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=180)

units = np.maximum(
    0,
    np.round(
        50
        + 9 * np.sin(np.arange(len(dates)) * 2 * np.pi / 7)
        + rng.normal(0, 6, len(dates))
    )
).astype(int)

df = pd.DataFrame({
    "date": dates,
    "units_sold": units,
    "selling_price": 100.0,
    "unit_cost": 60.0
})

data_source = "SIMULATED DEMO DATA"

# ---------- VALIDATE UPLOADED DATA ----------
if uploaded_file is not None:
    try:
        uploaded = pd.read_csv(uploaded_file)
        uploaded.columns = uploaded.columns.str.strip().str.lower()

        required = ["date", "units_sold", "selling_price", "unit_cost"]
        missing = [col for col in required if col not in uploaded.columns]

        if missing:
            st.sidebar.error("Missing columns: " + ", ".join(missing))
        else:
            candidate = uploaded.copy()
            candidate["date"] = pd.to_datetime(
                candidate["date"], errors="coerce"
            )

            for col in ["units_sold", "selling_price", "unit_cost"]:
                candidate[col] = pd.to_numeric(
                    candidate[col], errors="coerce"
                )

            candidate = candidate.dropna(subset=required)

            if candidate.empty:
                st.sidebar.error("No valid records found in the CSV.")
            elif (
                (candidate["units_sold"] < 0).any()
                or (candidate["selling_price"] < 0).any()
                or (candidate["unit_cost"] < 0).any()
            ):
                st.sidebar.error(
                    "Units, selling prices and costs must be non-negative."
                )
            else:
                df = candidate.sort_values("date").reset_index(drop=True)
                data_source = "UPLOADED CSV DATA"
                st.sidebar.success(f"Loaded {len(df):,} valid rows.")

    except Exception as error:
        st.sidebar.error(f"Could not read the CSV: {error}")

# ---------- METRICS ----------
df["revenue"] = df["units_sold"] * df["selling_price"]
df["estimated_cost"] = df["units_sold"] * df["unit_cost"]
df["gross_profit"] = df["revenue"] - df["estimated_cost"]

total_revenue = df["revenue"].sum()
total_cost = df["estimated_cost"].sum()
total_profit = df["gross_profit"].sum()
total_units = df["units_sold"].sum()
gross_margin = total_profit / total_revenue * 100 if total_revenue else 0

daily = (
    df.groupby("date", as_index=False)
    .agg(
        revenue=("revenue", "sum"),
        gross_profit=("gross_profit", "sum"),
        units_sold=("units_sold", "sum")
    )
    .sort_values("date")
)

def money(value):
    return f"₹{value:,.0f}"
 # ---------- PRODUCT PERFORMANCE ----------
if "product" in df.columns:
    st.subheader("Product Performance")

  
    product_summary = (
        df.groupby("product", dropna=False)
        .agg(
            units_sold=("units_sold", "sum"),
            revenue=("revenue", "sum"),
            estimated_cost=("estimated_cost", "sum"),
            gross_profit=("gross_profit", "sum")
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    product_summary["gross_margin_pct"] = (
        product_summary["gross_profit"]
        / product_summary["revenue"].replace(0, np.nan)
        * 100
    ).fillna(0)

    st.dataframe(
        product_summary,
        use_container_width=True,
        hide_index=True
    )

   
    st.bar_chart(
        product_summary.set_index("product")[
            ["revenue", "gross_profit"]
        ]
    )

else:
    st.info(
        "Upload a CSV with a 'product' column to unlock product-level analytics."
    )


# ---------- INVENTORY INSIGHTS ----------
if "stock_on_hand" in df.columns:
    st.subheader("Inventory Insights")

    inventory = df.copy()
    inventory["stock_on_hand"] = pd.to_numeric(
        inventory["stock_on_hand"], errors="coerce"
    )
    inventory = inventory.dropna(subset=["stock_on_hand"])

    if not inventory.empty:
        if "product" in inventory.columns:
            inventory_summary = (
                inventory.groupby("product", dropna=False)
                .agg(
                    stock_on_hand=("stock_on_hand", "min"),
                    units_sold=("units_sold", "sum")
                )
                .reset_index()
            )
        else:
            inventory_summary = pd.DataFrame({
                "product": ["All uploaded records"],
                "stock_on_hand": [inventory["stock_on_hand"].min()],
                "units_sold": [inventory["units_sold"].sum()]
            })

        inventory_summary["inventory_status"] = (
            inventory_summary["stock_on_hand"].apply(
                lambda stock: (
                    "Out of stock" if stock <= 0
                    else "Low stock" if stock <= 10
                    else "In stock"
                )
            )
        )

        st.dataframe(
            inventory_summary,
            use_container_width=True,
            hide_index=True
        )

        low_stock = inventory_summary[
            inventory_summary["inventory_status"].isin(
                ["Out of stock", "Low stock"]
            )
        ]

        if not low_stock.empty:
            st.warning(
                f"{len(low_stock)} product(s) need an inventory check."
            )
        else:
            st.success("No products fall below the low-stock threshold.")
else:
    st.info(
        "Upload a CSV with a 'stock_on_hand' column to enable inventory insights."
    )


# ---------- HEADER ----------
st.markdown("""
<div class="hero">
    <div class="eyebrow">RETAIL ANALYTICS PLATFORM / OVERVIEW</div>
    <div class="hero-title">Business Intelligence <span>AI</span></div>
    <div class="subtext">
        Understand performance. Forecast demand. Make better decisions.
    </div>
</div>
""", unsafe_allow_html=True)

if data_source == "SIMULATED DEMO DATA":
    st.info("Demo mode: figures below are simulated, not real business results.")
else:
    st.success(f"Using uploaded data · {len(df):,} valid records")

# ---------- EXECUTIVE OVERVIEW ----------
if page == "Executive Overview":

    a, b, c, d = st.columns(4)

    cards = [
        (a, "TOTAL REVENUE", money(total_revenue), "Sales value in selected data"),
        (b, "EST. GROSS PROFIT", money(total_profit), "Revenue minus estimated product cost"),
        (c, "GROSS MARGIN", f"{gross_margin:.1f}%", "Estimated gross profit / revenue"),
        (d, "UNITS SOLD", f"{total_units:,.0f}", "Total units recorded")
    ]

    for col, label, value, note in cards:
        with col:
            st.markdown(
                f'<div class="kpi"><div class="kpi-label">{label}</div>'
                f'<div class="kpi-value">{value}</div>'
                f'<div class="kpi-note">{note}</div></div>',
                unsafe_allow_html=True
            )

    st.write("")
    left, right = st.columns([1.65, 1])

    with left:
        st.markdown("### Revenue & Profit Trend")
        chart_data = daily.set_index("date")[["revenue", "gross_profit"]]
        st.line_chart(chart_data, color=["#3984ff", "#26d7a0"])

    with right:
        st.markdown("### Sales Composition")
        st.caption("Estimated share of revenue and product cost")
        composition = pd.DataFrame({
            "Amount": [max(total_cost, 0), max(total_profit, 0)]
        }, index=["Estimated product cost", "Estimated gross profit"])
        if composition["Amount"].sum() > 0:
            st.bar_chart(composition, color="#3984ff")
        else:
            st.write("No positive amounts to chart.")

    st.markdown("### Recent Daily Performance")
    st.dataframe(
        daily.tail(10).sort_values("date", ascending=False),
        use_container_width=True,
        hide_index=True
    )

# ---------- SALES ANALYSIS ----------
elif page == "Sales Analysis":
    st.markdown("## Sales Analysis")
    st.caption("Explore sales totals and daily patterns.")

    if len(daily) > 1:
        start_date = daily["date"].min().date()
        end_date = daily["date"].max().date()

        chosen = st.date_input(
            "Choose date range",
            value=(start_date, end_date),
            min_value=start_date,
            max_value=end_date
        )

        if isinstance(chosen, tuple) and len(chosen) == 2:
            start, end = chosen
            view = daily[
                (daily["date"].dt.date >= start)
                & (daily["date"].dt.date <= end)
            ]
        else:
            view = daily

    else:
        view = daily

    x, y, z = st.columns(3)
    x.metric("Revenue", money(view["revenue"].sum()))
    y.metric("Gross Profit", money(view["gross_profit"].sum()))
    z.metric("Units Sold", f"{view['units_sold'].sum():,.0f}")

    st.markdown("### Daily Units Sold")
    st.bar_chart(view.set_index("date")["units_sold"], color="#3984ff")

    st.markdown("### Daily Revenue")
    st.area_chart(view.set_index("date")["revenue"], color="#3984ff")

    st.markdown("### Sales Records")
    st.dataframe(view, use_container_width=True, hide_index=True)

# ---------- FORECAST & INSIGHTS ----------
elif page == "Forecast & Insights":
    st.markdown("## Forecast & Insights")
    st.caption("A transparent baseline forecast using recent average daily sales.")

    if len(daily) >= 1:
        recent = daily.tail(min(7, len(daily)))
        average_units = recent["units_sold"].mean()
        average_revenue = recent["revenue"].mean()

        future_dates = pd.date_range(
            daily["date"].max() + pd.Timedelta(days=1), periods=7
        )

        forecast = pd.DataFrame({
            "Date": future_dates,
            "Forecast Units": [round(average_units, 1)] * 7,
            "Forecast Revenue": [round(average_revenue, 2)] * 7
        })

        x, y, z = st.columns(3)
        x.metric("7-Day Forecast Units", f"{forecast['Forecast Units'].sum():,.0f}")
        y.metric("Average Daily Units", f"{average_units:,.1f}")
        z.metric("Average Daily Revenue", money(average_revenue))

        st.markdown("### Next Seven Days")
        st.bar_chart(
            forecast.set_index("Date")["Forecast Units"],
            color="#3984ff"
        )
        st.dataframe(forecast, use_container_width=True, hide_index=True)

        st.markdown("### Business Insights")

        if len(daily) >= 14:
            recent_revenue = daily.tail(7)["revenue"].mean()
            previous_revenue = daily.iloc[-14:-7]["revenue"].mean()

            if previous_revenue > 0:
                change = (recent_revenue - previous_revenue) / previous_revenue * 100

                if change > 2:
                    st.success(f"Recent average daily revenue is up {change:.1f}% versus the previous seven days.")
                elif change < -2:
                    st.warning(f"Recent average daily revenue is down {abs(change):.1f}% versus the previous seven days.")
                else:
                    st.info("Recent average daily revenue is broadly stable versus the previous seven days.")

        if len(daily) >= 2:
            if daily.iloc[-1]["revenue"] > daily.iloc[-2]["revenue"]:
                st.write("**Latest daily revenue:** Higher than the previous recorded day.")
            elif daily.iloc[-1]["revenue"] < daily.iloc[-2]["revenue"]:
                st.write("**Latest daily revenue:** Lower than the previous recorded day.")
            else:
                st.write("**Latest daily revenue:** Unchanged from the previous recorded day.")

        st.info(
            "Forecast limitation: this is a seven-day moving-average baseline, "
            "not the trained Random Forest model. It assumes recent demand "
            "is informative about the near future."
        )

# ---------- DATA EXPLORER ----------
else:
    st.markdown("## Data Explorer")
    st.caption("Review the records and calculations used by this dashboard.")

    st.metric("Records", f"{len(df):,}")
    st.write(f"**Data source:** {data_source}")
    st.write(f"**Date range:** {df['date'].min().date()} to {df['date'].max().date()}")

    st.markdown("### Data Preview")
    st.dataframe(df, use_container_width=True, hide_index=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download processed data as CSV",
        data=csv,
        file_name="business_intelligence_processed_data.csv",
        mime="text/csv"
    )

# ---------- FOOTER ----------
st.divider()
st.caption(
    f"BUSINESS INTELLIGENCE AI  •  {data_source}  •  "
    "Decision support prototype — validate estimates before business use."
)
