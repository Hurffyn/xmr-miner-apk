#!/bin/bash
# Build script for Android APK (requires Linux with Buildozer)

set -e

echo "========================================="
echo "Building XMR Miner for Android ARM64"
echo "========================================="

# Check Buildozer
if ! command -v buildozer &> /dev/null; then
    echo "Installing Buildozer..."
    pip install buildozer
fi

# Verify XMRig binary
if [ ! -f "bin/android_arm64/xmrig" ] || [ ! -x "bin/android_arm64/xmrig" ]; then
    echo "WARNING: xmrig ARM64 binary not found or not executable"
    echo "Place compiled ARM64 xmrig in bin/android_arm64/xmrig and chmod +x"
    echo ""
    echo "Options:"
    echo "1. Compile from source with Android NDK"
    echo "2. Install via Termux: pkg install xmrig"
    echo "3. Use third-party build (verify source!)"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install system dependencies (Ubuntu/Debian)
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    build-essential \
    git \
    ffmpeg \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev \
    openjdk-17-jdk \
    autoconf \
    libtool \
    pkg-config

# Accept Android SDK licenses
yes | buildozer android adb || true

# Build APK
cd android
echo "Building APK..."
buildozer -v android debug

echo "========================================="
echo "Build complete!"
echo "Output: android/bin/*.apk"
echo "Install: adb install android/bin/*.apk"
echo "========================================="
