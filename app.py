import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Tesla vs GameStop",
    page_icon="📈",
    layout="wide"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(0,191,255,0.12), transparent 30%),
        radial-gradient(circle at 90% 20%, rgba(255,107,107,0.10), transparent 30%),
        linear-gradient(135deg, #020617 0%, #0f172a 50%, #111827 100%);
    color: white;
}

/* Make all normal text white */
p, span, label {
    color: white !important;
}

/* Main title */
.main-title {
    font-size: 48px;
    font-weight: 800;
    text-align: center;
    margin-top: 10px;
    margin-bottom: 5px;
    background: linear-gradient(90deg, #00BFFF, #ffffff, #FF6B6B);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Subtitle */
.subtitle {
    text-align: center;
    font-size: 18px;
    color: #cbd5e1 !important;
    margin-bottom: 35px;
}

/* Section titles */
.section-title {
    font-size: 26px;
    font-weight: 700;
    color: white !important;
    margin-top: 25px;
    margin-bottom: 15px;
}

/* KPI Cards */
div[data-testid="stMetric"] {
    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,0.12),
            rgba(255,255,255,0.035)
        );

    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 20px;
    padding: 22px;

    box-shadow:
        0px 15px 35px rgba(0,0,0,0.35),
        inset 0px 1px 1px rgba(255,255,255,0.15);

    backdrop-filter: blur(15px);

    transition: transform 0.25s ease,
                box-shadow 0.25s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-7px) scale(1.02);

    box-shadow:
        0px 20px 45px rgba(0,0,0,0.5),
        0px 0px 25px rgba(0,191,255,0.15);
}

div[data-testid="stMetricLabel"] {
    color: #cbd5e1 !important;
}

div[data-testid="stMetricValue"] {
    color: white !important;
    font-size: 28px;
    font-weight: 700;
}

/* Graph containers */
div[data-testid="stPlotlyChart"] {
    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,0.07),
            rgba(255,255,255,0.025)
        );

    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px;
    padding: 8px;

    box-shadow:
        0px 15px 35px rgba(0,0,0,0.3),
        inset 0px 1px 1px rgba(255,255,255,0.08);
}

/* Insight cards */
.insight-card {
    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,0.10),
            rgba(255,255,255,0.035)
        );

    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 18px;

    padding: 20px;
    min-height: 125px;

    box-shadow:
        0px 12px 30px rgba(0,0,0,0.30);

    backdrop-filter: blur(12px);

    transition: transform 0.25s ease,
                box-shadow 0.25s ease;
}

.insight-card:hover {
    transform: translateY(-5px);

    box-shadow:
        0px 18px 35px rgba(0,0,0,0.4),
        0px 0px 20px rgba(0,191,255,0.10);
}

.insight-title {
    font-size: 17px;
    font-weight: 700;
    color: white !important;
    margin-bottom: 12px;
}

.insight-text {
    font-size: 15px;
    color: #e2e8f0 !important;
    line-height: 1.6;
}

/* Conclusion box */
.conclusion-box {
    background:
        linear-gradient(
            135deg,
            rgba(0,191,255,0.12),
            rgba(255,107,107,0.08)
        );

    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 22px;

    padding: 28px 32px;

    box-shadow:
        0px 15px 35px rgba(0,0,0,0.35);

    margin-top: 10px;
}

.conclusion-title {
    font-size: 24px;
    font-weight: 700;
    color: white !important;
    margin-bottom: 12px;
}

.conclusion-text {
    font-size: 16px;
    color: #e2e8f0 !important;
    line-height: 1.8;
}

