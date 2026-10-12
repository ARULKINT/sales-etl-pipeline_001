"""
Configuration module for the Sales Data ETL Pipeline.

Provides centralized path resolution, database configuration, logging settings,
and pipeline business constants. Ensures paths work consistently across all operating
systems and working directories.
"""
from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import List, Set


# Project root directory (parent of src/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Standard Directory Structure
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SQL_DIR = PROJECT_ROOT / "sql"
DOCS_DIR = PROJECT_ROOT / "docs"
REPORTS_DIR = PROJECT_ROOT / "reports"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, SQL_DIR, DOCS_DIR, REPORTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


@dataclass
class PipelineConfig:
    """ETL Pipeline Configuration settings."""
    
    # File Paths
    raw_file_path: Path = RAW_DATA_DIR / "sales_data.csv"
    processed_db_path: Path = PROCESSED_DATA_DIR / "sales.db"
    sql_queries_path: Path = SQL_DIR / "queries.sql"
    log_file_path: Path = PROJECT_ROOT / "pipeline.log"
    reports_output_dir: Path = REPORTS_DIR
    
    # Database Settings
    sales_table_name: str = "sales"
    audit_table_name: str = "etl_pipeline_audit"
    
    # Required raw and cleaned columns
    required_raw_columns: Set[str] = field(default_factory=lambda: {
        "order_id", "order_date", "product_name", "quantity", 
        "unit_price", "customer_id", "region"
    })
    
    required_clean_columns: Set[str] = field(default_factory=lambda: {
        "order_id", "order_date", "product_name", "quantity", 
        "unit_price", "customer_id", "region", "total_price", 
        "order_month", "order_year", "order_quarter", "day_of_week"
    })
    
    # Business Rules & Validation Thresholds
    min_quantity: int = 1
    min_unit_price: float = 0.01
    customer_id_pattern: str = r"^CUST\d{3}$"
    order_id_pattern: str = r"^ORD\d{4}$"
    
    # Known acronyms for text normalization
    known_acronyms: List[str] = field(default_factory=lambda: ["USB"])

    @property
    def db_connection_url(self) -> str:
        """SQLAlchemy connection string for SQLite."""
        # Convert path to posix standard format for SQLite URI
        resolved_path = self.processed_db_path.resolve().as_posix()
        return f"sqlite:///{resolved_path}"


# Default singleton config instance
default_config = PipelineConfig()
