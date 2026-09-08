from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


DATASETS = {
    "fund_master.csv": "fund_master_cleaned.csv",
    "aum_by_fund_house.csv": "aum_by_fund_house_cleaned.csv",
    "monthly_sip_inflows.csv": "monthly_sip_inflows_cleaned.csv",
    "category_inflows.csv": "category_inflows_cleaned.csv",
    "industry_folio_count.csv": "industry_folio_count_cleaned.csv",
    "portfolio_holdings.csv": "portfolio_holdings_cleaned.csv",
    "benchmark_indices.csv": "benchmark_indices_cleaned.csv",
}


def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    for column in df.select_dtypes(
        include=["object", "string"]
    ).columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

    return df


def clean_month_column(
    df: pd.DataFrame,
    column: str,
) -> pd.DataFrame:

    parsed = pd.to_datetime(
        df[column].astype("string"),
        format="%Y-%m",
        errors="coerce",
    )

    invalid = parsed.isna().sum()

    if invalid > 0:
        raise ValueError(
            f"{invalid} invalid month values found in '{column}'."
        )

    df[column] = parsed.dt.strftime("%Y-%m")

    return df


def clean_date_column(
    df: pd.DataFrame,
    column: str,
) -> pd.DataFrame:

    parsed = pd.to_datetime(
        df[column],
        errors="coerce",
    )

    invalid = parsed.isna().sum()

    if invalid > 0:
        raise ValueError(
            f"{invalid} invalid date values found in '{column}'."
        )

    df[column] = parsed.dt.strftime("%Y-%m-%d")

    return df


def convert_numeric_columns(
    df: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:

    for column in columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    return df


def validate_numeric_columns(
    df: pd.DataFrame,
    columns: list[str],
) -> None:

    for column in columns:

        if df[column].isna().any():
            raise ValueError(
                f"Missing/non-numeric values found in '{column}'."
            )

        if df[column].isin(
            [float("inf"), float("-inf")]
        ).any():
            raise ValueError(
                f"Infinite values found in '{column}'."
            )


def clean_fund_master() -> pd.DataFrame:

    input_file = RAW_DIR / "fund_master.csv"
    output_file = PROCESSED_DIR / "fund_master_cleaned.csv"

    df = pd.read_csv(input_file)

    print("\n===== FUND MASTER =====")
    print(f"Raw rows: {len(df):,}")

    df = clean_text_columns(df)

    df["amfi_code"] = pd.to_numeric(
        df["amfi_code"],
        errors="coerce",
    )

    df["launch_date"] = pd.to_datetime(
        df["launch_date"],
        errors="coerce",
    )

    numeric_columns = [
        "expense_ratio_pct",
        "exit_load_pct",
        "min_sip_amount",
        "min_lumpsum_amount",
    ]

    df = convert_numeric_columns(
        df,
        numeric_columns,
    )

    if df["amfi_code"].isna().any():
        raise ValueError(
            "Invalid AMFI codes in fund_master."
        )

    if df["launch_date"].isna().any():
        raise ValueError(
            "Invalid launch dates in fund_master."
        )

    validate_numeric_columns(
        df,
        numeric_columns,
    )

    if (df["expense_ratio_pct"] < 0).any():
        raise ValueError(
            "Negative expense ratios found."
        )

    if (df["exit_load_pct"] < 0).any():
        raise ValueError(
            "Negative exit loads found."
        )

    if (df["min_sip_amount"] < 0).any():
        raise ValueError(
            "Negative minimum SIP amounts found."
        )

    if (df["min_lumpsum_amount"] < 0).any():
        raise ValueError(
            "Negative minimum lumpsum amounts found."
        )

    duplicates = df.duplicated().sum()

    df = (
        df
        .drop_duplicates()
        .sort_values("amfi_code")
        .reset_index(drop=True)
    )

    df["launch_date"] = df["launch_date"].dt.strftime(
        "%Y-%m-%d"
    )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        output_file,
        index=False,
    )

    print(f"Duplicates removed: {duplicates:,}")
    print(f"Final rows: {len(df):,}")
    print(f"Output: {output_file}")

    return df


