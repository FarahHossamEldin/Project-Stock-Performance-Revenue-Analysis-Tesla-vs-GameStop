
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Tesla vs GameStop | Stock & Revenue Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

TESLA_COLOR = "#1f77b4"
GAMESTOP_COLOR = "#ff7f0e"

COLORS = {
    "Tesla": TESLA_COLOR,
    "GameStop": GAMESTOP_COLOR
}

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    [data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.18);
        padding: 16px;
        border-radius: 12px;
    }
    .insight-card {
        padding: 16px;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# 2. DATA LOADING AND CLEANING
# =========================================================

BASE_DIR = Path(__file__).resolve().parent


@st.cache_data
def load_csv(filename):
    path = BASE_DIR / filename

    if not path.exists():
        return None

    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()

    return df


def find_column(df, candidates):
    """Find a column using case-insensitive matching."""
    if df is None:
        return None

    lookup = {str(c).strip().lower(): c for c in df.columns}

    for candidate in candidates:
        if candidate.lower() in lookup:
            return lookup[candidate.lower()]

    return None


def clean_numeric(series):
    """Convert numbers stored as strings into numeric values."""
    return pd.to_numeric(
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip()
        .replace({"nan": None, "None": None, "": None}),
        errors="coerce"
    )


def prepare_stock_data(df):
    if df is None:
        return None

    date_col = find_column(
        df, ["Date", "Datetime", "Year", "Period"]
    )
    tesla_col = find_column(
        df, ["Tesla Close", "TSLA Close", "Tesla Stock Price",
             "TSLA", "Tesla"]
    )
    game_col = find_column(
        df, ["GameStop Close", "GME Close", "GameStop Stock Price",
             "GME", "GameStop"]
    )

    if not all([date_col, tesla_col, game_col]):
        return None

    result = df[[date_col, tesla_col, game_col]].copy()
    result.columns = ["Date", "Tesla", "GameStop"]

    result["Date"] = pd.to_datetime(
    result["Date"],
    errors="coerce",
    format="mixed",
    utc=True
).dt.tz_convert(None)
    )

    for col in ["Tesla", "GameStop"]:
        result[col] = clean_numeric(result[col])

    result = (
        result.dropna(subset=["Date"])
        .sort_values("Date")
        .drop_duplicates(subset=["Date"])
        .reset_index(drop=True)
    )

    return result if not result.empty else None


def prepare_revenue_data(df):
    if df is None:
        return None

    date_col = find_column(
        df, ["Date", "Year", "Fiscal Year", "Period"]
    )
    tesla_col = find_column(
        df, ["Tesla Revenue", "Tesla", "TSLA Revenue"]
    )
    game_col = find_column(
        df, ["GameStop Revenue", "GameStop", "GME Revenue"]
    )

    if not all([date_col, tesla_col, game_col]):
        return None

    result = df[[date_col, tesla_col, game_col]].copy()
    result.columns = ["Date", "Tesla", "GameStop"]

    # Support both year-only values and full dates.
    result["Date"] = pd.to_datetime(
        result["Date"].astype(str).str.strip(),
        errors="coerce"
    )

    for col in ["Tesla", "GameStop"]:
        result[col] = clean_numeric(result[col])

    result = (
        result.dropna(subset=["Date"])
        .sort_values("Date")
        .drop_duplicates(subset=["Date"])
        .reset_index(drop=True)
    )

    return result if not result.empty else None


# =========================================================
# 3. LOAD PROJECT FILES
# =========================================================

raw_stock = load_csv("stock_comparison.csv")
raw_revenue = load_csv("revenue_comparison.csv")

stock = prepare_stock_data(raw_stock)
revenue = prepare_revenue_data(raw_revenue)

if stock is None:
    st.error(
        "Could not prepare stock data. Check stock_comparison.csv "
        "and confirm it contains Date, Tesla Close, and GameStop Close "
        "(or equivalent supported column names)."
    )
    st.stop()

if revenue is None:
    st.error(
        "Could not prepare revenue data. Check revenue_comparison.csv "
        "and confirm it contains Date/Year, Tesla Revenue, and "
        "GameStop Revenue."
    )
    st.stop()

