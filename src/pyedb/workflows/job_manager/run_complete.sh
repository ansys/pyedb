#!/bin/bash

echo "🚀 Starting PyEDB Job Manager Complete Integration"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Start backend service in background
echo "Starting backend service..."
python setup_backend.py &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Check if backend is running
if ps -p $BACKEND_PID > /dev/null; then
    echo "✅ Backend service started (PID: $BACKEND_PID)"
else
    echo "❌ Backend service failed to start"
    exit 1
fi

# Start Streamlit app
echo "Starting Streamlit app..."
streamlit run app_integrated.py

# Cleanup on exit
echo "Cleaning up..."
kill $BACKEND_PID 2>/dev/null
deactivate

echo "✅ PyEDB Job Manager shutdown complete"