def clean_aum() -> pd.DataFrame:

    input_file = RAW_DIR / "aum_by_fund_house.csv"
    output_file = (
        PROCESSED_DIR / "aum_by_fund_house_cleaned.csv"
    )

    df = pd.read_csv(input_file)

    print("\n===== AUM BY FUND HOUSE =====")
    print(f"Raw rows: {len(df):,}")

    df = clean_text_columns(df)

    df = clean_date_column(
        df,
        "date",
    )

    numeric_columns = [
        "aum_lakh_crore",
        "aum_crore",
        "num_schemes",
    ]

    df = convert_numeric_columns(
        df,
        numeric_columns,
    )

    validate_numeric_columns(
        df,
        numeric_columns,
    )

    if (df["aum_lakh_crore"] < 0).any():
        raise ValueError(
            "Negative AUM values found."
        )

    if (df["aum_crore"] < 0).any():
        raise ValueError(
            "Negative AUM values found."
        )

    if (df["num_schemes"] <= 0).any():
        raise ValueError(
            "Invalid number of schemes found."
        )

    conversion_difference = (
        df["aum_lakh_crore"] * 100000
        - df["aum_crore"]
    ).abs()

    if (conversion_difference > 0.01).any():
        raise ValueError(
            "AUM unit consistency check failed."
        )

    duplicates = df.duplicated().sum()

    df = (
        df
        .drop_duplicates()
        .sort_values(
            ["date", "fund_house"]
        )
        .reset_index(drop=True)
    )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        output_file,
        index=False,
    )

    print(f"Duplicates removed: {duplicates:,}")
    print("AUM unit consistency: PASS")
    print(f"Final rows: {len(df):,}")
    print(f"Output: {output_file}")

    return df


def clean_monthly_sip() -> pd.DataFrame:

    input_file = RAW_DIR / "monthly_sip_inflows.csv"
    output_file = (
        PROCESSED_DIR / "monthly_sip_inflows_cleaned.csv"
    )

    df = pd.read_csv(input_file)

    print("\n===== MONTHLY SIP INFLOWS =====")
    print(f"Raw rows: {len(df):,}")

    df = clean_month_column(
        df,
        "month",
    )

    numeric_columns = [
        "sip_inflow_crore",
        "active_sip_accounts_crore",
        "new_sip_accounts_lakh",
        "sip_aum_lakh_crore",
    ]

    df = convert_numeric_columns(
        df,
        numeric_columns,
    )

    validate_numeric_columns(
        df,
        numeric_columns,
    )

    df["yoy_growth_pct"] = pd.to_numeric(
        df["yoy_growth_pct"],
        errors="coerce",
    )

    expected_yoy_nulls = 12

    actual_yoy_nulls = (
        df["yoy_growth_pct"]
        .isna()
        .sum()
    )

    if actual_yoy_nulls != expected_yoy_nulls:
        raise ValueError(
            "Unexpected number of YoY growth nulls: "
            f"{actual_yoy_nulls}; "
            f"expected {expected_yoy_nulls}."
        )

    if (df[numeric_columns] < 0).any().any():
        raise ValueError(
            "Negative SIP metrics found."
        )

    duplicates = df.duplicated().sum()

    df = (
        df
        .drop_duplicates()
        .sort_values("month")
        .reset_index(drop=True)
    )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        output_file,
        index=False,
    )

    print(f"Duplicates removed: {duplicates:,}")
    print(
        f"Expected YoY nulls preserved: "
        f"{actual_yoy_nulls}"
    )
    print(f"Final rows: {len(df):,}")
    print(f"Output: {output_file}")

    return df


def clean_category_inflows() -> pd.DataFrame:

    input_file = RAW_DIR / "category_inflows.csv"
    output_file = (
        PROCESSED_DIR / "category_inflows_cleaned.csv"
    )

    df = pd.read_csv(input_file)

    print("\n===== CATEGORY INFLOWS =====")
    print(f"Raw rows: {len(df):,}")

    df = clean_text_columns(df)

    df = clean_month_column(
        df,
        "month",
    )

    df["net_inflow_crore"] = pd.to_numeric(
        df["net_inflow_crore"],
        errors="coerce",
    )

    validate_numeric_columns(
        df,
        ["net_inflow_crore"],
    )

    duplicates = df.duplicated().sum()

    df = (
        df
        .drop_duplicates()
        .sort_values(
            ["month", "category"]
        )
        .reset_index(drop=True)
    )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        output_file,
        index=False,
    )

    print(f"Duplicates removed: {duplicates:,}")
    print(f"Final rows: {len(df):,}")
    print(f"Output: {output_file}")

    return df


