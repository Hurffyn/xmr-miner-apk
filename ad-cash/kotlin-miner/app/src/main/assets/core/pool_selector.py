import asyncio
import random
from typing import List, Tuple

from . import config


async def _probe(host: str, port: int, timeout: float) -> float:
    start = asyncio.get_event_loop().time()
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
        writer.close()
        if hasattr(writer, "wait_closed"):
            await writer.wait_closed()
        return asyncio.get_event_loop().time() - start
    except Exception:
        return float("inf")


async def pick_best_pool(pools: List[Tuple[str, int]] = None) -> Tuple[str, int, float]:
    """Return (host, port, latency_seconds)."""
    pools = pools or config.POOLS
    measurements = []
    for host, port in pools:
        best = float("inf")
        for _ in range(config.PING_ATTEMPTS):
            lat = await _probe(host, port, config.PING_TIMEOUT_SEC)
            best = min(best, lat)
        measurements.append((host, port, best))
    measurements = [m for m in measurements if m[2] != float("inf")]
    if not measurements:
        # fallback: random choice
        host, port = random.choice(pools)
        return host, port, float("inf")
    measurements.sort(key=lambda x: x[2])
    return measurements[0]


def pick_best_pool_sync(pools: List[Tuple[str, int]] = None) -> Tuple[str, int, float]:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create a new loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        # No event loop in current thread, create one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(pick_best_pool(pools))
