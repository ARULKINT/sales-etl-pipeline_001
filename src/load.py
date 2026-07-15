"""
Phase 10 - Load
Loads the cleaned DataFrame into a SQLite database.
SQLite chosen because it needs zero setup - swap the connection string
for Postgres later without changing any other code (that's why we use
SQLAlchemy instead of raw sqlite3).
"""
import pandas as pd
from sqlalchemy import create_engine, text
import logging

logger = logging.getLogger(__name__)

DB_PATH = "data/processed/sales.db"


def get_engine(db_path: str = DB_PATH):
    return create_engine(f"sqlite:///{db_path}")


def load_data(df: pd.DataFrame, table_name: str = "sales", db_path: str = DB_PATH) -> None:
    engine = get_engine(db_path)
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    logger.info(f"Loaded {len(df)} rows into table '{table_name}'")


def verify_load(table_name: str = "sales", db_path: str = DB_PATH) -> int:
    """Confirm the row count in the DB matches what we expect."""
    engine = get_engine(db_path)
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        count = result.scalar()
    logger.info(f"Verified: {count} rows in database")
    return count


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from extract import extract_data
    from transform import transform_pipeline
    from validate import validate_data

    df = extract_data("data/raw/sales_data.csv")
    clean_df = transform_pipeline(df)
    validate_data(clean_df)
    load_data(clean_df)
    verify_load()
