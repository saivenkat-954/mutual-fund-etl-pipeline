# Day 1 — Mutual Fund ETL & Data Ingestion

## Status
**CSV ingestion + quality analysis: COMPLETE**

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src/data_ingestion.py
python src/live_nav_fetch.py
```

## Folder structure

- `data/raw/` — 10 supplied CSV datasets + raw MFAPI JSON
- `data/processed/` — processed NAV outputs
- `src/` — ETL scripts
- `reports/` — data-quality report
- `notebooks/` — exploratory analysis
- `sql/` — SQL work
- `dashboard/` — dashboard work
- `documentation/` — submission documentation
- `ppt_slides/` — presentation
- `demo_video/` — demo recording

## Day 1 deliverables

- `src/data_ingestion.py`
- `src/live_nav_fetch.py`
- `requirements.txt`
- `reports/DAY1_DATA_QUALITY_SUMMARY.md`
- GitHub repository with Day 1 commit

## Git commit

```bash
git add .
git commit -m "Day 1: Data ingestion complete"
git push
```
