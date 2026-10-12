"""
Phase 1: Extract Module

Reads raw sales data from CSV files into a Pandas DataFrame.
Handles missing files, empty files, malformed rows, and character encoding issues gracefully.
"""
import logging
from pathlib import Path
from typing import List, Optional, Union
import pandas as pd

try:
    from .config import default_config, PipelineConfig
except (ImportError, ValueError):
    from config import default_config, PipelineConfig

logger = logging.getLogger(__name__)


def extract_data(
    file_path: Optional[Union[str, Path]] = None,
    config: Optional[PipelineConfig] = None
) -> pd.DataFrame:
    """
    Extracts raw sales data from a CSV file into a Pandas DataFrame.

    Parameters:
        file_path: Path to the raw CSV file. Defaults to config raw_file_path.
        config: Optional PipelineConfig instance.

    Returns:
        pd.DataFrame: Raw sales data.

    Raises:
        FileNotFoundError: If the source file does not exist.
        ValueError: If the file is empty or corrupted.
    """
    cfg = config or default_config
    target_path = Path(file_path) if file_path else cfg.raw_file_path

    if not target_path.exists():
        err_msg = f"Source CSV file not found at: {target_path}"
        logger.error(err_msg)
        raise FileNotFoundError(err_msg)

    # Attempt to read with multiple encodings to handle diverse exports
    encodings_to_try = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    df = None
    last_error = None

    for encoding in encodings_to_try:
        try:
            df = pd.read_csv(target_path, encoding=encoding)
            logger.debug(f"Successfully read {target_path.name} using encoding '{encoding}'")
            break
        except pd.errors.EmptyDataError:
            raise ValueError(f"Raw data file is completely empty: {target_path}")
        except (pd.errors.ParserError, UnicodeDecodeError) as e:
            last_error = e
            continue

    if df is None:
        raise ValueError(f"Failed to read CSV file {target_path}: {last_error}")

    # Validate essential header columns exist
    missing_cols = cfg.required_raw_columns - set(df.columns)
    if missing_cols:
        raise ValueError(
            f"Raw CSV file is missing required columns: {sorted(list(missing_cols))}. "
            f"Found columns: {list(df.columns)}"
        )

    file_size_kb = target_path.stat().st_size / 1024
    logger.info(
        f"Extracted {len(df):,} rows and {len(df.columns)} columns from "
        f"'{target_path.name}' ({file_size_kb:.1f} KB)"
    )
    return df


def extract_multiple(
    folder_path: Union[str, Path],
    pattern: str = "*.csv",
    config: Optional[PipelineConfig] = None
) -> pd.DataFrame:
    """
    Extracts and merges multiple CSV files matching a glob pattern into a single DataFrame.

    Parameters:
        folder_path: Directory containing CSV files.
        pattern: Glob pattern to filter files. Defaults to '*.csv'.
        config: Optional PipelineConfig instance.

    Returns:
        pd.DataFrame: Combined raw data.
    """
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(f"Source folder does not exist or is not a directory: {folder_path}")

    files = sorted(list(folder.glob(pattern)))
    if not files:
        raise FileNotFoundError(f"No files matching pattern '{pattern}' found in {folder_path}")

    logger.info(f"Discovered {len(files)} files matching '{pattern}' in {folder}")
    dfs: List[pd.DataFrame] = [extract_data(file_path=f, config=config) for f in files]
    combined_df = pd.concat(dfs, ignore_index=True)
    
    logger.info(f"Combined {len(files)} files -> {len(combined_df):,} total raw rows")
    return combined_df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    df_sample = extract_data()
    print(df_sample.head())
    print(f"\nShape: {df_sample.shape}")
