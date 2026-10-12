"""
Phase 7: Reporting Module

Generates publication-ready Executive Markdown and HTML Pipeline & Analytics Reports.
Transforms database queries and profiling data into structured executive summaries.
Zero external formatting dependencies (no tabulate requirement).
"""
from datetime import datetime
import logging
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd

try:
    from .config import default_config, PipelineConfig
except (ImportError, ValueError):
    from config import default_config, PipelineConfig

logger = logging.getLogger(__name__)


def _df_to_markdown_table(df: pd.DataFrame) -> str:
    """Formats a pandas DataFrame as a clean GitHub Markdown table."""
    headers = [str(c) for c in df.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |"
    ]
    for _, row in df.iterrows():
        row_vals = []
        for col in df.columns:
            val = row[col]
            if isinstance(val, float):
                row_vals.append(f"{val:,.2f}" if "price" in col or "revenue" in col or "spent" in col or "value" in col else str(val))
            else:
                row_vals.append(str(val))
        lines.append("| " + " | ".join(row_vals) + " |")
    return "\n".join(lines)


def generate_markdown_report(
    run_id: str,
    raw_profile: Dict[str, Any],
    clean_profile: Dict[str, Any],
    kpis: Dict[str, Any],
    query_results: Dict[str, pd.DataFrame],
    duration_sec: float,
    config: Optional[PipelineConfig] = None
) -> str:
    """
    Generates a comprehensive Markdown report string with tables and executive metrics.
    """
    cfg = config or default_config
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    raw_rows = raw_profile["row_count"]
    clean_rows = clean_profile["row_count"]
    dropped_rows = raw_rows - clean_rows
    retention_pct = round((clean_rows / raw_rows * 100), 2) if raw_rows > 0 else 0.0

    md = []
    md.append("# Sales ETL Pipeline — Executive & Data Quality Report")
    md.append(f"\n> **Run ID:** `{run_id}` | **Generated:** `{timestamp}` | **Execution Time:** `{duration_sec:.2f}s` | **Status:** `SUCCESS`\n")
    
    # 1. Executive Business KPIs
    md.append("## 1. Executive Business KPIs")
    md.append("| Metric | Value | Business Description |")
    md.append("| :--- | :--- | :--- |")
    md.append(f"| **Total Revenue** | **${kpis.get('total_revenue', 0.0):,.2f}** | Cumulative gross sales across cleaned transactions |")
    md.append(f"| **Total Orders** | **{kpis.get('total_orders', 0):,}** | Total distinct validated orders processed |")
    md.append(f"| **Active Customers** | **{kpis.get('active_customers', 0):,}** | Unique customer accounts with completed purchases |")
    md.append(f"| **Total Units Sold** | **{kpis.get('total_units_sold', 0):,}** | Physical products shipped |")
    md.append(f"| **Average Order Value (AOV)** | **${kpis.get('avg_order_value', 0.0):,.2f}** | Mean revenue generated per transaction |")
    md.append(f"| **Top Product by Revenue** | **{kpis.get('top_product', 'N/A')}** (${kpis.get('top_product_revenue', 0.0):,.2f}) | Highest grossing merchandise |")
    md.append(f"| **Top Region by Revenue** | **{kpis.get('top_region', 'N/A')}** (${kpis.get('top_region_revenue', 0.0):,.2f}) | Primary regional revenue driver |")
    md.append("")

    # 2. Pipeline Execution & Data Quality Audit
    md.append("## 2. Data Cleaning & Integrity Audit")
    md.append("| Pipeline Stage | Metric | Count / Value | Impact / Rule |")
    md.append("| :--- | :--- | :--- | :--- |")
    md.append(f"| **Extract** | Raw Input Rows | {raw_rows:,} | Extracted from raw CSV source |")
    md.append(f"| **Profiling** | Raw Missing Fields | {raw_profile.get('total_null_cells', 0):,} cells | Unattributed customer IDs & missing quantities |")
    md.append(f"| **Profiling** | Raw Duplicate Rows | {raw_profile.get('duplicate_rows', 0):,} rows | Repeated transaction submissions |")
    md.append(f"| **Profiling** | Raw Anomaly Quantities | {raw_profile.get('negative_quantity_rows', 0):,} rows | Non-positive / negative values |")
    md.append(f"| **Transform** | Total Rows Dropped | {dropped_rows:,} rows | Dropped corrupted, unparseable, or duplicate data |")
    md.append(f"| **Validate** | Final Clean Rows | {clean_rows:,} rows | Passed all 8 strict data validation assertions |")
    md.append(f"| **Quality Score** | Data Retention Rate | **{retention_pct}%** | Safe, reliable data loading threshold |")
    md.append("")

    # 3. SQL Analytics Query Results
    md.append("## 3. SQL Analytics Findings")
    for title, df in query_results.items():
        md.append(f"### {title}")
        md.append(_df_to_markdown_table(df))
        md.append("")

    # 4. Strategic Business Insights & Recommendations
    md.append("## 4. Strategic Business Insights")
    md.append(f"- **Product Focus:** `{kpis.get('top_product')}` is leading sales volume. Consider inventory prioritization and targeted bundling.")
    md.append(f"- **Regional Growth:** `{kpis.get('top_region')}` accounts for the highest regional revenue share. Explore regional promotion strategies for lower-volume territories.")
    md.append(f"- **Data Quality Assurance:** {dropped_rows} erroneous records were prevented from entering the analytics warehouse, ensuring reporting integrity.")
    md.append("")
    md.append("---")
    md.append("*Report automatically compiled by the Sales Data ETL Pipeline.*")

    return "\n".join(md)


