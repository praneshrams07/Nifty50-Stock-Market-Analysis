import pandas as pd
import numpy as np
import os
import json
import difflib
from sqlalchemy import create_engine

# --------------------- LOAD DB SETTINGS ---------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
settings_path = os.path.join(BASE_DIR, "db_settings.json")

if not os.path.exists(settings_path):
    print("❌ ERROR: db_settings.json not found. Run clean_data.py first.")
    exit()

with open(settings_path, "r") as f:
    db = json.load(f)

host = db["host"]
port = db["port"]
user = db["user"]
password = db["password"]
DB_NAME = db["db"]

print(f"🔐 Loaded DB settings from db_settings.json ({host})")

# SQLAlchemy engine
engine_url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{DB_NAME}"
engine = create_engine(engine_url)

# --------------------- LOAD DAILY DATA ---------------------
print("📥 Loading daily_data from MySQL...")
df = pd.read_sql("SELECT ticker, date, open, close, high, low, volume FROM daily_data", con=engine)

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["ticker", "date"])

print("✅ Loaded daily data successfully.")

# --------------------- LOAD SECTOR DATA ---------------------
sector_path = os.path.join(BASE_DIR, "dataset", "Sector_data.csv")

if not os.path.exists(sector_path):
    print("❌ ERROR: Sector_data.csv missing in dataset folder.")
    exit()

sec_df = pd.read_csv(sector_path)

# Clean sector data
sec_df.columns = ["company", "sector", "symbol"]
sec_df["ticker"] = sec_df["symbol"].str.split(":").str[-1].str.strip()
sec_df = sec_df[["ticker", "sector"]]

# --------------------- FUZZY MATCH SECTORS ---------------------
all_tickers = df["ticker"].unique().tolist()

def fuzzy_match(ticker):
    matches = difflib.get_close_matches(ticker, all_tickers, n=1, cutoff=0.7)
    return matches[0] if matches else None

sec_df["ticker_matched"] = sec_df["ticker"].apply(fuzzy_match)
sec_df["ticker_final"] = sec_df["ticker_matched"].fillna(sec_df["ticker"])

# Fix Airtel naming mismatch
sec_df.loc[sec_df["ticker_final"] == "AIRTEL", "ticker_final"] = "BHARTIARTL"

# Add missing BRITANNIA manually
if "BRITANNIA" not in sec_df["ticker_final"].values:
    sec_df.loc[len(sec_df)] = ["BRITANNIA", "FMCG", None, "BRITANNIA"]

final_sectors = sec_df[["ticker_final", "sector"]]
final_sectors.columns = ["ticker", "sector"]

# --------------------- METRIC 1: DAILY RETURNS ---------------------
df["return"] = df.groupby("ticker")["close"].pct_change()

# --------------------- METRIC 2: ANNUAL RETURNS ---------------------
latest = df.groupby("ticker")["close"].last()
first = df.groupby("ticker")["close"].first()
yearly = ((latest - first) / first * 100).reset_index()
yearly.columns = ["ticker", "annual_returns"]

# --------------------- METRIC 3: VOLATILITY ---------------------
vol = df.groupby("ticker")["return"].std().reset_index()
vol.columns = ["ticker", "volatility"]

# --------------------- METRIC 4: MONTHLY RETURNS ---------------------
df["month"] = df["date"].dt.to_period("M")
first_m = df.groupby(["ticker", "month"])["close"].first()
last_m = df.groupby(["ticker", "month"])["close"].last()

monthly = ((last_m - first_m) / first_m * 100).reset_index(name="monthly_return_%")
monthly["month"] = monthly["month"].dt.to_timestamp()

# --------------------- METRIC 5: CUMULATIVE RETURNS ---------------------
df["cumulative_returns"] = (1 + df["return"]).groupby(df["ticker"]).cumprod() - 1
cum_df = df[["ticker", "date", "cumulative_returns"]]

# --------------------- METRIC 6: AVG PRICE + AVG VOLUME ---------------------
df["average_price"] = (df["open"] + df["close"]) / 2
avg_df = df.groupby("ticker")[["average_price", "volume"]].mean().reset_index()

# --------------------- SUMMARY TABLE ---------------------
summary = (
    yearly.merge(vol, on="ticker", how="left")
          .merge(final_sectors, on="ticker", how="left")
)

# --------------------- SAVE ALL RESULTS TO SQL ---------------------
print("💾 Uploading analytics tables to SQL...")

yearly.to_sql("yearly_returns", con=engine, if_exists="replace", index=False)
vol.to_sql("volatility", con=engine, if_exists="replace", index=False)
monthly.to_sql("monthly_returns", con=engine, if_exists="replace", index=False)
cum_df.to_sql("cumulative_returns", con=engine, if_exists="replace", index=False)
avg_df.to_sql("avg_per_stock", con=engine, if_exists="replace", index=False)
summary.to_sql("summary", con=engine, if_exists="replace", index=False)

print("🎉 Analysis Complete!")
print("🎉 All analytics tables uploaded successfully!")
