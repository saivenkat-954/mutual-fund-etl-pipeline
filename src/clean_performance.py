from pathlib import Path

import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "scheme_performance.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "scheme_performance_cleaned.csv"
)


# ============================================================
# COLUMN DEFINITIONS
# ============================================================

RETURN_COLUMNS = [
    "return_1yr_pct",
    "return_3yr_pct",
    "return_5yr_pct",
    "benchmark_3yr_pct",
]

NUMERIC_COLUMNS = [
    "return_1yr_pct",
    "return_3yr_pct",
    "return_5yr_pct",
    "benchmark_3yr_pct",
    "alpha",
    "beta",
    "sharpe_ratio",
    "sortino_ratio",
    "std_dev_ann_pct",
    "max_drawdown_pct",
    "aum_crore",
    "expense_ratio_pct",
    "morningstar_rating",
]

TEXT_COLUMNS = [
    "scheme_name",
    "fund_house",
    "category",
    "plan",
    "risk_grade",
]


# ============================================================
# CLEANING FUNCTION
# ============================================================

def clean_scheme_performance() -> pd.DataFrame:
    """Clean and validate mutual-fund scheme performance data."""

    # --------------------------------------------------------
    # 1. LOAD RAW DATA
    # --------------------------------------------------------

    print("Loading scheme_performance.csv...")

    df = pd.read_csv(INPUT_FILE)

    raw_rows = len(df)

    print(f"Raw rows: {raw_rows:,}")
    print(f"Raw columns: {len(df.columns):,}")

    # --------------------------------------------------------
    # 2. VALIDATE REQUIRED COLUMNS
    # --------------------------------------------------------

    required_columns = {
        "amfi_code",
        "scheme_name",
        "fund_house",
        "category",
        "plan",
        "risk_grade",
        *RETURN_COLUMNS,
        "alpha",
        "beta",
        "sharpe_ratio",
        "sortino_ratio",
        "std_dev_ann_pct",
        "max_drawdown_pct",
        "aum_crore",
        "expense_ratio_pct",
        "morningstar_rating",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    print("Required columns: PASS")

    # --------------------------------------------------------
    # 3. CHECK INITIAL MISSING VALUES
    # --------------------------------------------------------

    missing_before = df.isna().sum().sum()

    print(f"Missing values before cleaning: {missing_before:,}")

    # --------------------------------------------------------
    # 4. CLEAN TEXT COLUMNS
    # --------------------------------------------------------

    for column in TEXT_COLUMNS:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

    # --------------------------------------------------------
    # 5. STANDARDIZE RISK GRADE
    # --------------------------------------------------------

    df["risk_grade"] = (
        df["risk_grade"]
        .str.strip()
        .str.title()
    )

    # --------------------------------------------------------
    # 6. CONVERT AMFI CODE TO NUMERIC
    # --------------------------------------------------------

    df["amfi_code"] = pd.to_numeric(
        df["amfi_code"],
        errors="coerce"
    )

    invalid_amfi = df["amfi_code"].isna().sum()

    if invalid_amfi > 0:
        raise ValueError(
            f"Found {invalid_amfi} invalid AMFI code values."
        )

    # --------------------------------------------------------
    # 7. CONVERT PERFORMANCE COLUMNS TO NUMERIC
    # --------------------------------------------------------

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # --------------------------------------------------------
    # 8. VALIDATE RETURN VALUES
    # --------------------------------------------------------

    invalid_return_rows = (
        df[RETURN_COLUMNS]
        .isna()
        .any(axis=1)
        .sum()
    )

    if invalid_return_rows > 0:
        raise ValueError(
            f"Found {invalid_return_rows} rows with "
            "missing or non-numeric return values."
        )

    # --------------------------------------------------------
    # 9. VALIDATE OTHER NUMERIC PERFORMANCE METRICS
    # --------------------------------------------------------

    invalid_numeric_rows = (
        df[NUMERIC_COLUMNS]
        .isna()
        .any(axis=1)
        .sum()
    )

    if invalid_numeric_rows > 0:
        raise ValueError(
            f"Found {invalid_numeric_rows} rows with "
            "missing or non-numeric performance metrics."
        )

    # --------------------------------------------------------
    # 10. CHECK INFINITE VALUES
    # --------------------------------------------------------

    infinite_rows = (
        df[NUMERIC_COLUMNS]
        .isin([float("inf"), float("-inf")])
        .any(axis=1)
        .sum()
    )

    if infinite_rows > 0:
        raise ValueError(
            f"Found {infinite_rows} rows containing "
            "infinite numeric values."
        )

    # --------------------------------------------------------
    # 11. VALIDATE EXPENSE RATIO
    # --------------------------------------------------------

    expense_outside_range = (
        (df["expense_ratio_pct"] < 0.1)
        | (df["expense_ratio_pct"] > 2.5)
    )

    expense_anomalies = expense_outside_range.sum()

    if expense_anomalies > 0:

        print(
            "\nWARNING: Expense-ratio anomalies detected:"
        )

        print(
            df.loc[
                expense_outside_range,
                [
                    "amfi_code",
                    "scheme_name",
                    "expense_ratio_pct",
                ],
            ].to_string(index=False)
        )

    else:

        print(
            "Expense ratio validation: PASS "
            "(all values within 0.1%–2.5%)"
        )

    # --------------------------------------------------------
    # 12. CHECK DUPLICATES
    # --------------------------------------------------------

    duplicates_removed = df.duplicated().sum()

    if duplicates_removed > 0:

        print(
            f"Removing duplicate rows: "
            f"{duplicates_removed:,}"
        )

        df = (
            df
            .drop_duplicates()
            .reset_index(drop=True)
        )

    else:

        print("Duplicate validation: PASS (0 duplicates)")

    # --------------------------------------------------------
    # 13. SORT DATA
    # --------------------------------------------------------

    df = (
        df
        .sort_values(
            by=["amfi_code"]
        )
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # 14. FINAL MISSING VALUE CHECK
    # --------------------------------------------------------

    missing_after = df.isna().sum().sum()

    if missing_after > 0:
        raise ValueError(
            f"Found {missing_after} missing values "
            "after cleaning."
        )

    # --------------------------------------------------------
    # 15. FINAL NUMERIC VALIDATION
    # --------------------------------------------------------

    invalid_final_numeric = (
        ~df[NUMERIC_COLUMNS]
        .apply(
            lambda column: pd.to_numeric(
                column,
                errors="coerce"
            ).notna()
        )
    ).any(axis=1).sum()

    if invalid_final_numeric > 0:
        raise ValueError(
            f"Found {invalid_final_numeric} rows with "
            "invalid final numeric values."
        )

    # --------------------------------------------------------
    # 16. CREATE OUTPUT DIRECTORY
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # 17. SAVE CLEANED DATA
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------------
    # 18. FINAL SUMMARY
    # --------------------------------------------------------

    print("\n")
    print("=" * 60)
    print("SCHEME PERFORMANCE CLEANING SUMMARY")
    print("=" * 60)

    print(f"Raw rows:                 {raw_rows:,}")
    print(f"Raw columns:              19")
    print(f"Duplicates removed:      {duplicates_removed:,}")
    print(f"Invalid AMFI codes:      {invalid_amfi:,}")
    print(f"Invalid return rows:     {invalid_return_rows:,}")
    print(f"Invalid numeric rows:    {invalid_numeric_rows:,}")
    print(f"Infinite-value rows:     {infinite_rows:,}")
    print(f"Expense anomalies:       {expense_anomalies:,}")
    print(f"Missing after cleaning:  {missing_after:,}")
    print(f"Final rows:              {len(df):,}")
    print(f"Final columns:           {len(df.columns):,}")

    print("\nOutput:")
    print(OUTPUT_FILE)

    print("\nRisk grades:")
    print(df["risk_grade"].value_counts().to_string())

    print("\nCleaning completed successfully.")
    print("=" * 60)

    return df


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    clean_scheme_performance()