/* Footer */
.footer {
    text-align: center;
    color: #94a3b8 !important;
    font-size: 14px;
    margin-top: 45px;
    padding: 25px;
    border-top: 1px solid rgba(255,255,255,0.08);
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# LOAD DATA
# =====================================================

stock_comparison = pd.read_csv("stock_comparison.csv")
revenue_comparison = pd.read_csv("revenue_comparison.csv")

stock_comparison["Date"] = pd.to_datetime(
    stock_comparison["Date"]
)

stock_comparison = (
    stock_comparison
    .sort_values("Date")
    .reset_index(drop=True)
)

revenue_comparison = (
    revenue_comparison
    .sort_values("Year")
    .reset_index(drop=True)
)

# =====================================================
# REVENUE GROWTH
# =====================================================

revenue_growth = revenue_comparison.copy()

revenue_growth["Tesla Revenue Growth (%)"] = (
    revenue_growth["Tesla Revenue"].pct_change() * 100
)

revenue_growth["GameStop Revenue Growth (%)"] = (
    revenue_growth["GameStop Revenue"].pct_change() * 100
)

# =====================================================
# HEADER
# =====================================================

st.markdown(
    '<div class="main-title">📈 Tesla vs GameStop</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Interactive Stock & Revenue Analysis Dashboard'
    '</div>',
    unsafe_allow_html=True
)

# =====================================================
# KPI CARDS
# =====================================================

latest_stock = stock_comparison.iloc[-1]
latest_revenue = revenue_comparison.iloc[-1]

latest_stock_date = latest_stock["Date"].strftime("%Y-%m-%d")
latest_revenue_year = int(latest_revenue["Year"])

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🚗 Tesla Stock Price — Latest",
        value=f"${latest_stock['Tesla Close']:.2f}"
    )

with col2:
    st.metric(
        label="🎮 GameStop Stock Price — Latest",
        value=f"${latest_stock['GameStop Close']:.2f}"
    )

with col3:
    st.metric(
        label=f"💰 Tesla Revenue — {latest_revenue_year}",
        value=f"${latest_revenue['Tesla Revenue']:,.0f}"
    )

with col4:
    st.metric(
        label=f"💰 GameStop Revenue — {latest_revenue_year}",
        value=f"${latest_revenue['GameStop Revenue']:,.0f}"
    )

st.caption(
    f"Stock prices shown for the latest available date: {latest_stock_date} | "
    f"Revenue figures shown for the latest available year: {latest_revenue_year}"
)

# =====================================================
# STOCK PRICE COMPARISON
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
    hovertemplate=(
        "<b>%{fullData.name}</b><br>"
        "Date: %{x}<br>"
        "Price: $%{y:.2f}"
        "<extra></extra>"
    )
)

fig_stock.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),

    xaxis=dict(
        title="Date",
        color="white",
        gridcolor="rgba(255,255,255,0.08)"
    ),

    yaxis=dict(
        title="Stock Price (USD)",
        color="white",
        gridcolor="rgba(255,255,255,0.08)"
    ),

    legend=dict(
        title="Company",
        font=dict(color="white")
    ),

    hovermode="x unified",
    height=500,

    margin=dict(
        l=20,
        r=20,
        t=30,
        b=20
    )
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
# REVENUE + GROWTH
# =====================================================

col_left, col_right = st.columns(2)

# =====================================================
# REVENUE GRAPH
# =====================================================

with col_left:

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
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "Year: %{x}<br>"
            "Revenue: $%{y:,.0f}"
            "<extra></extra>"
        )
    )

    fig_revenue.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),

        xaxis=dict(
            title="Year",
            color="white",
            gridcolor="rgba(255,255,255,0.08)"
        ),

        yaxis=dict(
            title="Revenue (USD)",
            color="white",
            gridcolor="rgba(255,255,255,0.08)"
        ),

        legend=dict(
            title="Company",
            font=dict(color="white")
        ),

        hovermode="x unified",
        height=430,

        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20
        )
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
# REVENUE GROWTH GRAPH
# =====================================================

