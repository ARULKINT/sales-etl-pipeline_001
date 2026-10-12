"""
Unit tests for Data Profiling module (src/profile_data.py).
"""
import os
import sys
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from profile_data import profile_data, compare_profiles, format_report_console


@pytest.fixture
def sample_profile_df():
    return pd.DataFrame({
        "order_id": ["ORD0001", "ORD0002", "ORD0002"],
        "quantity": [5, -2, None],
        "unit_price": [100.0, 50.0, 75.0],
        "customer_id": ["CUST001", None, "CUST002"]
    })


def test_profile_data_metrics(sample_profile_df):
    report = profile_data(sample_profile_df, "Test Dataset")
    assert report["row_count"] == 3
    assert report["column_count"] == 4
    assert report["null_counts"]["quantity"] == 1
    assert report["null_counts"]["customer_id"] == 1
    assert report["duplicate_rows"] == 0
    assert report["duplicate_orders"] == 1
    assert report["negative_quantity_rows"] == 1
    assert "quantity" in report["numeric_stats"]


def test_compare_profiles():
    raw_rep = {
        "row_count": 500,
        "duplicate_rows": 10,
        "total_null_cells": 35,
        "negative_quantity_rows": 5
    }
    clean_rep = {
        "row_count": 460,
        "duplicate_rows": 0,
        "total_null_cells": 0,
        "negative_quantity_rows": 0
    }
    diff = compare_profiles(raw_rep, clean_rep)
    assert diff["raw_rows"] == 500
    assert diff["clean_rows"] == 460
    assert diff["dropped_rows"] == 40
    assert diff["retention_rate_pct"] == 92.0


def test_format_report_console(sample_profile_df):
    report = profile_data(sample_profile_df)
    output = format_report_console(report)
    assert "DATA PROFILING REPORT" in output
    assert "Null Values per Column:" in output
