
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Tesla vs GameStop | Financial Analysis",
    page_icon="📈",
    layout="wide"
)

st.title("Tesla vs GameStop")
st.subheader("Stock Performance & Revenue Analysis")
st.markdown(
    "An interactive comparison of historical stock prices, "
    "revenue trends, and financial performance."
)

st.caption(
    "Data-driven analysis | Python · Pandas · Plotly · Streamlit"
)

# =========================================================
# THEME / CONSTANTS
# =========================================================

COLORS = {
    "Tesla": "#367BF5",
    "GameStop": "#F59E0B",
}

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    [data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.08);
        padding: 16px;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# DATA LOADING
# =========================================================

BASE_DIR = Path(__file__).resolve().parent


def load_csv(filename):
    path = BASE_DIR / filename

    if not path.exists():
        return None

    try:
        return pd.read_csv(path)
    except Exception:
        return None


def clean_column_names(df):
    df = df.copy()
    df.columns = [
        str(col).strip().replace("\ufeff", "")
        for col in df.columns
    ]
    return df


def normalize_name(name):
    return (
        str(name).lower()
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
        .replace(".", "")
        .replace("(", "")
        .replace(")", "")
    )


def find_date_column(df):
    for col in df.columns:
        name = normalize_name(col)

        if name in ["date", "datetime", "timestamp", "period"]:
            return col

    for col in df.columns:
        if "date" in normalize_name(col):
            return col

    return None


def parse_dates(series):
    # Handles mixed date formats and timezone differences.
    parsed = pd.to_datetime(
        series.astype(str).str.strip(),
        errors="coerce",
        format="mixed",
        utc=True
    )

    return parsed.dt.tz_convert(None)


