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
    min-height: 145px;

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
revenue_growth_comparison = pd.read_csv("comparison.csv")


# =====================================================
# DATA PREPARATION
# =====================================================

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

revenue_growth_comparison = (
    revenue_growth_comparison
    .sort_values("Year")
    .reset_index(drop=True)
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
# FILTERS
# =====================================================

st.markdown(
    '<div class="section-title">🎛️ Dashboard Filters</div>',
    unsafe_allow_html=True
)

filter_col1, filter_col2 = st.columns(2)

with filter_col1:

    period = st.selectbox(
        "Stock Price Period",
        [
            "All Time",
            "Last 5 Years",
            "Last 3 Years",
            "Last 1 Year"
        ]
    )

with filter_col2:

    company_filter = st.selectbox(
        "Company",
        [
            "Both",
            "Tesla",
            "GameStop"
        ]
    )


# =====================================================
# APPLY STOCK FILTER
# =====================================================

max_date = stock_comparison["Date"].max()

if period == "Last 5 Years":

    start_date = max_date - pd.DateOffset(years=5)

    filtered_stock = stock_comparison[
        stock_comparison["Date"] >= start_date
    ].copy()

elif period == "Last 3 Years":

    start_date = max_date - pd.DateOffset(years=3)

    filtered_stock = stock_comparison[
        stock_comparison["Date"] >= start_date
    ].copy()

elif period == "Last 1 Year":

    start_date = max_date - pd.DateOffset(years=1)

    filtered_stock = stock_comparison[
        stock_comparison["Date"] >= start_date
    ].copy()

else:

    filtered_stock = stock_comparison.copy()


# =====================================================
# KPI CALCULATIONS
# =====================================================

latest_stock = filtered_stock.iloc[-1]
first_stock = filtered_stock.iloc[0]

latest_revenue = revenue_comparison.iloc[-1]

latest_stock_date = latest_stock["Date"].strftime("%Y-%m-%d")
latest_revenue_year = int(latest_revenue["Year"])


# Real stock price change over selected period

tesla_stock_change = (
    (latest_stock["Tesla Close"] /
     first_stock["Tesla Close"]) - 1
) * 100

gamestop_stock_change = (
    (latest_stock["GameStop Close"] /
     first_stock["GameStop Close"]) - 1
) * 100


# =====================================================
# KPI SECTION
# =====================================================

st.markdown(
    '<div class="section-title">📌 Current Snapshot</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        label="🚗 Tesla Latest Price",
        value=f"${latest_stock['Tesla Close']:.2f}",
        delta=f"{tesla_stock_change:+.2f}%"
    )

with col2:

    st.metric(
        label="🎮 GameStop Latest Price",
        value=f"${latest_stock['GameStop Close']:.2f}",
        delta=f"{gamestop_stock_change:+.2f}%"
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
    f"Stock performance is measured from the beginning to the end "
    f"of the selected period. "
    f"Latest stock date: {latest_stock_date} | "
    f"Latest revenue year: {latest_revenue_year}"
)


# =====================================================
# STOCK PRICE COMPARISON
# =====================================================

st.markdown(
    '<div class="section-title">📈 Stock Price Comparison</div>',
    unsafe_allow_html=True
)

stock_columns = []

if company_filter in ["Both", "Tesla"]:
    stock_columns.append("Tesla Normalized")

if company_filter in ["Both", "GameStop"]:
    stock_columns.append("GameStop Normalized")


fig_stock = px.line(
    filtered_stock,
    x="Date",
    y=stock_columns,
    color_discrete_map={
        "Tesla Normalized": "#00BFFF",
        "GameStop Normalized": "#FF6B6B"
    }
)

fig_stock.update_traces(
    line=dict(width=3),
    hovertemplate=(
        "<b>%{fullData.name}</b><br>"
        "Date: %{x}<br>"
        "Normalized Price: %{y:.2f}"
        "<extra></extra>"
    )
)

fig_stock.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),

    title="Normalized Tesla vs GameStop Stock Performance",

    xaxis=dict(
        title="Date",
        color="white",
        gridcolor="rgba(255,255,255,0.08)"
    ),

    yaxis=dict(
        title="Normalized Price (Base = 100)",
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
        t=50,
        b=20
    )
)

