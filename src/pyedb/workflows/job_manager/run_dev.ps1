# ---------------------------------------------------------------------------
#  PyEDB Job-Manager – development launcher
# ---------------------------------------------------------------------------
$ErrorActionPreference = "Stop"

# ---- path arithmetic ------------------------------------------------------
$WORKFLOWS_DIR = $PSScriptRoot
$PYEDB_DIR     = Split-Path $WORKFLOWS_DIR        # …\workflows
$SRC_DIR       = Split-Path $PYEDB_DIR            # …\src   ← package root
$PYTHONPATH = Split-Path $SRC_DIR   # ← go up one more level to …\src

Write-Host "=== PyEDB Development Mode ===" -ForegroundColor Cyan
Write-Host "Workflows dir : $WORKFLOWS_DIR"
Write-Host "PyEDB dir     : $PYEDB_DIR"
Write-Host "SRC  dir      : $SRC_DIR"
Write-Host "PYTHONPATH    : $PYTHONPATH" -ForegroundColor Yellow

# ---- helpers --------------------------------------------------------------
function WriteInfo  { Write-Host "[INFO]  $args" -ForegroundColor Cyan  }
function WriteOk    { Write-Host "[OK]    $args" -ForegroundColor Green }
function WriteError { Write-Host "[ERROR] $args" -ForegroundColor Red   }

# ---- Python available? ----------------------------------------------------
WriteInfo "Checking Python …"
python --version
if ($LASTEXITCODE -ne 0) { throw "Python not found in PATH" }

# ---- install deps ---------------------------------------------------------
WriteInfo "Installing / upgrading dependencies …"
python -m pip install --upgrade pip
python -m pip install --upgrade streamlit aiohttp "python-socketio[client]" pandas numpy psutil

# ---- create runtime folders -----------------------------------------------
@("uploads","logs","temp") | ForEach-Object {
    $d = Join-Path $WORKFLOWS_DIR $_
    if (!(Test-Path $d)) { New-Item -ItemType Directory -Path $d | Out-Null }
}

# ---- test import ----------------------------------------------------------
WriteInfo "Testing backend import …"
$testPy = @"
import sys, traceback
sys.path.insert(0, r'$PYTHONPATH')
try:
    from pyedb.workflows.job_manager.backend.job_manager_handler import JobManagerHandler
    print('SUCCESS')
except Exception as e:
    traceback.print_exc()
    print('FAIL')
"@

$tmp = [System.IO.Path]::GetTempFileName() + ".py"
Set-Content -Path $tmp -Value $testPy -Encoding UTF8

$env:PYTHONPATH = $PYTHONPATH
$output = python $tmp
$ok     = $output -contains "SUCCESS"
Remove-Item $tmp -Force

if (!$ok) {
    Write-Host "----  Python traceback  ----" -ForegroundColor Yellow
    Write-Host ($output -join "`n")
    Write-Host "----------------------------" -ForegroundColor Yellow
    throw "Backend import failed - traceback printed above"
}
WriteOk "Backend import OK"

# ---- start backend job ----------------------------------------------------
WriteInfo "Starting backend service …"
$backendJob = Start-Job -ScriptBlock {
    param($pp, $wd)
    $env:PYTHONPATH = $pp
    Set-Location $wd
    python -m pyedb.workflows.job_manager.backend.service
} -ArgumentList $PYTHONPATH, $WORKFLOWS_DIR

# ---- wait for backend -----------------------------------------------------
$retries = 30
WriteInfo "Waiting for backend to come alive …"
for ($i=1; $i -le $retries; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:8080" -Method GET -TimeoutSec 5 -UseBasicParsing
        if ($r.StatusCode -eq 200) { WriteOk "Backend ready"; break }
    } catch { Start-Sleep 1 }
}
if ($i -gt $retries) { throw "Backend never answered on :8080" }

# ---- start Streamlit ------------------------------------------------------
Start-Process "http://localhost:8501"
WriteInfo "Starting Streamlit UI …"
python -m streamlit run app_integrated.py --server.port 8501