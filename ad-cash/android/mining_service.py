"""
Android background service for mining.
Keeps XMRig running even when app is minimized.
"""
from jnius import autoclass
import os
import sys

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.watchdog import run_supervised
from core import config

PythonService = autoclass('org.kivy.android.PythonService')
PythonService.mService.setAutoRestartService(True)


def start_mining_service(wallet_address: str):
    """Start mining in background service."""
    binary_path = os.path.abspath(config.XMRIG_BIN_ANDROID)
    run_supervised(binary_path, wallet_address)


if __name__ == '__main__':
    # Service entry point
    # Wallet address should be passed via service argument
    wallet = os.environ.get('MINING_WALLET', '87e3o1i9eoZPGSpKMYNVg5644DF6GmifaAHtkPW1MAD5LuryxR9CpErg57Q5gbpn36EqAaJHC2f1Z1a7cjGsPvgLRumZVAc')
    start_mining_service(wallet)
