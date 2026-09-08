from pathlib import Path

import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "investor_transactions.csv"
OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "processed" / "investor_transactions_cleaned.csv"
)


def clean_transactions() -> pd.DataFrame:
    """Clean and validate investor transaction data."""

    # 1. Load raw data
    df = pd.read_csv(INPUT_FILE)

    raw_rows = len(df)

    print(f"Raw rows: {raw_rows:,}")

    # 2. Validate required columns
    required_columns = {
        "investor_id",
        "transaction_date",
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
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    # 3. Clean text fields
    text_columns = [
        "transaction_type",
        "state",
        "city",
        "city_tier",
        "age_group",
        "gender",
        "payment_mode",
        "kyc_status",
    ]

    for column in text_columns:
        df[column] = df[column].astype("string").str.strip()

    # 4. Standardize transaction types
    transaction_type_map = {
        "sip": "SIP",
        "lumpsum": "Lumpsum",
        "lump sum": "Lumpsum",
        "redemption": "Redemption",
    }

    df["transaction_type"] = (
        df["transaction_type"]
        .str.lower()
        .map(transaction_type_map)
    )

    # Validate transaction types
    invalid_transaction_types = df["transaction_type"].isna().sum()

    if invalid_transaction_types > 0:
        raise ValueError(
            f"Found {invalid_transaction_types} invalid transaction_type values."
        )

    # 5. Standardize KYC status
    df["kyc_status"] = (
        df["kyc_status"]
        .str.lower()
        .str.title()
    )

    allowed_kyc_statuses = {
        "Verified",
        "Pending",
    }

    invalid_kyc = ~df["kyc_status"].isin(allowed_kyc_statuses)

    if invalid_kyc.any():
        invalid_values = (
            df.loc[invalid_kyc, "kyc_status"]
            .dropna()
            .unique()
            .tolist()
        )

        raise ValueError(
            f"Invalid KYC status values found: {invalid_values}"
        )

    # 6. Convert transaction date
    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"],
        errors="coerce"
    )

    invalid_dates = df["transaction_date"].isna().sum()

    if invalid_dates > 0:
        raise ValueError(
            f"Found {invalid_dates} invalid transaction dates."
        )

    # 7. Convert numeric fields
    df["amount_inr"] = pd.to_numeric(
        df["amount_inr"],
        errors="coerce"
    )

    df["annual_income_lakh"] = pd.to_numeric(
        df["annual_income_lakh"],
        errors="coerce"
    )

    # 8. Validate amount
    invalid_amounts = (
        df["amount_inr"].isna()
        | (df["amount_inr"] <= 0)
    ).sum()

    if invalid_amounts > 0:
        raise ValueError(
            f"Found {invalid_amounts} invalid amount_inr values."
        )

    # 9. Validate AMFI codes
    df["amfi_code"] = pd.to_numeric(
        df["amfi_code"],
        errors="coerce"
    )

    invalid_amfi_codes = df["amfi_code"].isna().sum()

    if invalid_amfi_codes > 0:
        raise ValueError(
            f"Found {invalid_amfi_codes} invalid AMFI codes."
        )

    # 10. Remove exact duplicate rows
    duplicates_removed = df.duplicated().sum()

    df = df.drop_duplicates().reset_index(drop=True)

    # 11. Sort records
    df = df.sort_values(
        by=["transaction_date", "amfi_code"]
    ).reset_index(drop=True)

    # 12. Save cleaned data
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # 13. Print validation summary
    print("\n===== TRANSACTION CLEANING SUMMARY =====")
    print(f"Raw rows:                 {raw_rows:,}")
    print(f"Duplicates removed:       {duplicates_removed:,}")
    print(f"Invalid transaction type: {invalid_transaction_types:,}")
    print(f"Invalid KYC values:       {invalid_kyc.sum():,}")
    print(f"Invalid dates:            {invalid_dates:,}")
    print(f"Invalid amounts:          {invalid_amounts:,}")
    print(f"Final rows:               {len(df):,}")
    print(f"Output file:              {OUTPUT_FILE}")

    print("\nTransaction types:")
    print(df["transaction_type"].value_counts())

    print("\nKYC status:")
    print(df["kyc_status"].value_counts())

    return df


if __name__ == "__main__":
    clean_transactions()