# Mutual Fund ETL Pipeline

An end-to-end **Mutual Fund data ingestion and ETL pipeline** built using Python and Pandas. The project ingests multiple mutual-fund datasets, performs data-quality validation, integrates live NAV data through MFAPI, and prepares structured data for downstream analytics.

---

## 📌 Project Overview

This project establishes the data-engineering foundation for a mutual-fund analytics platform.

The pipeline handles:

- CSV data ingestion
- Dataset profiling
- Data-quality validation
- AMFI scheme-code validation
- Live NAV API integration
- Raw API data preservation
- JSON-to-CSV transformation
- Processed data generation

---

## 🏗️ ETL Architecture

```text
┌─────────────────────────┐
│   10 CSV Data Sources   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│    Pandas Ingestion     │
│ Shape / Dtypes / Head   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   Data Quality Checks   │
│ Missing / Duplicates /  │
│ Referential Integrity   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│    Quality Report       │
└─────────────────────────┘


          MFAPI
            │
            ▼
      JSON Response
            │
            ▼
       Raw JSON Layer
            │
            ▼
    Pandas Transformation
            │
            ▼
     Processed NAV CSV
            │
            ▼
   nav_history_live.csv
```

---

## 📊 Datasets

The project uses 10 supplied datasets:

| Dataset | Rows | Columns | Description |
|---|---:|---:|---|
| `fund_master.csv` | 40 | 15 | Mutual-fund scheme master data |
| `nav_history.csv` | 46,000 | 3 | Historical NAV records |
| `aum_by_fund_house.csv` | 90 | 5 | AUM by fund house |
| `monthly_sip_inflows.csv` | 48 | 6 | Monthly SIP activity |
| `category_inflows.csv` | 144 | 3 | Category-level inflows |
| `industry_folio_count.csv` | 21 | 6 | Industry folio trends |
| `scheme_performance.csv` | 40 | 19 | Scheme performance metrics |
| `investor_transactions.csv` | 32,778 | 13 | Investor transaction data |
| `portfolio_holdings.csv` | 322 | 8 | Portfolio holdings |
| `benchmark_indices.csv` | 8,050 | 3 | Benchmark index history |

---

## 🏦 Fund Master

The `fund_master.csv` dataset contains **40 schemes** and **15 attributes**, including:

- AMFI scheme code
- Fund house
- Scheme name
- Category
- Sub-category
- Plan
- Launch date
- Benchmark
- Expense ratio
- Exit load
- Minimum SIP amount
- Minimum lumpsum amount
- Fund manager
- Risk category
- SEBI category code

---

## 📈 Live NAV Integration

MFAPI is used to retrieve live NAV information.

The task description mentions five schemes but lists six AMFI scheme codes. Therefore, all six listed schemes are handled by the pipeline.

| AMFI Code | Scheme |
|---:|---|
| `125497` | HDFC Top 100 Direct |
| `119551` | SBI Bluechip |
| `120503` | ICICI Bluechip |
| `118632` | Nippon Large Cap |
| `119092` | Axis Bluechip |
| `120841` | Kotak Bluechip |

### API Endpoint

```text
https://api.mfapi.in/mf/<AMFI_CODE>
```

### Data Flow

```text
MFAPI
  ↓
JSON Response
  ↓
Raw JSON
  ↓
Pandas DataFrame
  ↓
NAV CSV
  ↓
Combined NAV History
```

Raw API responses are stored in:

```text
data/raw/mfapi/
```

Processed NAV files are stored in:

```text
data/processed/nav/
```

Combined output:

```text
data/processed/nav_history_live.csv
```

---

## 🔍 Data Quality Checks

The ingestion pipeline performs:

- Dataset shape validation
- Data-type inspection
- Sample-record inspection
- Missing-value analysis
- Duplicate-row detection
- Basic numerical validation
- Date validation
- AMFI scheme-code validation
- NAV validation
- Portfolio-weight consistency checks

### Results

- ✅ All 10 datasets loaded successfully
- ✅ No duplicate rows detected
- ✅ No missing values in `fund_master`
- ✅ No missing values in `nav_history`
- ✅ No duplicate `amfi_code + date` combinations in `nav_history`
- ✅ AMFI codes are consistent across linked datasets
- ✅ NAV values are valid
- ✅ Transaction amounts are valid

### Data Quality Observation

`monthly_sip_inflows.csv` contains **12 missing `yoy_growth_pct` values** at the beginning of the dataset.

These are treated as expected analytical nulls because YoY growth requires a corresponding value from the previous year.

Detailed results are available in:

```text
reports/data_quality_summary.csv
```

---

## 📁 Project Structure

```text
mutual-fund-etl-pipeline/
│
├── data/
│   ├── raw/
│   │   ├── *.csv
│   │   └── mfapi/
│   │       └── *.json
│   │
│   └── processed/
│       └── nav/
│           └── *_nav.csv
│
├── notebooks/
│
├── sql/
│
├── dashboard/
│
├── reports/
│   ├── data_quality_summary.csv
│   └── data_quality_runtime.csv
│
├── src/
│   ├── data_ingestion.py
│   └── live_nav_fetch.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | ETL development |
| Pandas | Data ingestion & transformation |
| NumPy | Numerical processing |
| Requests | API integration |
| SciPy | Data analysis |
| SQLAlchemy | Database integration |
| Matplotlib | Visualization |
| Seaborn | Statistical visualization |
| Plotly | Interactive visualization |
| Jupyter | Exploratory analysis |

---

## ⚙️ Installation

### Clone the repository

```bash
git clone https://github.com/saivenkat-954/mutual-fund-etl-pipeline.git
cd mutual-fund-etl-pipeline
```

### Create virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

---

## ▶️ Run the Pipeline

### 1. Run CSV ingestion

```bash
python src/data_ingestion.py
```

This loads all CSV datasets and performs the initial data-quality checks.

### 2. Fetch live NAV data

```bash
python src/live_nav_fetch.py
```

This retrieves NAV data from MFAPI and creates the raw and processed outputs.

---

## 📦 Outputs

### Raw API responses

```text
data/raw/mfapi/
├── 118632.json
├── 119092.json
├── 119551.json
├── 120503.json
├── 120841.json
└── 125497.json
```

### Processed NAV files

```text
data/processed/nav/
├── 118632_nav.csv
├── 119092_nav.csv
├── 119551_nav.csv
├── 120503_nav.csv
├── 120841_nav.csv
└── 125497_nav.csv
```

### Combined NAV history

```text
data/processed/nav_history_live.csv
```

---

## 🚀 Future Scope

The pipeline can be extended with:

- SQL-based data warehouse
- Incremental ETL
- Scheduled data ingestion
- Automated data-quality tests
- Interactive mutual-fund dashboard
- Benchmark comparison
- Risk analytics
- Investor behaviour analytics
- Portfolio analytics
- Performance monitoring

---

## 👨‍💻 Author

**Poorna Chandra Sai Venkat Bommidi**

GitHub:  
https://github.com/saivenkat-954

---

## 📄 Project Status

**Day 1 — Data Ingestion & ETL: Completed ✅**