def clean_numeric(series):
    cleaned = (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace("£", "", regex=False)
        .str.replace("€", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip()
    )

    cleaned = cleaned.replace(
        ["", "nan", "None", "NaN", "-", "—"],
        np.nan
    )

    return pd.to_numeric(cleaned, errors="coerce")


def find_company_columns(df):
    """Find wide-format Tesla and GameStop columns."""
    found = {}

    for col in df.columns:
        name = normalize_name(col)

        if "tesla" in name or name in ["tsla", "tslaclose"]:
            found["Tesla"] = col

        elif (
            "gamestop" in name
            or name in ["gme", "gm e", "gmec​​lose"]
        ):
            found["GameStop"] = col

    return found


def find_metric_column(df, metric):
    """Find common stock-price or revenue column names."""
    candidates = []

    for col in df.columns:
        name = normalize_name(col)

        if metric == "stock":
            if any(
                word in name
                for word in [
                    "close", "stockprice", "shareprice",
                    "price", "adjclose"
                ]
            ):
                candidates.append(col)

        elif metric == "revenue":
            if "revenue" in name or "sales" in name:
                candidates.append(col)

    return candidates[0] if candidates else None


def prepare_data(df, metric):
    """
    Converts common wide or long CSV layouts into:
    Date, Tesla, GameStop
    """
    if df is None or df.empty:
        return None

    df = clean_column_names(df)

    date_col = find_date_column(df)

    if date_col is None:
        st.warning(
            f"Could not identify a date column in the {metric} dataset."
        )
        return None

    df["__date__"] = parse_dates(df[date_col])
    df = df.dropna(subset=["__date__"]).copy()

    if df.empty:
        st.warning(
            f"No valid dates were found in the {metric} dataset."
        )
        return None

    company_cols = find_company_columns(df)

    # Wide format: separate columns for Tesla and GameStop.
    if "Tesla" in company_cols and "GameStop" in company_cols:
        result = pd.DataFrame({
            "Date": df["__date__"],
            "Tesla": clean_numeric(df[company_cols["Tesla"]]),
            "GameStop": clean_numeric(df[company_cols["GameStop"]]),
        })

    else:
        # Long format: one company column and one metric column.
        company_col = None

        for col in df.columns:
            name = normalize_name(col)

            if name in [
                "company", "stock", "ticker", "symbol",
                "companyname", "name"
            ]:
                company_col = col
                break

        metric_col = find_metric_column(df, metric)

        if company_col is None or metric_col is None:
            # Try using the two most likely numeric columns
            # only when company columns can be identified.
            st.warning(
                f"Could not recognize the {metric} data layout. "
                "Expected separate Tesla and GameStop columns, "
                "or company/ticker and metric columns."
            )
            return None

        labels = df[company_col].astype(str).str.lower()

        company_names = np.select(
            [
                labels.str.contains("tesla")
                | labels.str.fullmatch("tsla"),

                labels.str.contains("gamestop")
                | labels.str.fullmatch("gme"),
            ],
            ["Tesla", "GameStop"],
            default=""
        )

        long_df = pd.DataFrame({
            "Date": df["__date__"],
            "Company": company_names,
            "Value": clean_numeric(df[metric_col]),
        })

        long_df = long_df[long_df["Company"] != ""]

        if long_df.empty:
            st.warning(
                f"No Tesla or GameStop records found in {metric} data."
            )
            return None

        result = long_df.pivot_table(
            index="Date",
            columns="Company",
            values="Value",
            aggfunc="last"
        ).reset_index()

        for company in ["Tesla", "GameStop"]:
            if company not in result.columns:
                result[company] = np.nan

        result = result[["Date", "Tesla", "GameStop"]]

    result = result.replace([np.inf, -np.inf], np.nan)
    result = result.dropna(subset=["Tesla", "GameStop"], how="all")
    result = result.sort_values("Date").drop_duplicates("Date")

    return result.reset_index(drop=True)


# =========================================================
# LOAD AVAILABLE DATASETS
# =========================================================

stock_raw = load_csv("stock_comparison.csv")
revenue_raw = load_csv("revenue_comparison.csv")

# Optional fallback file, if the individual files are absent.
combined_raw = load_csv("comparison.csv")

if stock_raw is None and combined_raw is not None:
    stock_raw = combined_raw

if revenue_raw is None and combined_raw is not None:
    revenue_raw = combined_raw

stock = prepare_data(stock_raw, "stock")
revenue = prepare_data(revenue_raw, "revenue")

if stock is None and revenue is None:
    st.error(
        "The dashboard could not load usable data. "
        "Please check that stock_comparison.csv and "
        "revenue_comparison.csv exist in the same folder as app.py "
        "and contain Date, Tesla, and GameStop columns."
    )
    st.stop()

# =========================================================
# SIDEBAR FILTERS
# =========================================================

available_dates = []

if stock is not None:
    available_dates.extend(stock["Date"].tolist())

if revenue is not None:
    available_dates.extend(revenue["Date"].tolist())

min_date = min(available_dates)
max_date = max(available_dates)

st.sidebar.header("Dashboard Filters")

date_range = st.sidebar.date_input(
    "Select analysis period",
    value=(min_date.date(), max_date.date()),
    min_value=min_date.date(),
    max_value=max_date.date()
)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date = pd.Timestamp(date_range[0])
    end_date = (
        pd.Timestamp(date_range[1])
        + pd.Timedelta(days=1)
        - pd.Timedelta(microseconds=1)
    )
else:
    start_date = pd.Timestamp(date_range)
    end_date = start_date + pd.Timedelta(days=1)

if stock is not None:
    stock_filtered = stock[
        stock["Date"].between(start_date, end_date)
    ].copy()
else:
    stock_filtered = None

if revenue is not None:
    revenue_filtered = revenue[
        revenue["Date"].between(start_date, end_date)
    ].copy()
else:
    revenue_filtered = None

if (
    stock_filtered is not None
    and stock_filtered.empty
    and revenue_filtered is not None
    and revenue_filtered.empty
):
    st.warning("No data is available for the selected period.")
    st.stop()

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def money(value, decimals=2):
    if pd.isna(value):
        return "N/A"

    return f"${value:,.{decimals}f}"


def compact_money(value):
    if pd.isna(value):
        return "N/A"

    value = float(value)
    absolute = abs(value)

    if absolute >= 1_000_000_000:
        return f"${value / 1_000_000_000:,.2f}B"

    if absolute >= 1_000_000:
        return f"${value / 1_000_000:,.2f}M"

    if absolute >= 1_000:
        return f"${value / 1_000:,.2f}K"

    return f"${value:,.2f}"


def growth_pct(series):
    values = series.dropna()

    if len(values) < 2:
        return np.nan

    first = values.iloc[0]
    last = values.iloc[-1]

    if first == 0:
        return np.nan

    return (last - first) / abs(first) * 100


def calculate_correlation(data):
    if data is None:
        return np.nan

    pair = data[["Tesla", "GameStop"]].dropna()

    if len(pair) < 2:
        return np.nan

    return pair["Tesla"].corr(pair["GameStop"])


def show_line_chart(data, title, y_title, normalize=False):
    plot_data = data.melt(
        id_vars="Date",
        value_vars=["Tesla", "GameStop"],
        var_name="Company",
        value_name="Value"
    ).dropna()

    if normalize:
        normalized = []

        for company in ["Tesla", "GameStop"]:
            company_data = plot_data[
                plot_data["Company"] == company
            ].sort_values("Date").copy()

            if not company_data.empty:
                first_value = company_data["Value"].iloc[0]

                if first_value != 0:
                    company_data["Value"] = (
                        company_data["Value"] / first_value
                    ) * 100

                normalized.append(company_data)

        if normalized:
            plot_data = pd.concat(normalized, ignore_index=True)

    fig = px.line(
        plot_data,
        x="Date",
        y="Value",
        color="Company",
        color_discrete_map=COLORS,
        title=title,
        markers=False,
        template="plotly_white"
    )

    fig.update_layout(
        height=450,
        hovermode="x unified",
        legend_title_text="Company",
        margin=dict(l=15, r=15, t=65, b=15),
        xaxis_title="Date",
        yaxis_title=y_title
    )

    return fig


# =========================================================
# EXECUTIVE SUMMARY
# =========================================================

st.header("Executive Summary")

if stock_filtered is not None and not stock_filtered.empty:
    stock_metrics = {}

    for company in ["Tesla", "GameStop"]:
        values = stock_filtered[company].dropna()

        stock_metrics[company] = {
            "latest": values.iloc[-1] if len(values) else np.nan,
            "first": values.iloc[0] if len(values) else np.nan,
            "growth": growth_pct(stock_filtered[company]),
            "high": values.max() if len(values) else np.nan,
            "low": values.min() if len(values) else np.nan,
        }

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Tesla Latest Price",
        money(stock_metrics["Tesla"]["latest"])
    )

    c2.metric(
        "GameStop Latest Price",
        money(stock_metrics["GameStop"]["latest"])
    )

    c3.metric(
        "Tesla Price Change",
        f'{stock_metrics["Tesla"]["growth"]:.2f}%'
        if pd.notna(stock_metrics["Tesla"]["growth"])
        else "N/A"
    )

    c4.metric(
        "GameStop Price Change",
        f'{stock_metrics["GameStop"]["growth"]:.2f}%'
        if pd.notna(stock_metrics["GameStop"]["growth"])
        else "N/A"
    )

