
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Business Intelligence AI",
    page_icon="📊",
    layout="wide"
)

st.title("Business Intelligence AI")
st.caption("Retail analytics, sales forecasting and business insights")
st.info("Prototype demo — using simulated retail data.")

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Choose a view",
    ["Executive Overview", "Sales Analysis", "Forecast & Insights"]
)

# Simulated demo dataset
rng = np.random.default_rng(42)
dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=365)

units = np.maximum(
    0,
    np.round(
        50 + 10 * np.sin(np.arange(365) * 2 * np.pi / 7)
        + rng.normal(0, 7, 365)
    )
).astype(int)

selling_price = 100
unit_cost = 60

df = pd.DataFrame({
    "date": dates,
    "units_sold": units,
    "revenue": units * selling_price,
    "estimated_cost_of_goods": units * unit_cost
})

df["estimated_gross_profit"] = (
    df["revenue"] - df["estimated_cost_of_goods"]
)

# Optional CSV upload
st.sidebar.divider()
uploaded_file = st.sidebar.file_uploader(
    "Upload sales CSV (optional)",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        uploaded = pd.read_csv(uploaded_file)
        st.sidebar.success("CSV uploaded successfully.")
        st.sidebar.write("Columns detected:")
        st.sidebar.write(uploaded.columns.tolist())
        st.warning(
            "CSV preview only: the dashboard continues to use demo data "
            "until your file is mapped to the required sales columns."
        )
        st.dataframe(uploaded.head(10), use_container_width=True)
    except Exception as e:
        st.sidebar.error(f"Could not read CSV: {e}")

if page == "Executive Overview":
    total_revenue = df["revenue"].sum()
    total_profit = df["estimated_gross_profit"].sum()
    margin = total_profit / total_revenue * 100 if total_revenue else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"{total_revenue:,.0f}")
    c2.metric("Estimated Gross Profit", f"{total_profit:,.0f}")
    c3.metric("Estimated Gross Margin", f"{margin:.1f}%")
    c4.metric("Units Sold", f"{df['units_sold'].sum():,.0f}")

    st.subheader("Daily Revenue")
    st.line_chart(df.set_index("date")["revenue"])

    st.subheader("Daily Estimated Gross Profit")
    st.area_chart(df.set_index("date")["estimated_gross_profit"])

elif page == "Sales Analysis":
    st.subheader("Sales Analysis")
    st.bar_chart(df.set_index("date")["units_sold"])
    st.dataframe(df.tail(14), use_container_width=True)

else:
    st.subheader("Seven-Day Sales Forecast")

    recent_average = df["units_sold"].tail(7).mean()
    forecast_dates = pd.date_range(
        df["date"].max() + pd.Timedelta(days=1),
        periods=7
    )

    forecast = pd.DataFrame({
        "Forecast Date": forecast_dates,
        "Predicted Units": [round(recent_average, 1)] * 7
    })

    st.dataframe(forecast, use_container_width=True)
    st.line_chart(
        forecast.set_index("Forecast Date")["Predicted Units"]
    )

    st.subheader("Business Insights")
    st.write(
        f"Average daily sales over the last seven days: "
        f"{recent_average:.1f} units."
    )
    st.write(
        "This initial forecast uses the recent seven-day average. "
        "It is a baseline estimate, not the trained Random Forest model."
    )

st.divider()
st.caption(
    "Demo only. Validate forecasts and costs against real business data "
    "before using them for decisions."
)
