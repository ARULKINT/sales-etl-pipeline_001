"""
Phase 7 - Data Profiling
We measure the mess BEFORE cleaning it, so we know exactly what
transform.py needs to fix, and can prove the fix worked afterward.
"""
import pandas as pd


def profile_data(df: pd.DataFrame) -> dict:
    """Return a dict summary of data quality issues."""
    report = {
        "row_count": len(df),
        "column_count": len(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "null_counts": df.isnull().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
        "negative_quantity_rows": int((df["quantity"] < 0).sum()) if "quantity" in df else None,
    }
    return report


def print_report(report: dict) -> None:
    print("=" * 50)
    print("DATA PROFILING REPORT")
    print("=" * 50)
    print(f"Rows: {report['row_count']}, Columns: {report['column_count']}")
    print("\nNull counts per column:")
    for col, count in report["null_counts"].items():
        if count > 0:
            print(f"  {col}: {count}")
    print(f"\nDuplicate rows: {report['duplicate_rows']}")
    print(f"Negative quantity rows: {report['negative_quantity_rows']}")
    print("=" * 50)


if __name__ == "__main__":
    from extract import extract_data
    df = extract_data("data/raw/sales_data.csv")
    report = profile_data(df)
    print_report(report)
