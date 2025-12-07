"""
XMR Miner - Android Version with Termux
Simplified version that runs in Termux environment
"""
import os
import sys
import subprocess
import time

print("=" * 50)
print("XMR MINER - TERMUX EDITION")
print("=" * 50)

# Configuration
POOL = "pool.supportxmr.com:443"
WALLET = "YOUR_WALLET_ADDRESS"
THREADS = 4

def check_termux():
    """Check if running in Termux"""
    if not os.path.exists("/data/data/com.termux"):
        print("ERROR: This script must run in Termux!")
        return False
    return True

def install_dependencies():
    """Install required packages"""
    print("\n[1/3] Installing dependencies...")
    packages = ["python", "clang", "cmake", "git", "make"]
    
    for pkg in packages:
        print(f"  Installing {pkg}...")
        subprocess.run(["pkg", "install", "-y", pkg], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
    
    print("✓ Dependencies installed")

def download_xmrig():
    """Download XMRig for Android"""
    print("\n[2/3] Downloading XMRig...")
    
    xmrig_dir = os.path.join(os.path.dirname(__file__), "xmrig")
    
    if not os.path.exists(xmrig_dir):
        subprocess.run([
            "git", "clone",
            "https://github.com/xmrig/xmrig.git",
            xmrig_dir
        ])
    
    print("✓ XMRig ready")
    return xmrig_dir

def build_xmrig(xmrig_dir):
    """Build XMRig"""
    print("\n[3/3] Building XMRig...")
    
    build_dir = os.path.join(xmrig_dir, "build")
    os.makedirs(build_dir, exist_ok=True)
    
    os.chdir(build_dir)
    subprocess.run(["cmake", ".."])
    subprocess.run(["make", "-j4"])
    
    print("✓ XMRig compiled")
    return os.path.join(build_dir, "xmrig")

def start_mining(xmrig_bin):
    """Start mining"""
    print("\n" + "=" * 50)
    print("STARTING MINER")
    print("=" * 50)
    print(f"Pool: {POOL}")
    print(f"Threads: {THREADS}")
    print("=" * 50)
    
    cmd = [
        xmrig_bin,
        "-o", POOL,
        "-u", WALLET,
        "-p", "android",
        "-t", str(THREADS),
        "--tls",
        "--donate-level=0"
    ]
    
    subprocess.run(cmd)

def main():
    if not check_termux():
        sys.exit(1)
    
    install_dependencies()
    xmrig_dir = download_xmrig()
    xmrig_bin = build_xmrig(xmrig_dir)
    start_mining(xmrig_bin)

if __name__ == "__main__":
    main()
