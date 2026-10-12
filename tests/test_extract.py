"""
Unit tests for the Extract module (src/extract.py).
"""
import os
from pathlib import Path
import sys
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from extract import extract_data, extract_multiple
from config import PipelineConfig


@pytest.fixture
def temp_csv_dir(tmp_path):
    """Creates temporary valid and invalid CSV files for testing."""
    valid_csv = tmp_path / "valid_sales.csv"
    valid_df = pd.DataFrame({
        "order_id": ["ORD0001", "ORD0002"],
        "order_date": ["2024-01-01", "2024-01-02"],
        "product_name": ["Laptop", "Mouse"],
        "quantity": [1, 2],
        "unit_price": [1000.0, 50.0],
        "customer_id": ["CUST001", "CUST002"],
        "region": ["North", "South"]
    })
    valid_df.to_csv(valid_csv, index=False)

    empty_csv = tmp_path / "empty.csv"
    empty_csv.write_text("")

    missing_cols_csv = tmp_path / "missing_cols.csv"
    pd.DataFrame({"foo": [1, 2], "bar": [3, 4]}).to_csv(missing_cols_csv, index=False)

    return {
        "dir": tmp_path,
        "valid": valid_csv,
        "empty": empty_csv,
        "missing_cols": missing_cols_csv
    }


def test_extract_valid_csv(temp_csv_dir):
    df = extract_data(file_path=temp_csv_dir["valid"])
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "order_id" in df.columns


def test_extract_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        extract_data(file_path="nonexistent_path_to_file.csv")


def test_extract_empty_csv(temp_csv_dir):
    with pytest.raises(ValueError, match="empty"):
        extract_data(file_path=temp_csv_dir["empty"])


def test_extract_missing_required_columns(temp_csv_dir):
    with pytest.raises(ValueError, match="missing required columns"):
        extract_data(file_path=temp_csv_dir["missing_cols"])


def test_extract_multiple_csvs(temp_csv_dir):
    # Create another valid csv
    valid2 = temp_csv_dir["dir"] / "valid_sales_2.csv"
    df2 = pd.DataFrame({
        "order_id": ["ORD0003"],
        "order_date": ["2024-01-03"],
        "product_name": ["Keyboard"],
        "quantity": [3],
        "unit_price": [75.0],
        "customer_id": ["CUST003"],
        "region": ["East"]
    })
    df2.to_csv(valid2, index=False)

    combined = extract_multiple(folder_path=temp_csv_dir["dir"], pattern="valid_*.csv")
    assert len(combined) == 3
    assert set(combined["order_id"]) == {"ORD0001", "ORD0002", "ORD0003"}
