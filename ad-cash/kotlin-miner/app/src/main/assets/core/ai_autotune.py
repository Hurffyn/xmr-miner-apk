import multiprocessing
from dataclasses import dataclass
from typing import Optional


@dataclass
class Telemetry:
    hash_rate: float
    threads: int
    cpu_temp: Optional[float]
    rejects: int
    accepts: int
    latency_ms: float
    throttled: bool
    cpu_busy: float
    battery_level: Optional[int]


def suggest_threads(telemetry: Telemetry) -> int:
    """
    Simple heuristic placeholder. Replace with real model:
    - If near thermal ceiling or throttled, back off threads by 1.
    - Else try to saturate logical CPUs.
    """
    logical_cpus = multiprocessing.cpu_count()
    target = logical_cpus
    if telemetry.cpu_temp and telemetry.cpu_temp > 82:
        target = max(1, telemetry.threads - 1)
    if telemetry.throttled:
        target = max(1, telemetry.threads - 1)
    if telemetry.cpu_busy > 0.9:
        target = max(1, target - 1)
    return max(1, min(target, logical_cpus))
