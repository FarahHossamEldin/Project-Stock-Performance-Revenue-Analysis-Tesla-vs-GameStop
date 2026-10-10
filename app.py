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

    background: linear-gradient(
        90deg,
        #00BFFF,
        #ffffff,
        #FF6B6B
    );

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

    transition:
        transform 0.25s ease,
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

    transition:
        transform 0.25s ease,
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

    border-top:
        1px solid rgba(255,255,255,0.08);
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# LOAD DATA
# =====================================================

stock_comparison = pd.read_csv("stock_comparison.csv")
revenue_comparison = pd.read_csv("revenue_comparison.csv")
revenue_growth_comparison = pd.read_csv("revenue_growth_comparison.csv")

# Clean and sort dates
stock_comparison["Date"] = (
    pd.to_datetime(stock_comparison["Date"], errors="coerce", utc=True)
    .dt.tz_localize(None)
)
stock_comparison = (
    stock_comparison.dropna(subset=["Date"])
    .sort_values("Date")
    .reset_index(drop=True)
)

# Keep revenue comparison to the shared period used in the notebook
revenue_comparison["Year"] = pd.to_numeric(
    revenue_comparison["Year"], errors="coerce"
)
revenue_comparison = (
    revenue_comparison.dropna(subset=["Year"])
    .sort_values("Year")
    .reset_index(drop=True)
)
revenue_comparison["Year"] = revenue_comparison["Year"].astype(int)
revenue_comparison = revenue_comparison.query("Year >= 2009 and Year <= 2020").copy()

# Recalculate growth from the shared revenue series so both companies use
# the same comparison window and 2009 is the baseline, not a growth year.
revenue_growth_comparison = revenue_comparison[["Year"]].copy()
revenue_growth_comparison["Tesla Growth %"] = (
    revenue_comparison["Tesla Revenue"].pct_change() * 100
)
revenue_growth_comparison["GameStop Growth %"] = (
    revenue_comparison["GameStop Revenue"].pct_change() * 100
)

COMPANY_COLUMNS = {
    "Tesla": {
        "stock": "Tesla Close",
        "revenue": "Tesla Revenue",
        "growth": "Tesla Growth %",
        "color": "#00BFFF",
        "emoji": "🚗",
    },
    "GameStop": {
        "stock": "GameStop Close",
        "revenue": "GameStop Revenue",
        "growth": "GameStop Growth %",
        "color": "#FF6B6B",
        "emoji": "🎮",
    },
}

# =====================================================
# HEADER
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
        ["All Time", "Last 5 Years", "Last 3 Years", "Last 1 Year"],
        help="This filter applies to stock-price charts and stock-price KPIs. Revenue stays on the shared 2009–2020 annual period."
    )

with filter_col2:
    company_filter = st.selectbox(
        "Company",
        ["Both", "Tesla", "GameStop"],
        help="This filter applies to the KPIs, charts, key insights, and conclusion throughout the dashboard."
    )

selected_companies = (
    ["Tesla", "GameStop"] if company_filter == "Both" else [company_filter]
)

# =====================================================
# APPLY STOCK PERIOD FILTER
# =====================================================

max_date = stock_comparison["Date"].max()
if period == "Last 5 Years":
    start_date = max_date - pd.DateOffset(years=5)
    filtered_stock = stock_comparison[stock_comparison["Date"] >= start_date].copy()
elif period == "Last 3 Years":
    start_date = max_date - pd.DateOffset(years=3)
    filtered_stock = stock_comparison[stock_comparison["Date"] >= start_date].copy()
elif period == "Last 1 Year":
    start_date = max_date - pd.DateOffset(years=1)
    filtered_stock = stock_comparison[stock_comparison["Date"] >= start_date].copy()
else:
    filtered_stock = stock_comparison.copy()

if filtered_stock.empty:
    st.warning("No stock-price records are available for the selected period.")
    st.stop()

filtered_stock = filtered_stock.sort_values("Date").reset_index(drop=True)
first_stock = filtered_stock.iloc[0]
latest_stock = filtered_stock.iloc[-1]
latest_stock_date = latest_stock["Date"].strftime("%Y-%m-%d")
stock_data_start = stock_comparison["Date"].min().strftime("%Y-%m-%d")
stock_data_end = stock_comparison["Date"].max().strftime("%Y-%m-%d")
revenue_start_year = int(revenue_comparison["Year"].min())
revenue_end_year = int(revenue_comparison["Year"].max())

