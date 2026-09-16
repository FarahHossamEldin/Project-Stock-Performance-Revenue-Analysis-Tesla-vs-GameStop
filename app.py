import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================================
# Page Configuration
# =====================================================

st.set_page_config(
    page_title="Tesla vs GameStop",
    page_icon="📈",
    layout="wide"
)

# =====================================================
# Custom CSS
# =====================================================

st.markdown("""
<style>

    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #111827 50%, #172554 100%);
        color: white;
    }

    .main-title {
        font-size: 42px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
        color: white;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #cbd5e1;
        margin-bottom: 35px;
    }

    .section-title {
        font-size: 26px;
        font-weight: 600;
        color: white;
        margin-top: 30px;
        margin-bottom: 15px;
    }

    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0px 8px 25px rgba(0, 0, 0, 0.25);
    }

    div[data-testid="stMetricLabel"] {
        color: #cbd5e1;
    }

    div[data-testid="stMetricValue"] {
        color: white;
        font-size: 28px;
    }

    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 14px;
        margin-top: 50px;
        padding: 20px;
    }

</style>
""", unsafe_allow_html=True)

# =====================================================
# Load Data
# =====================================================

stock_comparison = pd.read_csv("stock_comparison.csv")
revenue_comparison = pd.read_csv("revenue_comparison.csv")

# Convert dates
stock_comparison["Date"] = pd.to_datetime(stock_comparison["Date"])

# Sort data
stock_comparison = stock_comparison.sort_values("Date").reset_index(drop=True)
revenue_comparison = revenue_comparison.sort_values("Year").reset_index(drop=True)

# =====================================================
# Header
# =====================================================

st.markdown(
    '<div class="main-title">📈 Tesla vs GameStop</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Interactive Stock & Revenue Analysis Dashboard</div>',
    unsafe_allow_html=True
)

# =====================================================
# KPI Cards
# =====================================================

latest_stock = stock_comparison.iloc[-1]
latest_revenue = revenue_comparison.iloc[-1]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🚗 Tesla Stock Price",
        value=f"${latest_stock['Tesla Close']:.2f}"
    )

with col2:
    st.metric(
        label="🎮 GameStop Stock Price",
        value=f"${latest_stock['GameStop Close']:.2f}"
    )

with col3:
    st.metric(
        label="💰 Tesla Revenue",
        value=f"${latest_revenue['Tesla Revenue']:,.0f}"
    )

with col4:
    st.metric(
        label="💰 GameStop Revenue",
        value=f"${latest_revenue['GameStop Revenue']:,.0f}"
    )

# =====================================================
# Stock Price Comparison
# =====================================================

st.markdown(
    '<div class="section-title">📈 Stock Price Comparison</div>',
    unsafe_allow_html=True
)

fig_stock = px.line(
    stock_comparison,
    x="Date",
    y=["Tesla Close", "GameStop Close"],
    color_discrete_map={
        "Tesla Close": "#00BFFF",
        "GameStop Close": "#FF6B6B"
    }
)

fig_stock.update_traces(
    line=dict(width=3),
    hovertemplate="<b>%{fullData.name}</b><br>"
                  "Date: %{x}<br>"
                  "Price: $%{y:.2f}<extra></extra>"
)

fig_stock.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis_title="Date",
    yaxis_title="Stock Price (USD)",
    legend_title="Company",
    hovermode="x unified",
    height=500,
    margin=dict(l=20, r=20, t=40, b=20)
)

st.plotly_chart(
    fig_stock,
    width="stretch",
    config={
        "responsive": True,
        "displaylogo": False
    }
)

# =====================================================
# Revenue Comparison
# =====================================================

st.markdown(
    '<div class="section-title">💰 Revenue Comparison</div>',
    unsafe_allow_html=True
)

fig_revenue = px.line(
    revenue_comparison,
    x="Year",
    y=["Tesla Revenue", "GameStop Revenue"],
    color_discrete_map={
        "Tesla Revenue": "#00BFFF",
        "GameStop Revenue": "#FF6B6B"
    }
)

fig_revenue.update_traces(
    line=dict(width=3),
    hovertemplate="<b>%{fullData.name}</b><br>"
                  "Year: %{x}<br>"
                  "Revenue: $%{y:,.0f}<extra></extra>"
)

fig_revenue.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis_title="Year",
    yaxis_title="Revenue (USD)",
    legend_title="Company",
    hovermode="x unified",
    height=500,
    margin=dict(l=20, r=20, t=40, b=20)
)

st.plotly_chart(
    fig_revenue,
    width="stretch",
    config={
        "responsive": True,
        "displaylogo": False
    }
)

# =====================================================
# Revenue Growth Comparison
# =====================================================

st.markdown(
    '<div class="section-title">📊 Revenue Growth Comparison</div>',
    unsafe_allow_html=True
)

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
    color_discrete_map={
        "Tesla Revenue Growth (%)": "#00BFFF",
        "GameStop Revenue Growth (%)": "#FF6B6B"
    }
)

fig_growth.update_traces(
    line=dict(width=3),
    hovertemplate="<b>%{fullData.name}</b><br>"
                  "Year: %{x}<br>"
                  "Growth: %{y:.2f}%<extra></extra>"
)

fig_growth.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis_title="Year",
    yaxis_title="Revenue Growth (%)",
    legend_title="Company",
    hovermode="x unified",
    height=500,
    margin=dict(l=20, r=20, t=40, b=20)
)

st.plotly_chart(
    fig_growth,
    width="stretch",
    config={
        "responsive": True,
        "displaylogo": False
    }
)

# =====================================================
# Footer
# =====================================================

st.markdown(
    '<div class="footer">'
    'Built with Python • Pandas • Plotly • Streamlit'
    '</div>',
    unsafe_allow_html=True
)
