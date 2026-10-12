"""
Phase 4: Validate Module

Provides automated data validation assertions and sanity checks before loading into SQLite.
Guarantees zero dirty or corrupted records reach production tables.
Cross-platform safe (Windows, Linux, macOS).
"""
import logging
import re
from typing import Dict, Optional
import numpy as np
import pandas as pd

try:
    from .config import default_config, PipelineConfig
except (ImportError, ValueError):
    from config import default_config, PipelineConfig

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when data fails quality, schema, or integrity assertions."""
    pass


def validate_data(df: pd.DataFrame, config: Optional[PipelineConfig] = None) -> Dict[str, bool]:
    """
    Runs a comprehensive battery of data validation checks against the cleaned DataFrame.

    Parameters:
        df: Cleaned Pandas DataFrame.
        config: Optional PipelineConfig instance.

    Returns:
        Dict[str, bool]: Summary of passed validation checks.

    Raises:
        ValidationError: If any assertions fail.
    """
    cfg = config or default_config
    check_results: Dict[str, bool] = {}

    # Check 1: Non-empty DataFrame
    if len(df) == 0:
        raise ValidationError("Cleaned DataFrame is empty (0 rows). Check transformation filters.")
    check_results["non_empty_check"] = True

    # Check 2: Schema completeness
    required_cols = cfg.required_clean_columns
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        raise ValidationError(f"Missing required columns in cleaned data: {sorted(list(missing_cols))}")
    check_results["schema_completeness_check"] = True

    # Check 3: Zero nulls in mandatory columns
    null_counts = df[list(required_cols)].isnull().sum()
    if null_counts.sum() > 0:
        violating_cols = null_counts[null_counts > 0].to_dict()
        raise ValidationError(f"Found unexpected null values in cleaned dataset: {violating_cols}")
    check_results["null_values_check"] = True

    # Check 4: Positive quantities
    if (df["quantity"] < cfg.min_quantity).any():
        non_positive_count = int((df["quantity"] < cfg.min_quantity).sum())
        raise ValidationError(f"Found {non_positive_count} records with quantity < {cfg.min_quantity}")
    check_results["positive_quantity_check"] = True

    # Check 5: Positive unit prices
    if (df["unit_price"] < cfg.min_unit_price).any():
        invalid_price_count = int((df["unit_price"] < cfg.min_unit_price).sum())
        raise ValidationError(f"Found {invalid_price_count} records with unit price < {cfg.min_unit_price}")
    check_results["positive_price_check"] = True

    # Check 6: Calculation integrity (total_price == quantity * unit_price)
    expected_totals = (df["quantity"] * df["unit_price"]).round(2)
    # Using np.isclose to eliminate floating-point precision discrepancies
    discrepancies = ~np.isclose(df["total_price"], expected_totals, atol=0.01)
    if discrepancies.any():
        mismatch_count = int(discrepancies.sum())
        sample_mismatch = df[discrepancies][["order_id", "quantity", "unit_price", "total_price"]].head(3)
        raise ValidationError(
            f"Calculation mismatch in {mismatch_count} rows between total_price and (quantity * unit_price):\n{sample_mismatch}"
        )
    check_results["calculation_integrity_check"] = True

    # Check 7: No duplicate order IDs
    duplicate_orders = int(df["order_id"].duplicated().sum())
    if duplicate_orders > 0:
        raise ValidationError(f"Found {duplicate_orders} duplicate order_id records after cleaning")
    check_results["uniqueness_check"] = True

    # Check 8: Customer ID format
    if cfg.customer_id_pattern:
        invalid_cust = ~df["customer_id"].str.match(cfg.customer_id_pattern)
        if invalid_cust.any():
            invalid_samples = df[invalid_cust]["customer_id"].head(5).tolist()
            raise ValidationError(f"Customer IDs do not match required pattern '{cfg.customer_id_pattern}': {invalid_samples}")
    check_results["format_pattern_check"] = True

    # Safe logging without non-ASCII emoji that crash on Windows consoles
    msg = f"[VALIDATION PASSED] All {len(check_results)} assertions passed successfully on {len(df):,} records."
    logger.info(msg)
    print(f"=== {msg} ===")

    return check_results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    from extract import extract_data
    from transform import transform_pipeline

    raw_df = extract_data()
    clean_df = transform_pipeline(raw_df)
    validate_data(clean_df)
