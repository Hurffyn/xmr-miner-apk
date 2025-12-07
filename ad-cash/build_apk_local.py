#!/usr/bin/env python3
"""
Build APK locally without WSL/Docker using python-for-android
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_cmd(cmd, cwd=None):
    """Run command and return success status"""
    print(f"\n>>> {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    return result.returncode == 0

def main():
    print("=" * 60)
    print("XMR Miner APK Builder (Local)")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8+ required")
        return 1
    
    print(f"\nPython version: {sys.version}")
    
    # Install dependencies
    print("\n[1/5] Installing Python dependencies...")
    deps = [
        "Cython==0.29.36",
        "buildozer==1.5.0",
        "python-for-android",
        "kivy",
    ]
    
    for dep in deps:
        if not run_cmd(f"pip install {dep}"):
            print(f"WARNING: Failed to install {dep}, continuing...")
    
    # Setup paths
    root = Path(__file__).parent
    android_dir = root / "android"
    
    print(f"\n[2/5] Checking project structure...")
    print(f"Root: {root}")
    print(f"Android dir: {android_dir}")
    
    if not android_dir.exists():
        print("ERROR: android/ directory not found")
        return 1
    
    # Check buildozer.spec
    spec_file = android_dir / "buildozer.spec"
    if not spec_file.exists():
        print("ERROR: buildozer.spec not found")
        return 1
    
    print(f"Found: {spec_file}")
    
    # Check XMRig binary
    xmrig_bin = root / "bin" / "android_arm64" / "xmrig"
    if not xmrig_bin.exists():
        print(f"\nWARNING: XMRig binary not found at {xmrig_bin}")
        print("The APK will be built without the mining binary.")
        print("You'll need to add it manually or install via Termux.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return 1
    
    # Clean previous builds
    print("\n[3/5] Cleaning previous builds...")
    clean_dirs = [
        android_dir / ".buildozer",
        android_dir / "bin",
    ]
    
    for d in clean_dirs:
        if d.exists():
            print(f"Removing {d}")
            shutil.rmtree(d, ignore_errors=True)
    
    # Build APK
    print("\n[4/5] Building APK...")
    print("This will take 30-60 minutes on first build (downloads SDK/NDK)")
    print("Subsequent builds will be faster.\n")
    
    # Try buildozer
    os.chdir(android_dir)
    
    # Windows-specific: Buildozer doesn't work directly on Windows
    # We'll create a portable build script instead
    print("\nNOTE: Buildozer requires Linux/WSL or Docker on Windows.")
    print("\nGenerating portable build instructions...")
    
    instructions = """
╔══════════════════════════════════════════════════════════════════════════╗
║                    APK BUILD INSTRUCTIONS (Windows)                      ║
╚══════════════════════════════════════════════════════════════════════════╝

Option 1: GitHub Actions (EASIEST - No setup needed)
────────────────────────────────────────────────────
1. Create GitHub repository: https://github.com/new
2. In PowerShell, run:
   
   cd C:\\Users\\abiin\\Downloads\\ad-cash-miner\\ad-cash
   git remote add origin https://github.com/YOUR_USERNAME/xmr-miner.git
   git branch -M main
   git push -u origin main
   
3. Go to: https://github.com/YOUR_USERNAME/xmr-miner/actions
4. Wait ~30 min for build
5. Download APK from Artifacts

Option 2: WSL (Ubuntu)
──────────────────────
1. Install WSL:
   
   wsl --install -d Ubuntu-22.04
   
2. Restart PC
3. In Ubuntu terminal:
   
   cd /mnt/c/Users/abiin/Downloads/ad-cash-miner/ad-cash
   bash build_android.sh
   
4. APK will be in android/bin/

Option 3: Docker Desktop
────────────────────────
1. Install Docker Desktop: https://www.docker.com/products/docker-desktop
2. In PowerShell:
   
   cd C:\\Users\\abiin\\Downloads\\ad-cash-miner\\ad-cash\\android
   docker run --rm -v ${PWD}:/app kivy/buildozer android debug
   
3. APK in android/bin/

╔══════════════════════════════════════════════════════════════════════════╗
║ RECOMMENDED: Option 1 (GitHub Actions) - Zero configuration needed!     ║
╚══════════════════════════════════════════════════════════════════════════╝
"""
    
    print(instructions)
    
    # Save instructions to file
    instructions_file = root / "BUILD_APK_INSTRUCTIONS.txt"
    with open(instructions_file, 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"\n[5/5] Instructions saved to: {instructions_file}")
    
    # Try to detect if WSL is available
    print("\nChecking for WSL...")
    wsl_check = subprocess.run("wsl --list", shell=True, capture_output=True, text=True)
    
    if wsl_check.returncode == 0 and "Ubuntu" in wsl_check.stdout:
        print("\n✓ WSL with Ubuntu detected!")
        print("\nYou can build now with:")
        print("  wsl bash build_android.sh")
        
        response = input("\nBuild APK now with WSL? (y/n): ")
        if response.lower() == 'y':
            os.chdir(root)
            if run_cmd("wsl bash build_android.sh"):
                print("\n✓ APK build successful!")
                print(f"APK location: {android_dir / 'bin'}")
                return 0
            else:
                print("\n✗ Build failed. Check logs above.")
                return 1
    
    print("\n" + "=" * 60)
    print("Setup complete! Follow instructions above to build APK.")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
