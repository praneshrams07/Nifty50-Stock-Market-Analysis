# --------------------- REMOVE ALL WARNINGS ---------------------
import warnings
warnings.filterwarnings("ignore")

# --------------------- IMPORTS ---------------------
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os, json

# --------------------- STREAMLIT CONFIG ---------------------
st.set_page_config(page_title="Stock Analysis Dashboard", layout="wide")
st.title("📊 Nifty 50 Stock Performance Dashboard")
st.markdown("Visual insights from live MySQL data — volatility, returns, and sector performance")

# --------------------- LOAD DB SETTINGS ---------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
settings_path = os.path.join(BASE_DIR, "db_settings.json")

if not os.path.exists(settings_path):
    st.error("❌ db_settings.json not found. Run clean_data.py first.")
    st.stop()

with open(settings_path, "r") as f:
    db = json.load(f)

engine = create_engine(
    f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['db']}"
)

# --------------------- LOAD SQL DATA ---------------------
@st.cache_data(ttl=600)
def load_data():
    summary = pd.read_sql("SELECT * FROM summary", con=engine)
    cumulative = pd.read_sql("SELECT * FROM cumulative_returns", con=engine)
    monthly = pd.read_sql("SELECT * FROM monthly_returns", con=engine)
    daily = pd.read_sql("SELECT ticker, date, close FROM daily_data", con=engine)
    avg_df = pd.read_sql("SELECT * FROM avg_per_stock", con=engine)

    # Normalize col names
    for df in [summary, cumulative, monthly, daily, avg_df]:
        df.columns = [c.lower() for c in df.columns]

    cumulative["date"] = pd.to_datetime(cumulative["date"], errors="coerce")
    monthly["month"] = pd.to_datetime(monthly["month"], errors="coerce")
    daily["date"] = pd.to_datetime(daily["date"], errors="coerce")

    return summary, cumulative, monthly, daily, avg_df

summary, cumulative, monthly, daily, avg_df = load_data()

# --------------------- TABS ---------------------
tab0, tab1, tab2, tab3 = st.tabs([
    "🏠 Home",
    "📈 Cumulative Returns",
    "📅 Monthly Gainers/Losers",
    "🔗 Correlation of Stocks"
])

# =========================================================
# 🏠 TAB 0 — HOME
# =========================================================
with tab0:
    st.subheader("🏠 Market Overview Dashboard")

    green_stocks = (summary["annual_returns"] > 0).sum()
    red_stocks = (summary["annual_returns"] <= 0).sum()

    col1, col2, _, _ = st.columns(4)
    col1.metric("🟢 Green Stocks", green_stocks)
    col2.metric("🔴 Red Stocks", red_stocks)

    st.markdown("---")

    # Tableau Link
    st.subheader("📊 Explore the Full Tableau Dashboard")
    st.link_button(
        "🔗 View Tableau Dashboard on Tableau Public",
        "https://public.tableau.com/app/profile/praneshram.s/viz/Nifty50MarketOverviewAnnualReturnsVolatilityDashboard/Dashboard1"
    )

    st.markdown("### 📊 Average Price & Volume by Stock")
    avg_table = avg_df.sort_values("average_price", ascending=False)
    st.dataframe(
        avg_table.style.format({"average_price": "{:,.2f}", "volume": "{:,.0f}"}),
        width='stretch'
    )

# =========================================================
# 📈 TAB 1 — CUMULATIVE RETURNS
# =========================================================
with tab1:
    st.subheader("📈 Cumulative Return — Top 5 Performing Stocks")

    top5 = summary.sort_values("annual_returns", ascending=False)["ticker"].head(5).tolist()
    top5_df = cumulative[cumulative["ticker"].isin(top5)]

    fig = px.line(
        top5_df,
        x="date",
        y="cumulative_returns",
        color="ticker",
        title="Cumulative Returns Over Time"
    )
    fig.update_layout(xaxis_title="Date", yaxis_title="Cumulative Return")

    st.plotly_chart(fig, width='stretch')

# =========================================================
# 📅 TAB 2 — MONTHLY GAINERS & LOSERS
# =========================================================
with tab2:
    st.subheader("📅 Monthly Top Gainers & Losers")

    months = sorted(monthly["month"].dt.strftime("%Y-%m").unique(), reverse=True)
    selected_month = st.selectbox("Select Month", months)

    month_df = monthly[monthly["month"].dt.strftime("%Y-%m") == selected_month]

    gainers = month_df.sort_values("monthly_return_%", ascending=False).head(5)
    losers = month_df.sort_values("monthly_return_%", ascending=True).head(5)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"🏆 Top 5 Gainers — {selected_month}")
        fig1 = px.bar(
            gainers, x="ticker", y="monthly_return_%",
            color="monthly_return_%", color_continuous_scale="Greens"
        )
        st.plotly_chart(fig1, width='stretch')

    with col2:
        st.subheader(f"💔 Top 5 Losers — {selected_month}")
        fig2 = px.bar(
            losers, x="ticker", y="monthly_return_%",
            color="monthly_return_%", color_continuous_scale="Reds"
        )
        st.plotly_chart(fig2, width='stretch')

# =========================================================
# 🔗 TAB 3 — CORRELATION HEATMAP
# =========================================================
with tab3:
    st.subheader("📊 Stock Price Correlation Heatmap")

    df = daily.dropna(subset=["ticker", "close", "date"])
    pivot_df = df.pivot(index="date", columns="ticker", values="close").dropna(axis=1, how="all")
    corr = pivot_df.corr()

    fig = px.imshow(
        corr,
        title="Correlation Heatmap",
        zmin=-1, zmax=1,
        color_continuous_scale="RdBu_r"
    )

    fig.update_layout(width=1100, height=900)
    st.plotly_chart(fig, width='stretch')

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption("Developed by Praneshram S | Live SQL Data | Powered by Streamlit + Plotly")
