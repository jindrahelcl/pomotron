#!/bin/bash

# RaspiTRON Console Interface Launcher
# Sets up environment and starts the console application

echo "=== RaspiTRON Launcher ==="

# Resolve script directory and enter it
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

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

# Default HTTP timeout for RaspiTRON -> StoryTRON requests (seconds)
if [ -z "$STORYTRON_TIMEOUT" ]; then
    export STORYTRON_TIMEOUT=30
fi

# Setup virtual environment to avoid system Python restrictions (PEP 668)
VENV_DIR="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

PY="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"

#echo "Installing Python dependencies..."
#"$PIP" install --quiet --upgrade pip
#"$PIP" install --quiet -r "$SCRIPT_DIR/requirements.txt"

echo "Starting RaspiTRON..."
echo ""

# Start the application
"$PY" "$SCRIPT_DIR/main.py"