# Calculate revenue metrics on the shared 2009–2020 period.
revenue_means = revenue_comparison[
    ["Tesla Revenue", "GameStop Revenue"]
].mean()
revenue_change = {}
average_growth = {}
highest_growth = {}

for company in selected_companies:
    cfg = COMPANY_COLUMNS[company]
    revenue_col = cfg["revenue"]
    growth_col = cfg["growth"]
    revenue_change[company] = (
        (revenue_comparison[revenue_col].iloc[-1] /
         revenue_comparison[revenue_col].iloc[0]) - 1
    ) * 100
    average_growth[company] = revenue_growth_comparison[growth_col].dropna().mean()
    peak_idx = revenue_growth_comparison[growth_col].idxmax()
    peak_row = revenue_growth_comparison.loc[peak_idx]
    highest_growth[company] = {
        "value": peak_row[growth_col],
        "year": int(peak_row["Year"]),
    }

# =====================================================
# KPI SECTION
# =====================================================

st.markdown(
    '<div class="section-title">📌 Dashboard Snapshot</div>',
    unsafe_allow_html=True
)

kpi_items = []
for company in selected_companies:
    cfg = COMPANY_COLUMNS[company]
    stock_performance = (
        (latest_stock[cfg["stock"]] / first_stock[cfg["stock"]]) - 1
    ) * 100
    kpi_items.append({
        "label": f"{cfg['emoji']} {company} Latest Price (USD/share)",
        "value": f"${latest_stock[cfg['stock']]:.2f}",
        "delta": f"{stock_performance:+.2f}% in selected stock period",
    })
for company in selected_companies:
    cfg = COMPANY_COLUMNS[company]
    kpi_items.append({
        "label": f"💰 {company} Avg. Revenue ({revenue_start_year}–{revenue_end_year})",
        "value": f"${revenue_means[cfg['revenue']]:,.2f}M",
        "delta": "Annual average, USD millions",
    })

kpi_cols = st.columns(len(kpi_items))
for col, item in zip(kpi_cols, kpi_items):
    with col:
        st.metric(label=item["label"], value=item["value"], delta=item["delta"])

st.caption(
    f"Revenue KPIs and revenue charts use the shared {revenue_start_year}–{revenue_end_year} period. "
    f"Revenue values are in USD millions. Stock prices are in USD per share; "
    f"the provided comparison dataset spans {stock_data_start} to {stock_data_end}. "
    f"The selected stock period currently ends on {latest_stock_date}. "
    "The Stock Price Period filter affects stock-price views and stock KPIs; "
    "the Company filter affects all dashboard sections."
)

# =====================================================
# STOCK PRICE COMPARISON
# =====================================================

st.markdown(
    '<div class="section-title">📈 Stock Price Comparison</div>',
    unsafe_allow_html=True
)
stock_columns = [COMPANY_COLUMNS[c]["stock"] for c in selected_companies]
stock_color_map = {
    COMPANY_COLUMNS[c]["stock"]: COMPANY_COLUMNS[c]["color"]
    for c in selected_companies
}
fig_stock = px.line(
    filtered_stock, x="Date", y=stock_columns,
    color_discrete_map=stock_color_map,
    labels={"value": "Stock Price (USD)", "Date": "Date", "variable": "Company"}
)
fig_stock.update_traces(
    line=dict(width=3),
    hovertemplate="<b>%{fullData.name}</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>"
)
fig_stock.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    xaxis=dict(title="Date", color="white", gridcolor="rgba(255,255,255,0.08)"),
    yaxis=dict(title="Stock Price (USD)", color="white", gridcolor="rgba(255,255,255,0.08)"),
    legend=dict(title="Company", font=dict(color="white")),
    hovermode="x unified", height=500, margin=dict(l=20, r=20, t=30, b=20)
)
st.plotly_chart(fig_stock, width="stretch", config={"responsive": True, "displaylogo": False})

# =====================================================
# REVENUE + GROWTH CHARTS
# =====================================================