# Restrict calculations and charts to valid numeric observations.
stock_valid = stock.dropna(subset=["Tesla", "GameStop"]).copy()
revenue_valid = revenue.dropna(subset=["Tesla", "GameStop"]).copy()

if stock_valid.empty or revenue_valid.empty:
    st.error("The CSV files do not contain enough valid numeric data.")
    st.stop()

stock_valid["Year"] = stock_valid["Date"].dt.year
revenue_valid["Year"] = revenue_valid["Date"].dt.year

stock_valid["Tesla Return %"] = (
    stock_valid["Tesla"].pct_change() * 100
)
stock_valid["GameStop Return %"] = (
    stock_valid["GameStop"].pct_change() * 100
)

revenue_valid["Tesla Growth %"] = (
    revenue_valid["Tesla"].pct_change() * 100
)
revenue_valid["GameStop Growth %"] = (
    revenue_valid["GameStop"].pct_change() * 100
)


# =========================================================
# 4. HELPER FUNCTIONS
# =========================================================

def money(value, decimals=2):
    if pd.isna(value):
        return "N/A"
    return f"${value:,.{decimals}f}"


def percentage(value):
    if pd.isna(value):
        return "N/A"
    return f"{value:+.2f}%"


def total_return(series):
    """Price change from first to last observation, not dividends."""
    series = series.dropna()

    if len(series) < 2 or series.iloc[0] == 0:
        return float("nan")

    return (series.iloc[-1] / series.iloc[0] - 1) * 100


def revenue_growth(series):
    """First-to-last revenue change, not annualized growth."""
    series = series.dropna()

    if len(series) < 2 or series.iloc[0] == 0:
        return float("nan")

    return (series.iloc[-1] / series.iloc[0] - 1) * 100


def make_line_chart(
    df, x, columns, title, y_title, percent=False
):
    fig = go.Figure()

    for company in columns:
        fig.add_trace(
            go.Scatter(
                x=df[x],
                y=df[company],
                name=company,
                mode="lines",
                line=dict(color=COLORS[company], width=2.5),
                connectgaps=False,
                hovertemplate=(
                    "%{x|%Y-%m-%d}<br>"
                    + company
                    + ": %{y:,.2f}"
                    + ("%" if percent else "")
                    + "<extra></extra>"
                )
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title=y_title,
        template="plotly_white",
        hovermode="x unified",
        legend_title_text="Company",
        margin=dict(l=15, r=15, t=60, b=15)
    )

    return fig


# =========================================================
# 5. SIDEBAR FILTERS
# =========================================================

st.sidebar.title("📊 Dashboard Controls")
st.sidebar.caption("Tesla vs GameStop")

min_year = int(stock_valid["Year"].min())
max_year = int(stock_valid["Year"].max())

selected_years = st.sidebar.slider(
    "Stock analysis period",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1
)

stock_filtered = stock_valid[
    stock_valid["Year"].between(
        selected_years[0], selected_years[1]
    )
].copy()

if stock_filtered.empty:
    st.warning("No stock data available for this period.")
    st.stop()

rev_min_year = int(revenue_valid["Year"].min())
rev_max_year = int(revenue_valid["Year"].max())

revenue_years = st.sidebar.slider(
    "Revenue analysis period",
    min_value=rev_min_year,
    max_value=rev_max_year,
    value=(rev_min_year, rev_max_year),
    step=1
)

revenue_filtered = revenue_valid[
    revenue_valid["Year"].between(
        revenue_years[0], revenue_years[1]
    )
].copy()

if revenue_filtered.empty:
    st.warning("No revenue data available for this period.")
    st.stop()


# =========================================================
# 6. DASHBOARD HEADER
# =========================================================

st.title("📈 Tesla vs GameStop")
st.subheader("Stock Performance & Revenue Analysis")

st.markdown(
    """
    An interactive comparison of two very different companies:
    **Tesla**, an electric vehicle and clean-energy company, and
    **GameStop**, a video-game retailer.

    Explore historical stock prices, relative performance, revenue
    trends, and revenue growth to understand how their financial
    trajectories compare.
    """
)

st.caption(
    f"Stock period: {selected_years[0]}–{selected_years[1]} "
    f"| Revenue period: {revenue_years[0]}–{revenue_years[1]}"
)

st.divider()


# =========================================================
# 7. EXECUTIVE SUMMARY / KPI CARDS
# =========================================================

tesla_stock_return = total_return(stock_filtered["Tesla"])
game_stock_return = total_return(stock_filtered["GameStop"])

tesla_revenue_growth = revenue_growth(revenue_filtered["Tesla"])
game_revenue_growth = revenue_growth(revenue_filtered["GameStop"])

tesla_latest_price = stock_filtered["Tesla"].iloc[-1]
game_latest_price = stock_filtered["GameStop"].iloc[-1]

tesla_latest_revenue = revenue_filtered["Tesla"].iloc[-1]
game_latest_revenue = revenue_filtered["GameStop"].iloc[-1]

st.header("Executive Summary")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Tesla Stock Change",
    percentage(tesla_stock_return),
    help="Change from the first to the last available stock price "
         "in the selected period. Excludes dividends."
)

