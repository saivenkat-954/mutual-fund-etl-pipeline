from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SQL_DIR = PROJECT_ROOT / "sql"
DATABASE_FILE = PROJECT_ROOT / "mutual_fund.db"
SCHEMA_FILE = SQL_DIR / "schema.sql"


def load_schema(engine):
    schema_sql = SCHEMA_FILE.read_text(encoding="utf-8")

    statements = [
        statement.strip()
        for statement in schema_sql.split(";")
        if statement.strip()
    ]

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def create_supporting_tables(engine):
    tables = {
        "fact_sip_inflows": """
            CREATE TABLE IF NOT EXISTS fact_sip_inflows (
                month TEXT PRIMARY KEY,
                sip_inflow_crore REAL NOT NULL,
                active_sip_accounts_crore REAL NOT NULL,
                new_sip_accounts_lakh REAL NOT NULL,
                sip_aum_lakh_crore REAL NOT NULL,
                yoy_growth_pct REAL
            )
        """,
        "fact_category_inflows": """
            CREATE TABLE IF NOT EXISTS fact_category_inflows (
                month TEXT NOT NULL,
                category TEXT NOT NULL,
                net_inflow_crore REAL NOT NULL,
                PRIMARY KEY (month, category)
            )
        """,
        "fact_industry_folios": """
            CREATE TABLE IF NOT EXISTS fact_industry_folios (
                month TEXT PRIMARY KEY,
                total_folios_crore REAL NOT NULL,
                equity_folios_crore REAL NOT NULL,
                debt_folios_crore REAL NOT NULL,
                hybrid_folios_crore REAL NOT NULL,
                others_folios_crore REAL NOT NULL
            )
        """,
        "fact_portfolio_holdings": """
            CREATE TABLE IF NOT EXISTS fact_portfolio_holdings (
                holding_id INTEGER PRIMARY KEY AUTOINCREMENT,
                amfi_code INTEGER NOT NULL,
                stock_symbol TEXT NOT NULL,
                stock_name TEXT NOT NULL,
                sector TEXT NOT NULL,
                weight_pct REAL NOT NULL,
                market_value_cr REAL NOT NULL,
                current_price_inr REAL NOT NULL,
                portfolio_date TEXT NOT NULL,
                FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
            )
        """,
        "fact_benchmark_indices": """
            CREATE TABLE IF NOT EXISTS fact_benchmark_indices (
                date TEXT NOT NULL,
                index_name TEXT NOT NULL,
                close_value REAL NOT NULL,
                PRIMARY KEY (date, index_name)
            )
        """,
    }

    with engine.begin() as connection:
        for statement in tables.values():
            connection.execute(text(statement))


def load_dim_fund(engine):
    file = PROCESSED_DIR / "fund_master_cleaned.csv"

    df = pd.read_csv(file)

    df.to_sql(
        "dim_fund",
        engine,
        if_exists="append",
        index=False,
    )

    print(f"dim_fund loaded: {len(df):,}")


def create_dim_date(engine):
    date_frames = []

    nav = pd.read_csv(
        PROCESSED_DIR / "nav_history_cleaned.csv",
        usecols=["date"],
    )

    transactions = pd.read_csv(
        PROCESSED_DIR / "investor_transactions_cleaned.csv",
        usecols=["transaction_date"],
    )

    aum = pd.read_csv(
        PROCESSED_DIR / "aum_by_fund_house_cleaned.csv",
        usecols=["date"],
    )

    benchmarks = pd.read_csv(
        PROCESSED_DIR / "benchmark_indices_cleaned.csv",
        usecols=["date"],
    )

    portfolios = pd.read_csv(
        PROCESSED_DIR / "portfolio_holdings_cleaned.csv",
        usecols=["portfolio_date"],
    )

    date_frames.append(
        pd.to_datetime(nav["date"], errors="coerce")
    )

    date_frames.append(
        pd.to_datetime(
            transactions["transaction_date"],
            errors="coerce",
        )
    )

    date_frames.append(
        pd.to_datetime(aum["date"], errors="coerce")
    )

    date_frames.append(
        pd.to_datetime(benchmarks["date"], errors="coerce")
    )

    date_frames.append(
        pd.to_datetime(
            portfolios["portfolio_date"],
            errors="coerce",
        )
    )

    all_dates = pd.concat(
        date_frames,
        ignore_index=True,
    ).dropna().drop_duplicates()

    all_dates = all_dates.sort_values().reset_index(drop=True)

    dim_date = pd.DataFrame(
        {
            "full_date": all_dates.dt.strftime("%Y-%m-%d"),
            "year": all_dates.dt.year,
            "quarter": all_dates.dt.quarter,
            "month": all_dates.dt.month,
            "month_name": all_dates.dt.month_name(),
            "day": all_dates.dt.day,
            "day_of_week": all_dates.dt.dayofweek,
        }
    )

    dim_date.insert(
        0,
        "date_key",
        range(1, len(dim_date) + 1),
    )

    dim_date.to_sql(
        "dim_date",
        engine,
        if_exists="append",
        index=False,
    )

    print(f"dim_date loaded: {len(dim_date):,}")

    return dim_date


