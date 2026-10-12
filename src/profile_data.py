"""
Phase 2: Data Profiling Module

Analyzes and measures raw data quality before transformations, and generates
comparative audit reports after data cleaning to verify data integrity.
"""
from typing import Any, Dict, Optional
import pandas as pd


def profile_data(df: pd.DataFrame, dataset_name: str = "Raw Sales Data") -> Dict[str, Any]:
    """
    Computes an extensive data quality and statistical profile of a DataFrame.

    Parameters:
        df: Pandas DataFrame to profile.
        dataset_name: Label for the profile report.

    Returns:
        Dict[str, Any]: Comprehensive profiling metrics.
    """
    row_count = len(df)
    col_count = len(df.columns)
    
    # Missing values profiling
    null_counts = df.isnull().sum().to_dict()
    null_percentages = {
        col: round((count / row_count) * 100, 2) if row_count > 0 else 0.0
        for col, count in null_counts.items()
    }

    # Duplicates profiling
    duplicate_rows = int(df.duplicated().sum())
    duplicate_orders = int(df["order_id"].duplicated().sum()) if "order_id" in df else 0

    # Numeric range metrics
    numeric_stats: Dict[str, Dict[str, float]] = {}
    for col in ["quantity", "unit_price", "total_price"]:
        if col in df and pd.api.types.is_numeric_dtype(df[col]):
            series = df[col].dropna()
            if len(series) > 0:
                numeric_stats[col] = {
                    "min": float(series.min()),
                    "max": float(series.max()),
                    "mean": round(float(series.mean()), 2),
                    "median": round(float(series.median()), 2)
                }

    # Domain-specific anomaly counters
    negative_quantities = int((df["quantity"] < 0).sum()) if "quantity" in df and pd.api.types.is_numeric_dtype(df["quantity"]) else 0
    zero_quantities = int((df["quantity"] == 0).sum()) if "quantity" in df and pd.api.types.is_numeric_dtype(df["quantity"]) else 0

    return {
        "dataset_name": dataset_name,
        "row_count": row_count,
        "column_count": col_count,
        "columns": list(df.columns),
        "dtypes": {k: str(v) for k, v in df.dtypes.items()},
        "null_counts": null_counts,
        "null_percentages": null_percentages,
        "total_null_cells": int(df.isnull().sum().sum()),
        "duplicate_rows": duplicate_rows,
        "duplicate_orders": duplicate_orders,
        "negative_quantity_rows": negative_quantities,
        "zero_quantity_rows": zero_quantities,
        "numeric_stats": numeric_stats,
    }


def compare_profiles(raw_report: Dict[str, Any], clean_report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compares pre-clean and post-clean profiles to quantify data cleaning impact.
    """
    raw_rows = raw_report["row_count"]
    clean_rows = clean_report["row_count"]
    dropped_rows = raw_rows - clean_rows
    retention_rate = round((clean_rows / raw_rows * 100), 2) if raw_rows > 0 else 0.0

    return {
        "raw_rows": raw_rows,
        "clean_rows": clean_rows,
        "dropped_rows": dropped_rows,
        "retention_rate_pct": retention_rate,
        "raw_duplicates": raw_report["duplicate_rows"],
        "clean_duplicates": clean_report["duplicate_rows"],
        "raw_null_cells": raw_report["total_null_cells"],
        "clean_null_cells": clean_report["total_null_cells"],
        "raw_negative_qty": raw_report["negative_quantity_rows"],
        "clean_negative_qty": clean_report["negative_quantity_rows"],
    }


def format_report_console(report: Dict[str, Any]) -> str:
    """Format report cleanly for console without non-ASCII characters."""
    lines = [
        "=" * 60,
        f"DATA PROFILING REPORT: {report.get('dataset_name', 'Dataset')}",
        "=" * 60,
        f"Rows: {report['row_count']:,} | Columns: {report['column_count']}",
        f"Duplicate Rows: {report['duplicate_rows']} | Duplicate Orders: {report['duplicate_orders']}",
        f"Negative Quantities: {report['negative_quantity_rows']} | Zero Quantities: {report['zero_quantity_rows']}",
        "-" * 60,
        "Null Values per Column:"
    ]
    for col, count in report["null_counts"].items():
        pct = report["null_percentages"].get(col, 0.0)
        status = "[CLEAN]" if count == 0 else f"[MISSING: {count} ({pct}%)]"
        lines.append(f"  * {col:<15}: {status}")

    if report.get("numeric_stats"):
        lines.append("-" * 60)
        lines.append("Numeric Column Summary:")
        for col, stats in report["numeric_stats"].items():
            lines.append(f"  * {col}: Min={stats['min']}, Max={stats['max']}, Mean={stats['mean']}, Median={stats['median']}")

    lines.append("=" * 60)
    return "\n".join(lines)


def print_report(report: Dict[str, Any]) -> None:
    """Prints the console-safe data profiling report."""
    print(format_report_console(report))


if __name__ == "__main__":
    from extract import extract_data
    df_raw = extract_data()
    rep = profile_data(df_raw, "Raw Sales Input")
    print_report(rep)