k2.metric(
    "GameStop Stock Change",
    percentage(game_stock_return),
    help="Change from the first to the last available stock price "
         "in the selected period. Excludes dividends."
)

k3.metric(
    "Tesla Revenue Change",
    percentage(tesla_revenue_growth),
    help="Change from the first to the last available revenue "
         "observation in the selected period."
)

k4.metric(
    "GameStop Revenue Change",
    percentage(game_revenue_growth),
    help="Change from the first to the last available revenue "
         "observation in the selected period."
)

st.caption(
    "Stock changes are price changes, not total shareholder returns. "
    "Revenue changes compare the endpoints of the selected period."
)


# =========================================================
# 8. STOCK PERFORMANCE
# =========================================================

st.divider()
st.header("1. Stock Market Performance")

st.markdown(
    "Compare historical closing prices and relative growth. "
    "Stock prices are shown in USD."
)

tab1, tab2, tab3 = st.tabs([
    "Closing Prices",
    "Indexed Performance",
    "Daily Returns"
])

with tab1:
    fig = make_line_chart(
        stock_filtered,
        "Date",
        ["Tesla", "GameStop"],
        "Historical Closing Stock Prices",
        "Closing Price (USD)"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "Interpretation: closing-price levels are useful for tracking "
        "each stock over time, but they do not directly measure which "
        "investment performed better because the stocks started at "
        "different prices."
    )

with tab2:
    indexed = stock_filtered[["Date", "Tesla", "GameStop"]].copy()

    for company in ["Tesla", "GameStop"]:
        first_price = indexed[company].iloc[0]

        if pd.notna(first_price) and first_price != 0:
            indexed[company] = (
                indexed[company] / first_price
            ) * 100
        else:
            indexed[company] = float("nan")

    fig = make_line_chart(
        indexed,
        "Date",
        ["Tesla", "GameStop"],
        "Relative Stock Performance (First Observation = 100)",
        "Indexed Value"
    )

    fig.add_hline(
        y=100,
        line_dash="dash",
        line_color="gray",
        annotation_text="Starting baseline = 100"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        """
        **How to read this chart**

        - An indexed value of **150** means the stock price is 50%
          above its starting value in the selected period.
        - A value of **80** means the price is 20% below its starting value.
        - Comparing the lines helps identify which stock gained or lost
          more proportionally, regardless of its original share price.
        """
    )

with tab3:
    returns = stock_filtered[
        ["Date", "Tesla Return %", "GameStop Return %"]
    ].melt(
        id_vars="Date",
        var_name="Company",
        value_name="Daily Return (%)"
    )

    returns["Company"] = returns["Company"].replace({
        "Tesla Return %": "Tesla",
        "GameStop Return %": "GameStop"
    })

    fig = px.line(
        returns,
        x="Date",
        y="Daily Return (%)",
        color="Company",
        color_discrete_map=COLORS,
        title="Daily Percentage Price Changes",
        template="plotly_white"
    )

    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.update_layout(
        hovermode="x unified",
        xaxis_title="Date",
        yaxis_title="Daily Return (%)"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Daily returns measure the percentage change from one available "
        "stock observation to the next. Large spikes indicate unusually "
        "large price movements, not necessarily a change in business revenue."
    )


# =========================================================
# 9. REVENUE ANALYSIS
# =========================================================

st.divider()
st.header("2. Revenue Analysis")

st.markdown(
    "Revenue reflects sales generated by the business. It is not the "
    "same as profit, cash flow, or stock-market performance."
)

