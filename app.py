
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
stock_period_start = filtered_stock["Date"].min().strftime("%Y-%m-%d")
stock_period_end = filtered_stock["Date"].max().strftime("%Y-%m-%d")
fig_stock.update_layout(
    title=f"Historical Stock Prices ({stock_period_start} to {stock_period_end})",
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    xaxis=dict(title="Date", color="white", gridcolor="rgba(255,255,255,0.08)"),
    yaxis=dict(title="Stock Price (USD per share)", color="white", gridcolor="rgba(255,255,255,0.08)"),
    legend=dict(title="Company", font=dict(color="white")),
    hovermode="x unified", height=500, margin=dict(l=20, r=20, t=60, b=20)
)
st.plotly_chart(fig_stock, width="stretch", config={"responsive": True, "displaylogo": False})

# Normalize each company's prices to 100 at the start of the selected period.
# This compares relative performance rather than the companies' different share-price levels.
normalized_stock = filtered_stock[["Date"]].copy()
normalized_columns = []
normalized_color_map = {}
for company in selected_companies:
    stock_col = COMPANY_COLUMNS[company]["stock"]
    normalized_col = f"{company} Normalized Price"
    baseline = filtered_stock[stock_col].iloc[0]
    normalized_stock[normalized_col] = (filtered_stock[stock_col] / baseline) * 100
    normalized_columns.append(normalized_col)
    normalized_color_map[normalized_col] = COMPANY_COLUMNS[company]["color"]

st.markdown('<div class="section-title">📐 Normalized Stock Performance</div>', unsafe_allow_html=True)
fig_normalized = px.line(
    normalized_stock, x="Date", y=normalized_columns,
    color_discrete_map=normalized_color_map,
    labels={"value": "Normalized Price (Start = 100)", "Date": "Date", "variable": "Company"}
)
fig_normalized.update_traces(
    line=dict(width=3),
    hovertemplate="<b>%{fullData.name}</b><br>Date: %{x}<br>Normalized value: %{y:.2f}<extra></extra>"
)
fig_normalized.update_layout(
    title=f"Relative Stock Performance (Base = 100; {stock_period_start} to {stock_period_end})",
    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    xaxis=dict(title="Date", color="white", gridcolor="rgba(255,255,255,0.08)"),
    yaxis=dict(title="Normalized Price (Start = 100)", color="white", gridcolor="rgba(255,255,255,0.08)"),
    legend=dict(title="Company", font=dict(color="white")),
    hovermode="x unified", height=470, margin=dict(l=20, r=20, t=60, b=20)
)
st.plotly_chart(fig_normalized, width="stretch", config={"responsive": True, "displaylogo": False})
st.caption(
    "Why normalize? Both stocks are rebased to 100 at the beginning of the selected period. "
    "This removes the effect of their different starting share prices and makes relative performance "
    "easier to compare. A value of 150 means the stock is 50% above its starting price for this period; "
    "a value of 80 means it is 20% below its starting price."
)

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
        title=f"Annual Revenue ({revenue_start_year}–{revenue_end_year})",
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis=dict(title="Year", color="white", gridcolor="rgba(255,255,255,0.08)"),
        yaxis=dict(title="Revenue (USD millions)", color="white", gridcolor="rgba(255,255,255,0.08)"),
        legend=dict(title="Company", font=dict(color="white")),
        hovermode="x unified", height=430, margin=dict(l=20, r=20, t=60, b=20)
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
        title=f"Year-over-Year Revenue Growth ({revenue_start_year + 1}–{revenue_end_year})",
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis=dict(title="Year", color="white", gridcolor="rgba(255,255,255,0.08)"),
        yaxis=dict(title="Year-over-Year Revenue Growth (%)", color="white", gridcolor="rgba(255,255,255,0.08)"),
        legend=dict(title="Company", font=dict(color="white")),
        hovermode="x unified", height=430, margin=dict(l=20, r=20, t=60, b=20)
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
st.caption("Company-specific insights are arranged side by side: Tesla on the left and GameStop on the right.")