st.plotly_chart(
    fig_stock,
    use_container_width=True,
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
        },
        title="Tesla vs GameStop Revenue"
    )

    fig_revenue.update_traces(
        line=dict(width=3),
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "Year: %{x}<br>"
            "Revenue: $%{y:,.0f} million"
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
            title="Revenue (USD Millions)",
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
            t=50,
            b=20
        )
    )

    st.plotly_chart(
        fig_revenue,
        use_container_width=True,
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
        revenue_growth_comparison,
        x="Year",
        y=[
            "Tesla Growth %",
            "GameStop Growth %"
        ],
        color_discrete_map={
            "Tesla Growth %": "#00BFFF",
            "GameStop Growth %": "#FF6B6B"
        },
        title="Year-over-Year Revenue Growth"
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
            title="Year-over-Year Revenue Growth (%)",
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
            t=50,
            b=20
        )
    )

    st.plotly_chart(
        fig_growth,
        use_container_width=True,
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


# Average YoY growth

tesla_avg_growth = (
    revenue_growth_comparison["Tesla Growth %"]
    .dropna()
    .mean()
)

gamestop_avg_growth = (
    revenue_growth_comparison["GameStop Growth %"]
    .dropna()
    .mean()
)


# Overall revenue change

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


# Highest growth year

tesla_highest_growth_row = revenue_growth_comparison.loc[
    revenue_growth_comparison["Tesla Growth %"].idxmax()
]

gamestop_highest_growth_row = revenue_growth_comparison.loc[
    revenue_growth_comparison["GameStop Growth %"].idxmax()
]


tesla_highest_growth = (
    tesla_highest_growth_row["Tesla Growth %"]
)

gamestop_highest_growth = (
    gamestop_highest_growth_row["GameStop Growth %"]
)


tesla_highest_growth_year = int(
    tesla_highest_growth_row["Year"]
)

gamestop_highest_growth_year = int(
    gamestop_highest_growth_row["Year"]
)


# =====================================================
# INSIGHT CARDS
# =====================================================

insight1, insight2, insight3, insight4 = st.columns(4)


with insight1:

    st.markdown(
        f'<div class="insight-card">'
        f'<div class="insight-title">'
        f'📈 Tesla Avg. Revenue Growth'
        f'</div>'
        f'<div class="insight-text">'
        f'Tesla revenue grew by an average of '
        f'<b>{tesla_avg_growth:.2f}% per year</b> '
        f'across the available revenue data.'
        f'<br><br>'
        f'<small>'
        f'Average of year-over-year growth rates.'
        f'</small>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )


with insight2:

    st.markdown(
        f'<div class="insight-card">'
        f'<div class="insight-title">'
        f'🎮 GameStop Avg. Revenue Growth'
        f'</div>'
        f'<div class="insight-text">'
        f'GameStop revenue grew by an average of '
        f'<b>{gamestop_avg_growth:.2f}% per year</b> '
        f'across the available revenue data.'
        f'<br><br>'
        f'<small>'
        f'Average of year-over-year growth rates.'
        f'</small>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )


with insight3:

    st.markdown(
        f'<div class="insight-card">'
        f'<div class="insight-title">'
        f'🚗 Tesla Revenue Expansion'
        f'</div>'
        f'<div class="insight-text">'
        f'Tesla revenue increased by '
        f'<b>{tesla_revenue_change:.2f}%</b> '
        f'from the first to the latest available year.'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )


with insight4:

    st.markdown(
        f'<div class="insight-card">'
        f'<div class="insight-title">'
        f'🏆 Highest Revenue Growth'
        f'</div>'
        f'<div class="insight-text">'
        f'Tesla recorded its highest growth of '
        f'<b>{tesla_highest_growth:.2f}%</b> '
        f'in <b>{tesla_highest_growth_year}</b>.<br><br>'
        f'GameStop recorded '
        f'<b>{gamestop_highest_growth:.2f}%</b> '
        f'in <b>{gamestop_highest_growth_year}</b>.'
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

    f'The analysis provides a combined view of stock price '
    f'movements, revenue trends, revenue growth, and normalized '
    f'stock performance for Tesla and GameStop. '

    f'Tesla demonstrated strong long-term revenue expansion, '
    f'with an average year-over-year revenue growth of '
    f'<b>{tesla_avg_growth:.2f}%</b>, while GameStop recorded '
    f'<b>{gamestop_avg_growth:.2f}%</b> across the available '
    f'revenue data. '

    f'<br><br>'

    f'The revenue comparison highlights different financial '
    f'growth patterns between the two companies. Tesla experienced '
    f'rapid long-term expansion, while GameStop experienced a '
    f'more variable revenue trajectory followed by a declining trend. '

    f'<br><br>'

    f'The stock analysis also demonstrates that stock price '
    f'performance does not necessarily move in line with revenue '
    f'performance. Normalizing both stock prices to a common base '
    f'of 100 provides a clearer comparison of their relative '
    f'stock performance despite their different starting prices. '

    f'<br><br>'

    f'Overall, combining revenue trends, revenue growth, historical '
    f'stock prices, and normalized stock performance provides a '
    f'more comprehensive view of how the two companies evolved '
    f'over time.'

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
