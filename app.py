
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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

.subtitle {
    text-align: center;
    font-size: 18px;
    color: #cbd5e1 !important;
    margin-bottom: 35px;
}

.section-title {
    font-size: 26px;
    font-weight: 700;
    color: white !important;
    margin-top: 25px;
    margin-bottom: 15px;
}

div[data-testid="stMetric"] {
    background: linear-gradient(
        145deg,
        rgba(255,255,255,0.12),
        rgba(255,255,255,0.035)
    );
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0px 15px 35px rgba(0,0,0,0.35);
    backdrop-filter: blur(15px);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
    box-shadow: 0px 20px 45px rgba(0,0,0,0.5);
}

div[data-testid="stMetricLabel"] {
    color: #cbd5e1 !important;
}

div[data-testid="stMetricValue"] {
    color: white !important;
    font-size: 27px;
    font-weight: 700;
}

div[data-testid="stPlotlyChart"] {
    background: linear-gradient(
        145deg,
        rgba(255,255,255,0.07),
        rgba(255,255,255,0.025)
    );
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px;
    padding: 8px;
    box-shadow: 0px 15px 35px rgba(0,0,0,0.3);
}

.insight-card {
    background: linear-gradient(
        145deg,
        rgba(255,255,255,0.10),
        rgba(255,255,255,0.035)
    );
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 18px;
    padding: 20px;
    min-height: 175px;
    box-shadow: 0px 12px 30px rgba(0,0,0,0.30);
    backdrop-filter: blur(12px);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.insight-card:hover {
    transform: translateY(-4px);
    box-shadow: 0px 18px 35px rgba(0,0,0,0.4);
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
    line-height: 1.7;
}

.conclusion-box {
    background: linear-gradient(
        135deg,
        rgba(0,191,255,0.12),
        rgba(255,107,107,0.08)
    );
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 22px;
    padding: 28px 32px;
    box-shadow: 0px 15px 35px rgba(0,0,0,0.35);
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

.note-box {
    background: rgba(255,255,255,0.045);
    border-left: 3px solid #00BFFF;
    border-radius: 10px;
    padding: 14px 20px;
    margin: 10px 0 20px 0;
    color: #cbd5e1;
    line-height: 1.8;
}

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

@st.cache_data
def load_data():
    stock = pd.read_csv("stock_comparison.csv")
    revenue = pd.read_csv("revenue_comparison.csv")

    stock["Date"] = (
        pd.to_datetime(stock["Date"], errors="coerce", utc=True)
        .dt.tz_localize(None)
    )

    stock = (
        stock.dropna(subset=["Date"])
        .sort_values("Date")
        .reset_index(drop=True)
    )

    revenue["Year"] = pd.to_numeric(
        revenue["Year"], errors="coerce"
    )

    revenue = (
        revenue.dropna(subset=["Year"])
        .sort_values("Year")
        .reset_index(drop=True)
    )

    revenue["Year"] = revenue["Year"].astype(int)

    revenue = (
        revenue.query("Year >= 2009 and Year <= 2020")
        .copy()
        .reset_index(drop=True)
    )

    required_stock = ["Tesla Close", "GameStop Close"]
    required_revenue = [
        "Tesla Revenue",
        "GameStop Revenue"
    ]

    for col in required_stock:
        stock[col] = pd.to_numeric(stock[col], errors="coerce")

    for col in required_revenue:
        revenue[col] = pd.to_numeric(revenue[col], errors="coerce")

    return stock, revenue


try:
    stock_comparison, revenue_comparison = load_data()

    if stock_comparison.empty or revenue_comparison.empty:
        st.error("One or more datasets are empty after cleaning.")
        st.stop()

    if not {"Date", "Tesla Close", "GameStop Close"}.issubset(
        stock_comparison.columns
    ):
        st.error("The stock CSV is missing one or more required columns.")
        st.stop()

    if not {
        "Year", "Tesla Revenue", "GameStop Revenue"
    }.issubset(revenue_comparison.columns):
        st.error("The revenue CSV is missing one or more required columns.")
        st.stop()

except FileNotFoundError as e:
    st.error(
        f"Missing file: {e.filename}. "
        "Make sure all required CSV files are in the app directory."
    )
    st.stop()

except Exception as e:
    st.error(f"Unable to load the datasets: {e}")
    st.stop()


# =====================================================
# COMPANY CONFIGURATION
# =====================================================

COMPANY_COLUMNS = {
    "Tesla": {
        "stock": "Tesla Close",
        "revenue": "Tesla Revenue",
        "color": "#00BFFF",
        "emoji": "🚗",
    },
    "GameStop": {
        "stock": "GameStop Close",
        "revenue": "GameStop Revenue",
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
    '<div class="subtitle">'
    'Interactive Stock Performance & Revenue Analysis'
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
        ],
        help=(
            "Changes the stock-price chart, stock KPIs, "
            "and stock-related insights. Revenue analysis "
            "continues to use the shared 2009–2020 period."
        )
    )

with filter_col2:
    company_filter = st.selectbox(
        "Company",
        ["Both", "Tesla", "GameStop"],
        help=(
            "Filters the companies displayed in the KPI cards, "
            "charts, insights, and conclusion."
        )
    )

selected_companies = (
    ["Tesla", "GameStop"]
    if company_filter == "Both"
    else [company_filter]
)


# =====================================================
# FILTER STOCK DATA
# =====================================================

max_date = stock_comparison["Date"].max()

if pd.isna(max_date):
    st.error("No valid dates were found in the stock dataset.")
    st.stop()

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

filtered_stock = (
    filtered_stock.sort_values("Date")
    .reset_index(drop=True)
)

if filtered_stock.empty:
    st.warning("No stock-price records are available for this period.")
    st.stop()


# Actual date ranges represented by the available observations
stock_data_start = stock_comparison["Date"].min()
stock_data_end = stock_comparison["Date"].max()

filtered_stock_start = filtered_stock["Date"].min()
filtered_stock_end = filtered_stock["Date"].max()

stock_start_label = filtered_stock_start.strftime("%Y-%m-%d")
stock_end_label = filtered_stock_end.strftime("%Y-%m-%d")

full_stock_start_label = stock_data_start.strftime("%Y-%m-%d")
full_stock_end_label = stock_data_end.strftime("%Y-%m-%d")

revenue_start_year = int(revenue_comparison["Year"].min())
revenue_end_year = int(revenue_comparison["Year"].max())

if len(revenue_comparison) < 2:
    st.error("At least two annual revenue observations are required.")
    st.stop()


# =====================================================
# REVENUE METRICS
# =====================================================

revenue_growth_comparison = revenue_comparison[["Year"]].copy()

for company, cfg in COMPANY_COLUMNS.items():
    revenue_col = cfg["revenue"]

    revenue_growth_comparison[cfg["revenue"] + " Growth"] = (
        revenue_comparison[revenue_col].pct_change() * 100
    )

GROWTH_COLUMNS = {
    "Tesla": "Tesla Revenue Growth",
    "GameStop": "GameStop Revenue Growth"
}

revenue_means = {
    company: revenue_comparison[cfg["revenue"]].mean()
    for company, cfg in COMPANY_COLUMNS.items()
}

revenue_change = {}
average_growth = {}
highest_growth = {}
lowest_growth = {}
highest_revenue = {}
lowest_revenue = {}

for company, cfg in COMPANY_COLUMNS.items():
    revenue_col = cfg["revenue"]
    growth_col = GROWTH_COLUMNS[company]

    valid_revenue = revenue_comparison[
        ["Year", revenue_col]
    ].dropna()

    valid_growth = revenue_growth_comparison[
        ["Year", growth_col]
    ].dropna()

    first_revenue = valid_revenue.iloc[0]
    last_revenue = valid_revenue.iloc[-1]

    if first_revenue[revenue_col] != 0:
        revenue_change[company] = (
            last_revenue[revenue_col] /
            first_revenue[revenue_col] - 1
        ) * 100
    else:
        revenue_change[company] = float("nan")

    average_growth[company] = valid_growth[growth_col].mean()

    if not valid_growth.empty:
        max_growth_row = valid_growth.loc[
            valid_growth[growth_col].idxmax()
        ]
        min_growth_row = valid_growth.loc[
            valid_growth[growth_col].idxmin()
        ]

        highest_growth[company] = {
            "value": max_growth_row[growth_col],
            "year": int(max_growth_row["Year"])
        }

        lowest_growth[company] = {
            "value": min_growth_row[growth_col],
            "year": int(min_growth_row["Year"])
        }

    valid_revenue_rows = valid_revenue.dropna(
        subset=[revenue_col]
    )

    max_revenue_row = valid_revenue_rows.loc[
        valid_revenue_rows[revenue_col].idxmax()
    ]

    min_revenue_row = valid_revenue_rows.loc[
        valid_revenue_rows[revenue_col].idxmin()
    ]

    highest_revenue[company] = {
        "value": max_revenue_row[revenue_col],
        "year": int(max_revenue_row["Year"])
    }

    lowest_revenue[company] = {
        "value": min_revenue_row[revenue_col],
        "year": int(min_revenue_row["Year"])
    }


# =====================================================
# STOCK METRICS
# =====================================================

stock_metrics = {}

for company in selected_companies:
    stock_col = COMPANY_COLUMNS[company]["stock"]

    company_stock = (
        filtered_stock[["Date", stock_col]]
        .dropna(subset=[stock_col])
        .sort_values("Date")
    )

    if company_stock.empty:
        stock_metrics[company] = None
        continue

    first_row = company_stock.iloc[0]
    last_row = company_stock.iloc[-1]

    min_row = company_stock.loc[
        company_stock[stock_col].idxmin()
    ]

    max_row = company_stock.loc[
        company_stock[stock_col].idxmax()
    ]

    first_price = first_row[stock_col]
    latest_price = last_row[stock_col]

    if first_price != 0:
        price_change = (
            latest_price / first_price - 1
        ) * 100
    else:
        price_change = float("nan")

    stock_metrics[company] = {
        "first_price": first_price,
        "latest_price": latest_price,
        "latest_date": last_row["Date"],
        "first_date": first_row["Date"],
        "change": price_change,
        "min_price": min_row[stock_col],
        "min_date": min_row["Date"],
        "max_price": max_row[stock_col],
        "max_date": max_row["Date"],
        "observations": len(company_stock)
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
    metrics = stock_metrics[company]

    if metrics is not None:
        kpi_items.append({
            "label": f"{cfg['emoji']} {company} Latest Stock Price",
            "value": f"${metrics['latest_price']:.2f}",
            "delta": (
                f"As of "
                f"{metrics['latest_date'].strftime('%Y-%m-%d')}"
            )
        })

for company in selected_companies:
    cfg = COMPANY_COLUMNS[company]

    kpi_items.append({
        "label": f"💰 {company} Average Annual Revenue",
        "value": f"${revenue_means[company]:,.2f}M",
        "delta": f"FY {revenue_start_year}–{revenue_end_year}"
    })

kpi_cols = st.columns(len(kpi_items))

for col, item in zip(kpi_cols, kpi_items):
    with col:
        st.metric(
            label=item["label"],
            value=item["value"],
            delta=item["delta"]
        )


# =====================================================
# DATA COVERAGE NOTES
# =====================================================

st.markdown(
    f"""
    <div class="note-box">
        <b>📅 Data Coverage & Methodology</b>
        <ul>
            <li>
                <b>Full stock-price dataset:</b>
                {full_stock_start_label} to {full_stock_end_label}.
            </li>
            <li>
                <b>Selected stock-price period:</b>
                {stock_start_label} to {stock_end_label}.
                Each KPI card displays the latest available price
                date for its company.
            </li>
            <li>
                <b>Revenue dataset:</b>
                FY {revenue_start_year} to FY {revenue_end_year}.
                Revenue comparisons use the same annual period
                for both companies.
            </li>
            <li>
                <b>Units:</b> Stock prices are in USD per share;
                revenue figures are in USD millions.
            </li>
            <li>
                <b>Revenue growth:</b> Year-over-year percentage
                change. {revenue_start_year} is the baseline year,
                so the first growth observation is for
                {revenue_start_year + 1}.
            </li>
            <li>
                The stock period filter affects stock-related
                charts, KPIs, and insights only. Revenue charts
                and metrics remain on the shared annual period.
            </li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True
)


# =====================================================
# CHART THEME HELPER
# =====================================================

def style_figure(fig, height=430, title=None):
    fig.update_layout(
        title=dict(
            text=title or "",
            x=0.02,
            xanchor="left",
            font=dict(size=19, color="white")
        ),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        legend=dict(
            title="Company",
            font=dict(color="white"),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="x unified",
        height=height,
        margin=dict(l=25, r=25, t=85, b=30)
    )

    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.12)"
    )

    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.12)"
    )

    return fig


# =====================================================
# STOCK PRICE COMPARISON
# =====================================================

st.markdown(
    '<div class="section-title">📈 Stock Price Comparison</div>',
    unsafe_allow_html=True
)

stock_columns = [
    COMPANY_COLUMNS[c]["stock"]
    for c in selected_companies
]

stock_color_map = {
    COMPANY_COLUMNS[c]["stock"]: COMPANY_COLUMNS[c]["color"]
    for c in selected_companies
}

fig_stock = px.line(
    filtered_stock,
    x="Date",
    y=stock_columns,
    color_discrete_map=stock_color_map,
    labels={
        "value": "Stock Price (USD per share)",
        "Date": "Date",
        "variable": "Company"
    }
)

fig_stock.update_traces(
    line=dict(width=3),
    connectgaps=False,
    hovertemplate=(
        "<b>%{fullData.name}</b><br>"
        "Date: %{x|%Y-%m-%d}<br>"
        "Price: $%{y:,.2f}"
        "<extra></extra>"
    )
)

fig_stock = style_figure(
    fig_stock,
    height=520,
    title=(
        f"Historical Stock Prices | "
        f"{stock_start_label} to {stock_end_label}"
    )
)

fig_stock.update_yaxes(
    title="Stock Price (USD per share)"
)

st.plotly_chart(
    fig_stock,
    width="stretch",
    config={"responsive": True, "displaylogo": False}
)


# =====================================================
# NORMALIZED STOCK PERFORMANCE
# =====================================================

st.markdown(
    '<div class="section-title">📊 Normalized Stock Performance</div>',
    unsafe_allow_html=True
)

normalized_stock = pd.DataFrame({
    "Date": filtered_stock["Date"]
})

normalized_color_map = {}

for company in selected_companies:
    stock_col = COMPANY_COLUMNS[company]["stock"]

    company_prices = pd.to_numeric(
        filtered_stock[stock_col], errors="coerce"
    )

    valid_prices = company_prices.dropna()

    if valid_prices.empty:
        continue

    base_price = valid_prices.iloc[0]

    if base_price == 0:
        continue

    normalized_stock[company] = (
        company_prices / base_price
    ) * 100

    normalized_color_map[company] = (
        COMPANY_COLUMNS[company]["color"]
    )

normalized_columns = [
    company for company in selected_companies
    if company in normalized_stock.columns
]

if normalized_columns:
    fig_normalized = px.line(
        normalized_stock,
        x="Date",
        y=normalized_columns,
        color_discrete_map=normalized_color_map,
        labels={
            "value": "Normalized Stock Performance (Base = 100)",
            "Date": "Date",
            "variable": "Company"
        }
    )

    for company in normalized_columns:
        fig_normalized.update_traces(
            line=dict(width=3),
            connectgaps=False,
            selector={"name": company}
        )

    fig_normalized = style_figure(
        fig_normalized,
        height=500,
        title=(
            f"Relative Stock Performance | "
            f"{stock_start_label} to {stock_end_label}"
        )
    )

    fig_normalized.update_yaxes(
        title="Normalized Value (Starting Value = 100)"
    )

    fig_normalized.add_hline(
        y=100,
        line_dash="dash",
        line_color="rgba(255,255,255,0.55)",
        annotation_text="Starting Point = 100",
        annotation_position="bottom right"
    )

    st.plotly_chart(
        fig_normalized,
        width="stretch",
        config={"responsive": True, "displaylogo": False}
    )

    st.markdown(
        f"""
        <div class="note-box">
            <b>How to read this chart</b>
            <ul>
                <li>
                    <b>Period covered:</b>
                    {stock_start_label} to {stock_end_label}.
                </li>
                <li>
                    Each stock is rebased to 100 using its first
                    available valid closing price in the selected
                    period.
                </li>
                <li>
                    A normalized value of 150 represents a 50%
                    increase from the starting price. A value of
                    80 represents a 20% decrease.
                </li>
                <li>
                    This chart compares percentage performance
                    rather than actual share prices in USD.
                </li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.warning(
        "Normalized stock performance cannot be calculated "
        "for the selected companies and period."
    )


# =====================================================
# STOCK PRICE PERFORMANCE INSIGHTS
# =====================================================

st.markdown(
    '<div class="section-title">🔎 Stock Performance Insights</div>',
    unsafe_allow_html=True
)

stock_insight_items = []

for company in selected_companies:
    cfg = COMPANY_COLUMNS[company]
    metrics = stock_metrics[company]

    if metrics is None:
        stock_insight_items.append((
            f"{cfg['emoji']} {company}: Data Availability",
            "No valid stock prices are available for the selected period."
        ))
        continue

    change = metrics["change"]

    if pd.isna(change):
        performance_text = (
            "The percentage change cannot be calculated "
            "because the initial price is zero or invalid."
        )
    elif change > 0:
        performance_text = (
            f"The stock increased by <b>{change:+.2f}%</b> "
            "between the first and latest available observations."
        )
    elif change < 0:
        performance_text = (
            f"The stock decreased by <b>{change:.2f}%</b> "
            "between the first and latest available observations."
        )
    else:
        performance_text = (
            "The first and latest available stock prices were equal."
        )

    stock_insight_items.append((
        f"{cfg['emoji']} {company}: Period Performance",
        f"Opening observation: <b>${metrics['first_price']:,.2f}</b> "
        f"on {metrics['first_date'].strftime('%Y-%m-%d')}. "
        f"Latest observation: <b>${metrics['latest_price']:,.2f}</b> "
        f"on {metrics['latest_date'].strftime('%Y-%m-%d')}. "
        f"{performance_text}"
    ))

    stock_insight_items.append((
        f"📊 {company}: Price Range",
        f"Period low: <b>${metrics['min_price']:,.2f}</b> "
        f"on {metrics['min_date'].strftime('%Y-%m-%d')}. "
        f"Period high: <b>${metrics['max_price']:,.2f}</b> "
        f"on {metrics['max_date'].strftime('%Y-%m-%d')}. "
        f"The observed price range was "
        f"<b>${metrics['max_price'] - metrics['min_price']:,.2f}</b>."
    ))


stock_insights_by_company = {
    company: [] for company in selected_companies
}

for title, body in stock_insight_items:
    for company in selected_companies:
        if company in title:
            stock_insights_by_company[company].append(
                (title, body)
            )
            break

stock_insight_cols = st.columns(2)

for col_index, company in enumerate(selected_companies):
    with stock_insight_cols[col_index]:
        for title, body in stock_insights_by_company[company]:
            st.markdown(
                f'<div class="insight-card">'
                f'<div class="insight-title">{title}</div>'
                f'<div class="insight-text">{body}</div>'
                f'</div>',
                unsafe_allow_html=True
            )


# =====================================================
# REVENUE COMPARISON
# =====================================================

col_left, col_right = st.columns(2)

with col_left:
    st.markdown(
        '<div class="section-title">💰 Revenue Comparison</div>',
        unsafe_allow_html=True
    )

    revenue_columns = [
        COMPANY_COLUMNS[c]["revenue"]
        for c in selected_companies
    ]

    revenue_color_map = {
        COMPANY_COLUMNS[c]["revenue"]: COMPANY_COLUMNS[c]["color"]
        for c in selected_companies
    }

    fig_revenue = px.line(
        revenue_comparison,
        x="Year",
        y=revenue_columns,
        color_discrete_map=revenue_color_map,
        markers=True,
        labels={
            "value": "Revenue (USD millions)",
            "Year": "Fiscal Year",
            "variable": "Company"
        }
    )

    fig_revenue.update_traces(
        line=dict(width=3),
        marker=dict(size=7),
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "Year: %{x}<br>"
            "Revenue: $%{y:,.2f}M"
            "<extra></extra>"
        )
    )

    fig_revenue = style_figure(
        fig_revenue,
        height=440,
        title=(
            f"Annual Revenue | "
            f"{revenue_start_year}–{revenue_end_year}"
        )
    )

    fig_revenue.update_yaxes(
        title="Revenue (USD millions)"
    )

    fig_revenue.update_xaxes(
        dtick=1,
        title="Fiscal Year"
    )

    st.plotly_chart(
        fig_revenue,
        width="stretch",
        config={"responsive": True, "displaylogo": False}
    )


# =====================================================
# REVENUE GROWTH
# =====================================================

with col_right:
    st.markdown(
        '<div class="section-title">📊 Revenue Growth</div>',
        unsafe_allow_html=True
    )

    growth_columns = [
        GROWTH_COLUMNS[c]
        for c in selected_companies
    ]

    growth_color_map = {
        GROWTH_COLUMNS[c]: COMPANY_COLUMNS[c]["color"]
        for c in selected_companies
    }

    fig_growth = px.bar(
        revenue_growth_comparison,
        x="Year",
        y=growth_columns,
        barmode="group",
        color_discrete_map=growth_color_map,
        labels={
            "value": "Revenue Growth (%)",
            "Year": "Fiscal Year",
            "variable": "Company"
        }
    )

    fig_growth.update_traces(
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "Year: %{x}<br>"
            "YoY Growth: %{y:.2f}%"
            "<extra></extra>"
        )
    )

    fig_growth.add_hline(
        y=0,
        line_dash="dash",
        line_color="rgba(255,255,255,0.55)",
        annotation_text="0% growth",
        annotation_position="bottom right"
    )

    fig_growth = style_figure(
        fig_growth,
        height=440,
        title=(
            f"Year-over-Year Revenue Growth | "
            f"{revenue_start_year + 1}–{revenue_end_year}"
        )
    )

    fig_growth.update_yaxes(
        title="Year-over-Year Growth (%)",
        zeroline=True
    )

    fig_growth.update_xaxes(
        dtick=1,
        title="Fiscal Year"
    )

    st.plotly_chart(
        fig_growth,
        width="stretch",
        config={"responsive": True, "displaylogo": False}
    )

st.caption(
    f"Revenue growth is calculated as the percentage change "
    f"from the previous year's revenue. "
    f"{revenue_start_year} is the baseline, so the growth chart "
    f"covers {revenue_start_year + 1}–{revenue_end_year}. "
    "Negative bars indicate a year-over-year revenue decline."
)


# =====================================================
# REVENUE INSIGHTS
# =====================================================

st.markdown(
    '<div class="section-title">💡 Revenue Insights</div>',
    unsafe_allow_html=True
)

revenue_insight_items = []

for company in selected_companies:
    cfg = COMPANY_COLUMNS[company]
    revenue_col = cfg["revenue"]

    start_revenue = revenue_comparison.iloc[0][revenue_col]
    end_revenue = revenue_comparison.iloc[-1][revenue_col]

    revenue_insight_items.append((
        f"{cfg['emoji']} {company}: Long-Term Revenue Change",
        f"Revenue changed from <b>${start_revenue:,.2f}M</b> "
        f"in {revenue_start_year} to "
        f"<b>${end_revenue:,.2f}M</b> in {revenue_end_year}. "
        f"Overall change across the comparison window: "
        f"<b>{revenue_change[company]:+,.2f}%</b>."
    ))

    revenue_insight_items.append((
        f"📈 {company}: Average Annual Growth",
        f"Average year-over-year revenue growth was "
        f"<b>{average_growth[company]:+.2f}%</b> across "
        f"{revenue_start_year + 1}–{revenue_end_year}. "
        "This is the arithmetic mean of annual growth rates, "
        "not a compound annual growth rate (CAGR)."
    ))

    peak = highest_growth[company]
    trough = lowest_growth[company]

    revenue_insight_items.append((
        f"🏆 {company}: Best & Worst Growth Years",
        f"Strongest growth: <b>{peak['value']:+.2f}%</b> in "
        f"{peak['year']}. "
        f"Weakest growth: <b>{trough['value']:+.2f}%</b> in "
        f"{trough['year']}. "
        "These identify the most positive and most negative "
        "annual changes in the available revenue series."
    ))

    max_rev = highest_revenue[company]
    min_rev = lowest_revenue[company]

    revenue_insight_items.append((
        f"💵 {company}: Highest & Lowest Revenue",
        f"Highest recorded annual revenue in the shared period: "
        f"<b>${max_rev['value']:,.2f}M</b> in {max_rev['year']}. "
        f"Lowest recorded annual revenue: "
        f"<b>${min_rev['value']:,.2f}M</b> in {min_rev['year']}."
    ))


revenue_insights_by_company = {
    company: [] for company in selected_companies
}

for title, body in revenue_insight_items:
    for company in selected_companies:
        if company in title:
            revenue_insights_by_company[company].append(
                (title, body)
            )
            break

insight_cols = st.columns(2)

for col_index, company in enumerate(selected_companies):
    with insight_cols[col_index]:
        for title, body in revenue_insights_by_company[company]:
            st.markdown(
                f'<div class="insight-card">'
                f'<div class="insight-title">{title}</div>'
                f'<div class="insight-text">{body}</div>'
                f'</div>',
                unsafe_allow_html=True
            )


# =====================================================
# HEAD-TO-HEAD COMPARISON
# =====================================================

if len(selected_companies) == 2:
    st.markdown(
        '<div class="section-title">⚖️ Head-to-Head Comparison</div>',
        unsafe_allow_html=True
    )

    tesla_mean = revenue_means["Tesla"]
    gme_mean = revenue_means["GameStop"]

    tesla_avg_growth = average_growth["Tesla"]
    gme_avg_growth = average_growth["GameStop"]

    comparison_col1, comparison_col2 = st.columns(2)

    with comparison_col1:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-title">💰 Average Annual Revenue</div>
                <div class="insight-text">
                    Tesla: <b>${tesla_mean:,.2f}M</b><br>
                    GameStop: <b>${gme_mean:,.2f}M</b><br><br>
                    """
            + (
                f"Tesla's average annual revenue was "
                f"<b>{tesla_mean / gme_mean:.2f} times</b> "
                f"GameStop's average."
                if gme_mean != 0
                else "The average revenue ratio cannot be calculated because GameStop's average is zero."
            )
            + """
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with comparison_col2:
        growth_difference = tesla_avg_growth - gme_avg_growth

        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-title">📈 Average Revenue Growth</div>
                <div class="insight-text">
                    Tesla: <b>{tesla_avg_growth:+.2f}%</b><br>
                    GameStop: <b>{gme_avg_growth:+.2f}%</b><br><br>
                    The difference between their average annual
                    growth rates was <b>{growth_difference:+.2f}
                    percentage points</b>.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )






# =====================================================
# CONCLUSION
# =====================================================

st.markdown(
    '<div class="section-title">🔎 Conclusion</div>',
    unsafe_allow_html=True
)

if len(selected_companies) == 2:
    tesla_start = revenue_comparison.iloc[0]["Tesla Revenue"]
    tesla_end = revenue_comparison.iloc[-1]["Tesla Revenue"]

    gme_start = revenue_comparison.iloc[0]["GameStop Revenue"]
    gme_end = revenue_comparison.iloc[-1]["GameStop Revenue"]

    tesla_avg = average_growth["Tesla"]
    gme_avg = average_growth["GameStop"]

    tesla_peak = highest_growth["Tesla"]
    gme_peak = highest_growth["GameStop"]

    tesla_stock = stock_metrics["Tesla"]
    gme_stock = stock_metrics["GameStop"]

    # Normalized stock performance over the selected period
    tesla_normalized_end = None
    gme_normalized_end = None

    for company in ["Tesla", "GameStop"]:
        stock_col = COMPANY_COLUMNS[company]["stock"]

        valid_prices = (
            filtered_stock[["Date", stock_col]]
            .dropna(subset=[stock_col])
            .sort_values("Date")
        )

        if not valid_prices.empty:
            first_price = valid_prices.iloc[0][stock_col]
            last_price = valid_prices.iloc[-1][stock_col]

            if first_price != 0:
                normalized_end = (
                    last_price / first_price
                ) * 100

                if company == "Tesla":
                    tesla_normalized_end = normalized_end
                else:
                    gme_normalized_end = normalized_end

    if tesla_avg > gme_avg:
        growth_winner = "Tesla"
    elif gme_avg > tesla_avg:
        growth_winner = "GameStop"
    else:
        growth_winner = (
            "neither company; their average growth rates were equal"
        )

    conclusion = f"""
    <b>1. Revenue trajectory:</b><br>
    Across the shared {revenue_start_year}–{revenue_end_year} period,
    Tesla's revenue changed from
<span style="white-space: nowrap;">${tesla_start:,.2f}M to</span>
${tesla_end:,.2f}M, representing a
    <b>{revenue_change['Tesla']:+,.2f}%</b> total change.
   GameStop's revenue changed from
<span style="white-space: nowrap;">${gme_start:,.2f}M to</span>
${gme_end:,.2f}M, representing a
    <b>{revenue_change['GameStop']:+,.2f}%</b> total change.

    <br><br><b>2. Growth consistency and variation:</b><br>
    Tesla's average annual revenue growth was
    <b>{tesla_avg:+.2f}%</b>, compared with
    <b>{gme_avg:+.2f}%</b> for GameStop.
    The strongest annual revenue growth occurred in
    {tesla_peak['year']} for Tesla
    ({tesla_peak['value']:+.2f}%) and in
    {gme_peak['year']} for GameStop
    ({gme_peak['value']:+.2f}%).
    These averages can conceal considerable year-to-year variation,
    so the annual growth chart should be considered alongside
    the long-term revenue trend.

    <br><br><b>3. Market performance and normalized comparison:</b><br>
    The stock-price analysis covers the selected period,
    {stock_start_label} to {stock_end_label}.
    """

    if tesla_stock is not None:
        conclusion += (
            f" Tesla's observed stock-price change was "
            f"<b>{tesla_stock['change']:+.2f}%</b>."
            if not pd.isna(tesla_stock["change"])
            else " Tesla's stock-price percentage change could not be calculated."
        )

    if gme_stock is not None:
        conclusion += (
            f" GameStop's observed stock-price change was "
            f"<b>{gme_stock['change']:+.2f}%</b>."
            if not pd.isna(gme_stock["change"])
            else " GameStop's stock-price percentage change could not be calculated."
        )

    if (
        tesla_normalized_end is not None
        and gme_normalized_end is not None
    ):
        conclusion += (
            f" When both stocks are rebased to 100 at the start "
            f"of the selected period, Tesla finishes at "
            f"<b>{tesla_normalized_end:.2f}</b> and GameStop at "
            f"<b>{gme_normalized_end:.2f}</b>. "
            f"This corresponds to a normalized change of "
            f"<b>{tesla_normalized_end - 100:+.2f}%</b> for Tesla "
            f"and <b>{gme_normalized_end - 100:+.2f}%</b> for "
            f"GameStop. Normalization makes their relative "
            f"percentage performance easier to compare despite "
            f"different starting share prices."
        )

    conclusion += f"""

    <br><br><b>4. Overall interpretation:</b><br>
    {growth_winner} had the higher average annual revenue growth
    rate over the shared period. However, revenue size, revenue
    growth, and stock-price performance describe different aspects
    of a company's financial story. A higher average growth rate
    does not necessarily mean a company had higher revenue in
    every year.

    Stock-price performance provides a separate market perspective.
    Share prices can reflect investor expectations, perceived risk,
    and other market conditions, not just reported revenue.
    The normalized chart compares relative stock performance over
    the selected dates, while the original price chart preserves
    actual share prices in USD.

    <br><br><b>Final takeaway:</b><br>
    The strongest interpretation comes from considering revenue
    size, long-term revenue change, year-over-year growth,
    actual stock prices, and normalized stock performance together.
    These indicators complement one another, but none alone
    explains the full financial picture. The analysis describes
    historical observations and is not investment advice or
    a prediction of future returns.
    """

else:
    company = selected_companies[0]
    cfg = COMPANY_COLUMNS[company]

    start_revenue = revenue_comparison.iloc[0][cfg["revenue"]]
    end_revenue = revenue_comparison.iloc[-1][cfg["revenue"]]

    peak = highest_growth[company]
    trough = lowest_growth[company]
    stock = stock_metrics[company]

    conclusion = f"""
    <b>1. Long-term revenue performance:</b><br>
    {company}'s revenue changed from
    ${start_revenue:,.2f}M in {revenue_start_year} to
    ${end_revenue:,.2f}M in {revenue_end_year}, representing a
    <b>{revenue_change[company]:+,.2f}%</b> total change.

    <br><br><b>2. Revenue growth:</b><br>
    Average annual revenue growth was
    <b>{average_growth[company]:+.2f}%</b>.
    The strongest growth occurred in {peak['year']}
    ({peak['value']:+.2f}%), while the weakest occurred in
    {trough['year']} ({trough['value']:+.2f}%).
    This highlights why average growth should be considered
    alongside individual annual results.

    <br><br><b>3. Stock performance:</b><br>
    The selected stock-price period is
    {stock_start_label} to {stock_end_label}.
    """

    if stock is not None and not pd.isna(stock["change"]):
        conclusion += (
            f" The observed stock-price change was "
            f"<b>{stock['change']:+.2f}%</b>."
        )
    else:
        conclusion += (
            " A valid stock-price percentage change was not available."
        )

    # Add normalized performance for the selected company
    if stock is not None and not pd.isna(stock["change"]):
        conclusion += (
            f" On the normalized chart, the stock starts at 100 "
            f"and finishes at "
            f"<b>{100 + stock['change']:.2f}</b>, representing "
            f"the same <b>{stock['change']:+.2f}%</b> change "
            f"over the selected period."
        )

    conclusion += """
    <br><br><b>Final takeaway:</b><br>
    Revenue and stock prices provide complementary but distinct
    perspectives. Stock prices can respond to market expectations
    and other factors beyond reported revenue. These historical
    findings are descriptive and are not investment advice.
    """


st.markdown(
    f"""
    <div class="conclusion-box">
        <div class="conclusion-title">
            What Does the Analysis Show?
        </div>
        <div class="conclusion-text">
            {conclusion}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)




# =====================================================
# FOOTER
# =====================================================

st.markdown(
    """
    <div class="footer">
        Built with Python • Pandas • Plotly • Streamlit
        <br>
        Tesla vs GameStop Financial Analysis
        <br>
        Driven by curiosity. Powered by data. Focused on impact.
    </div>
    """,
    unsafe_allow_html=True
)
