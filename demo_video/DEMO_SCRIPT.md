# Day 1 Demo Video Script (2–4 minutes)

1. Show the project folder structure.
2. Open `requirements.txt` and explain the main Python libraries.
3. Show the 10 CSV datasets in `data/raw`.
4. Run `python src/data_ingestion.py`.
5. Show shape, dtypes, head and quality checks.
6. Open `reports/DAY1_DATA_QUALITY_SUMMARY.md`.
7. Explain the 12 missing YoY values as expected because prior-year data is unavailable.
8. Show AMFI referential-integrity validation.
9. Open `src/live_nav_fetch.py` and explain the MFAPI request + raw JSON + flattened CSV flow.
10. Show Git commit:
   `Day 1: Data ingestion complete`
