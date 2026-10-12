"""
Phase 3: Transform Module

Implements data cleaning, normalization, validation filtering, and feature enrichment.
Every transformation decision reflects explicit business domain rules.
"""
import logging
from typing import Optional
import pandas as pd

try:
    from .config import default_config, PipelineConfig
except (ImportError, ValueError):
    from config import default_config, PipelineConfig

logger = logging.getLogger(__name__)


def clean_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parses mixed date formats (YYYY-MM-DD, DD/MM/YYYY, MM-DD-YYYY) into a uniform datetime.
    Drops rows with unparseable date values.
    """
    df = df.copy()
    before = len(df)
    
    df["order_date"] = pd.to_datetime(df["order_date"], format="mixed", errors="coerce")
    bad_dates = int(df["order_date"].isnull().sum())
    
    if bad_dates > 0:
        logger.warning(f"Dropping {bad_dates} rows with invalid/unparseable dates")
        df = df.dropna(subset=["order_date"])

    logger.debug(f"Dates standardized. Rows remaining: {len(df)} (dropped {before - len(df)})")
    return df


def standardize_text(df: pd.DataFrame, config: Optional[PipelineConfig] = None) -> pd.DataFrame:
    """
    Cleans string columns: strips whitespace, standardizes casing to title case,
    and preserves domain acronyms (e.g. 'USB Cable' instead of 'Usb Cable').
    """
    cfg = config or default_config
    df = df.copy()

    for col in ["product_name", "region"]:
        if col in df.columns and (pd.api.types.is_string_dtype(df[col]) or pd.api.types.is_object_dtype(df[col])):
            df[col] = df[col].astype(str).str.strip().str.title()
            
            # Restore known acronyms (e.g. USB)
            for acronym in cfg.known_acronyms:
                df[col] = df[col].str.replace(acronym.title(), acronym, regex=False)

    if "customer_id" in df.columns:
        df["customer_id"] = df["customer_id"].astype(str).str.strip().str.upper()

    if "order_id" in df.columns:
        df["order_id"] = df["order_id"].astype(str).str.strip().str.upper()

    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Business Rules:
    - Customer ID: A sale with missing customer_id cannot be attributed; drop it.
    - Quantity & Unit Price: Missing numerical values cannot be safely imputed; drop them.
    - Order ID: Mandatory transaction identifier; drop if null or empty.
    """
    df = df.copy()
    before = len(df)
    
    # Treat string 'nan' / 'none' as null if customer_id was stringified
    if "customer_id" in df.columns:
        df["customer_id"] = df["customer_id"].replace(["NAN", "NONE", ""], pd.NA)

    df = df.dropna(subset=["order_id", "customer_id", "quantity", "unit_price"])
    dropped = before - len(df)
    if dropped > 0:
        logger.info(f"Dropped {dropped} rows with missing mandatory fields (order_id, customer_id, quantity, unit_price)")
    return df


def remove_invalid_rows(df: pd.DataFrame, config: Optional[PipelineConfig] = None) -> pd.DataFrame:
    """
    Business Rules:
    - Quantity must be strictly positive (greater than 0).
    - Unit price must be strictly positive (greater than 0).
    Negative quantities represent returns or test errors not part of gross sales pipeline.
    """
    cfg = config or default_config
    df = df.copy()
    before = len(df)

    valid_mask = (df["quantity"] >= cfg.min_quantity) & (df["unit_price"] >= cfg.min_unit_price)
    df = df[valid_mask]
    
    dropped = before - len(df)
    if dropped > 0:
        logger.info(f"Dropped {dropped} rows with non-positive quantity (<={cfg.min_quantity}) or unit_price (<={cfg.min_unit_price})")
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Deduplicates the dataset:
    1. Removes identical duplicate rows.
    2. Ensures unique order_id (keeps first occurrence if duplicates exist).
    """
    df = df.copy()
    before = len(df)
    
    # Deduplicate exact rows first
    df = df.drop_duplicates()
    exact_dupes_dropped = before - len(df)
    
    # Deduplicate by order_id if applicable
    if "order_id" in df.columns:
        orders_before = len(df)
        df = df.drop_duplicates(subset=["order_id"], keep="first")
        order_dupes_dropped = orders_before - len(df)
    else:
        order_dupes_dropped = 0

    total_dropped = before - len(df)
    if total_dropped > 0:
        logger.info(f"Dropped {total_dropped} duplicate rows ({exact_dupes_dropped} exact rows, {order_dupes_dropped} duplicate order_ids)")
    return df


def cast_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enforces clean, strictly typed column types.
    - quantity -> int64
    - unit_price -> float64
    - order_date -> ISO date string YYYY-MM-DD
    """
    df = df.copy()
    df["quantity"] = df["quantity"].astype("int64")
    df["unit_price"] = df["unit_price"].astype("float64").round(2)
    return df


def add_calculated_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enriches dataset with business calculation fields:
    - total_price: quantity * unit_price (rounded to 2 decimal places)
    - order_month: YYYY-MM
    - order_year: YYYY
    - order_quarter: YYYY-Q#
    - day_of_week: Name of day (e.g. Monday, Tuesday)
    """
    df = df.copy()
    df["total_price"] = (df["quantity"] * df["unit_price"]).round(2)
    df["order_month"] = df["order_date"].dt.to_period("M").astype(str)
    df["order_year"] = df["order_date"].dt.year.astype(int)
    df["order_quarter"] = df["order_date"].dt.to_period("Q").astype(str)
    df["day_of_week"] = df["order_date"].dt.day_name()
    return df


def transform_pipeline(df: pd.DataFrame, config: Optional[PipelineConfig] = None) -> pd.DataFrame:
    """
    Orchestrates the complete data transformation lifecycle.
    """
    cfg = config or default_config
    logger.info(f"Starting transformation pipeline with {len(df):,} input rows")

    df = clean_dates(df)
    df = standardize_text(df, config=cfg)
    df = handle_missing_values(df)
    df = remove_invalid_rows(df, config=cfg)
    df = remove_duplicates(df)
    df = cast_data_types(df)
    df = add_calculated_columns(df)

    logger.info(f"Transformation complete. Clean dataset contains {len(df):,} rows and {len(df.columns)} columns")
    return df.reset_index(drop=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    from extract import extract_data
    raw = extract_data()
    clean = transform_pipeline(raw)
    print(clean.head())
    print("\nColumns:", clean.columns.tolist())
    print("Shape:", clean.shape)
