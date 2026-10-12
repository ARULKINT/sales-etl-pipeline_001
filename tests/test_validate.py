"""
Unit tests for the Validate module (src/validate.py).
"""
import os
import sys
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from validate import validate_data, ValidationError
from config import default_config


@pytest.fixture
def valid_clean_df():
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


def test_validate_data_passes(valid_clean_df):
    results = validate_data(valid_clean_df)
    assert all(results.values())


def test_validate_fails_on_empty():
    empty_df = pd.DataFrame()
    with pytest.raises(ValidationError, match="empty"):
        validate_data(empty_df)


def test_validate_fails_on_missing_column(valid_clean_df):
    invalid_df = valid_clean_df.drop(columns=["customer_id"])
    with pytest.raises(ValidationError, match="Missing required columns"):
        validate_data(invalid_df)


def test_validate_fails_on_null_values(valid_clean_df):
    invalid_df = valid_clean_df.copy()
    invalid_df.loc[0, "customer_id"] = None
    with pytest.raises(ValidationError, match="Found unexpected null values"):
        validate_data(invalid_df)


def test_validate_fails_on_negative_quantity(valid_clean_df):
    invalid_df = valid_clean_df.copy()
    invalid_df.loc[0, "quantity"] = -5
    with pytest.raises(ValidationError, match="quantity <"):
        validate_data(invalid_df)


def test_validate_fails_on_calculation_discrepancy(valid_clean_df):
    invalid_df = valid_clean_df.copy()
    invalid_df.loc[0, "total_price"] = 99999.0  # Mismatched total
    with pytest.raises(ValidationError, match="Calculation mismatch"):
        validate_data(invalid_df)


def test_validate_fails_on_duplicate_orders(valid_clean_df):
    invalid_df = pd.concat([valid_clean_df, valid_clean_df.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValidationError, match="duplicate order_id"):
        validate_data(invalid_df)


def test_validate_fails_on_invalid_customer_pattern(valid_clean_df):
    invalid_df = valid_clean_df.copy()
    invalid_df.loc[0, "customer_id"] = "BAD_ID_99"
    with pytest.raises(ValidationError, match="Customer IDs do not match"):
        validate_data(invalid_df)
