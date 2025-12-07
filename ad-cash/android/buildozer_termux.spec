[app]
title = XMR Miner Pro
package.name = xmrminer
package.domain = com.xmrminer
source.dir = ..
source.include_exts = py,png,jpg,kv,atlas,json,sh
source.include_patterns = assets/*,bin/android_arm64/*,core/*,android/*
entrypoint = android/main.py
version = 1.0.0

# Requirements with full Termux-like environment
requirements = python3,kivy,pexpect,psutil,requests,base58,pycryptodome,pynacl,numpy,sh

# Android permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,WAKE_LOCK,ACCESS_NETWORK_STATE,FOREGROUND_SERVICE,REQUEST_INSTALL_PACKAGES

# Android settings
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 31
android.arch = arm64-v8a
python_version = 3.11
kivy_version = 2.2.0

# Services
services = MiningService:android/mining_service.py

# Additional features
android.gradle_dependencies = 
android.add_src = bin/android_arm64
presplash.color = #000000
orientation = portrait
fullscreen = 0

# Bootstrap with proot support
p4a.bootstrap = sdl2
p4a.branch = master

# Build options
android.logcat_filters = *:S python:D
android.release_artifact = apk
log_level = 2
warn_on_root = 1

[buildozer]
build_dir = ./.buildozer
bin_dir = ./bin