if revenue_filtered is not None and not revenue_filtered.empty:
    st.markdown("#### Revenue Overview")

    rc1, rc2 = st.columns(2)

    for col, company in zip([rc1, rc2], ["Tesla", "GameStop"]):
        values = revenue_filtered[company].dropna()

        latest_revenue = values.iloc[-1] if len(values) else np.nan

        col.metric(
            f"{company} Latest Revenue",
            compact_money(latest_revenue)
        )

# =========================================================
# STOCK PERFORMANCE
# =========================================================

st.divider()
st.header("1. Stock Performance")

if stock_filtered is None or stock_filtered.empty:
    st.info("Stock data is not available for this period.")
else:
    st.markdown(
        "Explore how each stock price changed over the selected period."
    )

    tab1, tab2, tab3 = st.tabs([
        "Historical Prices",
        "Normalized Performance",
        "Price Distribution"
    ])

    with tab1:
        st.plotly_chart(
            show_line_chart(
                stock_filtered,
                "Historical Stock Prices",
                "Stock Price ($)"
            ),
            use_container_width=True
        )

    with tab2:
        st.caption(
            "Both stocks start at an index of 100. "
            "This compares relative change rather than absolute price."
        )

        st.plotly_chart(
            show_line_chart(
                stock_filtered,
                "Relative Stock Performance (Base = 100)",
                "Indexed Price",
                normalize=True
            ),
            use_container_width=True
        )

    with tab3:
        distribution = stock_filtered.melt(
            id_vars="Date",
            value_vars=["Tesla", "GameStop"],
            var_name="Company",
            value_name="Price"
        ).dropna()

        fig = px.box(
            distribution,
            x="Company",
            y="Price",
            color="Company",
            color_discrete_map=COLORS,
            points="outliers",
            title="Stock Price Distribution",
            template="plotly_white"
        )

        fig.update_layout(height=400)

        st.plotly_chart(fig, use_container_width=True)

    # Stock statistics
    stats_rows = []

    for company in ["Tesla", "GameStop"]:
        values = stock_filtered[company].dropna()

        stats_rows.append({
            "Company": company,
            "Observations": len(values),
            "First Price": values.iloc[0] if len(values) else np.nan,
            "Latest Price": values.iloc[-1] if len(values) else np.nan,
            "Minimum": values.min() if len(values) else np.nan,
            "Maximum": values.max() if len(values) else np.nan,
            "Average": values.mean() if len(values) else np.nan,
            "Price Change (%)": growth_pct(stock_filtered[company])
        })

    st.subheader("Stock Performance Statistics")

    stats_df = pd.DataFrame(stats_rows)

    st.dataframe(
        stats_df.style.format({
            "First Price": "${:,.2f}",
            "Latest Price": "${:,.2f}",
            "Minimum": "${:,.2f}",
            "Maximum": "${:,.2f}",
            "Average": "${:,.2f}",
            "Price Change (%)": "{:.2f}%"
        }, na_rep="N/A"),
        use_container_width=True,
        hide_index=True
    )

