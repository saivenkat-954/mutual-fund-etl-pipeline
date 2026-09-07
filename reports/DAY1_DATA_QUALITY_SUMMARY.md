# Day 1 — Data Ingestion & Data Quality Summary

## 1. Dataset ingestion

All **10 supplied CSV datasets** were loaded successfully using Pandas.

| Dataset | Rows | Columns | Missing cells | Duplicate rows | Date range |
|---|---:|---:|---:|---:|---|
| `fund_master` | 40 | 15 | 0 | 0 | N/A → N/A |
| `nav_history` | 46,000 | 3 | 0 | 0 | 2022-01-03 → 2026-05-29 |
| `aum_by_fund_house` | 90 | 5 | 0 | 0 | 2022-03-31 → 2025-12-31 |
| `monthly_sip_inflows` | 48 | 6 | 12 | 0 | 2022-01-01 → 2025-12-01 |
| `category_inflows` | 144 | 3 | 0 | 0 | 2024-04-01 → 2025-03-01 |
| `industry_folio_count` | 21 | 6 | 0 | 0 | 2022-01-01 → 2025-12-01 |
| `scheme_performance` | 40 | 19 | 0 | 0 | N/A → N/A |
| `investor_transactions` | 32,778 | 13 | 0 | 0 | 2024-01-01 → 2025-05-30 |
| `portfolio_holdings` | 322 | 8 | 0 | 0 | 2025-12-31 → 2025-12-31 |
| `benchmark_indices` | 8,050 | 3 | 0 | 0 | 2022-01-03 → 2026-05-29 |


## 2. Schema observations

### fund_master
- 40 schemes
- 15 columns
- Key fields: `amfi_code`, `fund_house`, `scheme_name`, `category`, `sub_category`, `plan`, `risk_category`
- No missing cells or duplicate rows.

### nav_history
- 46,000 records
- 40 AMFI scheme codes
- No missing cells, duplicate rows, duplicate `amfi_code + date` pairs, or non-positive NAV values.

### Other datasets
- AUM by fund house: 90 rows
- Monthly SIP inflows: 48 rows
- Category inflows: 144 rows
- Industry folio count: 21 rows
- Scheme performance: 40 rows
- Investor transactions: 32,778 rows
- Portfolio holdings: 322 rows
- Benchmark indices: 8,050 rows

## 3. Missing-value anomaly

`monthly_sip_inflows.yoy_growth_pct` contains **12 missing values**.

These correspond to the first 12 monthly records, where a year-over-year comparison is not available in the supplied time window. This is treated as an expected analytical null rather than a broken source record.

## 4. Referential integrity

| Validation | Result |
|---|---|
| Every `fund_master.amfi_code` exists in `nav_history` | **PASS** |
| Every performance AMFI code exists in `fund_master` | **PASS** |
| Every transaction AMFI code exists in `fund_master` | **PASS** |
| Every portfolio-holding AMFI code exists in `fund_master` | **PASS** |

No orphan AMFI codes were found.

## 5. Fund-master exploration

### Unique fund houses
Aditya Birla Sun Life MF, Axis Mutual Fund, DSP Mutual Fund, HDFC Mutual Fund, ICICI Prudential MF, Kotak Mahindra MF, Mirae Asset MF, Nippon India MF, SBI Mutual Fund, UTI Mutual Fund

### Categories
Debt, Equity

### Sub-categories
ELSS, Flexi Cap, Gilt, Index, Index/ETF, Large & Mid Cap, Large Cap, Liquid, Mid Cap, Short Duration, Small Cap, Value

### Risk categories
High, Low, Moderate, Moderately High, Very High

## 6. Assigned MFAPI schemes

The task text says five key schemes but lists six scheme codes. To avoid omitting an assigned scheme, the implementation covers all six:

| AMFI code | Scheme | Fund house | Plan |
|---:|---|---|---|
| 118632 | Nippon India Large Cap Fund - Regular - Growth | Nippon India MF | Regular |
| 119092 | Axis Bluechip Fund - Regular - Growth | Axis Mutual Fund | Regular |
| 119551 | SBI Bluechip Fund - Regular Plan - Growth | SBI Mutual Fund | Regular |
| 120503 | ICICI Pru Bluechip Fund - Regular - Growth | ICICI Prudential MF | Regular |
| 120841 | Kotak Bluechip Fund - Regular - Growth | Kotak Mahindra MF | Regular |
| 125497 | HDFC Top 100 Fund - Direct Plan - Growth | HDFC Mutual Fund | Direct |


## 7. Additional quality checks

- NAV duplicate `amfi_code + date` records: **0**
- NAV values <= 0: **0**
- Fund-master expense ratio outside 0–5%: **0**
- Fund-master exit load outside 0–5%: **0**
- Non-positive transaction amounts: **0**
- Negative portfolio weights: **0**
- Portfolio weight totals outside 99.95%–100.05%: **0**
- AUM unit consistency maximum absolute difference: **0.000000000116 crore**
- Benchmark close values <= 0: **0**

Portfolio weights are effectively 100% per scheme/date, with tiny ±0.02 percentage-point differences caused by rounding.

## 8. Conclusion

**Day 1 data ingestion is complete.** The supplied datasets load cleanly, AMFI code relationships are consistent, and the observed missing YoY values have a clear time-series explanation.

The next ETL step is to fetch the live MFAPI NAV data for the six listed schemes, save the raw JSON responses, flatten them to CSV, and compare the live scheme universe with the supplied `fund_master`/`nav_history`.
