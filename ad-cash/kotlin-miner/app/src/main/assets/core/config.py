POOLS = [
    ("gulf.moneroocean.stream", 10128),
    ("pool.supportxmr.com", 3333),
    ("xmr-eu1.nanopool.org", 14433),
    ("xmr.2miners.com", 2222),
    ("hashvault.pro", 3333),
    ("moneroocean.stream", 10032),
    ("supportxmr.com", 5555),
    ("xmrpool.net", 3333),
    ("c3pool.com", 15555),
    ("nanopool.org", 14444),
]

DEFAULT_THERMAL_C = 90
DEFAULT_BATTERY_MIN = 15  # percent
WATCHDOG_INTERVAL_SEC = 30
PING_TIMEOUT_SEC = 3.0
PING_ATTEMPTS = 2

# Thread limits will be determined at runtime; these are caps
THREAD_CAP_RATIO = 1.0  # use all logical CPUs by default

# Paths to xmrig binaries (override via CLI/env as needed)
XMRIG_BIN_ANDROID = "../bin/android_arm64/xmrig"
XMRIG_BIN_WINDOWS = "bin/windows_x64/xmrig.exe"

# Coin price API toggle
ENABLE_PRICE_LOOKUP = False
COINGECKO_ID = "monero"
FIAT_CODE = "usd"
