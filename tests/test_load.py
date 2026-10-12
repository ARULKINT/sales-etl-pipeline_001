"""
Unit tests for the Load module (src/load.py).
"""
import os
from pathlib import Path
import sys
import pandas as pd
import pytest
from sqlalchemy import text

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from load import get_engine, load_data, verify_load, log_pipeline_audit, create_indexes
from config import PipelineConfig


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_sales.db"
    cfg = PipelineConfig(processed_db_path=db_file)
    return {"cfg": cfg, "path": db_file}


@pytest.fixture
def sample_clean_df():
    return pd.DataFrame({
        "order_id": ["ORD0001", "ORD0002"],
        "order_date": ["2024-01-01", "2024-01-02"],
        "product_name": ["Laptop", "Mouse"],
        "quantity": [1, 2],
        "unit_price": [1000.0, 50.0],
        "customer_id": ["CUST001", "CUST002"],
        "region": ["North", "South"],
        "total_price": [1000.0, 100.0],
        "order_month": ["2024-01", "2024-01"],
        "order_year": [2024, 2024],
        "order_quarter": ["2024-Q1", "2024-Q1"],
        "day_of_week": ["Monday", "Tuesday"]
    })


def test_load_data_and_verify(temp_db, sample_clean_df):
    cfg = temp_db["cfg"]
    load_data(sample_clean_df, config=cfg)
    count = verify_load(config=cfg)
    assert count == 2

    # Check database content
    engine = get_engine(config=cfg)
    with engine.connect() as conn:
        res = conn.execute(text(f"SELECT product_name FROM {cfg.sales_table_name} ORDER BY order_id")).fetchall()
        assert [r[0] for r in res] == ["Laptop", "Mouse"]


def test_log_pipeline_audit(temp_db):
    cfg = temp_db["cfg"]
    run_id = log_pipeline_audit(
        raw_rows=100,
        clean_rows=90,
        status="SUCCESS",
        duration_sec=0.45,
        config=cfg
    )
    assert isinstance(run_id, str)

    engine = get_engine(config=cfg)
    with engine.connect() as conn:
        res = conn.execute(text(f"SELECT run_id, raw_rows, clean_rows, status FROM {cfg.audit_table_name}")).first()
        assert res[0] == run_id
        assert res[1] == 100
        assert res[2] == 90
        assert res[3] == "SUCCESS"
