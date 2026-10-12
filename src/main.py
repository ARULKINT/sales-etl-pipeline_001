"""
Sales Data ETL Pipeline — Main Orchestrator

End-to-End Orchestrator:
Extract -> Profile -> Transform -> Validate -> Load -> Analytics -> Executive Report

Usage:
    python src/main.py
    python src/main.py --input data/raw/sales_data.csv --generate-report
"""
import argparse
import io
import logging
from pathlib import Path
import sys
import time
import uuid

# Ensure src/ directory and project root are in sys.path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import default_config, PipelineConfig
from extract import extract_data
from profile_data import profile_data, print_report, compare_profiles
from transform import transform_pipeline
from validate import validate_data, ValidationError
from load import load_data, verify_load, log_pipeline_audit
from analytics import execute_queries, compute_executive_kpis, export_query_results_to_csv
from report import generate_markdown_report, save_reports


def setup_logging(log_file: Path, verbose: bool = False) -> logging.Logger:
    """Configures cross-platform safe logging to both file (UTF-8) and console."""
    log_level = logging.DEBUG if verbose else logging.INFO

    # Windows-safe console stream
    stream_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        handlers=[file_handler, stream_handler],
        force=True
    )
    return logging.getLogger("sales_etl_pipeline")


def run_pipeline(
    raw_file: str = None,
    db_path: str = None,
    skip_analytics: bool = False,
    generate_report: bool = True,
    verbose: bool = False
) -> dict:
    """
    Executes the complete, modernized ETL pipeline lifecycle.
    """
    start_time = time.time()
    run_id = str(uuid.uuid4())[:8]

    # Initialize configuration
    cfg = default_config
    if raw_file:
        cfg.raw_file_path = Path(raw_file)
    if db_path:
        cfg.processed_db_path = Path(db_path)

    logger = setup_logging(cfg.log_file_path, verbose=verbose)
    logger.info(f"=== ETL PIPELINE STARTED [Run ID: {run_id}] ===")
    logger.info(f"Source file: {cfg.raw_file_path}")
    logger.info(f"Target database: {cfg.processed_db_path}")

    try:
        # Stage 1: Extract
        s1_start = time.time()
        logger.info("Stage 1/7: Extracting raw data...")
        raw_df = extract_data(file_path=cfg.raw_file_path, config=cfg)
        s1_duration = time.time() - s1_start
        logger.info(f"Stage 1/7 completed in {s1_duration:.2f}s ({len(raw_df):,} raw records)")

        # Stage 2: Profile (Before Cleaning)
        logger.info("Stage 2/7: Profiling raw data quality...")
        raw_profile = profile_data(raw_df, dataset_name="Raw Data Profile")
        print_report(raw_profile)

        # Stage 3: Transform
        s3_start = time.time()
        logger.info("Stage 3/7: Transforming and cleaning records...")
        clean_df = transform_pipeline(raw_df, config=cfg)
        s3_duration = time.time() - s3_start
        logger.info(f"Stage 3/7 completed in {s3_duration:.2f}s ({len(clean_df):,} clean records)")

        # Stage 4: Validate
        logger.info("Stage 4/7: Running data validation assertions...")
        validation_results = validate_data(clean_df, config=cfg)

        # Stage 5: Load
        s5_start = time.time()
        logger.info("Stage 5/7: Loading data into SQLite database...")
        load_data(clean_df, config=cfg)
        loaded_count = verify_load(config=cfg)
        s5_duration = time.time() - s5_start
        logger.info(f"Stage 5/7 completed in {s5_duration:.2f}s (Verified {loaded_count:,} records in DB)")

        # Stage 6: Analytics & KPIs
        kpis = {}
        query_results = {}
        if not skip_analytics:
            logger.info("Stage 6/7: Executing SQL analytical queries...")
            query_results = execute_queries(config=cfg)
            kpis = compute_executive_kpis(config=cfg)
            export_query_results_to_csv(query_results, config=cfg)
            logger.info(f"Executive KPIs computed: Total Revenue = ${kpis['total_revenue']:,.2f}")
        else:
            logger.info("Stage 6/7: Skipped SQL analytics as requested.")

        # Stage 7: Reporting
        clean_profile = profile_data(clean_df, dataset_name="Clean Data Profile")
        audit_diff = compare_profiles(raw_profile, clean_profile)
        total_duration = time.time() - start_time

        if generate_report:
            logger.info("Stage 7/7: Compiling Executive and Data Quality Reports...")
            report_md = generate_markdown_report(
                run_id=run_id,
                raw_profile=raw_profile,
                clean_profile=clean_profile,
                kpis=kpis,
                query_results=query_results,
                duration_sec=total_duration,
                config=cfg
            )
            saved_paths = save_reports(report_md, config=cfg)
            logger.info(f"Reports successfully generated at: {saved_paths['markdown']}")

        # Record audit entry in SQLite
        log_pipeline_audit(
            raw_rows=len(raw_df),
            clean_rows=len(clean_df),
            status="SUCCESS",
            duration_sec=total_duration,
            run_id=run_id,
            notes=f"Retention: {audit_diff['retention_rate_pct']}%. Loaded {loaded_count} rows.",
            config=cfg
        )

        logger.info(f"=== PIPELINE COMPLETED SUCCESSFULLY IN {total_duration:.2f}s ===")
        print("\n" + "=" * 60)
        print(f"PIPELINE RUN SUMMARY: SUCCESS [Run ID: {run_id}]")
        print(f"Raw Input: {len(raw_df):,} | Clean Loaded: {len(clean_df):,} | Dropped: {audit_diff['dropped_rows']}")
        print(f"Retention Rate: {audit_diff['retention_rate_pct']}% | Duration: {total_duration:.2f}s")
        if kpis:
            print(f"Total Revenue: ${kpis.get('total_revenue', 0.0):,.2f} | Orders: {kpis.get('total_orders', 0)}")
        print("=" * 60 + "\n")

        return {
            "run_id": run_id,
            "status": "SUCCESS",
            "raw_rows": len(raw_df),
            "clean_rows": len(clean_df),
            "duration_sec": total_duration,
            "kpis": kpis
        }

    except FileNotFoundError as e:
        logger.error(f"Pipeline stopped - missing file: {e}")
        sys.exit(1)
    except ValidationError as e:
        logger.error(f"Pipeline stopped - validation assertion failure: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Pipeline stopped - unexpected error: {e}")
        sys.exit(1)


def parse_arguments():
    """Parses command-line arguments for pipeline execution."""
    parser = argparse.ArgumentParser(description="Sales Data ETL Pipeline Orchestrator")
    parser.add_argument("--input", type=str, help="Path to input raw CSV file", default=None)
    parser.add_argument("--db", type=str, help="Path to output SQLite database", default=None)
    parser.add_argument("--skip-analytics", action="store_true", help="Skip running analytical SQL queries")
    parser.add_argument("--generate-report", action="store_true", default=True, help="Generate executive report artifacts (enabled by default)")
    parser.add_argument("--no-report", action="store_true", help="Do not generate report artifacts")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose debug logging")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    should_report = False if args.no_report else args.generate_report
    run_pipeline(
        raw_file=args.input,
        db_path=args.db,
        skip_analytics=args.skip_analytics,
        generate_report=should_report,
        verbose=args.verbose
    )