def save_reports(
    report_content_md: str,
    output_dir: Optional[Path] = None,
    config: Optional[PipelineConfig] = None
) -> Dict[str, Path]:
    """
    Saves generated report to Markdown and HTML formats.
    """
    cfg = config or default_config
    target_dir = output_dir or cfg.reports_output_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    md_path = target_dir / "pipeline_execution_report.md"
    md_path.write_text(report_content_md, encoding="utf-8")
    logger.info(f"Saved Markdown report to: {md_path}")

    # Generate lightweight HTML version
    html_path = target_dir / "pipeline_execution_report.html"
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sales ETL Pipeline - Executive Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 1000px; margin: 40px auto; padding: 0 24px; color: #1f2937; background-color: #f9fafb; }}
        .card {{ background: #ffffff; padding: 36px; border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05); }}
        h1 {{ color: #111827; border-bottom: 2px solid #e5e7eb; padding-bottom: 12px; margin-top: 0; }}
        h2 {{ color: #1f2937; margin-top: 32px; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px; }}
        h3 {{ color: #374151; margin-top: 24px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 18px 0; font-size: 14px; }}
        th, td {{ border: 1px solid #e5e7eb; padding: 10px 14px; text-align: left; }}
        th {{ background-color: #f3f4f6; font-weight: 600; color: #111827; }}
        tr:nth-child(even) {{ background-color: #f9fafb; }}
        code {{ background: #f3f4f6; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; color: #dc2626; }}
        blockquote {{ border-left: 4px solid #2563eb; margin: 0 0 20px 0; padding: 12px 18px; background: #eff6ff; color: #1e40af; border-radius: 0 8px 8px 0; }}
        ul {{ padding-left: 20px; }}
        li {{ margin-bottom: 8px; }}
    </style>
</head>
<body>
    <div class="card">
        <pre style="white-space: pre-wrap; font-family: inherit;">{report_content_md}</pre>
    </div>
</body>
</html>"""
    html_path.write_text(html_content, encoding="utf-8")
    logger.info(f"Saved HTML report to: {html_path}")

    return {"markdown": md_path, "html": html_path}
