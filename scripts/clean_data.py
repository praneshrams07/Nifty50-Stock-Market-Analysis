import os
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine, text
import json   # <-- added for saving credentials

# --------------------- PATH SETUP ---------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "dataset", "Clean_Data")

# --------------------- MYSQL DEFAULTS ---------------------
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 3306
DEFAULT_USER = "root"
DEFAULT_PASSWORD = ""  # blank default
DB_NAME = "stockdata"

print("🔐 MySQL Connection Setup")
host = input(f"Hostname [{DEFAULT_HOST}]: ") or DEFAULT_HOST
port = input(f"Port [{DEFAULT_PORT}]: ") or DEFAULT_PORT
user = input(f"Username [{DEFAULT_USER}]: ") or DEFAULT_USER
password = input("Password (leave blank if none): ") or DEFAULT_PASSWORD

# --------------------- SAVE DB SETTINGS FOR analysis.py ---------------------
settings_path = os.path.join(BASE_DIR, "db_settings.json")

with open(settings_path, "w") as f:
    json.dump({
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "db": DB_NAME
    }, f)

print(f"💾 Saved DB settings to: {settings_path}")

# --------------------- MYSQL CONNECTION ---------------------
try:
    conn = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password
    )
    cursor = conn.cursor()
    print("✅ Connected to MySQL server.")
except mysql.connector.Error as err:
    print(f"❌ Error connecting to MySQL: {err}")
    exit()

# --------------------- CREATE DATABASE ---------------------
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
print(f"✅ Database '{DB_NAME}' is ready.")
cursor.close()
conn.close()

# --------------------- SQLALCHEMY ENGINE ---------------------
connection_url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{DB_NAME}"
engine = create_engine(connection_url)

# --------------------- CREATE daily_data TABLE ---------------------
create_table_query = """
CREATE TABLE IF NOT EXISTS daily_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(20),
    date DATE,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume BIGINT,
    month_folder VARCHAR(20)
);
"""

with engine.begin() as connection:
    connection.execute(text(create_table_query))

print("✅ Table 'daily_data' is ready.")

# --------------------- UPLOAD CLEAN CSVs ---------------------
def upload_csvs():
    for file in os.listdir(DATA_DIR):
        if file.endswith(".csv"):
            file_path = os.path.join(DATA_DIR, file)
            df = pd.read_csv(file_path)

            # Clean column names (force lowercase)
            df.columns = [c.strip().lower() for c in df.columns]

            # ❗ Remove unwanted 'month' column (not needed in SQL)
            if "month" in df.columns:
                df.drop(columns=["month"], inplace=True)

            # Fix date column
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date

            # Add missing columns if needed
            required_cols = ["ticker", "date", "open", "high", "low", "close", "volume", "month_folder"]
            for col in required_cols:
                if col not in df.columns:
                    df[col] = None

            # Set ticker = filename if missing
            ticker_name = os.path.splitext(file)[0]
            df["ticker"] = df["ticker"].fillna(ticker_name)

            print(f"⬆️ Uploading {file} ({len(df)} rows)...")
            df.to_sql("daily_data", con=engine, if_exists="append", index=False)

    print("🎉 All CSVs uploaded successfully!")

# --------------------- RUN ---------------------
if __name__ == "__main__":
    upload_csvs()