with col_right:

    st.markdown(
        '<div class="section-title">📊 Revenue Growth</div>',
        unsafe_allow_html=True
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
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "Year: %{x}<br>"
            "Growth: %{y:.2f}%"
            "<extra></extra>"
        )
    )

    fig_growth.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),

        xaxis=dict(
            title="Year",
            color="white",
            gridcolor="rgba(255,255,255,0.08)"
        ),

        yaxis=dict(
            title="Revenue Growth (%)",
            color="white",
            gridcolor="rgba(255,255,255,0.08)"
        ),

        legend=dict(
            title="Company",
            font=dict(color="white")
        ),

        hovermode="x unified",
        height=430,

        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20
        )
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
# KEY INSIGHTS
# =====================================================

st.markdown(
    '<div class="section-title">💡 Key Insights</div>',
    unsafe_allow_html=True
)

tesla_avg_growth = (
    revenue_growth["Tesla Revenue Growth (%)"]
    .dropna()
    .mean()
)

gamestop_avg_growth = (
    revenue_growth["GameStop Revenue Growth (%)"]
    .dropna()
    .mean()
)

tesla_revenue_change = (
    (
        latest_revenue["Tesla Revenue"]
        / revenue_comparison["Tesla Revenue"].iloc[0]
    ) - 1
) * 100

gamestop_revenue_change = (
    (
        latest_revenue["GameStop Revenue"]
        / revenue_comparison["GameStop Revenue"].iloc[0]
    ) - 1
) * 100

insight1, insight2, insight3, insight4 = st.columns(4)

with insight1:
    st.markdown(
        f'<div class="insight-card">'
        f'<div class="insight-title">📈 Tesla Avg. Growth</div>'
        f'<div class="insight-text">'
        f'Tesla recorded an average period-over-period revenue growth '
        f'of <b>{tesla_avg_growth:.2f}%</b> across the available data.'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with insight2:
    st.markdown(
        f'<div class="insight-card">'
        f'<div class="insight-title">🎮 GameStop Avg. Growth</div>'
        f'<div class="insight-text">'
        f'GameStop recorded an average period-over-period revenue growth '
        f'of <b>{gamestop_avg_growth:.2f}%</b> across the available data.'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with insight3:
    st.markdown(
        f'<div class="insight-card">'
        f'<div class="insight-title">🚗 Tesla Revenue Change</div>'
        f'<div class="insight-text">'
        f'Tesla revenue changed by <b>{tesla_revenue_change:.2f}%</b> '
        f'from the first to the latest available year.'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with insight4:
    st.markdown(
        f'<div class="insight-card">'
        f'<div class="insight-title">🎮 GameStop Revenue Change</div>'
        f'<div class="insight-text">'
        f'GameStop revenue changed by <b>{gamestop_revenue_change:.2f}%</b> '
        f'from the first to the latest available year.'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

# =====================================================
# CONCLUSION
# =====================================================

st.markdown(
    '<div class="section-title">🔎 Conclusion</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="conclusion-box">'
    f'<div class="conclusion-title">'
    f'What does the analysis show?'
    f'</div>'
    f'<div class="conclusion-text">'
    f'The dashboard provides a combined view of stock price movements, '
    f'revenue trends, and revenue growth for Tesla and GameStop. '
    f'Across the available revenue data, Tesla shows an average '
    f'period-over-period growth of <b>{tesla_avg_growth:.2f}%</b>, '
    f'while GameStop shows <b>{gamestop_avg_growth:.2f}%</b>. '
    f'The revenue comparison highlights how the two companies have '
    f'evolved financially over time, while the stock price chart shows '
    f'how their market prices changed across the available trading period.'
    f'<br><br>'
    f'Together, these visualizations demonstrate how financial data can '
    f'be transformed into an interactive dashboard for easier analysis '
    f'and exploration.'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True
)

# =====================================================
# FOOTER
# =====================================================

st.markdown(
    '<div class="footer">'
    'Built with Python • Pandas • Plotly • Streamlit'
    '<br>'
    'Tesla vs GameStop Financial Analysis'
    '</div>',
    unsafe_allow_html=True
)
