from pathlib import Path

import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "nav_history.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "nav_history_cleaned.csv"


def clean_nav_history() -> pd.DataFrame:
    """Clean and validate historical mutual-fund NAV data."""

    # 1. Load raw data
    df = pd.read_csv(INPUT_FILE)

    print(f"Raw rows: {len(df):,}")

    # 2. Validate required columns
    required_columns = {"amfi_code", "date", "nav"}

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    # 3. Convert date to datetime
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # 4. Convert NAV to numeric
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")

    # 5. Check invalid dates
    invalid_dates = df["date"].isna().sum()

    if invalid_dates > 0:
        raise ValueError(
            f"Found {invalid_dates} invalid date values."
        )

    # 6. Sort by AMFI code and date
    df = df.sort_values(
        by=["amfi_code", "date"]
    ).reset_index(drop=True)

    # 7. Remove duplicate AMFI code + date records
    duplicates_removed = df.duplicated(
        subset=["amfi_code", "date"]
    ).sum()

    df = df.drop_duplicates(
        subset=["amfi_code", "date"],
        keep="first"
    ).reset_index(drop=True)

    # 8. Forward-fill missing NAV within each scheme
    missing_nav_before = df["nav"].isna().sum()

    df["nav"] = (
        df.groupby("amfi_code")["nav"]
        .ffill()
    )

    missing_nav_after = df["nav"].isna().sum()

    # 9. Validate NAV values
    invalid_nav = (df["nav"] <= 0).sum()

    if invalid_nav > 0:
        raise ValueError(
            f"Found {invalid_nav} NAV values <= 0."
        )

    # 10. Check whether missing NAVs remain
    if missing_nav_after > 0:
        raise ValueError(
            f"{missing_nav_after} missing NAV values remain after forward-fill."
        )

    # 11. Save cleaned dataset
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # 12. Print validation summary
    print("\n===== NAV HISTORY CLEANING SUMMARY =====")
    print(f"Raw rows:                  {len(df) + duplicates_removed:,}")
    print(f"Duplicates removed:        {duplicates_removed:,}")
    print(f"Missing NAV before fill:   {missing_nav_before:,}")
    print(f"Missing NAV after fill:    {missing_nav_after:,}")
    print(f"NAV <= 0:                  {invalid_nav:,}")
    print(f"Final rows:                {len(df):,}")
    print(f"Output file:               {OUTPUT_FILE}")

    return df


if __name__ == "__main__":
    clean_nav_history()