[app]

# Application title
title = XMR Miner

# Package name
package.name = xmrminer

# Package domain (reverse DNS)
package.domain = com.xmrminer

# Version
version = 1.0.0

# Source directory
source.dir = ..

# Source files to include
source.include_exts = py,png,jpg,kv,atlas,json

# Source files to exclude
source.exclude_exts = spec

# Application entry point
source.include_patterns = assets/*,bin/android_arm64/*

# Entry point
entrypoint = android/main.py

# Android permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,WAKE_LOCK,ACCESS_NETWORK_STATE,FOREGROUND_SERVICE

# Android API level
android.api = 31

# Minimum API level
android.minapi = 21

# Android NDK version
android.ndk = 25b

# Android SDK version
android.sdk = 31

# Python version
python_version = 3.11

# Kivy version
kivy_version = 2.2.0

# Requirements
requirements = python3,kivy,psutil,requests,base58,pycryptodome,pynacl,numpy

# Presplash background color
presplash.color = #000000

# Icon
#icon.filename = %(source.dir)s/data/icon.png

# Supported orientations
orientation = portrait

# Services
services = MiningService:android/mining_service.py

# Android arch
android.archs = arm64-v8a

# Android gradle dependencies
android.gradle_dependencies = 

# Android AAB/APK format
android.release_artifact = apk

# Android logcat filters
android.logcat_filters = *:S python:D

# Copy external files
android.add_src = bin/android_arm64

# Background service
[app:services]

# Allow background execution
android.background_mode = always

[buildozer]

# Log level
log_level = 2

# Display warning if buildozer is run as root
warn_on_root = 1

# Build directory
build_dir = ./.buildozer

# Binary directory
bin_dir = ./bin