insight_cols = st.columns(2 if len(selected_companies) == 2 else 1)
for col, company in zip(insight_cols, selected_companies):
    cfg = COMPANY_COLUMNS[company]
    revenue_col = cfg["revenue"]
    growth_col = cfg["growth"]
    stock_col = cfg["stock"]
    company_stock = filtered_stock[["Date", stock_col]].dropna().sort_values("Date")
    first_row = company_stock.iloc[0]
    latest_row = company_stock.iloc[-1]
    period_return = ((latest_row[stock_col] / first_row[stock_col]) - 1) * 100
    low_idx = company_stock[stock_col].idxmin()
    high_idx = company_stock[stock_col].idxmax()
    low_row = company_stock.loc[low_idx]
    high_row = company_stock.loc[high_idx]
    peak = highest_growth[company]
    avg_growth = average_growth[company]
    revenue_first = revenue_comparison[revenue_col].iloc[0]
    revenue_last = revenue_comparison[revenue_col].iloc[-1]

    bullets = [
        f"<li><b>Average annual revenue growth:</b> {avg_growth:.2f}% from {revenue_start_year + 1} to {revenue_end_year}.</li>",
        f"<li><b>Revenue change:</b> ${revenue_first:,.0f}M in {revenue_start_year} to ${revenue_last:,.0f}M in {revenue_end_year} ({revenue_change[company]:+,.2f}%).</li>",
        f"<li><b>Strongest revenue-growth year:</b> {peak['year']} at {peak['value']:.2f}% year over year.</li>",
        f"<li><b>Stock-price change:</b> {period_return:+,.2f}% from ${first_row[stock_col]:.2f} on {first_row['Date'].strftime('%Y-%m-%d')} to ${latest_row[stock_col]:.2f} on {latest_row['Date'].strftime('%Y-%m-%d')}.</li>",
        f"<li><b>Period low:</b> ${low_row[stock_col]:.2f} on {low_row['Date'].strftime('%Y-%m-%d')}.</li>",
        f"<li><b>Period high:</b> ${high_row[stock_col]:.2f} on {high_row['Date'].strftime('%Y-%m-%d')}.</li>",
    ]
    with col:
        st.markdown(
            f'<div class="insight-card"><div class="insight-title">{cfg["emoji"]} {company} Insights</div>'
            f'<div class="insight-text"><ul>{"".join(bullets)}</ul></div></div>',
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
    tesla_first = revenue_comparison["Tesla Revenue"].iloc[0]
    tesla_last = revenue_comparison["Tesla Revenue"].iloc[-1]
    gme_first = revenue_comparison["GameStop Revenue"].iloc[0]
    gme_last = revenue_comparison["GameStop Revenue"].iloc[-1]
    tesla_stock_return = ((filtered_stock["Tesla Close"].iloc[-1] / filtered_stock["Tesla Close"].iloc[0]) - 1) * 100
    gme_stock_return = ((filtered_stock["GameStop Close"].iloc[-1] / filtered_stock["GameStop Close"].iloc[0]) - 1) * 100
    tesla_norm_end = (filtered_stock["Tesla Close"].iloc[-1] / filtered_stock["Tesla Close"].iloc[0]) * 100
    gme_norm_end = (filtered_stock["GameStop Close"].iloc[-1] / filtered_stock["GameStop Close"].iloc[0]) * 100

    conclusion_items = [
        (
            "1. Revenue trajectory",
            f"Across the shared {revenue_start_year}–{revenue_end_year} period, Tesla's revenue changed "
            f"from ${tesla_first:,.2f}M to ${tesla_last:,.2f}M, representing a "
            f"{tesla_change:+,.2f}% total change. GameStop's revenue changed from "
            f"${gme_first:,.2f}M to ${gme_last:,.2f}M, representing a "
            f"{gme_change:+,.2f}% total change."
        ),
        (
            "2. Stock-price performance",
            f"From {stock_period_start} to {stock_period_end}, Tesla's stock price changed by "
            f"{tesla_stock_return:+,.2f}%, while GameStop's changed by {gme_stock_return:+,.2f}%. "
            "These results describe the selected stock-price period, which can be changed using the dashboard filter."
        ),
        (
            "3. Normalized comparison and interpretation",
            f"With both stocks rebased to 100 at the start of the selected period, Tesla finished at "
            f"{tesla_norm_end:.2f} and GameStop at {gme_norm_end:.2f}. This makes their relative performance "
            "easier to compare despite different starting share prices. Revenue and stock prices measure "
            "different aspects of performance; stock prices also reflect investor expectations and broader "
            "market factors, not revenue alone. Reviewing revenue levels, annual growth, stock prices, and "
            "normalized performance together gives a more complete view of the two companies."
        )
    ]

else:
    company = selected_companies[0]
    cfg = COMPANY_COLUMNS[company]
    peak = highest_growth[company]
    revenue_first = revenue_comparison[cfg["revenue"]].iloc[0]
    revenue_last = revenue_comparison[cfg["revenue"]].iloc[-1]
    stock_return = (
        (filtered_stock[cfg["stock"]].iloc[-1] /
         filtered_stock[cfg["stock"]].iloc[0]) - 1
    ) * 100
    normalized_end = (
        filtered_stock[cfg["stock"]].iloc[-1] /
        filtered_stock[cfg["stock"]].iloc[0]
    ) * 100

    conclusion_items = [
        (
            "1. Revenue trajectory",
            f"Across the shared {revenue_start_year}–{revenue_end_year} period, {company}'s revenue changed "
            f"from ${revenue_first:,.2f}M to ${revenue_last:,.2f}M, representing a "
            f"{revenue_change[company]:+,.2f}% total change. Average annual year-over-year revenue growth "
            f"was {average_growth[company]:.2f}%, and the strongest annual growth was "
            f"{peak['value']:.2f}% in {peak['year']}."
        ),
        (
            "2. Stock-price performance",
            f"From {stock_period_start} to {stock_period_end}, {company}'s stock price changed by "
            f"{stock_return:+,.2f}%. This result reflects the stock-price period selected in the dashboard."
        ),
        (
            "3. Normalized comparison and interpretation",
            f"With the starting stock price set to 100, {company}'s normalized ending value was "
            f"{normalized_end:.2f}. Revenue and stock price measure different aspects of performance, "
            "so they should be considered together rather than using one metric alone to explain the other."
        )
    ]

conclusion_html = "".join(
    f"""
    <div style="
        margin-bottom: 18px;
        white-space: normal;
        overflow-wrap: break-word;
        word-wrap: break-word;
        line-height: 1.8;
    ">
        <div style="
            font-size: 17px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 6px;
        ">{heading}</div>
        <p style="
            margin: 0;
            color: #e2e8f0;
            white-space: normal;
            overflow-wrap: break-word;
            word-wrap: break-word;
            line-height: 1.8;
        ">{body}</p>
    </div>
    """
    for heading, body in conclusion_items
)

st.markdown(
    f"""
    <div class="conclusion-box" style="
        width: 100%;
        max-width: 100%;
        box-sizing: border-box;
        white-space: normal;
        overflow-wrap: break-word;
        word-wrap: break-word;
    ">
        <div class="conclusion-title">What does the analysis show?</div>
        <div class="conclusion-text" style="
            width: 100%;
            max-width: 100%;
            box-sizing: border-box;
            white-space: normal;
            overflow-wrap: break-word;
            word-wrap: break-word;
            word-break: normal;
        ">
            {conclusion_html}
        </div>
    </div>
    """,
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
