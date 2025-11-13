import os
import pandas as pd
from sqlalchemy import create_engine
import json

# --------------------- PATH SETUP ---------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_PATH = os.path.join(BASE_DIR, "db_settings.json")

# --------------------- LOAD DB SETTINGS FROM JSON ---------------------
if not os.path.exists(SETTINGS_PATH):
    raise FileNotFoundError("❌ db_settings.json not found. Run clean_data.py first.")

with open(SETTINGS_PATH, "r") as f:
    db = json.load(f)

DB_USER = db["user"]
DB_PASSWORD = db["password"]
DB_HOST = db["host"]
DB_PORT = db["port"]
DB_NAME = db["db"]

# --------------------- DB CONNECTION ---------------------
engine = create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# --------------------- EXPORT DIRECTORY ---------------------
OUTPUT_DIR = os.path.join(BASE_DIR, "dataset", "results")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --------------------- EXPORT FUNCTION ---------------------
def export_table(table_name, output_filename):
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    print(f"📤 Exporting {table_name} → {output_path}")
    df = pd.read_sql(f"SELECT * FROM {table_name}", con=engine)
    df.to_excel(output_path, index=False)
    print(f"✅ {len(df)} rows written to {output_filename}")

# --------------------- EXPORT FOR TABLEAU ---------------------
exports = {
    "summary": "summary.xlsx",
}

for table, filename in exports.items():
    export_table(table, filename)

print("\n🎉 All datasets exported successfully for Tableau Public!")
print(f"📁 Files saved in: {OUTPUT_DIR}")


