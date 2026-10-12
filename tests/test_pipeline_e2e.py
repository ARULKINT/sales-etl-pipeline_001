"""
End-to-End Integration Test for the complete Sales ETL Pipeline.
"""
import os
from pathlib import Path
import sys
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from main import run_pipeline


def test_full_pipeline_e2e(tmp_path):
    # Create raw messy test CSV
    raw_csv = tmp_path / "raw_test_sales.csv"
    test_data = pd.DataFrame({
        "order_id": ["ORD0001", "ORD0002", "ORD0003", "ORD0004", "ORD0001"], # ORD0001 duplicate
        "order_date": ["2024-01-01", "15/02/2024", "not-a-date", "2024-03-01", "2024-01-01"],
        "product_name": ["laptop", "MOUSE", "KEYBOARD", "usb cable", "laptop"],
        "quantity": [2, -1, 3, 4, 2], # ORD0002 negative quantity
        "unit_price": [1200.0, 50.0, 100.0, 25.0, 1200.0],
        "customer_id": ["CUST001", "CUST002", None, "CUST004", "CUST001"], # ORD0003 missing customer
        "region": ["north", "south", "east", "west", "north"]
    })
    test_data.to_csv(raw_csv, index=False)

    db_path = tmp_path / "processed_e2e.db"

    # Run pipeline end to end
    result = run_pipeline(
        raw_file=str(raw_csv),
        db_path=str(db_path),
        skip_analytics=False,
        generate_report=True,
        verbose=False
    )

    assert result["status"] == "SUCCESS"
    assert result["raw_rows"] == 5
    # ORD0001: clean
    # ORD0002: negative quantity -> dropped
    # ORD0003: missing customer & invalid date -> dropped
    # ORD0004: clean
    # ORD0001 (duplicate): dropped
    assert result["clean_rows"] == 2
    assert db_path.exists()
    assert result["kpis"]["total_orders"] == 2
