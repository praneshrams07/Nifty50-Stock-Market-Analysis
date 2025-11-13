import os
import yaml
import pandas as pd

# --------------------- PATH SETUP ---------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, "dataset", "Raw_Data")
OUTPUT_DIR = os.path.join(BASE_DIR, "dataset", "Clean_Data")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --------------------- EXTRACTION ---------------------
def extract_yaml_to_csv():
    print(f"🔍 Reading data from: {RAW_DATA_DIR}")

    all_data = {}

    # Loop through each month folder (e.g., 2024-09)
    for month_folder in sorted(os.listdir(RAW_DATA_DIR)):
        month_path = os.path.join(RAW_DATA_DIR, month_folder)
        if not os.path.isdir(month_path):
            continue

        print(f"\n📂 Processing Month: {month_folder}")

        # Loop through YAML files inside each month
        for file in sorted(os.listdir(month_path)):
            if not file.endswith(".yaml"):
                continue

            file_path = os.path.join(month_path, file)
            with open(file_path, "r") as f:
                records = yaml.safe_load(f)

            if not isinstance(records, list):
                continue

            # Add month info and group by Ticker
            for record in records:
                ticker = record.get("Ticker")
                if not ticker:
                    continue
                record["month_folder"] = month_folder
                all_data.setdefault(ticker, []).append(record)

    # Save CSV for each Ticker
    for ticker, rows in all_data.items():
        df = pd.DataFrame(rows)
        df.to_csv(os.path.join(OUTPUT_DIR, f"{ticker}.csv"), index=False)
        print(f"✅ Saved {ticker}.csv ({len(df)} rows)")

    print("\n🎉 Extraction complete! All CSVs stored in Clean_Data/")

# --------------------- MAIN ---------------------
if __name__ == "__main__":
    extract_yaml_to_csv()
