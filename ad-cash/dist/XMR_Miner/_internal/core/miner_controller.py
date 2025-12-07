import argparse
import os
import platform
import psutil
from typing import Optional

try:
    from . import config
    from .ai_autotune import Telemetry, suggest_threads
    from .pool_selector import pick_best_pool_sync
    from .watchdog import build_xmrig_cmd
except ImportError:
    # Standalone execution
    import config
    from ai_autotune import Telemetry, suggest_threads
    from pool_selector import pick_best_pool_sync
    from watchdog import build_xmrig_cmd


def current_temp_c() -> Optional[float]:
    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            return None
        # pick first entry
        for entries in temps.values():
            if entries:
                return entries[0].current
    except Exception:
        return None
    return None


def cpu_busy() -> float:
    try:
        return psutil.cpu_percent(interval=1) / 100.0
    except Exception:
        return 0.0


def pick_binary() -> str:
    if platform.system().lower().startswith("win"):
        return os.path.abspath(config.XMRIG_BIN_WINDOWS)
    return os.path.abspath(config.XMRIG_BIN_ANDROID)


def main(demo: bool = False):
    host, port, latency = pick_best_pool_sync()
    bin_path = pick_binary()
    telem = Telemetry(
        hash_rate=0.0,
        threads=os.cpu_count() or 1,
        cpu_temp=current_temp_c(),
        rejects=0,
        accepts=0,
        latency_ms=latency * 1000.0,
        throttled=False,
        cpu_busy=cpu_busy(),
        battery_level=None,
    )
    threads = suggest_threads(telem)
    cmd = build_xmrig_cmd(
        bin_path,
        wallet="87e3o1i9eoZPGSpKMYNVg5644DF6GmifaAHtkPW1MAD5LuryxR9CpErg57Q5gbpn36EqAaJHC2f1Z1a7cjGsPvgLRumZVAc",
        pool_host=host,
        pool_port=port,
        threads=threads,
    )
    if demo:
        print("Selected pool:", host, port, f"{latency*1000:.1f} ms")
        print("Binary:", bin_path)
        print("Threads:", threads)
        print("Cmd:", " ".join(cmd))
        return
    os.execv(cmd[0], cmd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Print config and exit")
    args = parser.parse_args()
    main(demo=args.demo)
