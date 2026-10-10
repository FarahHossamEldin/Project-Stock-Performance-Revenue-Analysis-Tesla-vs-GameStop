# =====================================================
# TESLA vs GAMESTOP - INTERACTIVE ANALYSIS DASHBOARD
# =====================================================
# Files expected next to this app.py:
#   stock_comparison.csv, revenue_comparison.csv, revenue_growth_comparison.csv
# =====================================================

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Tesla vs GameStop | Interactive Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =====================================================
# CONSTANTS
# =====================================================

TESLA = "Tesla"
GME = "GameStop"
COMPANIES = [TESLA, GME]

COLORS = {TESLA: "#00BFFF", GME: "#FF6B6B"}
ACCENT = "#FBBF24"
GRID = "rgba(255,255,255,0.08)"
PLOT_CONFIG = {"displaylogo": False, "responsive": True}

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

PRESETS = [
    "All Time",
    "10 Years",
    "5 Years",
    "3 Years",
    "1 Year",
    "Year to Date",
    "GME Squeeze (Dec 2020 - Mar 2021)",
    "Custom range",
]


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
}

.block-container { padding-top: 2rem; }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1220 0%, #0f172a 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}

.main-title {
    font-size: 48px;
    font-weight: 800;
    text-align: center;
    margin-top: 0;
    margin-bottom: 5px;
    background: linear-gradient(90deg, #00BFFF, #ffffff, #FF6B6B);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    color: #cbd5e1;
    margin-bottom: 14px;
}

.chips { text-align: center; margin-bottom: 28px; }

.chip {
    display: inline-block;
    padding: 5px 14px;
    margin: 3px 4px;
    font-size: 13px;
    color: #e2e8f0;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 999px;
}

.section-title {
    font-size: 24px;
    font-weight: 700;
    color: white;
    margin-top: 22px;
    margin-bottom: 4px;
}

.section-note {
    font-size: 14px;
    color: #94a3b8;
    margin-bottom: 12px;
}

/* Tabs */

div[data-baseweb="tab-list"] { gap: 6px; }

button[data-baseweb="tab"] {
    font-size: 16px;
    font-weight: 600;
    padding: 10px 18px;
    border-radius: 12px 12px 0 0;
}

/* KPI cards */

div[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(255,255,255,0.12), rgba(255,255,255,0.035));
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 20px;
    padding: 20px 22px;
    box-shadow: 0px 15px 35px rgba(0,0,0,0.35), inset 0px 1px 1px rgba(255,255,255,0.15);
    backdrop-filter: blur(15px);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0px 20px 45px rgba(0,0,0,0.5), 0px 0px 25px rgba(0,191,255,0.15);
}

div[data-testid="stMetricValue"] { font-size: 28px; font-weight: 700; }

/* Chart containers */

div[data-testid="stPlotlyChart"] {
    background: linear-gradient(145deg, rgba(255,255,255,0.07), rgba(255,255,255,0.025));
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px;
    padding: 8px;
    box-shadow: 0px 15px 35px rgba(0,0,0,0.3), inset 0px 1px 1px rgba(255,255,255,0.08);
}

/* Insight cards */