# =========================================================
# REVENUE ANALYSIS
# =========================================================

st.divider()
st.header("2. Revenue Analysis")

if revenue_filtered is None or revenue_filtered.empty:
    st.info("Revenue data is not available for this period.")
else:
    rev_long = revenue_filtered.melt(
        id_vars="Date",
        value_vars=["Tesla", "GameStop"],
        var_name="Company",
        value_name="Revenue"
    ).dropna()

    rev_long = rev_long.sort_values("Date")

    rtab1, rtab2 = st.tabs([
        "Revenue Trends",
        "Revenue Growth"
    ])

    with rtab1:
        fig = px.line(
            rev_long,
            x="Date",
            y="Revenue",
            color="Company",
            color_discrete_map=COLORS,
            markers=True,
            title="Historical Revenue",
            template="plotly_white"
        )

        fig.update_layout(
            height=450,
            hovermode="x unified",
            yaxis_title="Revenue ($, as recorded in dataset)",
            xaxis_title="Date"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "Revenue units depend on the original dataset. "
            "Check the source notebook before interpreting the scale."
        )

    with rtab2:
        growth_data = rev_long.copy()

        growth_data["Revenue Growth (%)"] = (
            growth_data.groupby("Company")["Revenue"]
            .pct_change(fill_method=None) * 100
        )

        growth_data = growth_data.replace(
            [np.inf, -np.inf], np.nan
        ).dropna(subset=["Revenue Growth (%)"])

        if not growth_data.empty:
            fig = px.bar(
                growth_data,
                x="Date",
                y="Revenue Growth (%)",
                color="Company",
                color_discrete_map=COLORS,
                barmode="group",
                title="Period-over-Period Revenue Growth",
                template="plotly_white"
            )

            fig.update_layout(
                height=450,
                yaxis_title="Revenue Growth (%)",
                xaxis_title="Date"
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(
                "Not enough consecutive revenue observations "
                "to calculate growth."
            )

    revenue_stats = []

    for company in ["Tesla", "GameStop"]:
        values = revenue_filtered[company].dropna()

        revenue_stats.append({
            "Company": company,
            "Observations": len(values),
            "First Revenue": values.iloc[0] if len(values) else np.nan,
            "Latest Revenue": values.iloc[-1] if len(values) else np.nan,
            "Minimum Revenue": values.min() if len(values) else np.nan,
            "Maximum Revenue": values.max() if len(values) else np.nan,
            "Revenue Change (%)": growth_pct(revenue_filtered[company])
        })

    st.subheader("Revenue Summary")

    st.dataframe(
        pd.DataFrame(revenue_stats).style.format({
            "First Revenue": "{:,.2f}",
            "Latest Revenue": "{:,.2f}",
            "Minimum Revenue": "{:,.2f}",
            "Maximum Revenue": "{:,.2f}",
            "Revenue Change (%)": "{:.2f}%"
        }, na_rep="N/A"),
        use_container_width=True,
        hide_index=True
    )

# =========================================================
# PRICE VS REVENUE
# =========================================================

st.divider()
st.header("3. Stock Price vs Revenue")

if (
    stock_filtered is not None
    and revenue_filtered is not None
    and not stock_filtered.empty
    and not revenue_filtered.empty
):
    st.markdown(
        "Compare stock prices and reported revenue separately "
        "for each company. Revenue and stock prices have "
        "different units, so they use separate y-axes."
    )

    for company in ["Tesla", "GameStop"]:
        left, right = st.columns(2)

        company_stock = stock_filtered[
            ["Date", company]
        ].dropna()

        company_revenue = revenue_filtered[
            ["Date", company]
        ].dropna()

        with left:
            st.subheader(f"{company}: Stock Price")

            fig = px.line(
                company_stock,
                x="Date",
                y=company,
                title=f"{company} Stock Price",
                color_discrete_sequence=[COLORS[company]],
                template="plotly_white"
            )

            fig.update_layout(
                height=350,
                xaxis_title="Date",
                yaxis_title="Price ($)",
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

        with right:
            st.subheader(f"{company}: Revenue")

            fig = px.line(
                company_revenue,
                x="Date",
                y=company,
                title=f"{company} Revenue",
                color_discrete_sequence=[COLORS[company]],
                markers=True,
                template="plotly_white"
            )

            fig.update_layout(
                height=350,
                xaxis_title="Date",
                yaxis_title="Revenue (dataset units)",
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

# =========================================================
# AUTOMATED INSIGHTS
# =========================================================

st.divider()
st.header("4. Key Insights")

insight_count = 0

if stock_filtered is not None and not stock_filtered.empty:
    tsla_growth = growth_pct(stock_filtered["Tesla"])
    gme_growth = growth_pct(stock_filtered["GameStop"])

    if pd.notna(tsla_growth) and pd.notna(gme_growth):
        stronger = (
            "Tesla"
            if tsla_growth > gme_growth
            else "GameStop"
            if gme_growth > tsla_growth
            else "both companies equally"
        )

        st.markdown(
            f"**1. Relative price change:** {stronger} "
            f"recorded the larger percentage change over the "
            f"selected period. Tesla: {tsla_growth:.2f}%; "
            f"GameStop: {gme_growth:.2f}%."
        )
        insight_count += 1

    for company in ["Tesla", "GameStop"]:
        values = stock_filtered[company].dropna()

        if len(values) >= 2:
            high = values.max()
            low = values.min()
            latest = values.iloc[-1]

            st.markdown(
                f"**{insight_count + 1}. {company} price range:** "
                f"The observed prices ranged from {money(low)} "
                f"to {money(high)}. The latest recorded price in "
                f"the selected period was {money(latest)}."
            )
            insight_count += 1

if revenue_filtered is not None and not revenue_filtered.empty:
    for company in ["Tesla", "GameStop"]:
        revenue_growth = growth_pct(revenue_filtered[company])

        if pd.notna(revenue_growth):
            st.markdown(
                f"**{insight_count + 1}. {company} revenue:** "
                f"The first-to-last observed revenue change was "
                f"{revenue_growth:.2f}% over the selected period."
            )
            insight_count += 1

if (
    stock_filtered is not None
    and not stock_filtered.empty
    and revenue_filtered is not None
    and not revenue_filtered.empty
):
    st.markdown(
        "**Interpretation note:** Stock prices reflect market "
        "expectations and other influences, not revenue alone. "
        "These charts are descriptive and do not establish "
        "that revenue changes caused stock-price movements."
    )

if insight_count == 0:
    st.info(
        "There is not enough valid data in the selected period "
        "to generate insights."
    )

# =========================================================
# CONCLUSION
# =========================================================

st.divider()
st.header("5. Conclusion")

if (
    stock_filtered is not None
    and not stock_filtered.empty
    and revenue_filtered is not None
    and not revenue_filtered.empty
):
    tsla_price_growth = growth_pct(stock_filtered["Tesla"])
    gme_price_growth = growth_pct(stock_filtered["GameStop"])

    tsla_revenue_growth = growth_pct(revenue_filtered["Tesla"])
    gme_revenue_growth = growth_pct(revenue_filtered["GameStop"])

    conclusion_parts = []

    if pd.notna(tsla_price_growth) and pd.notna(gme_price_growth):
        if tsla_price_growth > gme_price_growth:
            conclusion_parts.append(
                "Tesla showed the larger percentage change in "
                "stock price during the selected period."
            )
        elif gme_price_growth > tsla_price_growth:
            conclusion_parts.append(
                "GameStop showed the larger percentage change in "
                "stock price during the selected period."
            )
        else:
            conclusion_parts.append(
                "Both stocks showed the same first-to-last "
                "percentage change in the selected period."
            )

    if (
        pd.notna(tsla_revenue_growth)
        and pd.notna(gme_revenue_growth)
    ):
        if tsla_revenue_growth > gme_revenue_growth:
            conclusion_parts.append(
                "Tesla also recorded the larger first-to-last "
                "revenue change in the selected period."
            )
        elif gme_revenue_growth > tsla_revenue_growth:
            conclusion_parts.append(
                "GameStop recorded the larger first-to-last "
                "revenue change in the selected period."
            )
        else:
            conclusion_parts.append(
                "Both companies recorded the same first-to-last "
                "revenue percentage change in the selected period."
            )

    for sentence in conclusion_parts:
        st.write(sentence)

    st.write(
        "Overall, the comparison highlights why stock-market "
        "performance and reported revenue should be examined "
        "together but interpreted as different measures. "
        "The conclusion applies only to the dates and records "
        "included in the selected dataset."
    )

else:
    st.write(
        "Use the available price and revenue charts to assess "
        "each company's performance. A complete conclusion "
        "requires valid stock and revenue records for the "
        "selected period."
    )

# =========================================================
# DATA PREVIEW / DOWNLOAD
# =========================================================

with st.expander("View cleaned data"):
    if stock_filtered is not None:
        st.subheader("Stock Data")
        st.dataframe(stock_filtered, use_container_width=True)

        st.download_button(
            "Download stock data",
            data=stock_filtered.to_csv(index=False).encode("utf-8"),
            file_name="filtered_stock_data.csv",
            mime="text/csv"
        )

    if revenue_filtered is not None:
        st.subheader("Revenue Data")
        st.dataframe(revenue_filtered, use_container_width=True)

        st.download_button(
            "Download revenue data",
            data=revenue_filtered.to_csv(index=False).encode("utf-8"),
            file_name="filtered_revenue_data.csv",
            mime="text/csv"
        )

st.divider()
st.caption(
    "Educational data analysis project | "
    "Historical data does not guarantee future performance."
)
