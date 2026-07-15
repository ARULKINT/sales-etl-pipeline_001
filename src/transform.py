"""
Phase 8 - Transform
Every cleaning decision here should be explainable in an interview:
WHY did we drop/fill this, not just what we did.
"""
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def clean_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Parse mixed date formats into a single standard format."""
    df = df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"], format="mixed", dayfirst=False, errors="coerce")
    bad_dates = df["order_date"].isnull().sum()
    if bad_dates:
        logger.warning(f"{bad_dates} rows had unparseable dates -> dropped")
    df = df.dropna(subset=["order_date"])
    return df


def standardize_text(df: pd.DataFrame) -> pd.DataFrame:
    """Fix inconsistent casing in text columns."""
    df = df.copy()
    df["product_name"] = df["product_name"].str.strip().str.title()
    df["region"] = df["region"].str.strip().str.title()
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Business rule: a sale with no customer_id can't be attributed to
    anyone, so we drop it. Missing quantity we treat as data entry
    error and drop too (can't safely guess quantity sold).
    """
    df = df.copy()
    before = len(df)
    df = df.dropna(subset=["customer_id", "quantity"])
    logger.info(f"Dropped {before - len(df)} rows with missing customer_id/quantity")
    return df


def remove_invalid_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Business rule: quantity must be positive - negative/zero is bad data."""
    df = df.copy()
    before = len(df)
    df = df[df["quantity"] > 0]
    logger.info(f"Dropped {before - len(df)} rows with invalid quantity")
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    before = len(df)
    df = df.drop_duplicates()
    logger.info(f"Dropped {before - len(df)} duplicate rows")
    return df


def add_calculated_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived columns the business actually asks about."""
    df = df.copy()
    df["total_price"] = (df["quantity"] * df["unit_price"]).round(2)
    df["order_month"] = df["order_date"].dt.to_period("M").astype(str)
    return df


def transform_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """Run all transform steps in order."""
    df = clean_dates(df)
    df = standardize_text(df)
    df = handle_missing_values(df)
    df = remove_invalid_rows(df)
    df = remove_duplicates(df)
    df = add_calculated_columns(df)
    return df.reset_index(drop=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from extract import extract_data
    df = extract_data("data/raw/sales_data.csv")
    clean_df = transform_pipeline(df)
    print(clean_df.head())
    print(f"\nFinal shape: {clean_df.shape}")
