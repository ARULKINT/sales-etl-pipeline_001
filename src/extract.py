"""
Phase 6 - Extract
Reads raw CSV(s) into a DataFrame. Handles missing files and bad reads
instead of letting the whole pipeline crash.
"""
import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_data(file_path: str) -> pd.DataFrame:
    """Read a CSV file into a DataFrame with basic error handling."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Source file not found: {file_path}")

    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        raise ValueError(f"File is empty: {file_path}")
    except pd.errors.ParserError as e:
        raise ValueError(f"Could not parse CSV: {e}")

    logger.info(f"Extracted {len(df)} rows from {path.name}")
    return df


def extract_multiple(folder_path: str, pattern: str = "*.csv") -> pd.DataFrame:
    """Combine multiple CSVs from a folder into one DataFrame."""
    folder = Path(folder_path)
    files = list(folder.glob(pattern))

    if not files:
        raise FileNotFoundError(f"No files matching '{pattern}' in {folder_path}")

    dfs = [extract_data(str(f)) for f in files]
    combined = pd.concat(dfs, ignore_index=True)
    logger.info(f"Combined {len(files)} files -> {len(combined)} total rows")
    return combined


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    df = extract_data("data/raw/sales_data.csv")
    print(df.head())
    print(f"\nShape: {df.shape}")