.insight-card {
    background: linear-gradient(145deg, rgba(255,255,255,0.10), rgba(255,255,255,0.035));
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 18px;
    padding: 20px;
    min-height: 170px;
    box-shadow: 0px 12px 30px rgba(0,0,0,0.30);
    backdrop-filter: blur(12px);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.insight-card:hover {
    transform: translateY(-5px);
    box-shadow: 0px 18px 35px rgba(0,0,0,0.4), 0px 0px 20px rgba(0,191,255,0.10);
}

.insight-title { font-size: 17px; font-weight: 700; color: white; margin-bottom: 12px; }
.insight-text  { font-size: 15px; color: #e2e8f0; line-height: 1.6; }

/* Scorecards */

.scorecard {
    background: linear-gradient(145deg, rgba(255,255,255,0.09), rgba(255,255,255,0.03));
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 18px;
    padding: 18px 22px 10px 22px;
    box-shadow: 0px 12px 30px rgba(0,0,0,0.30);
    margin-bottom: 14px;
}

.sc-title { font-size: 19px; font-weight: 700; color: white; margin-bottom: 10px; }

.sc-row {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}

.sc-row:last-child { border-bottom: none; }
.sc-label { color: #94a3b8; font-size: 14px; }
.sc-value { color: white; font-size: 15px; font-weight: 600; text-align: right; }

/* Conclusion box */

.conclusion-box {
    background: linear-gradient(135deg, rgba(0,191,255,0.12), rgba(255,107,107,0.08));
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 22px;
    padding: 26px 32px;
    box-shadow: 0px 15px 35px rgba(0,0,0,0.35);
    margin-top: 10px;
    margin-bottom: 14px;
}

.conclusion-title { font-size: 22px; font-weight: 700; color: white; margin-bottom: 12px; }
.conclusion-text  { font-size: 16px; color: #e2e8f0; line-height: 1.8; }
.conclusion-text li { margin-bottom: 6px; }

/* Footer */

.footer {
    text-align: center;
    color: #94a3b8;
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

@st.cache_data(show_spinner=False)
def load_data():
    # ---- Stock prices ----
    stock = pd.read_csv("stock_comparison.csv")
    stock["Date"] = (
        pd.to_datetime(stock["Date"], errors="coerce", utc=True)
        .dt.tz_localize(None)
        .dt.normalize()
    )
    stock = (
        stock.dropna(subset=["Date"])
        .sort_values("Date")
        .drop_duplicates("Date")
        .set_index("Date")
        .rename(columns={"Tesla Close": TESLA, "GameStop Close": GME})[COMPANIES]
        .dropna()
    )

    # ---- Revenue (USD millions) ----
    revenue = pd.read_csv("revenue_comparison.csv")
    revenue["Year"] = pd.to_numeric(revenue["Year"], errors="coerce")
    revenue = (
        revenue.dropna(subset=["Year"])
        .astype({"Year": int})
        .sort_values("Year")
        .set_index("Year")
        .rename(columns={"Tesla Revenue": TESLA, "GameStop Revenue": GME})[COMPANIES]
    )

    # ---- Revenue growth (stored as fractions: 0.25 = 25%) ----
    growth = pd.read_csv("revenue_growth_comparison.csv")
    growth["Year"] = pd.to_numeric(growth["Year"], errors="coerce")
    growth = (
        growth.dropna(subset=["Year"])
        .astype({"Year": int})
        .sort_values("Year")
        .set_index("Year")
        .rename(columns={"Tesla Growth %": TESLA, "GameStop Growth %": GME})[COMPANIES]
        / 100.0
    )

    return stock, revenue, growth


stock, revenue, growth = load_data()

DATA_MIN = stock.index.min()
DATA_MAX = stock.index.max()

# Full-history helpers (computed once, then sliced by the selected range)
daily_full = stock.pct_change()
ma50_full = stock.rolling(50).mean()
ma200_full = stock.rolling(200).mean()
year_end = stock.groupby(stock.index.year).last()
annual_ret = year_end.pct_change()   # first (partial) year is NaN


# =====================================================
# HELPERS
# =====================================================

def fmt_pct(v, decimals=1, sign=True):
    """Format a fraction (0.25) as a percentage string."""
    if v is None or pd.isna(v):
        return "—"
    v = v * 100
    d = 0 if abs(v) >= 1000 else decimals
    return f"{v:+,.{d}f}%" if sign else f"{v:,.{d}f}%"


def fmt_rev(v):
    """Format revenue given in USD millions."""
    if v is None or pd.isna(v):
        return "—"
    return f"${v / 1000:,.1f}B" if abs(v) >= 1000 else f"${v:,.0f}M"


def fmt_date(d):
    return pd.Timestamp(d).strftime("%b %d, %Y")


def style_fig(fig, height=450, xtitle=None, ytitle=None, log=False,
              tickprefix=None, ticksuffix=None):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=height,
        margin=dict(l=20, r=20, t=50, b=20),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1, font=dict(color="white")),
        xaxis=dict(title=xtitle, gridcolor=GRID),
        yaxis=dict(title=ytitle, gridcolor=GRID,
                   type="log" if log else "linear",
                   tickprefix=tickprefix, ticksuffix=ticksuffix),
    )
    return fig


def show(fig, key):
    st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG, key=key)


def section(title, note=None):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if note:
        st.markdown(f'<div class="section-note">{note}</div>', unsafe_allow_html=True)


def insight_card(title, body):
    return (
        f'<div class="insight-card">'
        f'<div class="insight-title">{title}</div>'
        f'<div class="insight-text">{body}</div>'
        f'</div>'
    )


def scorecard(title, color, rows):
    items = "".join(
        f'<div class="sc-row"><span class="sc-label">{label}</span>'
        f'<span class="sc-value">{value}</span></div>'
        for label, value in rows
    )
    return (
        f'<div class="scorecard" style="border-top:3px solid {color}">'
        f'<div class="sc-title">{title}</div>{items}</div>'
    )


def resolve_range(preset):
    years = {"10 Years": 10, "5 Years": 5, "3 Years": 3, "1 Year": 1}
    if preset in years:
        return max(DATA_MIN, DATA_MAX - pd.DateOffset(years=years[preset])), DATA_MAX
    if preset == "Year to Date":
        return max(DATA_MIN, pd.Timestamp(DATA_MAX.year, 1, 1)), DATA_MAX
    if preset == PRESETS[6]:
        return pd.Timestamp("2020-12-01"), pd.Timestamp("2021-03-31")
    return DATA_MIN, DATA_MAX


def perf_metrics(prices):
    prices = prices.dropna()
    rets = prices.pct_change().dropna()
    days = (prices.index[-1] - prices.index[0]).days
    total = prices.iloc[-1] / prices.iloc[0] - 1
    cagr = (1 + total) ** (365.25 / days) - 1 if days >= 360 else np.nan
    dd = prices / prices.cummax() - 1
    return dict(
        latest=prices.iloc[-1],
        total=total,
        cagr=cagr,
        vol=rets.std() * np.sqrt(252),
        max_dd=dd.min(), max_dd_date=dd.idxmin(),
        peak=prices.max(), peak_date=prices.idxmax(),
        best_day=rets.max(), best_day_date=rets.idxmax(),
        worst_day=rets.min(), worst_day_date=rets.idxmin(),
        up_days=(rets > 0).mean(),
    )


def rev_cagr(series):
    s = series.dropna()
    if len(s) < 2 or s.iloc[0] <= 0:
        return np.nan
    n = s.index[-1] - s.index[0]
    return (s.iloc[-1] / s.iloc[0]) ** (1 / n) - 1


# =====================================================
# SIDEBAR CONTROLS
# =====================================================

with st.sidebar:
    st.markdown("## 🎛️ Dashboard Controls")

    preset = st.selectbox("Stock time range", PRESETS, index=0)

    if preset == "Custom range":
        picked = st.date_input(
            "Select start and end dates",
            value=(DATA_MIN.date(), DATA_MAX.date()),
            min_value=DATA_MIN.date(),
            max_value=DATA_MAX.date(),
        )
        if isinstance(picked, (list, tuple)) and len(picked) == 2:
            start, end = pd.Timestamp(picked[0]), pd.Timestamp(picked[1])
        else:
            start, end = DATA_MIN, DATA_MAX
            st.caption("Pick both a start and an end date.")
    else:
        start, end = resolve_range(preset)

    if end < start:
        start, end = end, start

    companies = st.multiselect("Companies", COMPANIES, default=COMPANIES)
    if not companies:
        st.warning("Select at least one company - showing both.")
        companies = COMPANIES

    log_scale = st.checkbox(
        "Logarithmic price axis",
        value=True,
        help="Recommended for long ranges: Tesla grew so much that "
             "GameStop looks flat on a linear axis.",
    )