def clean_industry_folios() -> pd.DataFrame:

    input_file = RAW_DIR / "industry_folio_count.csv"
    output_file = (
        PROCESSED_DIR
        / "industry_folio_count_cleaned.csv"
    )

    df = pd.read_csv(input_file)

    print("\n===== INDUSTRY FOLIO COUNT =====")
    print(f"Raw rows: {len(df):,}")

    df = clean_month_column(
        df,
        "month",
    )

    numeric_columns = [
        "total_folios_crore",
        "equity_folios_crore",
        "debt_folios_crore",
        "hybrid_folios_crore",
        "others_folios_crore",
    ]

    df = convert_numeric_columns(
        df,
        numeric_columns,
    )

    validate_numeric_columns(
        df,
        numeric_columns,
    )

    if (df[numeric_columns] < 0).any().any():
        raise ValueError(
            "Negative folio counts found."
        )

    duplicates = df.duplicated().sum()

    df = (
        df
        .drop_duplicates()
        .sort_values("month")
        .reset_index(drop=True)
    )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        output_file,
        index=False,
    )

    print(f"Duplicates removed: {duplicates:,}")
    print(f"Final rows: {len(df):,}")
    print(f"Output: {output_file}")

    return df


def clean_portfolio_holdings() -> pd.DataFrame:

    input_file = RAW_DIR / "portfolio_holdings.csv"
    output_file = (
        PROCESSED_DIR
        / "portfolio_holdings_cleaned.csv"
    )

    df = pd.read_csv(input_file)

    print("\n===== PORTFOLIO HOLDINGS =====")
    print(f"Raw rows: {len(df):,}")

    df = clean_text_columns(df)

    df["amfi_code"] = pd.to_numeric(
        df["amfi_code"],
        errors="coerce",
    )

    df = clean_date_column(
        df,
        "portfolio_date",
    )

    numeric_columns = [
        "weight_pct",
        "market_value_cr",
        "current_price_inr",
    ]

    df = convert_numeric_columns(
        df,
        numeric_columns,
    )

    validate_numeric_columns(
        df,
        numeric_columns,
    )

    if df["amfi_code"].isna().any():
        raise ValueError(
            "Invalid AMFI codes found."
        )

    if (df["weight_pct"] < 0).any():
        raise ValueError(
            "Negative portfolio weights found."
        )

    if (df["market_value_cr"] < 0).any():
        raise ValueError(
            "Negative market values found."
        )

    if (df["current_price_inr"] <= 0).any():
        raise ValueError(
            "Invalid current prices found."
        )

    weight_totals = (
        df
        .groupby(
            ["amfi_code", "portfolio_date"]
        )["weight_pct"]
        .sum()
    )

    invalid_weight_groups = (
        (weight_totals < 99.9)
        | (weight_totals > 100.1)
    ).sum()

    if invalid_weight_groups > 0:
        raise ValueError(
            f"{invalid_weight_groups} portfolio groups "
            "do not sum approximately to 100%."
        )

    duplicates = df.duplicated().sum()

    df = (
        df
        .drop_duplicates()
        .sort_values(
            [
                "amfi_code",
                "portfolio_date",
                "weight_pct",
            ],
            ascending=[
                True,
                True,
                False,
            ],
        )
        .reset_index(drop=True)
    )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        output_file,
        index=False,
    )

    print(f"Duplicates removed: {duplicates:,}")
    print(
        "Portfolio weight validation: PASS "
        f"({invalid_weight_groups} invalid groups)"
    )
    print(f"Final rows: {len(df):,}")
    print(f"Output: {output_file}")

    return df


def clean_benchmark_indices() -> pd.DataFrame:

    input_file = RAW_DIR / "benchmark_indices.csv"
    output_file = (
        PROCESSED_DIR
        / "benchmark_indices_cleaned.csv"
    )

    df = pd.read_csv(input_file)

    print("\n===== BENCHMARK INDICES =====")
    print(f"Raw rows: {len(df):,}")

    df = clean_text_columns(df)

    df = clean_date_column(
        df,
        "date",
    )

    df["close_value"] = pd.to_numeric(
        df["close_value"],
        errors="coerce",
    )

    validate_numeric_columns(
        df,
        ["close_value"],
    )

    if (df["close_value"] <= 0).any():
        raise ValueError(
            "Non-positive benchmark close values found."
        )

    duplicates = df.duplicated().sum()

    df = (
        df
        .drop_duplicates()
        .sort_values(
            ["date", "index_name"]
        )
        .reset_index(drop=True)
    )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        output_file,
        index=False,
    )

    print(f"Duplicates removed: {duplicates:,}")
    print(f"Final rows: {len(df):,}")
    print(f"Output: {output_file}")

    return df


def main() -> None:

    print("=" * 60)
    print("DAY 2 — REMAINING DATA CLEANING PIPELINE")
    print("=" * 60)

    clean_fund_master()
    clean_aum()
    clean_monthly_sip()
    clean_category_inflows()
    clean_industry_folios()
    clean_portfolio_holdings()
    clean_benchmark_indices()

    print("\n" + "=" * 60)
    print("ALL REMAINING DATASETS CLEANED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()