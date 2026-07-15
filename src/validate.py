"""
Phase 9 - Validate
Catches silent bugs in transform.py before bad data reaches the database.
If any check fails, the pipeline should stop — never load unvalidated data.
"""
import pandas as pd


class ValidationError(Exception):
    pass


def validate_data(df: pd.DataFrame) -> None:
    """Run a series of assertions. Raises ValidationError on failure."""

    if len(df) == 0:
        raise ValidationError("DataFrame is empty after transform - check your filters")

    required_cols = {"order_id", "order_date", "product_name", "quantity",
                      "unit_price", "customer_id", "region", "total_price"}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        raise ValidationError(f"Missing expected columns: {missing_cols}")

    null_counts = df[list(required_cols)].isnull().sum()
    if null_counts.sum() > 0:
        raise ValidationError(f"Found unexpected nulls:\n{null_counts[null_counts > 0]}")

    if (df["quantity"] <= 0).any():
        raise ValidationError("Found non-positive quantity values after cleaning")

    if (df["total_price"] != (df["quantity"] * df["unit_price"]).round(2)).any():
        raise ValidationError("total_price does not match quantity * unit_price")

    if df.duplicated().sum() > 0:
        raise ValidationError("Duplicate rows still present after cleaning")

    print(f"✅ Validation passed: {len(df)} rows, all checks OK")


if __name__ == "__main__":
    from extract import extract_data
    from transform import transform_pipeline

    df = extract_data("data/raw/sales_data.csv")
    clean_df = transform_pipeline(df)
    validate_data(clean_df)
