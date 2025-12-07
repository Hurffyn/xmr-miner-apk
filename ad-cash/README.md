# Monero Miner - AI Optimized (Android ARM64 & Windows x64)

> **Ultra-advanced** Monero (RandomX) miner with embedded Python, XMRig integration, neural network auto-tuning, minimal UI (balance-focused), and full automation.

## 🚀 Features

### ✅ Complete Automation
- ✅ Auto-generates Monero wallet locally (offline cryptography)
- ✅ Secure storage: **Windows DPAPI** | **Android Keystore** | **Linux keyring**
- ✅ Auto-selects best pool by latency (moneroocean, supportxmr, minexmr, xmrpool)
- ✅ Starts mining immediately on launch

### 🧠 AI Neural Network
- ✅ **Real-time optimization**: MLP neural network continuously learns from telemetry
- ✅ Auto-adjusts threads based on: hashrate, CPU temp, throttling, battery, latency
- ✅ Maximizes H/s while respecting thermal/battery limits
- ✅ Background training with persistent model

### 🔋 Safety & Protection
- ✅ **Thermal protection**: Auto-reduces load at 85°C (configurable)
- ✅ **Battery guard**: Pauses mining below 20% battery (Android)
- ✅ **Throttle detection**: Backs off when CPU throttling detected
- ✅ Cross-platform sensor monitoring (temperature, battery, CPU usage)

### 📊 Minimal UI (MAX Performance)
- ✅ **Balance display**: Real-time XMR balance from pool API
- ✅ **Hashrate**: Current mining speed (H/s)
- ✅ **Start/Pause**: Single button control
- ✅ No charts, no bloat - pure performance focus

### 🛠️ Technical Stack
- ✅ **XMRig**: Latest binaries embedded (Windows x64 included, ARM64 needs compilation)
- ✅ **Python**: Fully embedded via PyInstaller (Windows) / Buildozer (Android)
- ✅ **Pool API**: MoneroOcean, SupportXMR balance lookups
- ✅ **Watchdog**: Auto-restart on crash

---

## 📁 Project Structure

```
core/
  ├── config.py              # Pool list, thermal limits, paths
  ├── wallet_gen.py          # Offline Monero wallet generation (Keccak, ed25519)
  ├── wallet_storage.py      # DPAPI/Keystore secure storage
  ├── pool_selector.py       # Latency probe + best pool picker
  ├── balance_tracker.py     # Parse XMRig output + pool API
  ├── ai_neural.py           # MLP optimizer with continuous training
  ├── platform_sensors.py    # Battery/temp/throttle detection
  ├── watchdog.py            # XMRig process supervision
  └── metrics.py             # CoinGecko price API (optional)

android/
  ├── main.py                # Kivy UI with AI integration
  ├── buildozer.spec         # APK build configuration
  └── mining_service.py      # Background service (keeps mining alive)

windows/
  ├── launcher.py            # Tkinter UI with AI integration
  └── pyinstaller.spec       # EXE build configuration

bin/
  ├── windows_x64/xmrig.exe  # ✅ Downloaded (6.24.0)
  └── android_arm64/xmrig    # ⚠️ Placeholder (needs compilation - see below)
```

---

## 🎯 Quick Start

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Test Core (Desktop)
```bash
# Demo mode (shows config without mining)
python core/miner_controller.py --demo

# Windows UI test
python windows/launcher.py

# Android UI test (desktop preview)
pip install kivy
python android/main.py
```

---

## 🏗️ Build Instructions

### 🪟 Windows EXE

**Requirements**: Python 3.11+, Windows 10+

```bash
# Automated build
./build_windows.sh

# Manual build
pip install -r requirements.txt pyinstaller
pyinstaller windows/pyinstaller.spec --clean

# Output: dist/XMR_Miner/XMR_Miner.exe
```

**Bundle includes**:
- XMRig 6.24.0 x64
- Python runtime
- All dependencies
- AI model storage

---

### 🤖 Android APK

**Requirements**: Linux (Ubuntu/Debian), Android SDK/NDK, Buildozer

#### ⚠️ XMRig ARM64 Binary Required
Official XMRig releases don't include Android ARM64 builds. **Options**:

**Option A: Compile from source (recommended)**
```bash
git clone https://github.com/xmrig/xmrig
cd xmrig && mkdir build && cd build
cmake .. -DCMAKE_TOOLCHAIN_FILE=$ANDROID_NDK/build/cmake/android.toolchain.cmake \
         -DANDROID_ABI=arm64-v8a \
         -DANDROID_PLATFORM=android-21 \
         -DWITH_HWLOC=OFF
make -j$(nproc)
cp xmrig /var/www/ad-cash/bin/android_arm64/
chmod +x /var/www/ad-cash/bin/android_arm64/xmrig
```

**Option B: Termux build**
```bash
# On Android device with Termux
pkg install xmrig
cp $(which xmrig) /sdcard/xmrig_arm64
# Transfer to development machine
```

**Option C: Third-party build** (⚠️ verify source!)

#### Build APK
```bash
# Automated build
./build_android.sh

# Manual build
cd android
buildozer -v android debug

# Output: android/bin/*.apk
# Install: adb install android/bin/*.apk
```

---

## 🔐 Wallet Management

