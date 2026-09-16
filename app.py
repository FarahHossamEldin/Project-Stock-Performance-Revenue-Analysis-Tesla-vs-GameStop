
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Tesla vs GameStop",
    page_icon="📈",
    layout="wide"
)

# Load data
stock_comparison = pd.read_csv("stock_comparison.csv")

# Create interactive chart
fig = px.line(
    stock_comparison,
    x="Date",
    y=["Tesla Close", "GameStop Close"],
    title="Tesla vs GameStop Stock Price",
    color_discrete_map={
        "Tesla Close": "#1f77b4",
        "GameStop Close": "#ff7f0e"
    }
)

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Stock Price (USD)",
    template="plotly_white"
)

st.title("Tesla vs GameStop Stock Analysis")

st.write(
    "Interactive comparison of Tesla and GameStop stock prices."
)

st.plotly_chart(
    fig,
    width="stretch",
    config={"responsive": True}
)
