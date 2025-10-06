# Simple PyEDB Job Manager Startup for Windows

Write-Host "=== PyEDB Job Manager Startup ===" -ForegroundColor Cyan

# Check Python
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "Python not found!" -ForegroundColor Red
    exit 1
}

# Check PyEDB
python -c "import pyedb" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "PyEDB not found. Install with: pip install pyedb" -ForegroundColor Red
    exit 1
}

# Install packages
Write-Host "Installing packages..." -ForegroundColor Green
python -m pip install streamlit aiohttp "python-socketio[client]" pandas numpy psutil

# Create directories
@("uploads", "logs", "temp") | ForEach-Object { New-Item -ItemType Directory -Path $_ -Force | Out-Null }

# Start backend in background
Write-Host "Starting backend service..." -ForegroundColor Yellow
Start-Process python -ArgumentList "-m pyedb.workflows.job_manager.service" -NoNewWindow

# Wait a bit
Start-Sleep 5

# Open browser
Start-Process "http://localhost:8501"

# Start Streamlit
Write-Host "Starting Streamlit app..." -ForegroundColor Green
python -m streamlit run app_integrated.py --server.port 8501