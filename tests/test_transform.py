"""
Unit tests for the Transform module (src/transform.py).
"""
import os
import sys
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from transform import (
    clean_dates, standardize_text, handle_missing_values,
    remove_invalid_rows, remove_duplicates, cast_data_types,
    add_calculated_columns, transform_pipeline
)


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "order_id": ["ORD1", "ORD2", "ORD3", "ORD4"],
        "order_date": ["2024-01-05", "15/01/2024", "01-20-2024", "not-a-date"],
        "product_name": ["mouse", "KEYBOARD", " usb cable ", "webcam"],
        "quantity": [2, None, -1, 5],
        "unit_price": [20.0, 50.0, 100.0, 80.0],
        "customer_id": ["cust001", "CUST002", None, "CUST004"],
        "region": ["north", "south", "east", "west"],
    })


def test_clean_dates_drops_unparseable(sample_df):
    result = clean_dates(sample_df)
    assert len(result) == 3  # "not-a-date" row dropped
    assert pd.api.types.is_datetime64_any_dtype(result["order_date"])


def test_standardize_text_casing_and_acronyms(sample_df):
    df = clean_dates(sample_df)
    result = standardize_text(df)
    assert "Mouse" in result["product_name"].values
    assert "Keyboard" in result["product_name"].values
    assert "USB Cable" in result["product_name"].values  # Acronym preservation
    assert "CUST001" in result["customer_id"].values    # Customer ID uppercase


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


def test_cast_data_types(sample_df):
    df = clean_dates(sample_df)
    df = handle_missing_values(df)
    df = remove_invalid_rows(df)
    result = cast_data_types(df)
    assert pd.api.types.is_integer_dtype(result["quantity"])
    assert pd.api.types.is_float_dtype(result["unit_price"])


def test_add_calculated_columns(sample_df):
    df = clean_dates(sample_df)
    df = handle_missing_values(df)
    df = remove_invalid_rows(df)
    result = add_calculated_columns(df)
    expected_total = (result["quantity"] * result["unit_price"]).round(2)
    assert (result["total_price"] == expected_total).all()
    assert "order_month" in result.columns
    assert "order_year" in result.columns
    assert "order_quarter" in result.columns
    assert "day_of_week" in result.columns


def test_remove_duplicates():
    df = pd.DataFrame({
        "order_id": ["ORD1", "ORD1", "ORD2"],
        "quantity": [1, 1, 2],
        "unit_price": [10.0, 10.0, 20.0]
    })
    result = remove_duplicates(df)
    assert len(result) == 2
    assert result["order_id"].tolist() == ["ORD1", "ORD2"]


def test_transform_pipeline_full_integration(sample_df):
    clean = transform_pipeline(sample_df)
    assert len(clean) >= 1
    assert "total_price" in clean.columns
    assert clean["quantity"].dtype == "int64"