def get_date_key_map(engine):
    query = """
        SELECT date_key, full_date
        FROM dim_date
    """

    date_map = pd.read_sql(
        query,
        engine,
    )

    return dict(
        zip(
            date_map["full_date"],
            date_map["date_key"],
        )
    )


def load_fact_nav(engine, date_map):
    file = PROCESSED_DIR / "nav_history_cleaned.csv"

    df = pd.read_csv(file)

    df["date_key"] = df["date"].map(date_map)

    if df["date_key"].isna().any():
        raise ValueError(
            "Missing date_key values in fact_nav."
        )

    df = df[
        [
            "amfi_code",
            "date_key",
            "nav",
        ]
    ]

    df.to_sql(
        "fact_nav",
        engine,
        if_exists="append",
        index=False,
    )

    print(f"fact_nav loaded: {len(df):,}")


def load_fact_transactions(engine, date_map):
    file = (
        PROCESSED_DIR
        / "investor_transactions_cleaned.csv"
    )

    df = pd.read_csv(file)

    df["date_key"] = df["transaction_date"].map(
        date_map
    )

    if df["date_key"].isna().any():
        raise ValueError(
            "Missing date_key values in fact_transactions."
        )

    df = df[
        [
            "investor_id",
            "transaction_date",
            "date_key",
            "amfi_code",
            "transaction_type",
            "amount_inr",
            "state",
            "city",
            "city_tier",
            "age_group",
            "gender",
            "annual_income_lakh",
            "payment_mode",
            "kyc_status",
        ]
    ]

    df.to_sql(
        "fact_transactions",
        engine,
        if_exists="append",
        index=False,
    )

    print(
        f"fact_transactions loaded: {len(df):,}"
    )


def load_fact_performance(engine):
    file = (
        PROCESSED_DIR
        / "scheme_performance_cleaned.csv"
    )

    df = pd.read_csv(file)

    df.to_sql(
        "fact_performance",
        engine,
        if_exists="append",
        index=False,
    )

    print(
        f"fact_performance loaded: {len(df):,}"
    )


def load_fact_aum(engine, date_map):
    file = (
        PROCESSED_DIR
        / "aum_by_fund_house_cleaned.csv"
    )

    df = pd.read_csv(file)

    df["date_key"] = df["date"].map(
        date_map
    )

    if df["date_key"].isna().any():
        raise ValueError(
            "Missing date_key values in fact_aum."
        )

    df = df[
        [
            "date_key",
            "date",
            "fund_house",
            "aum_lakh_crore",
            "aum_crore",
            "num_schemes",
        ]
    ]

    df.to_sql(
        "fact_aum",
        engine,
        if_exists="append",
        index=False,
    )

    print(f"fact_aum loaded: {len(df):,}")


def load_fact_sip_inflows(engine):
    file = (
        PROCESSED_DIR
        / "monthly_sip_inflows_cleaned.csv"
    )

    df = pd.read_csv(file)

    df.to_sql(
        "fact_sip_inflows",
        engine,
        if_exists="append",
        index=False,
    )

    print(
        f"fact_sip_inflows loaded: {len(df):,}"
    )


