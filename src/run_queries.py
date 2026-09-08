from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_FILE = PROJECT_ROOT / "mutual_fund.db"
QUERIES_FILE = PROJECT_ROOT / "sql" / "queries.sql"


def load_queries():
    sql = QUERIES_FILE.read_text(
        encoding="utf-8"
    )

    queries = [
        query.strip()
        for query in sql.split(";")
        if query.strip()
    ]

    return queries


def run_queries():

    engine = create_engine(
        f"sqlite:///{DATABASE_FILE}"
    )

    queries = load_queries()

    print("=" * 70)
    print("DAY 2 — ANALYTICAL SQL QUERIES")
    print("=" * 70)

    with engine.connect() as connection:

        for number, query in enumerate(
            queries,
            start=1,
        ):

            print("\n")
            print("=" * 70)
            print(f"QUERY {number}")
            print("=" * 70)

            df = pd.read_sql(
                text(query),
                connection,
            )

            if df.empty:
                print("No results found.")
            else:
                print(
                    df.to_string(
                        index=False
                    )
                )

    print("\n")
    print("=" * 70)
    print("ALL QUERIES EXECUTED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    run_queries()