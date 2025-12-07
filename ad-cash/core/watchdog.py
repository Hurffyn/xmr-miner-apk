import subprocess
import time
from typing import Optional

from . import config
from .pool_selector import pick_best_pool_sync


def build_xmrig_cmd(binary_path: str, wallet: str, pool_host: str, pool_port: int, threads: int) -> list:
    cmd = [
        binary_path,
        "-o",
        f"{pool_host}:{pool_port}",
        "-u",
        wallet,
        "-p",
        "x",
        "-k",
        "-t",
        str(threads),
        "--cpu-priority=5",  # Maximum CPU priority
        "--randomx-mode=auto",  # Auto-detect best RandomX mode
        "--randomx-no-rdmsr",  # Skip MSR checks (since they fail anyway)
        "--cpu-max-threads-hint=100",  # Use all available threads
        "--donate-level=0",  # Remove developer donation to keep 100% hashing time
    ]
    
    # Only use TLS for specific ports that support it
    if pool_port in [443, 10128, 10032]:
        cmd.append("--tls")
    
    return cmd


def run_supervised(binary_path: str, wallet: str, threads: Optional[int] = None):
    host, port, latency = pick_best_pool_sync()
    t = threads
    if t is None:
        t = max(1, int(config.THREAD_CAP_RATIO * subprocess.os.cpu_count()))
    cmd = build_xmrig_cmd(binary_path, wallet, host, port, t)
    while True:
        try:
            proc = subprocess.Popen(cmd)
            proc.wait()
        except Exception:
            pass
        time.sleep(config.WATCHDOG_INTERVAL_SEC)
        # Recompute best pool in case topology changed
        host, port, latency = pick_best_pool_sync()
        cmd = build_xmrig_cmd(binary_path, wallet, host, port, t)
