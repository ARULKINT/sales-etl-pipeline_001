# ==============================================================================
# Sales ETL Pipeline Runner (PowerShell)
# ==============================================================================
$ErrorActionPreference = "Stop"

Write-Host ">>> Starting Sales ETL Pipeline execution..." -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check virtual environment
if (Test-Path "$ScriptDir\venv\Scripts\python.exe") {
    $PythonExe = "$ScriptDir\venv\Scripts\python.exe"
} else {
    $PythonExe = "python"
}

Write-Host ">>> Using Python: $PythonExe" -ForegroundColor Gray
& $PythonExe src/main.py --generate-report

if ($LASTEXITCODE -eq 0) {
    Write-Host ">>> Pipeline completed successfully!" -ForegroundColor Green
} else {
    Write-Host ">>> Pipeline execution failed with exit code $LASTEXITCODE." -ForegroundColor Red
    exit $LASTEXITCODE
}
