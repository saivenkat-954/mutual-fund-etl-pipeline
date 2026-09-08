# Mutual Fund ETL Pipeline — Data Dictionary

## 1. Project Overview

This data dictionary documents the datasets used in the Mutual Fund ETL Pipeline, including source CSV files, cleaned datasets, and the SQLite analytical database.

The project processes mutual fund information including fund metadata, NAV history, investor transactions, fund performance, AUM, SIP inflows, portfolio holdings, industry folios, category inflows, and benchmark indices.

---

# 2. Source and Processed Datasets

## 2.1 fund_master.csv

### Description

Master reference dataset containing mutual fund scheme-level information.

| Column | Data Type | Definition | Unit / Format |
|---|---|---|---|
| amfi_code | INTEGER | Unique AMFI identifier for the mutual fund scheme | Code |
| fund_house | TEXT | Name of the asset management company | Text |
| scheme_name | TEXT | Full name of the mutual fund scheme | Text |
| category | TEXT | Broad investment category | Text |
| sub_category | TEXT | Detailed fund sub-category | Text |
| plan | TEXT | Investment plan type | Regular / Direct |
| launch_date | DATE | Scheme launch date | YYYY-MM-DD |
| benchmark | TEXT | Benchmark index associated with the scheme | Text |
| expense_ratio_pct | REAL | Annual expense ratio charged by the scheme | Percentage |
| exit_load_pct | REAL | Exit load applicable to the scheme | Percentage |
| min_sip_amount | REAL | Minimum investment amount required for SIP | INR |
| min_lumpsum_amount | REAL | Minimum lump-sum investment amount | INR |
| fund_manager | TEXT | Fund manager responsible for the scheme | Text |
| risk_category | TEXT | Risk classification of the scheme | Text |
| sebi_category_code | TEXT | SEBI category classification code | Code |

### Source

`data/raw/fund_master.csv`

### Processed

`data/processed/fund_master_cleaned.csv`

### Row Count

40

---

# 2.2 nav_history.csv

### Description

Historical Net Asset Value data for mutual fund schemes.

| Column | Data Type | Definition | Unit / Format |
|---|---|---|---|
| amfi_code | INTEGER | AMFI scheme identifier | Code |
| date | DATE | Date on which NAV was recorded | YYYY-MM-DD |
| nav | REAL | Net Asset Value of the scheme | INR |

### Primary Key

`amfi_code + date`

### Source

`data/raw/nav_history.csv`

### Processed

`data/processed/nav_history_cleaned.csv`

### Row Count

46,000

---

# 2.3 aum_by_fund_house.csv

### Description

Assets Under Management information aggregated at fund-house level.

| Column | Data Type | Definition | Unit / Format |
|---|---|---|---|
| date | DATE | Reporting date | YYYY-MM-DD |
| fund_house | TEXT | Name of the mutual fund house | Text |
| aum_lakh_crore | REAL | Assets under management represented in lakh crore | Lakh crore |
| aum_crore | REAL | Assets under management | Crore INR |
| num_schemes | INTEGER | Number of schemes managed by the fund house | Count |

### Primary Key

`date + fund_house`

### Source

`data/raw/aum_by_fund_house.csv`

### Processed

`data/processed/aum_by_fund_house_cleaned.csv`

### Row Count

90

---

# 2.4 monthly_sip_inflows.csv

### Description

Monthly Systematic Investment Plan activity and inflow information.

| Column | Data Type | Definition | Unit / Format |
|---|---|---|---|
| month | TEXT | Reporting month | YYYY-MM |
| sip_inflow_crore | REAL | Monthly SIP inflow | Crore INR |
| active_sip_accounts_crore | REAL | Number of active SIP accounts | Crore accounts |
| new_sip_accounts_lakh | REAL | Newly registered SIP accounts | Lakh accounts |
| sip_aum_lakh_crore | REAL | SIP-related AUM | Lakh crore |
| yoy_growth_pct | REAL | Year-over-year SIP inflow growth | Percentage |

### Source

`data/raw/monthly_sip_inflows.csv`

### Processed

`data/processed/monthly_sip_inflows_cleaned.csv`

### Row Count

48

### Data Quality Note

The first 12 months contain missing YoY growth values because a previous-year comparison is unavailable.

---

# 2.5 category_inflows.csv

### Description

Monthly net mutual fund inflows grouped by investment category.

| Column | Data Type | Definition | Unit / Format |
|---|---|---|---|
| month | TEXT | Reporting month | YYYY-MM |
| category | TEXT | Mutual fund investment category | Text |
| net_inflow_crore | REAL | Net inflow into the category | Crore INR |

### Primary Key

`month + category`

### Source

`data/raw/category_inflows.csv`

### Processed