revenue_chart = revenue_filtered.melt(
    id_vars="Date",
    value_vars=["Tesla", "GameStop"],
    var_name="Company",
    value_name="Revenue"
)

fig = px.line(
    revenue_chart,
    x="Date",
    y="Revenue",
    color="Company",
    color_discrete_map=COLORS,
    markers=True,
    title="Historical Revenue Comparison",
    template="plotly_white"
)

fig.update_layout(
    hovermode="x unified",
    xaxis_title="Year",
    yaxis_title="Revenue (USD)",
    legend_title="Company"
)

st.plotly_chart(fig, use_container_width=True)

r1, r2 = st.columns(2)

with r1:
    fig = px.bar(
        revenue_chart,
        x="Date",
        y="Revenue",
        color="Company",
        barmode="group",
        color_discrete_map=COLORS,
        title="Revenue by Reporting Period",
        template="plotly_white"
    )
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Revenue (USD)"
    )
    st.plotly_chart(fig, use_container_width=True)

with r2:
    growth_chart = revenue_filtered[
        ["Date", "Tesla Growth %", "GameStop Growth %"]
    ].melt(
        id_vars="Date",
        var_name="Company",
        value_name="Revenue Growth (%)"
    )

    growth_chart["Company"] = growth_chart["Company"].replace({
        "Tesla Growth %": "Tesla",
        "GameStop Growth %": "GameStop"
    })

    fig = px.bar(
        growth_chart,
        x="Date",
        y="Revenue Growth (%)",
        color="Company",
        barmode="group",
        color_discrete_map=COLORS,
        title="Period-over-Period Revenue Growth",
        template="plotly_white"
    )

    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Revenue Growth (%)"
    )

    st.plotly_chart(fig, use_container_width=True)


# =========================================================
# 10. DATA SUMMARY TABLES
# =========================================================

st.divider()
st.header("3. Financial Summary")

summary = pd.DataFrame({
    "Metric": [
        "First Stock Price (USD)",
        "Latest Stock Price (USD)",
        "Stock Price Change (%)",
        "First Revenue (USD)",
        "Latest Revenue (USD)",
        "Revenue Change (%)"
    ],
    "Tesla": [
        stock_filtered["Tesla"].iloc[0],
        tesla_latest_price,
        tesla_stock_return,
        revenue_filtered["Tesla"].iloc[0],
        tesla_latest_revenue,
        tesla_revenue_growth
    ],
    "GameStop": [
        stock_filtered["GameStop"].iloc[0],
        game_latest_price,
        game_stock_return,
        revenue_filtered["GameStop"].iloc[0],
        game_latest_revenue,
        game_revenue_growth
    ]
})

with st.expander("View detailed comparison table"):
    st.dataframe(
        summary,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Metric": st.column_config.TextColumn("Metric"),
            "Tesla": st.column_config.NumberColumn(
                "Tesla", format="%.2f"
            ),
            "GameStop": st.column_config.NumberColumn(
                "GameStop", format="%.2f"
            )
        }
    )

with st.expander("View stock data"):
    st.dataframe(
        stock_filtered,
        hide_index=True,
        use_container_width=True
    )

with st.expander("View revenue data"):
    st.dataframe(
        revenue_filtered,
        hide_index=True,
        use_container_width=True
    )


# =========================================================
# 11. AUTOMATED INSIGHTS
# =========================================================

st.divider()
st.header("4. Key Insights")

# Stock performance insight
if pd.notna(tesla_stock_return) and pd.notna(game_stock_return):
    if tesla_stock_return > game_stock_return:
        stock_winner = "Tesla"
        stock_gap = tesla_stock_return - game_stock_return
    elif game_stock_return > tesla_stock_return:
        stock_winner = "GameStop"
        stock_gap = game_stock_return - tesla_stock_return
    else:
        stock_winner = "Both stocks recorded the same endpoint change"
        stock_gap = 0

    st.markdown(
        f"""
        <div class="insight-card">
        <b>📈 Relative stock performance</b><br>
        Over the selected period, <b>{stock_winner}</b> had the stronger
        endpoint price change. The difference between the two changes
        was <b>{stock_gap:.2f} percentage points</b>.
        </div>
        """,
        unsafe_allow_html=True
    )

