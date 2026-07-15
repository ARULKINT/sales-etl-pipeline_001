"""
Phase 13 - Automation
Runs the full ETL pipeline end to end with one command:
    python src/main.py
Logs every stage and stops safely if something fails.
"""
import logging
import sys
from pathlib import Path

from extract import extract_data
from profile_data import profile_data, print_report
from transform import transform_pipeline
from validate import validate_data, ValidationError
from load import load_data, verify_load

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

RAW_FILE = "data/raw/sales_data.csv"


def run_pipeline():
    logger.info("=== ETL PIPELINE STARTED ===")

    try:
        logger.info("Stage 1/5: Extract")
        df = extract_data(RAW_FILE)

        logger.info("Stage 2/5: Profile (before cleaning)")
        report = profile_data(df)
        print_report(report)

        logger.info("Stage 3/5: Transform")
        clean_df = transform_pipeline(df)

        logger.info("Stage 4/5: Validate")
        validate_data(clean_df)

        logger.info("Stage 5/5: Load")
        load_data(clean_df)
        verify_load()

        logger.info("=== PIPELINE COMPLETED SUCCESSFULLY ===")
        return clean_df

    except FileNotFoundError as e:
        logger.error(f"Pipeline stopped - missing file: {e}")
        sys.exit(1)
    except ValidationError as e:
        logger.error(f"Pipeline stopped - validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Pipeline stopped - unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_pipeline()