def load_fact_category_inflows(engine):
    file = (
        PROCESSED_DIR
        / "category_inflows_cleaned.csv"
    )

    df = pd.read_csv(file)

    df.to_sql(
        "fact_category_inflows",
        engine,
        if_exists="append",
        index=False,
    )

    print(
        f"fact_category_inflows loaded: {len(df):,}"
    )


def load_fact_industry_folios(engine):
    file = (
        PROCESSED_DIR
        / "industry_folio_count_cleaned.csv"
    )

    df = pd.read_csv(file)

    df.to_sql(
        "fact_industry_folios",
        engine,
        if_exists="append",
        index=False,
    )

    print(
        f"fact_industry_folios loaded: {len(df):,}"
    )


def load_fact_portfolio_holdings(engine):
    file = (
        PROCESSED_DIR
        / "portfolio_holdings_cleaned.csv"
    )

    df = pd.read_csv(file)

    df.to_sql(
        "fact_portfolio_holdings",
        engine,
        if_exists="append",
        index=False,
    )

    print(
        f"fact_portfolio_holdings loaded: {len(df):,}"
    )


def load_fact_benchmark_indices(engine):
    file = (
        PROCESSED_DIR
        / "benchmark_indices_cleaned.csv"
    )

    df = pd.read_csv(file)

    df.to_sql(
        "fact_benchmark_indices",
        engine,
        if_exists="append",
        index=False,
    )

    print(
        f"fact_benchmark_indices loaded: {len(df):,}"
    )


def verify_row_counts(engine):
    expected = {
        "dim_fund": 40,
        "dim_date": None,
        "fact_nav": 46000,
        "fact_transactions": 32778,
        "fact_performance": 40,
        "fact_aum": 90,
        "fact_sip_inflows": 48,
        "fact_category_inflows": 144,
        "fact_industry_folios": 21,
        "fact_portfolio_holdings": 322,
        "fact_benchmark_indices": 8050,
    }

    print("\n===== DATABASE ROW COUNT VERIFICATION =====")

    with engine.connect() as connection:

        for table, expected_count in expected.items():

            result = connection.execute(
                text(
                    f"SELECT COUNT(*) FROM {table}"
                )
            )

            actual_count = result.scalar()

            if (
                expected_count is not None
                and actual_count != expected_count
            ):
                raise ValueError(
                    f"{table}: expected "
                    f"{expected_count:,}, got "
                    f"{actual_count:,}"
                )

            print(
                f"{table:30} {actual_count:,}"
            )

    print("Row count verification: PASS")


def verify_foreign_keys(engine):
    print("\n===== FOREIGN KEY VERIFICATION =====")

    with engine.connect() as connection:

        result = connection.execute(
            text("PRAGMA foreign_key_check")
        )

        violations = result.fetchall()

    if violations:
        print("Foreign key violations:")
        for violation in violations:
            print(violation)

        raise ValueError(
            "Foreign key validation failed."
        )

    print("Foreign key validation: PASS")


def main():

    print("=" * 60)
    print("DAY 2 — SQLITE DATABASE LOADING")
    print("=" * 60)

    engine = create_engine(
        f"sqlite:///{DATABASE_FILE}"
    )

    load_schema(engine)

    create_supporting_tables(engine)

    load_dim_fund(engine)

    create_dim_date(engine)

    date_map = get_date_key_map(engine)

    load_fact_nav(
        engine,
        date_map,
    )

    load_fact_transactions(
        engine,
        date_map,
    )

    load_fact_performance(engine)

    load_fact_aum(
        engine,
        date_map,
    )

    load_fact_sip_inflows(engine)

    load_fact_category_inflows(engine)

    load_fact_industry_folios(engine)

    load_fact_portfolio_holdings(engine)

    load_fact_benchmark_indices(engine)

    verify_row_counts(engine)

    verify_foreign_keys(engine)

    print("\n" + "=" * 60)
    print("DATABASE LOADING COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print(f"Database: {DATABASE_FILE}")


if __name__ == "__main__":
    main()