# Revenue insight
if pd.notna(tesla_revenue_growth) and pd.notna(game_revenue_growth):
    if tesla_revenue_growth > game_revenue_growth:
        revenue_winner = "Tesla"
        revenue_gap = tesla_revenue_growth - game_revenue_growth
    elif game_revenue_growth > tesla_revenue_growth:
        revenue_winner = "GameStop"
        revenue_gap = game_revenue_growth - tesla_revenue_growth
    else:
        revenue_winner = "Both companies recorded the same endpoint change"
        revenue_gap = 0

    st.markdown(
        f"""
        <div class="insight-card">
        <b>💰 Revenue trajectory</b><br>
        <b>{revenue_winner}</b> recorded the stronger change in revenue
        between the first and last observations of the selected period.
        The difference was <b>{revenue_gap:.2f} percentage points</b>.
        </div>
        """,
        unsafe_allow_html=True
    )

# Revenue direction insight
tesla_revenue_direction = (
    "increased" if tesla_revenue_growth > 0
    else "decreased" if tesla_revenue_growth < 0
    else "remained unchanged"
)

game_revenue_direction = (
    "increased" if game_revenue_growth > 0
    else "decreased" if game_revenue_growth < 0
    else "remained unchanged"
)

st.markdown(
    f"""
    <div class="insight-card">
    <b>🔎 Business growth</b><br>
    Tesla's revenue {tesla_revenue_direction} by
    <b>{percentage(tesla_revenue_growth)}</b> across the selected
    endpoints, while GameStop's revenue {game_revenue_direction} by
    <b>{percentage(game_revenue_growth)}</b>.
    </div>
    """,
    unsafe_allow_html=True
)

# Volatility insight
tesla_volatility = stock_filtered["Tesla Return %"].std()
game_volatility = stock_filtered["GameStop Return %"].std()

if pd.notna(tesla_volatility) and pd.notna(game_volatility):
    if tesla_volatility > game_volatility:
        volatility_text = (
            "Tesla had the higher standard deviation of daily price changes."
        )
    elif game_volatility > tesla_volatility:
        volatility_text = (
            "GameStop had the higher standard deviation of daily price changes."
        )
    else:
        volatility_text = (
            "Both stocks had the same standard deviation of daily price changes."
        )

    st.markdown(
        f"""
        <div class="insight-card">
        <b>⚡ Price volatility</b><br>
        {volatility_text} This describes historical price variability,
        not the probability of future gains or losses.
        </div>
        """,
        unsafe_allow_html=True
    )

st.caption(
    "Insights are calculated from the selected data and date ranges. "
    "Endpoint comparisons do not describe every movement between those dates."
)


# =========================================================
# 12. FINAL CONCLUSION
# =========================================================

st.divider()
st.header("5. Conclusion")

st.markdown(
    f"""
    This analysis compares Tesla and GameStop from two perspectives:
    **stock-market performance** and **business revenue**.

    - **Stock performance:** Tesla's endpoint price change was
      {percentage(tesla_stock_return)}, compared with
      {percentage(game_stock_return)} for GameStop.

    - **Revenue performance:** Tesla's revenue changed by
      {percentage(tesla_revenue_growth)}, while GameStop's revenue
      changed by {percentage(game_revenue_growth)} between the first
      and last observations in the selected revenue period.

    - **Risk perspective:** daily price variability helps explain how
      differently the stocks moved over time, but historical volatility
      alone cannot predict future returns.

    **Overall takeaway:** stock-price growth and revenue growth measure
    different aspects of a company. A stock can move differently from
    its underlying revenue because market expectations, profitability,
    business risks, and other factors also influence its valuation.
    Therefore, the strongest conclusion comes from evaluating both
    financial trends together rather than treating either metric alone
    as a complete measure of business performance.
    """
)

st.info(
    "This dashboard is for educational and analytical purposes only. "
    "It does not constitute investment advice."
)


# =========================================================
# 13. FOOTER
# =========================================================

st.divider()

st.caption(
    "Tesla vs GameStop Stock Performance & Revenue Analysis | "
    "Python • Pandas • Plotly • Streamlit"
)

st.caption(
    "Historical data analysis — past performance does not guarantee "
    "future results."
)
