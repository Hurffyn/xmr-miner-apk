"""
Platform-specific battery and temperature sensors.
"""
import os
import platform
import psutil
from typing import Optional


def get_battery_level() -> Optional[int]:
    """Get battery level percentage (0-100) or None if not available."""
    try:
        battery = psutil.sensors_battery()
        if battery:
            return int(battery.percent)
    except Exception:
        pass
    
    # Android-specific (requires Java/JNI or adb shell)
    if platform.system() == 'Linux' and ('ANDROID_ROOT' in os.environ or 'ANDROID_DATA' in os.environ):
        try:
            # Try reading from Android system files
            with open('/sys/class/power_supply/battery/capacity', 'r') as f:
                return int(f.read().strip())
        except Exception:
            pass
    
    return None


def is_charging() -> bool:
    """Check if device is charging."""
    try:
        battery = psutil.sensors_battery()
        if battery:
            return battery.power_plugged
    except Exception:
        pass
    
    # Android-specific
    if platform.system() == 'Linux' and ('ANDROID_ROOT' in os.environ or 'ANDROID_DATA' in os.environ):
        try:
            with open('/sys/class/power_supply/battery/status', 'r') as f:
                status = f.read().strip().lower()
                return 'charging' in status or 'full' in status
        except Exception:
            pass
    
    return False


def get_cpu_temperature() -> Optional[float]:
    """Get CPU temperature in Celsius or None if not available."""
    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            return None
        
        # Try common sensor names
        for name in ['coretemp', 'cpu_thermal', 'k10temp', 'zenpower', 'acpitz']:
            if name in temps and temps[name]:
                return temps[name][0].current
        
        # Fallback: first available sensor
        for entries in temps.values():
            if entries:
                return entries[0].current
    except Exception:
        pass
    
    # Android-specific
    if platform.system() == 'Linux':
        try:
            # Try common thermal zones
            for zone in range(10):
                path = f'/sys/class/thermal/thermal_zone{zone}/temp'
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        # Usually in millidegrees
                        temp = int(f.read().strip()) / 1000.0
                        if 20 < temp < 120:  # Sanity check
                            return temp
        except Exception:
            pass
    
    return None


def is_throttling() -> bool:
    """Detect if CPU is being throttled."""
    try:
        # Check CPU frequency scaling
        freq = psutil.cpu_freq()
        if freq:
            # If current is significantly below max, likely throttling
            if freq.max > 0 and freq.current < freq.max * 0.7:
                return True
    except Exception:
        pass
    
    # Linux throttling detection
    if platform.system() == 'Linux':
        try:
            # Check thermal throttle events (Intel)
            if os.path.exists('/sys/devices/system/cpu/cpu0/thermal_throttle/core_throttle_count'):
                with open('/sys/devices/system/cpu/cpu0/thermal_throttle/core_throttle_count', 'r') as f:
                    count = int(f.read().strip())
                    # If count is increasing, throttling occurred
                    return count > 0
        except Exception:
            pass
    
    return False


def should_reduce_load(thermal_limit: float = 90.0, battery_min: int = 15) -> bool:
    """
    Determine if mining should be reduced/paused.
    Returns True if thermal or battery limits are exceeded.
    """
    temp = get_cpu_temperature()
    if temp and temp >= thermal_limit:
        return True
    
    battery = get_battery_level()
    if battery is not None and battery <= battery_min and not is_charging():
        return True
    
    # Removed throttling check - too sensitive
    
    return False


class PlatformMonitor:
    """Continuous monitoring of platform sensors."""
    
    def __init__(self, thermal_limit: float = 90.0, battery_min: int = 15):
        self.thermal_limit = thermal_limit
        self.battery_min = battery_min
    
    def get_state(self) -> dict:
        """Get current platform state."""
        return {
            'cpu_temp': get_cpu_temperature(),
            'battery_level': get_battery_level(),
            'is_charging': is_charging(),
            'is_throttling': is_throttling(),
            'should_reduce': should_reduce_load(self.thermal_limit, self.battery_min),
            'cpu_usage': psutil.cpu_percent(interval=0.5) / 100.0,
        }