`data/processed/category_inflows_cleaned.csv`

### Row Count

144

---

# 2.6 industry_folio_count.csv

### Description

Monthly investor folio counts grouped by asset category.

| Column | Data Type | Definition | Unit / Format |
|---|---|---|---|
| month | TEXT | Reporting month | YYYY-MM |
| total_folios_crore | REAL | Total mutual fund folios | Crore |
| equity_folios_crore | REAL | Equity folios | Crore |
| debt_folios_crore | REAL | Debt folios | Crore |
| hybrid_folios_crore | REAL | Hybrid fund folios | Crore |
| others_folios_crore | REAL | Other category folios | Crore |

### Primary Key

`month`

### Source

`data/raw/industry_folio_count.csv`

### Processed

`data/processed/industry_folio_count_cleaned.csv`

### Row Count

21

---

# 2.7 investor_transactions.csv

### Description

Investor-level mutual fund transaction records.

| Column | Data Type | Definition | Unit / Format |
|---|---|---|---|
| investor_id | TEXT | Unique investor identifier | ID |
| transaction_date | DATE | Date of transaction | YYYY-MM-DD |
| amfi_code | INTEGER | AMFI scheme identifier | Code |
| transaction_type | TEXT | Type of transaction | SIP / Lumpsum / Redemption |
| amount_inr | REAL | Transaction amount | INR |
| state | TEXT | Investor state | Text |
| city | TEXT | Investor city | Text |
| city_tier | TEXT | Classification of city | Tier |
| age_group | TEXT | Investor age group | Category |
| gender | TEXT | Investor gender | Category |
| annual_income_lakh | REAL | Investor annual income | Lakh INR |
| payment_mode | TEXT | Method used for payment | UPI / Cheque / Net Banking / Mandate |
| kyc_status | TEXT | Investor KYC status | Verified / Pending |

### Foreign Key

`amfi_code → dim_fund.amfi_code`

### Source

`data/raw/investor_transactions.csv`

### Processed

`data/processed/investor_transactions_cleaned.csv`

### Row Count

32,778

---

# 2.8 portfolio_holdings.csv

### Description

Individual securities held within mutual fund portfolios.

| Column | Data Type | Definition | Unit / Format |
|---|---|---|---|
| amfi_code | INTEGER | AMFI scheme identifier | Code |
| stock_symbol | TEXT | Stock exchange symbol | Text |
| stock_name | TEXT | Name of the holding | Text |
| sector | TEXT | Industry sector of the holding | Text |
| weight_pct | REAL | Portfolio allocation percentage | Percentage |
| market_value_cr | REAL | Market value of holding | Crore INR |
| current_price_inr | REAL | Current security price | INR |
| portfolio_date | DATE | Portfolio reporting date | YYYY-MM-DD |

### Foreign Key

`amfi_code → dim_fund.amfi_code`

### Source

`data/raw/portfolio_holdings.csv`

### Processed

`data/processed/portfolio_holdings_cleaned.csv`

### Row Count

322

---

# 2.9 scheme_performance.csv

### Description

Performance, risk, and evaluation metrics for mutual fund schemes.

| Column | Data Type | Definition | Unit / Format |
|---|---|---|---|
| amfi_code | INTEGER | AMFI scheme identifier | Code |
| scheme_name | TEXT | Mutual fund scheme name | Text |
| fund_house | TEXT | Asset management company | Text |
| category | TEXT | Fund category | Text |
| plan | TEXT | Investment plan | Regular / Direct |
| return_1yr_pct | REAL | One-year return | Percentage |
| return_3yr_pct | REAL | Three-year return | Percentage |
| return_5yr_pct | REAL | Five-year return | Percentage |
| benchmark_3yr_pct | REAL | Three-year benchmark return | Percentage |
| alpha | REAL | Excess risk-adjusted return measure | Metric |
| beta | REAL | Sensitivity to market movements | Metric |
| sharpe_ratio | REAL | Risk-adjusted return measure | Ratio |
| sortino_ratio | REAL | Downside-risk-adjusted return measure | Ratio |
| std_dev_ann_pct | REAL | Annualized return volatility | Percentage |
| max_drawdown_pct | REAL | Maximum observed portfolio decline | Percentage |
| aum_crore | REAL | Assets under management | Crore INR |
| expense_ratio_pct | REAL | Annual expense ratio | Percentage |
| morningstar_rating | REAL | Morningstar rating | Rating |
| risk_grade | TEXT | Risk classification | Text |

### Foreign Key

`amfi_code → dim_fund.amfi_code`

### Source

`data/raw/scheme_performance.csv`

### Processed

`data/processed/scheme_performance_cleaned.csv`

### Row Count

40

---

# 2.10 benchmark_indices.csv

### Description

