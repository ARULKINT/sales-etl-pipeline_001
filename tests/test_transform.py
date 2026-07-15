"""
Phase 14 - Testing
Basic unit tests. Run with: pytest tests/
"""
import sys
import os
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from transform import (
    clean_dates, standardize_text, handle_missing_values,
    remove_invalid_rows, remove_duplicates, add_calculated_columns
)


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "order_id": ["ORD1", "ORD2", "ORD3", "ORD4"],
        "order_date": ["2024-01-05", "15/01/2024", "01-20-2024", "not-a-date"],
        "product_name": ["mouse", "KEYBOARD", " Monitor ", "webcam"],
        "quantity": [2, None, -1, 5],
        "unit_price": [20.0, 50.0, 100.0, 80.0],
        "customer_id": ["CUST001", "CUST002", None, "CUST004"],
        "region": ["north", "south", "east", "west"],
    })


def test_clean_dates_drops_unparseable(sample_df):
    result = clean_dates(sample_df)
    assert len(result) == 3  # the "not-a-date" row should be dropped
    assert pd.api.types.is_datetime64_any_dtype(result["order_date"])


def test_standardize_text_title_case(sample_df):
    df = clean_dates(sample_df)
    result = standardize_text(df)
    assert "Mouse" in result["product_name"].values
    assert "Keyboard" in result["product_name"].values


def test_handle_missing_values_drops_nulls(sample_df):
    df = clean_dates(sample_df)
    result = handle_missing_values(df)
    assert result["customer_id"].isnull().sum() == 0
    assert result["quantity"].isnull().sum() == 0


def test_remove_invalid_rows_drops_negative_quantity(sample_df):
    df = clean_dates(sample_df)
    df = handle_missing_values(df)
    result = remove_invalid_rows(df)
    assert (result["quantity"] > 0).all()


def test_add_calculated_columns_total_price(sample_df):
    df = clean_dates(sample_df)
    df = handle_missing_values(df)
    df = remove_invalid_rows(df)
    result = add_calculated_columns(df)
    expected = result["quantity"] * result["unit_price"]
    assert (result["total_price"] == expected.round(2)).all()


def test_remove_duplicates():
    df = pd.DataFrame({"a": [1, 1, 2], "b": [1, 1, 2]})
    result = remove_duplicates(df)
    assert len(result) == 2
