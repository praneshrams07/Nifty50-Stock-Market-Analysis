# 📈 Nifty 50 Stock Market Analysis (Python + MySQL + Streamlit + Tableau)

A complete end-to-end stock market analytics system that processes Nifty 50 data, cleans it, stores it in MySQL, computes insights, and visualizes the trends using Streamlit and Tableau Public.

---

## 🚀 Features

✅ Automatic MySQL database setup & table creation  
✅ Clean & standardized stock data ingestion  
✅ Summary metrics: annual returns, volatility, sector performance  
✅ Monthly gainers & losers  
✅ Cumulative returns for top-performing stocks  
✅ Interactive Streamlit dashboard  
✅ Tableau dashboard for deeper visualization  
✅ Export-ready Excel datasets for Tableau  
✅ JSON-based dynamic DB config (no hard-coded credentials)

---

## 🏗️ Project Structure

```
Nifty50-Stock-Market-Analysis/
│
├── scripts/
│   ├── clean_data.py          → Creates DB, table, loads CSVs
│   ├── analysis.py            → Generates summary tables
│   ├── export_for_tableau.py  → Creates Excel files for Tableau
│   └── app.py                 → Streamlit Dashboard
│
├── dataset/                   → Raw and cleaned data files
├── db_settings.json           → Auto-generated MySQL credentials
├── requirements.txt           → Python dependencies
└── README.md
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/praneshrams07/Nifty50-Stock-Market-Analysis.git
cd Nifty50-Stock-Market-Analysis
```

### 2️⃣ Create & activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate    # macOS / Linux
venv\Scripts\activate       # Windows
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Run data ingestion
```bash
python scripts/clean_data.py
```

### 5️⃣ Run analysis & create summary tables
```bash
python scripts/analysis.py
```

### 6️⃣ Export datasets for Tableau
```bash
python scripts/export_for_tableau.py
```

### 7️⃣ Launch Streamlit dashboard
```bash
streamlit run scripts/app.py
```

---

## 🧠 Built With

- Python  
- Streamlit  
- Tableau Public  
- MySQL  
- Pandas, NumPy  
- SQLAlchemy  

---

## ✨ Author
**Praneshram S**

