from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

csv_files = sorted(RAW.glob("*.csv"))
print(f"Found {len(csv_files)} CSV files.")

if len(csv_files) != 10:
    print("WARNING: Expected 10 CSV files.")

rows = []
datasets = {}

for path in csv_files:
    df = pd.read_csv(path, low_memory=False)
    datasets[path.stem] = df

    print("\n" + "=" * 90)
    print(f"FILE: {path.name}")
    print("SHAPE:", df.shape)
    print("\nDTYPES:")
    print(df.dtypes.to_string())
    print("\nHEAD:")
    print(df.head().to_string(index=False))
    print("\nMISSING VALUES:")
    print(df.isna().sum()[lambda s: s > 0].to_string() or "None")
    print("\nDUPLICATE ROWS:", df.duplicated().sum())

    rows.append({
        "dataset": path.name,
        "rows": len(df),
        "columns": len(df.columns),
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum())
    })

pd.DataFrame(rows).to_csv(REPORTS / "data_quality_runtime.csv", index=False)
print("\nSaved reports/data_quality_runtime.csv")
