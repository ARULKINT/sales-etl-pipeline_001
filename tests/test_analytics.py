"""
Unit tests for Analytics module (src/analytics.py).
"""
import os
from pathlib import Path
import sys
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from analytics import parse_sql_queries, execute_queries, compute_executive_kpis, export_query_results_to_csv
from load import load_data, get_engine
from config import PipelineConfig


@pytest.fixture
def analytics_test_env(tmp_path):
    db_file = tmp_path / "test_analytics.db"
    cfg = PipelineConfig(processed_db_path=db_file)
    sample_df = pd.DataFrame({
        "order_id": ["ORD0001", "ORD0002", "ORD0003"],
        "order_date": ["2024-01-01", "2024-01-02", "2024-02-01"],
        "product_name": ["Laptop", "Mouse", "Laptop"],
        "quantity": [1, 2, 2],
        "unit_price": [1000.0, 50.0, 1000.0],
        "customer_id": ["CUST001", "CUST002", "CUST001"],
        "region": ["North", "South", "North"],
        "total_price": [1000.0, 100.0, 2000.0],
        "order_month": ["2024-01", "2024-01", "2024-02"],
        "order_year": [2024, 2024, 2024],
        "order_quarter": ["2024-Q1", "2024-Q1", "2024-Q1"],
        "day_of_week": ["Monday", "Tuesday", "Thursday"]
    })
    load_data(sample_df, config=cfg)
    return {"cfg": cfg, "dir": tmp_path}


def test_parse_sql_queries():
    queries = parse_sql_queries()
    assert len(queries) >= 4
    for q in queries:
        assert "id" in q
        assert "title" in q
        assert "SELECT" in q["sql"].upper()


def test_execute_queries_and_kpis(analytics_test_env):
    cfg = analytics_test_env["cfg"]
    results = execute_queries(config=cfg)
    assert len(results) >= 4

    kpis = compute_executive_kpis(config=cfg)
    assert kpis["total_revenue"] == 3100.0
    assert kpis["total_orders"] == 3
    assert kpis["active_customers"] == 2
    assert kpis["top_product"] == "Laptop"
    assert kpis["top_region"] == "North"


def test_export_query_results_to_csv(analytics_test_env):
    cfg = analytics_test_env["cfg"]
    results = execute_queries(config=cfg)
    exported = export_query_results_to_csv(results, output_dir=analytics_test_env["dir"], config=cfg)
    assert len(exported) == len(results)
    for p in exported:
        assert p.exists()
        assert p.stat().st_size > 0
