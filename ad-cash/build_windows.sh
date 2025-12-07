#!/bin/bash
# Build script for Windows EXE (run on Windows or Wine)

set -e

echo "========================================="
echo "Building XMR Miner for Windows x64"
echo "========================================="

# Check Python
python --version || python3 --version

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt pyinstaller

# Verify XMRig binary
if [ ! -f "bin/windows_x64/xmrig.exe" ]; then
    echo "ERROR: xmrig.exe not found in bin/windows_x64/"
    echo "Download from: https://github.com/xmrig/xmrig/releases"
    exit 1
fi

# Build with PyInstaller
echo "Building executable..."
pyinstaller windows/pyinstaller.spec --clean

echo "========================================="
echo "Build complete!"
echo "Output: dist/XMR_Miner/"
echo "Run: dist/XMR_Miner/XMR_Miner.exe"
echo "========================================="
