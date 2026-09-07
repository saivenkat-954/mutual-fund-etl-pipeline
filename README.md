# Mutual Fund ETL Pipeline

An end-to-end Mutual Fund data ingestion and ETL pipeline built for Day 1 of the project.

## Project Objective

The objective is to build a reliable data-engineering foundation for mutual-fund analytics by:

- Ingesting 10 structured CSV datasets using Pandas
- Inspecting dataset shape, data types and sample records
- Performing basic data-quality checks
- Identifying data anomalies
- Fetching live NAV data from MFAPI
- Preserving raw API responses
- Transforming API JSON into analysis-ready CSV files
- Validating AMFI scheme-code relationships

## ETL Architecture

10 CSV Datasets
        ↓
Pandas Data Ingestion
        ↓
Shape / Dtypes / Head
        ↓
Data Quality Validation
        ↓
Quality Report


MFAPI
        ↓
JSON Response
        ↓
Raw JSON Storage
        ↓
Pandas Transformation
        ↓
Processed NAV CSV
        ↓
nav_history_live.csv

## Datasets

| Dataset | Rows | Columns | Purpose |
|---|---:|---:|---|
| fund_master.csv | 40 | 15 | Scheme master data |
| nav_history.csv | 46,000 | 3 | Historical NAV |
| aum_by_fund_house.csv | 90 | 5 | AUM by fund house |
| monthly_sip_inflows.csv | 48 | 6 | Monthly SIP activity |
| category_inflows.csv | 144 | 3 | Category inflows |
| industry_folio_count.csv | 21 | 6 | Folio trends |
| scheme_performance.csv | 40 | 19 | Scheme performance |
| investor_transactions.csv | 32,778 | 13 | Investor transactions |
| portfolio_holdings.csv | 322 | 8 | Portfolio holdings |
| benchmark_indices.csv | 8,050 | 3 | Benchmark history |

## Live NAV Integration

The task mentions five schemes but lists six AMFI codes. Therefore, all six listed schemes were fetched:

| AMFI Code | Scheme |
|---:|---|
| 125497 | HDFC Top 100 Direct |
| 119551 | SBI Bluechip |
| 120503 | ICICI Bluechip |
| 118632 | Nippon Large Cap |
| 119092 | Axis Bluechip |
| 120841 | Kotak Bluechip |

API endpoint:

`https://api.mfapi.in/mf/<AMFI_CODE>`

Raw responses are stored in:

`data/raw/mfapi/`

Processed NAV files are stored in:

`data/processed/nav/`

Combined output:

`data/processed/nav_history_live.csv`

## Data Quality Findings

- All 10 datasets were loaded successfully.
- No duplicate rows were found.
- No missing values were found in fund_master.
- No missing values were found in nav_history.
- No duplicate AMFI-code/date combinations were found in nav_history.
- AMFI codes are consistent across the linked datasets.
- monthly_sip_inflows contains 12 missing yoy_growth_pct values at the beginning of the time series.
- The 12 YoY values are expected analytical nulls because prior-year comparison data is unavailable.
- Portfolio weights are approximately 100%, with small rounding differences.

Detailed report:

`reports/DAY1_DATA_QUALITY_SUMMARY.md`

## Project Structure

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
│       ├── nav/
│       │   └── *_nav.csv
│       └── nav_history_live.csv
│
├── src/
│   ├── data_ingestion.py
│   └── live_nav_fetch.py
│
├── notebooks/
├── sql/
├── dashboard/
├── reports/
├── documentation/
├── ppt_slides/
├── demo_video/
│
├── requirements.txt
├── README.md
└── .gitignore