### Auto-Generated Wallets
- First run creates a new Monero wallet automatically
- **Cryptography**: Offline Keccak-256 + ed25519 (no monero-wallet-rpc needed)
- **Storage**: Encrypted via platform API (DPAPI/Keystore)

### Manual Wallet
Replace auto-generated address in UI or edit default in:
- `core/miner_controller.py`
- `windows/launcher.py`
- `android/main.py`

**⚠️ BACKUP YOUR KEYS**: Spend/view keys shown on first generation. Store securely!

---

## ⚙️ Configuration

Edit `core/config.py`:

```python
# Pool list (auto-selects best latency)
POOLS = [
    ("moneroocean.stream", 443),
    ("supportxmr.com", 3333),
    ("minexmr.com", 443),
    ("xmrpool.net", 443),
]

# Safety limits
DEFAULT_THERMAL_C = 85       # Reduce load above this temp
DEFAULT_BATTERY_MIN = 20     # Pause below this battery %

# Price lookup (optional)
ENABLE_PRICE_LOOKUP = False  # CoinGecko API for fiat conversion
```

---

## 🧪 AI Model Training

The neural network trains automatically in background:

1. **Collects telemetry**: hashrate, CPU temp, threads, throttling, latency, battery
2. **Predicts optimal threads**: Maximizes H/s while respecting constraints
3. **Persists model**: Saved to `~/.xmrminer/ai_model.pkl`
4. **Improves over time**: More data = better predictions

**Manual training reset**:
```bash
rm ~/.xmrminer/ai_model.pkl
```

---

## 📊 Pool API Balance

Supported pools for real-time balance:

| Pool | API Endpoint |
|------|-------------|
| MoneroOcean | `https://api.moneroocean.stream/miner/{wallet}/stats` |
| SupportXMR | `https://supportxmr.com/api/miner/{wallet}/stats` |

Balance updates every ~30 seconds during mining.

---

## 🛡️ Safety & Legal

### ⚠️ Important Disclaimers

1. **Mining requires user consent**: Do not deploy without explicit permission
2. **Jurisdiction compliance**: Check local laws regarding cryptocurrency mining
3. **Platform policies**: Google Play/App Store prohibit mining apps
4. **Power consumption**: Mining drains battery and generates heat
5. **Hardware wear**: Extended mining may reduce device lifespan

### Thermal Protection
- Default limit: **85°C**
- Auto-reduces threads when approaching limit
- Pauses if thermal runaway detected

### Battery Protection
- Auto-pauses below **20%** battery (if not charging)
- Resumes when plugged in or battery recovers

---

## 📦 Dependencies

```
psutil          # System monitoring (CPU, temp, battery)
requests        # Pool API / price lookup
base58          # Monero address encoding
pycryptodome    # Keccak-256 hashing
PyNaCl          # ed25519 cryptography
numpy           # Neural network math
scikit-learn    # (Optional) Advanced ML features
kivy            # Android UI (Buildozer requirement)
pyinstaller     # Windows EXE packaging
```

---

## 🚧 Known Limitations

- ❌ **No official ARM64 XMRig binary**: Must compile manually
- ⚠️ **Wallet generation simplified**: Production needs full BIP39 mnemonic support
- ⚠️ **Pool APIs vary**: Only MoneroOcean/SupportXMR balance tested
- ⚠️ **Android Keystore stub**: Requires Java/JNI integration for full security
- ⚠️ **Background service**: Android 12+ may kill background mining (needs foreground service)

---

## 🎓 Usage Examples

### Windows
1. Run `XMR_Miner.exe`
2. Wallet auto-generates (backup keys shown once!)
3. Click **Start** → Mining begins automatically
4. Balance updates in real-time

### Android
1. Install APK: `adb install xmrminer.apk`
2. Grant permissions (storage, network)
3. Wallet auto-generates on first launch
4. Tap **Start Mining**
5. Lock screen → mining continues in background (if service works)

---

## 🔧 Troubleshooting

### Windows: "XMRig not found"
- Verify `bin/windows_x64/xmrig.exe` exists
- Check antivirus (may quarantine miners)

### Android: "Permission denied"
- Run `chmod +x bin/android_arm64/xmrig`
- Check SELinux policies (may block execution)

### Zero hashrate
- Check pool connectivity: `ping moneroocean.stream`
- Verify wallet address format (95 characters, starts with `4` or `8`)

### AI not optimizing
- Needs ~10+ samples to start predictions
- Check model file: `ls ~/.xmrminer/ai_model.pkl`

---

## 📜 License & Credits

- **XMRig**: GPL-3.0 (https://github.com/xmrig/xmrig)
- **Monero**: BSD-3-Clause (https://github.com/monero-project/monero)
- **This project**: Educational purposes only - use responsibly

**Contributors welcome!** PRs for:
- Full BIP39 mnemonic support
- More pool API integrations
- LSTM neural network upgrade
- iOS port

---

## 🆘 Support

**Issues**: Open GitHub issue with logs  
**Wallet backup**: `~/.xmrminer/wallet.enc` (encrypted)  
**Logs**: Check console output or `buildozer.log` (Android)

---

**⚡ Built for maximum hashrate with minimal overhead. Happy mining! ⚡**
