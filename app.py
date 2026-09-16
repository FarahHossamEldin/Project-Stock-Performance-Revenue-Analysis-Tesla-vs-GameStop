import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Tesla vs GameStop",
    page_icon="📈",
    layout="wide"
)

# -----------------------------
# Load data
# -----------------------------

stock_comparison = pd.read_csv("stock_comparison.csv")
revenue_comparison = pd.read_csv("revenue_comparison.csv")

# Convert stock Date to datetime
stock_comparison["Date"] = pd.to_datetime(stock_comparison["Date"])

# Sort data
stock_comparison = stock_comparison.sort_values("Date").reset_index(drop=True)
revenue_comparison = revenue_comparison.sort_values("Year").reset_index(drop=True)

# -----------------------------
# Page title
# -----------------------------

st.title("Tesla vs GameStop Stock Analysis")

st.write(
    "Interactive comparison of Tesla and GameStop stock prices and revenue."
)

# -----------------------------
# KPI Cards
# -----------------------------

latest_stock = stock_comparison.iloc[-1]
latest_revenue = revenue_comparison.iloc[-1]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Tesla Stock Price",
        value=f"${latest_stock['Tesla Close']:.2f}"
    )

with col2:
    st.metric(
        label="GameStop Stock Price",
        value=f"${latest_stock['GameStop Close']:.2f}"
    )

with col3:
    st.metric(
        label="Tesla Revenue",
        value=f"${latest_revenue['Tesla Revenue']:,.0f}"
    )

with col4:
    st.metric(
        label="GameStop Revenue",
        value=f"${latest_revenue['GameStop Revenue']:,.0f}"
    )

# -----------------------------
# Stock Price Comparison
# -----------------------------

fig_stock = px.line(
    stock_comparison,
    x="Date",
    y=["Tesla Close", "GameStop Close"],
    title="Tesla vs GameStop Stock Price",
    color_discrete_map={
        "Tesla Close": "#1f77b4",
        "GameStop Close": "#ff7f0e"
    }
)

fig_stock.update_layout(
    xaxis_title="Date",
    yaxis_title="Stock Price (USD)",
    template="plotly_white"
)

st.plotly_chart(
    fig_stock,
    width="stretch",
    config={"responsive": True}
)

# -----------------------------
# Revenue Comparison
# -----------------------------

fig_revenue = px.line(
    revenue_comparison,
    x="Year",
    y=["Tesla Revenue", "GameStop Revenue"],
    title="Tesla vs GameStop Revenue",
    color_discrete_map={
        "Tesla Revenue": "#1f77b4",
        "GameStop Revenue": "#ff7f0e"
    }
)

fig_revenue.update_layout(
    xaxis_title="Year",
    yaxis_title="Revenue (USD)",
    template="plotly_white"
)

st.plotly_chart(
    fig_revenue,
    width="stretch",
    config={"responsive": True}
)

# -----------------------------
# Revenue Growth Comparison
# -----------------------------

revenue_growth = revenue_comparison.copy()

revenue_growth["Tesla Revenue Growth (%)"] = (
    revenue_growth["Tesla Revenue"].pct_change() * 100
)

revenue_growth["GameStop Revenue Growth (%)"] = (
    revenue_growth["GameStop Revenue"].pct_change() * 100
)

fig_growth = px.line(
    revenue_growth,
    x="Year",
    y=[
        "Tesla Revenue Growth (%)",
        "GameStop Revenue Growth (%)"
    ],
    title="Tesla vs GameStop Revenue Growth Comparison",
    color_discrete_map={
        "Tesla Revenue Growth (%)": "#1f77b4",
        "GameStop Revenue Growth (%)": "#ff7f0e"
    }
)

fig_growth.update_layout(
    xaxis_title="Year",
    yaxis_title="Revenue Growth (%)",
    template="plotly_white"
)

st.plotly_chart(
    fig_growth,
    width="stretch",
    config={"responsive": True}
)
