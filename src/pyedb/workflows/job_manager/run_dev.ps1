# PyEB Development Mode - Path Fix
# Correctly handles the directory structure

# Get current location and calculate correct paths
$CURRENT_DIR = Get-Location
$WORKFLOWS_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PYEDB_DIR = Split-Path -Parent $WORKFLOWS_DIR
$SRC_DIR = Split-Path -Parent $PYEDB_DIR
$PROJECT_ROOT = Split-Path -Parent $SRC_DIR

Write-Host "=== PyEDB Development Mode - Path Debug ===" -ForegroundColor Cyan
Write-Host "Current Directory: $CURRENT_DIR" -ForegroundColor Gray
Write-Host "Workflows Directory: $WORKFLOWS_DIR" -ForegroundColor Gray
Write-Host "PyEDB Directory: $PYEDB_DIR" -ForegroundColor Gray
Write-Host "SRC Directory: $SRC_DIR" -ForegroundColor Gray
Write-Host "Project Root: $PROJECT_ROOT" -ForegroundColor Gray

# The Python path should be the src directory containing pyedb
$PYTHONPATH = $SRC_DIR

Write-Host "Python Path: $PYTHONPATH" -ForegroundColor Yellow

# Simple functions
function WriteSuccess { param($msg) Write-Host "[OK] $msg" -ForegroundColor Green }
function WriteError { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red }
function WriteInfo { param($msg) Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function WriteDebug { param($msg) Write-Host "[DEBUG] $msg" -ForegroundColor Magenta }

try {
    # Check Python
    WriteInfo "Checking Python installation..."
    python --version
    if ($LASTEXITCODE -ne 0) {
        WriteError "Python not found in PATH"
        exit 1
    }

    # Verify the exact path structure
    WriteDebug "Verifying directory structure..."
    WriteDebug "Looking for pyedb in: $PYTHONPATH"

    $expectedPyedbPath = "$PYTHONPATH\pyedb"
    if (Test-Path $expectedPyedbPath) {
        WriteSuccess "Found pyedb directory at: $expectedPyedbPath"

        # Check for the specific backend file
        $backendFile = "$expectedPyedbPath\workflows\job_manager\backend\job_manager_handler.py"
        if (Test-Path $backendFile) {
            WriteSuccess "Found backend handler: $backendFile"
        } else {
            WriteError "Backend handler NOT found at: $backendFile"
            # Show what's actually there
            WriteError "Contents of job_manager directory:"
            Get-ChildItem "$expectedPyedbPath\workflows\job_manager" | ForEach-Object {
                WriteError "  $($_.Name)"
            }
            exit 1
        }
    } else {
        WriteError "pyedb directory NOT found at: $expectedPyedbPath"
        WriteError "Contents of PYTHONPATH directory:"
        Get-ChildItem $PYTHONPATH | ForEach-Object {
            WriteError "  $($_.Name)"
        }
        exit 1
    }

    # Test import with the correct path
    WriteInfo "Testing backend import..."

    $testScript = @"
import sys
sys.path.insert(0, r'$PYTHONPATH')

from pyedb.workflows.job_manager.backend.job_manager_handler import JobManagerHandler
detected = JobManagerHandler._detect_scheduler()
print(f'SUCCESS:{detected.value}')
"@

    $tempFile = [System.IO.Path]::GetTempFileName() + ".py"
    Set-Content -Path $tempFile -Value $testScript

    $env:PYTHONPATH = $PYTHONPATH
    $result = python $tempFile
    $exitCode = $LASTEXITCODE

    Remove-Item $tempFile -Force

    if ($exitCode -eq 0 -and $result -like "SUCCESS:*") {
        $scheduler = $result.Split(':')[1]
        WriteSuccess "Backend import successful! Detected: $scheduler"
    } else {
        WriteError "Backend import failed: $result"
        exit 1
    }

    # Install dependencies
    WriteInfo "Installing dependencies..."
    python -m pip install --upgrade pip
    python -m pip install streamlit aiohttp "python-socketio[client]" pandas numpy psutil

    # Create directories
    WriteInfo "Creating directories..."
    @("uploads", "logs", "temp") | ForEach-Object {
        $dir = "$WORKFLOWS_DIR\$_"
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            WriteSuccess "Created $dir"
        }
    }

    # Start backend
    WriteInfo "Starting backend service..."
    $env:PYTHONPATH = $PYTHONPATH

    $backendJob = Start-Job -ScriptBlock {
        param($pythonPath, $workflowsDir)
        $env:PYTHONPATH = $pythonPath
        Set-Location $workflowsDir
        python -m pyedb.workflows.job_manager.service
    } -ArgumentList $PYTHONPATH, $WORKFLOWS_DIR

    # Wait for backend
    WriteInfo "Waiting for backend to start..."
    $maxRetries = 30

    for ($i = 1; $i -le $maxRetries; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8080" -Method GET -TimeoutSec 5 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                WriteSuccess "Backend is ready!"
                break
            }
        } catch {
            if ($i % 5 -eq 0) {
                Write-Host "." -NoNewline
            }
            Start-Sleep -Seconds 1
        }
    }

    if ($i -gt $maxRetries) {
        WriteError "Backend failed to start"
        exit 1
    }

    Write-Host "" # New line

    # Start Streamlit
    Start-Process "http://localhost:8501"

    WriteSuccess "Starting Streamlit app..."
    Write-Host ""
    Write-Host "🚀 PyEDB Job Manager is ready!" -ForegroundColor Green
    Write-Host "📱 UI: http://localhost:8501" -ForegroundColor Cyan
    Write-Host "🔧 Backend: http://localhost:8080" -ForegroundColor Cyan
    Write-Host ""

    python -m streamlit run app_integrated.py --server.port 8501

} catch {
    WriteError "Script failed: $_"
    exit 1
} finally {
    WriteInfo "Cleaning up..."
    if ($backendJob) {
        Stop-Job $backendJob -ErrorAction SilentlyContinue
        Remove-Job $backendJob -ErrorAction SilentlyContinue
    }
}