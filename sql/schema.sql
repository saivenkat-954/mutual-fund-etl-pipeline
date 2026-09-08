PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS fact_nav;
DROP TABLE IF EXISTS fact_transactions;
DROP TABLE IF EXISTS fact_performance;
DROP TABLE IF EXISTS fact_aum;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_fund;

CREATE TABLE dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    fund_house TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    category TEXT,
    sub_category TEXT,
    plan TEXT,
    launch_date TEXT,
    benchmark TEXT,
    expense_ratio_pct REAL,
    exit_load_pct REAL,
    min_sip_amount REAL,
    min_lumpsum_amount REAL,
    fund_manager TEXT,
    risk_category TEXT,
    sebi_category_code TEXT
);

CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date TEXT NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL
);

CREATE TABLE fact_nav (
    amfi_code INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    nav REAL NOT NULL,
    PRIMARY KEY (amfi_code, date_key),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

CREATE TABLE fact_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id TEXT NOT NULL,
    transaction_date TEXT NOT NULL,
    date_key INTEGER NOT NULL,
    amfi_code INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,
    amount_inr REAL NOT NULL,
    state TEXT,
    city TEXT,
    city_tier TEXT,
    age_group TEXT,
    gender TEXT,
    annual_income_lakh REAL,
    payment_mode TEXT,
    kyc_status TEXT,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_performance (
    amfi_code INTEGER PRIMARY KEY,
    scheme_name TEXT NOT NULL,
    fund_house TEXT NOT NULL,
    category TEXT,
    plan TEXT,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    aum_crore REAL,
    expense_ratio_pct REAL,
    morningstar_rating REAL,
    risk_grade TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_aum (
    date_key INTEGER NOT NULL,
    date TEXT NOT NULL,
    fund_house TEXT NOT NULL,
    aum_lakh_crore REAL NOT NULL,
    aum_crore REAL NOT NULL,
    num_schemes INTEGER NOT NULL,
    PRIMARY KEY (date_key, fund_house),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

CREATE INDEX idx_fact_nav_date
ON fact_nav(date_key);

CREATE INDEX idx_fact_nav_fund
ON fact_nav(amfi_code);

CREATE INDEX idx_fact_transactions_date
ON fact_transactions(date_key);

CREATE INDEX idx_fact_transactions_fund
ON fact_transactions(amfi_code);

CREATE INDEX idx_fact_transactions_state
ON fact_transactions(state);

CREATE INDEX idx_fact_performance_category
ON fact_performance(category);

CREATE INDEX idx_fact_aum_date
ON fact_aum(date_key);

CREATE INDEX idx_fact_aum_fund_house
ON fact_aum(fund_house);