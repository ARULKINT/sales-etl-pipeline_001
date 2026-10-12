# 04. Setup & Installation Guide

This guide walks you through setting up the Sales ETL Pipeline across Windows, macOS, and Linux systems.

---

## 1. Prerequisites

Before installing, ensure your environment meets the minimum requirements:
* **Python:** Version 3.10, 3.11, 3.12, 3.13, or 3.14 (Verified compatible).
* **Git:** Version 2.30+ installed.
* **Storage:** 100 MB free disk space for raw data, database, and generated reports.

Verify your installed Python version:
```bash
python --version
# Output should be Python 3.10.x or higher
```

---

## 2. Step-by-Step Installation

### Step 1: Clone or Open the Repository
```bash
git clone https://github.com/your-username/sales-etl-pipeline.git
cd sales-etl-pipeline
```

### Step 2: Create a Virtual Environment
Isolating dependencies in a dedicated virtual environment prevents package conflicts.

* **On Windows (PowerShell or Command Prompt):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
  *(If execution policies block scripts in PowerShell, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

* **On macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### Step 3: Upgrade Pip
```bash
python -m pip install --upgrade pip
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

Alternatively, install the project in editable developer mode:
```bash
pip install -e .
```

---

## 3. Verifying Installation

Verify that all dependencies and test suites execute cleanly:
```bash
pytest tests/ -v
```

Expected output:
```text
============================= test session starts =============================
platform win32 -- Python 3.14.x, pytest-9.x.x
collected 30 items

tests/test_analytics.py ...                                              [ 10%]
tests/test_extract.py .....                                              [ 26%]
tests/test_load.py ..                                                    [ 33%]
tests/test_pipeline_e2e.py .                                             [ 36%]
tests/test_profile.py ...                                                [ 46%]
tests/test_transform.py ........                                         [ 73%]
tests/test_validate.py ........                                          [100%]

============================= 30 passed in 1.51s ==============================
```

---

## 4. Generating Synthetic Test Data (Optional)

If you wish to re-generate synthetic raw data with intentional anomalies (nulls, duplicates, negative numbers, mixed dates):
```bash
python data/raw/generate_sample_data.py
```
This generates a fresh `data/raw/sales_data.csv` with 508 messy records.

---

## 5. Troubleshooting Common Setup Issues

### Issue 1: Windows Console Unicode / Charmap Error
* **Symptom:** `UnicodeEncodeError: 'charmap' codec can't encode character...`
* **Root Cause:** Legacy Windows consoles use code page `cp1252` instead of UTF-8.
* **Solution:** The modernized pipeline codebase uses cross-platform safe tags (`[VALIDATION PASSED]`) and UTF-8 file handlers. To set your PowerShell console to UTF-8 globally:
  ```powershell
  $OutputEncoding = [System.Text.Encoding]::UTF8
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  ```

### Issue 2: Virtual Environment Activation Restricted on Windows
* **Symptom:** `Activate.ps1 cannot be loaded because running scripts is disabled on this system.`
* **Solution:** Open PowerShell as your current user and run:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
  ```

### Issue 3: SQLite File Locked (`sqlite3.OperationalError: database is locked`)
* **Symptom:** Pipeline fails during Stage 5 (Load) reporting that the database is locked.
* **Root Cause:** An external tool (such as DB Browser for SQLite or VS Code SQLite extension) is holding an open lock on `data/processed/sales.db`.
* **Solution:** Close any external database inspection tools before running `python src/main.py`.
