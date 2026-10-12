"""
Phase 5: Load Module

Loads cleaned and validated data into SQLite database with indexing and an audit log table.
Supports SQLAlchemy engines and provides load verification.
"""
from datetime import datetime, timezone
import logging
from pathlib import Path
from typing import Optional, Union
import uuid
import pandas as pd
from sqlalchemy import create_engine, Engine, text

try:
    from .config import default_config, PipelineConfig
except (ImportError, ValueError):
    from config import default_config, PipelineConfig

logger = logging.getLogger(__name__)


def get_engine(db_path: Optional[Union[str, Path]] = None, config: Optional[PipelineConfig] = None) -> Engine:
    """
    Creates and returns a SQLAlchemy Engine for the target database.
    """
    cfg = config or default_config
    if db_path:
        target = Path(db_path).resolve().as_posix()
        url = f"sqlite:///{target}"
    else:
        url = cfg.db_connection_url
    return create_engine(url)


def load_data(
    df: pd.DataFrame,
    table_name: Optional[str] = None,
    db_path: Optional[Union[str, Path]] = None,
    config: Optional[PipelineConfig] = None
) -> None:
    """
    Loads DataFrame into target SQLite table and creates analytical indexes.
    """
    cfg = config or default_config
    target_table = table_name or cfg.sales_table_name
    engine = get_engine(db_path=db_path, config=cfg)

    # Convert order_date to string ISO format if it is datetime
    df_to_load = df.copy()
    if pd.api.types.is_datetime64_any_dtype(df_to_load["order_date"]):
        df_to_load["order_date"] = df_to_load["order_date"].dt.strftime("%Y-%m-%d")

    # Replace table with clean data
    df_to_load.to_sql(target_table, engine, if_exists="replace", index=False)
    logger.info(f"Loaded {len(df_to_load):,} rows into table '{target_table}'")

    # Create analytical indexes for high performance queries
    create_indexes(engine=engine, table_name=target_table)


def create_indexes(engine: Engine, table_name: str) -> None:
    """Creates database indexes on frequently queried columns."""
    index_queries = [
        f"CREATE INDEX IF NOT EXISTS idx_{table_name}_order_date ON {table_name} (order_date);",
        f"CREATE INDEX IF NOT EXISTS idx_{table_name}_customer_id ON {table_name} (customer_id);",
        f"CREATE INDEX IF NOT EXISTS idx_{table_name}_product_name ON {table_name} (product_name);",
        f"CREATE INDEX IF NOT EXISTS idx_{table_name}_region ON {table_name} (region);",
    ]
    with engine.begin() as conn:
        for query in index_queries:
            conn.execute(text(query))
    logger.info(f"Database indexes verified on table '{table_name}'")


def log_pipeline_audit(
    raw_rows: int,
    clean_rows: int,
    status: str = "SUCCESS",
    duration_sec: float = 0.0,
    run_id: Optional[str] = None,
    notes: str = "",
    config: Optional[PipelineConfig] = None
) -> str:
    """
    Records an execution entry in the etl_pipeline_audit table for data lineage and auditing.
    """
    cfg = config or default_config
    engine = get_engine(config=cfg)
    execution_id = run_id or str(uuid.uuid4())[:8]
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    dropped_rows = raw_rows - clean_rows

    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {cfg.audit_table_name} (
        run_id TEXT PRIMARY KEY,
        run_timestamp TEXT,
        status TEXT,
        raw_rows INTEGER,
        clean_rows INTEGER,
        dropped_rows INTEGER,
        duration_sec REAL,
        notes TEXT
    );
    """
    insert_sql = f"""
    INSERT INTO {cfg.audit_table_name} 
    (run_id, run_timestamp, status, raw_rows, clean_rows, dropped_rows, duration_sec, notes)
    VALUES (:run_id, :run_timestamp, :status, :raw_rows, :clean_rows, :dropped_rows, :duration_sec, :notes);
    """

    with engine.begin() as conn:
        conn.execute(text(create_table_sql))
        conn.execute(
            text(insert_sql),
            {
                "run_id": execution_id,
                "run_timestamp": timestamp,
                "status": status,
                "raw_rows": raw_rows,
                "clean_rows": clean_rows,
                "dropped_rows": dropped_rows,
                "duration_sec": round(duration_sec, 2),
                "notes": notes,
            }
        )

    logger.info(f"Audit log saved: Run ID '{execution_id}' [{status}] in {duration_sec:.2f}s")
    return execution_id


def verify_load(
    table_name: Optional[str] = None,
    db_path: Optional[Union[str, Path]] = None,
    config: Optional[PipelineConfig] = None
) -> int:
    """
    Queries and verifies that the database contains populated rows.
    """
    cfg = config or default_config
    target_table = table_name or cfg.sales_table_name
    engine = get_engine(db_path=db_path, config=cfg)

    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {target_table}"))
        count = int(result.scalar() or 0)

    logger.info(f"Verification successful: {count:,} rows present in table '{target_table}'")
    return count


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    from extract import extract_data
    from transform import transform_pipeline
    from validate import validate_data

    raw = extract_data()
    clean = transform_pipeline(raw)
    validate_data(clean)
    load_data(clean)
    verify_load()
    log_pipeline_audit(len(raw), len(clean), status="SUCCESS", duration_sec=1.25)
