"""
Phase 6: Analytics Module

Executes business analytical queries against the processed SQL database,
computes executive KPIs, and exports structured analysis tables.
"""
import logging
from pathlib import Path
import re
from typing import Any, Dict, List, Optional
import pandas as pd
from sqlalchemy import Engine, text

try:
    from .config import default_config, PipelineConfig
    from .load import get_engine
except (ImportError, ValueError):
    from config import default_config, PipelineConfig
    from load import get_engine

logger = logging.getLogger(__name__)


def parse_sql_queries(sql_file_path: Optional[Path] = None, config: Optional[PipelineConfig] = None) -> List[Dict[str, str]]:
    """
    Parses individual queries and their comments/titles from a .sql file.
    """
    cfg = config or default_config
    file_path = sql_file_path or cfg.sql_queries_path

    if not file_path.exists():
        raise FileNotFoundError(f"SQL queries file not found at: {file_path}")

    content = file_path.read_text(encoding="utf-8")
    raw_statements = [s.strip() for s in content.split(";") if s.strip()]
    parsed_queries = []

    for idx, stmt in enumerate(raw_statements, start=1):
        lines = stmt.splitlines()
        comments = []
        sql_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("--"):
                clean_comment = stripped.lstrip("-").strip()
                # Skip divider lines and generic phase comments
                if clean_comment and not clean_comment.startswith("=") and not clean_comment.startswith("Sales Data"):
                    comments.append(clean_comment)
            else:
                sql_lines.append(line)

        title = comments[0] if comments else f"Query {idx}"
        sql_text = "\n".join(sql_lines).strip()

        if sql_text:
            parsed_queries.append({
                "id": f"Q{idx}",
                "title": title,
                "sql": sql_text
            })

    logger.debug(f"Parsed {len(parsed_queries)} queries from {file_path.name}")
    return parsed_queries


def execute_queries(
    engine: Optional[Engine] = None,
    queries: Optional[List[Dict[str, str]]] = None,
    config: Optional[PipelineConfig] = None
) -> Dict[str, pd.DataFrame]:
    """
    Executes each parsed SQL query against the database and returns a dictionary of DataFrames.
    """
    cfg = config or default_config
    eng = engine or get_engine(config=cfg)
    query_list = queries or parse_sql_queries(config=cfg)
    results: Dict[str, pd.DataFrame] = {}

    with eng.connect() as conn:
        for q in query_list:
            q_id = q["id"]
            title = q["title"]
            try:
                df = pd.read_sql_query(text(q["sql"]), conn)
                df.attrs["title"] = title
                results[title] = df
                logger.info(f"Executed analytical query '{title}': returned {len(df)} rows")
            except Exception as e:
                logger.error(f"Error executing query '{title}': {e}")
                raise e

    return results


def compute_executive_kpis(
    engine: Optional[Engine] = None,
    config: Optional[PipelineConfig] = None
) -> Dict[str, Any]:
    """
    Calculates high-level executive business performance KPIs directly from the sales database.
    """
    cfg = config or default_config
    eng = engine or get_engine(config=cfg)

    kpi_query = f"""
    SELECT
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(DISTINCT customer_id) AS active_customers,
        SUM(quantity) AS total_units_sold,
        ROUND(SUM(total_price), 2) AS total_revenue,
        ROUND(AVG(total_price), 2) AS avg_order_value,
        ROUND(MIN(total_price), 2) AS min_order_value,
        ROUND(MAX(total_price), 2) AS max_order_value
    FROM {cfg.sales_table_name};
    """

    top_prod_query = f"""
    SELECT product_name, ROUND(SUM(total_price), 2) AS revenue
    FROM {cfg.sales_table_name}
    GROUP BY product_name
    ORDER BY revenue DESC
    LIMIT 1;
    """

    top_region_query = f"""
    SELECT region, ROUND(SUM(total_price), 2) AS revenue
    FROM {cfg.sales_table_name}
    GROUP BY region
    ORDER BY revenue DESC
    LIMIT 1;
    """

    with eng.connect() as conn:
        kpi_row = conn.execute(text(kpi_query)).mappings().first()
        top_prod_row = conn.execute(text(top_prod_query)).mappings().first()
        top_region_row = conn.execute(text(top_region_query)).mappings().first()

    return {
        "total_revenue": float(kpi_row["total_revenue"] or 0),
        "total_orders": int(kpi_row["total_orders"] or 0),
        "active_customers": int(kpi_row["active_customers"] or 0),
        "total_units_sold": int(kpi_row["total_units_sold"] or 0),
        "avg_order_value": float(kpi_row["avg_order_value"] or 0),
        "min_order_value": float(kpi_row["min_order_value"] or 0),
        "max_order_value": float(kpi_row["max_order_value"] or 0),
        "top_product": str(top_prod_row["product_name"] if top_prod_row else "N/A"),
        "top_product_revenue": float(top_prod_row["revenue"] if top_prod_row else 0.0),
        "top_region": str(top_region_row["region"] if top_region_row else "N/A"),
        "top_region_revenue": float(top_region_row["revenue"] if top_region_row else 0.0),
    }


def export_query_results_to_csv(
    results: Dict[str, pd.DataFrame],
    output_dir: Optional[Path] = None,
    config: Optional[PipelineConfig] = None
) -> List[Path]:
    """
    Exports analytics query DataFrames to individual CSV files for downstream reporting.
    """
    cfg = config or default_config
    target_dir = output_dir or (cfg.processed_db_path.parent / "analytics_exports")
    target_dir.mkdir(parents=True, exist_ok=True)
    exported_files = []

    for title, df in results.items():
        clean_name = re.sub(r"[^\w\s-]", "", title).strip().lower().replace(" ", "_")
        csv_file = target_dir / f"{clean_name}.csv"
        df.to_csv(csv_file, index=False)
        exported_files.append(csv_file)
        logger.info(f"Saved analytics export: {csv_file.name}")

    return exported_files
