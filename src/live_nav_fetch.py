from pathlib import Path
from datetime import datetime, timezone
import json
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "mfapi"
OUT = ROOT / "data" / "processed" / "nav"
RAW.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

SCHEMES = {
    "125497": "HDFC Top 100 Direct",
    "119551": "SBI Bluechip",
    "120503": "ICICI Bluechip",
    "118632": "Nippon Large Cap",
    "119092": "Axis Bluechip",
    "120841": "Kotak Bluechip",
}

frames = []

for code, task_name in SCHEMES.items():
    url = f"https://api.mfapi.in/mf/{code}"
    print(f"Fetching {code} — {task_name}")
    response = requests.get(
        url,
        timeout=30,
        headers={"User-Agent": "day1-mf-etl-project/1.0"},
    )
    response.raise_for_status()
    payload = response.json()

    (RAW / f"{code}.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    meta = payload.get("meta", {})
    records = payload.get("data", [])

    rows = []
    for record in records:
        row = dict(record)
        row["amfi_code"] = int(code)
        row["task_scheme_name"] = task_name
        row["fund_house"] = meta.get("fund_house")
        row["scheme_type"] = meta.get("scheme_type")
        row["scheme_category"] = meta.get("scheme_category")
        row["scheme_start_date"] = meta.get("scheme_start_date")
        row["fetched_at_utc"] = datetime.now(timezone.utc).isoformat()
        rows.append(row)

    df = pd.DataFrame(rows)

    if "date" in df:
        df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    if "nav" in df:
        df["nav"] = pd.to_numeric(df["nav"], errors="coerce")

    df.to_csv(OUT / f"{code}_nav.csv", index=False)
    frames.append(df)

combined = pd.concat(frames, ignore_index=True)
combined.to_csv(ROOT / "data" / "processed" / "nav_history_live.csv", index=False)

print("\nLive NAV ingestion complete.")
print("Rows:", len(combined))
print("Schemes:", combined["amfi_code"].nunique())
