#!/bin/bash
# Setup script for Widevine L1 Dumper

set -e

echo "======================================"
echo "Widevine L1 Dumper - Setup Script"
echo "======================================"

# Check Python version
echo "[1/5] Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION found"

# Check ADB
echo "\n[2/5] Checking ADB installation..."
if ! command -v adb &> /dev/null; then
    echo "⚠ Warning: ADB not found in PATH"
    echo "  Please install Android SDK Platform Tools"
    echo "  Linux: sudo apt-get install android-tools-adb"
    echo "  macOS: brew install android-platform-tools"
    echo "  Windows: Download from https://developer.android.com/studio"
else
    ADB_VERSION=$(adb version | head -n 1)
    echo "✓ $ADB_VERSION"
fi

# Create virtual environment (optional)
echo "\n[3/5] Setting up Python environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "\n[4/5] Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
fi

# Install dependencies
echo "\n[5/5] Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✓ Dependencies installed"
else
    echo "✗ requirements.txt not found"
    exit 1
fi

echo "\n======================================"
echo "✓ Setup completed successfully!"
echo "======================================"
echo "\nTo activate the virtual environment:"
echo "  source venv/bin/activate"
echo "\nTo run the dumper:"
echo "  python widevine_dumper.py --help"
echo ""
