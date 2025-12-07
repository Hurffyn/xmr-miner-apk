#!/bin/bash
set -e

echo "=========================================="
echo "BUILD APK COM TERMUX EMBUTIDO"
echo "=========================================="

cd android

# Install dependencies
pip install buildozer cython==0.29.36

# Clean previous builds
rm -rf .buildozer bin

# Build APK
buildozer -v android debug

echo ""
echo "=========================================="
echo "BUILD CONCLUÍDO!"
echo "=========================================="
echo "APK: android/bin/xmrminer-*.apk"
