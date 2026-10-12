"""
Sales Data ETL Pipeline Package.

A production-grade, modular Extract-Transform-Load (ETL) pipeline providing:
- Data extraction from heterogeneous CSV sources with multi-encoding fallback.
- Empirical pre-cleaning data profiling and quality measurement.
- Domain-driven transformation, normalization, and feature enrichment.
- Strict pre-load validation assertions preventing data corruption.
- Persistent loading into SQLite with analytical indexing and execution auditing.
- Automated SQL analytics query execution and executive KPI computation.
- Automated executive reporting in GitHub Markdown and responsive HTML.
"""

from .config import PipelineConfig, default_config
from .extract import extract_data, extract_multiple
from .profile_data import profile_data, compare_profiles, print_report
from .transform import transform_pipeline
from .validate import validate_data, ValidationError
from .load import load_data, verify_load, log_pipeline_audit, get_engine
from .analytics import execute_queries, compute_executive_kpis, parse_sql_queries
from .report import generate_markdown_report, save_reports

__version__ = "2.0.0"
__all__ = [
    "PipelineConfig",
    "default_config",
    "extract_data",
    "extract_multiple",
    "profile_data",
    "compare_profiles",
    "print_report",
    "transform_pipeline",
    "validate_data",
    "ValidationError",
    "load_data",
    "verify_load",
    "log_pipeline_audit",
    "get_engine",
    "execute_queries",
    "compute_executive_kpis",
    "parse_sql_queries",
    "generate_markdown_report",
    "save_reports",
]
