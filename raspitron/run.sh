#!/bin/bash

# RaspiTRON Console Interface Launcher
# Sets up environment and starts the console application

echo "=== RaspiTRON Launcher ==="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed"
    exit 1
fi

# Set default StoryTRON URL if not configured
if [ -z "$STORYTRON_URL" ]; then
    echo "Using default StoryTRON URL: http://localhost:5000"
    export STORYTRON_URL="http://localhost:5000"
else
    echo "Using configured StoryTRON URL: $STORYTRON_URL"
fi

# Check if requirements are installed
if ! python3 -c "import requests" 2>/dev/null; then
    echo "Installing requirements..."
    pip install -r requirements.txt
fi

echo "Starting RaspiTRON..."
echo ""

# Start the application
python3 main.py