col_left, col_right = st.columns(2)

with col_left:
    st.markdown('<div class="section-title">💰 Revenue Comparison</div>', unsafe_allow_html=True)
    revenue_columns = [COMPANY_COLUMNS[c]["revenue"] for c in selected_companies]
    revenue_color_map = {
        COMPANY_COLUMNS[c]["revenue"]: COMPANY_COLUMNS[c]["color"]
        for c in selected_companies
    }
    fig_revenue = px.line(
        revenue_comparison, x="Year", y=revenue_columns,
        color_discrete_map=revenue_color_map,
        labels={"value": "Revenue (USD millions)", "Year": "Year", "variable": "Company"}
    )
    fig_revenue.update_traces(
        line=dict(width=3),
        hovertemplate="<b>%{fullData.name}</b><br>Year: %{x}<br>Revenue: $%{y:,.0f}M<extra></extra>"
    )
    fig_revenue.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis=dict(title="Year", color="white", gridcolor="rgba(255,255,255,0.08)"),
        yaxis=dict(title="Revenue (USD millions)", color="white", gridcolor="rgba(255,255,255,0.08)"),
        legend=dict(title="Company", font=dict(color="white")),
        hovermode="x unified", height=430, margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig_revenue, width="stretch", config={"responsive": True, "displaylogo": False})

with col_right:
    st.markdown('<div class="section-title">📊 Revenue Growth</div>', unsafe_allow_html=True)
    growth_columns = [COMPANY_COLUMNS[c]["growth"] for c in selected_companies]
    growth_color_map = {
        COMPANY_COLUMNS[c]["growth"]: COMPANY_COLUMNS[c]["color"]
        for c in selected_companies
    }
    fig_growth = px.line(
        revenue_growth_comparison, x="Year", y=growth_columns,
        color_discrete_map=growth_color_map,
        labels={"value": "Year-over-Year Revenue Growth (%)", "Year": "Year", "variable": "Company"}
    )
    fig_growth.update_traces(
        line=dict(width=3),
        hovertemplate="<b>%{fullData.name}</b><br>Year: %{x}<br>Growth: %{y:.2f}%<extra></extra>"
    )
    fig_growth.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis=dict(title="Year", color="white", gridcolor="rgba(255,255,255,0.08)"),
        yaxis=dict(title="Year-over-Year Revenue Growth (%)", color="white", gridcolor="rgba(255,255,255,0.08)"),
        legend=dict(title="Company", font=dict(color="white")),
        hovermode="x unified", height=430, margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig_growth, width="stretch", config={"responsive": True, "displaylogo": False})

st.caption(
    f"Revenue growth is recalculated consistently from the shared {revenue_start_year}–{revenue_end_year} revenue series. "
    f"{revenue_start_year} is the baseline year, so growth starts in {revenue_start_year + 1}."
)

# =====================================================
# KEY INSIGHTS
# =====================================================

st.markdown('<div class="section-title">💡 Key Insights</div>', unsafe_allow_html=True)

insight_items = []
for company in selected_companies:
    cfg = COMPANY_COLUMNS[company]
    growth_value = average_growth[company]
    insight_items.append((
        f"{cfg['emoji']} {company}: Average Revenue Growth",
        f"Average year-over-year revenue growth was <b>{growth_value:.2f}%</b> per year "
        f"from {revenue_start_year + 1} to {revenue_end_year}. "
        + (
            "This reflects strong average growth, although the rate varied considerably by year."
            if growth_value > 0 else
            "On average, revenue declined slightly over the measured annual intervals."
        )
    ))
    insight_items.append((
        f"📊 {company}: Revenue Change",
        f"Revenue moved from <b>${revenue_comparison[cfg['revenue']].iloc[0]:,.0f}M</b> in "
        f"{revenue_start_year} to <b>${revenue_comparison[cfg['revenue']].iloc[-1]:,.0f}M</b> in "
        f"{revenue_end_year}, a total change of <b>{revenue_change[company]:+,.2f}%</b>."
    ))