Historical benchmark index values.

| Column | Data Type | Definition | Unit / Format |
|---|---|---|---|
| date | DATE | Index observation date | YYYY-MM-DD |
| index_name | TEXT | Name of benchmark index | Text |
| close_value | REAL | Closing index value | Index points |

### Primary Key

`date + index_name`

### Source

`data/raw/benchmark_indices.csv`

### Processed

`data/processed/benchmark_indices_cleaned.csv`

### Row Count

8,050

---

# 3. SQLite Database Dictionary

Database:

`mutual_fund.db`

---

## 3.1 dim_fund

### Description

Central fund dimension containing master information about mutual fund schemes.

### Primary Key

`amfi_code`

### Source

`fund_master_cleaned.csv`

---

## 3.2 dim_date

### Description

Date dimension used for consistent time-based analysis across fact tables.

| Column | Data Type | Definition |
|---|---|---|
| date_key | INTEGER | Surrogate date identifier |
| full_date | TEXT | Full calendar date |
| year | INTEGER | Calendar year |
| quarter | INTEGER | Calendar quarter |
| month | INTEGER | Month number |
| month_name | TEXT | Month name |
| day | INTEGER | Day of month |
| day_of_week | INTEGER | Day-of-week number |

### Primary Key

`date_key`

### Row Count

1,297

---

## 3.3 fact_nav

### Description

Historical NAV observations for mutual fund schemes.

| Column | Data Type | Definition |
|---|---|---|
| amfi_code | INTEGER | Fund identifier |
| date_key | INTEGER | Date dimension identifier |
| nav | REAL | Net Asset Value |

### Primary Key

`amfi_code + date_key`

### Foreign Keys

- `amfi_code → dim_fund.amfi_code`
- `date_key → dim_date.date_key`

### Row Count

46,000

---

## 3.4 fact_transactions

### Description

Investor mutual fund transaction fact table.

| Column | Data Type | Definition |
|---|---|---|
| transaction_id | INTEGER | Database-generated transaction identifier |
| investor_id | TEXT | Investor identifier |
| transaction_date | TEXT | Transaction date |
| date_key | INTEGER | Date dimension identifier |
| amfi_code | INTEGER | Fund identifier |
| transaction_type | TEXT | Transaction type |
| amount_inr | REAL | Transaction amount |
| state | TEXT | Investor state |
| city | TEXT | Investor city |
| city_tier | TEXT | City classification |
| age_group | TEXT | Investor age group |
| gender | TEXT | Investor gender |
| annual_income_lakh | REAL | Annual investor income |
| payment_mode | TEXT | Payment method |
| kyc_status | TEXT | KYC status |

### Primary Key

`transaction_id`

### Foreign Keys

- `amfi_code → dim_fund.amfi_code`
- `date_key → dim_date.date_key`

### Row Count

32,778

---

## 3.5 fact_performance

### Description

Fund-level performance and risk metrics.

### Primary Key

`amfi_code`

### Foreign Key

`amfi_code → dim_fund.amfi_code`

### Row Count

40

---

## 3.6 fact_aum

### Description

Fund-house-level Assets Under Management information.

| Column | Data Type | Definition |
|---|---|---|
| date_key | INTEGER | Date dimension identifier |
| date | TEXT | Reporting date |
| fund_house | TEXT | Fund house |
| aum_lakh_crore | REAL | AUM in lakh crore |
| aum_crore | REAL | AUM in crore INR |
| num_schemes | INTEGER | Number of schemes |

### Primary Key

`date_key + fund_house`

### Foreign Key

`date_key → dim_date.date_key`

### Row Count

90

---

## 3.7 fact_sip_inflows

### Description

Monthly SIP inflow and account activity.

### Primary Key

`month`

### Row Count

48

---

## 3.8 fact_category_inflows

### Description

Monthly net inflows by mutual fund category.

### Primary Key

`month + category`

### Row Count

144

---

## 3.9 fact_industry_folios

### Description

Monthly mutual fund folio distribution across investment categories.

### Primary Key

`month`

### Row Count

21

---

## 3.10 fact_portfolio_holdings

### Description

Fund portfolio security-level holdings.

### Primary Key

`holding_id`

### Foreign Key

`amfi_code → dim_fund.amfi_code`

### Row Count

322

---

## 3.11 fact_benchmark_indices

### Description

Historical benchmark index observations.

### Primary Key

`date + index_name`

### Row Count

8,050

---

# 4. Database Relationships

The main database relationships are:

```text
                    dim_date
                   /   |    \
                  /    |     \
                 /     |      \
                ↓      ↓       ↓
          fact_nav  fact_transactions  fact_aum
              ↑          ↑
              |          |
              └── dim_fund
                    ↑
                    |
             fact_performance