insight_cols = st.columns(len(insight_items))
for col, (title, body) in zip(insight_cols, insight_items):
    with col:
        st.markdown(
            f'<div class="insight-card"><div class="insight-title">{title}</div>'
            f'<div class="insight-text">{body}</div></div>',
            unsafe_allow_html=True
        )

# Peak-growth highlights are limited to the selected companies.
peak_bits = []
for company in selected_companies:
    peak = highest_growth[company]
    peak_bits.append(
        f"<b>{company}</b> recorded its strongest annual revenue growth in "
        f"<b>{peak['year']}</b> at <b>{peak['value']:.2f}%</b>."
    )
st.markdown(
    '<div class="insight-card" style="margin-top:16px;">'
    '<div class="insight-title">🏆 Strongest Annual Growth</div>'
    f'<div class="insight-text">{" ".join(peak_bits)}</div>'
    '</div>',
    unsafe_allow_html=True
)

# =====================================================
# CONCLUSION
# =====================================================

st.markdown('<div class="section-title">🔎 Conclusion</div>', unsafe_allow_html=True)

if len(selected_companies) == 2:
    tesla_avg = average_growth["Tesla"]
    gme_avg = average_growth["GameStop"]
    tesla_change = revenue_change["Tesla"]
    gme_change = revenue_change["GameStop"]
    conclusion = (
        f"Across the shared {revenue_start_year}–{revenue_end_year} revenue window, "
        f"<b>Tesla’s revenue increased by {tesla_change:,.2f}%</b>, from "
        f"${revenue_comparison['Tesla Revenue'].iloc[0]:,.0f}M to "
        f"${revenue_comparison['Tesla Revenue'].iloc[-1]:,.0f}M. "
        f"<b>GameStop’s revenue changed by {gme_change:+.2f}%</b>, from "
        f"${revenue_comparison['GameStop Revenue'].iloc[0]:,.0f}M to "
        f"${revenue_comparison['GameStop Revenue'].iloc[-1]:,.0f}M. "
        f"Average annual revenue growth was {tesla_avg:.2f}% for Tesla and "
        f"{gme_avg:.2f}% for GameStop over 2010–2020, with the annual growth chart "
        "showing that neither company followed a perfectly steady path. "
        "Tesla’s largest annual revenue jump in the shared period was in 2013, while "
        "GameStop’s strongest year-over-year increase was in 2018. "
        "The stock-price chart adds a market-performance perspective, but stock prices "
        "and company revenue measure different things: a share price is affected by "
        "market expectations and other factors, not revenue alone. "
        "Taken together, the charts show why financial comparisons are stronger when "
        "long-term market prices, revenue levels, and year-over-year changes are reviewed together."
    )
else:
    company = selected_companies[0]
    cfg = COMPANY_COLUMNS[company]
    peak = highest_growth[company]
    conclusion = (
        f"Across the shared {revenue_start_year}–{revenue_end_year} revenue window, "
        f"<b>{company} revenue changed by {revenue_change[company]:+,.2f}%</b>, from "
        f"${revenue_comparison[cfg['revenue']].iloc[0]:,.0f}M to "
        f"${revenue_comparison[cfg['revenue']].iloc[-1]:,.0f}M. "
        f"Average annual revenue growth over 2010–2020 was "
        f"<b>{average_growth[company]:.2f}%</b>, and the strongest annual increase "
        f"was <b>{peak['value']:.2f}% in {peak['year']}</b>. "
        "The stock-price chart provides a separate market-performance view for the "
        "selected stock period. Stock prices and revenue are related but not equivalent "
        "measures, so neither should be used alone to explain the other."
    )

st.markdown(
    '<div class="conclusion-box">'
    '<div class="conclusion-title">What does the analysis show?</div>'
    f'<div class="conclusion-text">{conclusion}<br><br>'
    'This project demonstrates an end-to-end analysis workflow: collecting and cleaning '
    'financial datasets, aligning a shared comparison period, calculating revenue growth, '
    'and communicating results through interactive charts and metrics.'
    '</div></div>',
    unsafe_allow_html=True
)

# =====================================================
# FOOTER
# =====================================================

st.markdown(
    '<div class="footer">Built with Python • Pandas • Plotly • Streamlit'
    '<br>Tesla vs GameStop Financial Analysis</div>',
    unsafe_allow_html=True
)
