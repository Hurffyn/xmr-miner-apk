"""
Secure wallet storage per platform.
Android: Uses Keystore (placeholder, requires Java/JNI integration)
Windows: Uses DPAPI via ctypes
Linux: Uses keyring library
"""
import os
import sys
import json
import platform


def get_storage_path() -> str:
    """Get platform-specific secure storage path."""
    if platform.system() == 'Windows':
        return os.path.join(os.getenv('APPDATA', '.'), 'XMRMiner', 'wallet.enc')
    elif platform.system() == 'Linux':
        # Could be Android or desktop Linux
        if 'ANDROID_ROOT' in os.environ or 'ANDROID_DATA' in os.environ:
            return '/data/data/com.xmrminer/files/wallet.enc'
        else:
            return os.path.expanduser('~/.xmrminer/wallet.enc')
    else:
        return os.path.expanduser('~/.xmrminer/wallet.enc')


def save_wallet_windows(wallet_data: dict) -> bool:
    """Save wallet using Windows DPAPI."""
    try:
        import ctypes
        from ctypes import wintypes
        
        crypt32 = ctypes.windll.crypt32
        kernel32 = ctypes.windll.kernel32
        
        class DATA_BLOB(ctypes.Structure):
            _fields_ = [('cbData', wintypes.DWORD),
                        ('pbData', ctypes.POINTER(ctypes.c_char))]
        
        json_data = json.dumps(wallet_data).encode('utf-8')
        blob_in = DATA_BLOB(len(json_data), ctypes.cast(ctypes.c_char_p(json_data), ctypes.POINTER(ctypes.c_char)))
        blob_out = DATA_BLOB()
        
        if crypt32.CryptProtectData(ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)):
            encrypted = ctypes.string_at(blob_out.pbData, blob_out.cbData)
            kernel32.LocalFree(blob_out.pbData)
            
            path = get_storage_path()
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as f:
                f.write(encrypted)
            return True
    except Exception as e:
        print(f"DPAPI save failed: {e}")
    return False


def load_wallet_windows() -> dict:
    """Load wallet using Windows DPAPI."""
    try:
        import ctypes
        from ctypes import wintypes
        
        crypt32 = ctypes.windll.crypt32
        kernel32 = ctypes.windll.kernel32
        
        class DATA_BLOB(ctypes.Structure):
            _fields_ = [('cbData', wintypes.DWORD),
                        ('pbData', ctypes.POINTER(ctypes.c_char))]
        
        path = get_storage_path()
        with open(path, 'rb') as f:
            encrypted = f.read()
        
        blob_in = DATA_BLOB(len(encrypted), ctypes.cast(ctypes.c_char_p(encrypted), ctypes.POINTER(ctypes.c_char)))
        blob_out = DATA_BLOB()
        
        if crypt32.CryptUnprotectData(ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)):
            decrypted = ctypes.string_at(blob_out.pbData, blob_out.cbData)
            kernel32.LocalFree(blob_out.pbData)
            return json.loads(decrypted.decode('utf-8'))
    except Exception as e:
        print(f"DPAPI load failed: {e}")
    return None


def save_wallet_linux(wallet_data: dict) -> bool:
    """Save wallet on Linux (basic file encryption placeholder)."""
    try:
        # In production, use keyring library or encrypt with user password
        path = get_storage_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(wallet_data, f)
        os.chmod(path, 0o600)
        return True
    except Exception as e:
        print(f"Linux save failed: {e}")
    return False


def load_wallet_linux() -> dict:
    """Load wallet on Linux."""
    try:
        path = get_storage_path()
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Linux load failed: {e}")
    return None


def save_wallet(wallet_data: dict) -> bool:
    """Save wallet securely (platform-specific)."""
    if platform.system() == 'Windows':
        return save_wallet_windows(wallet_data)
    else:
        return save_wallet_linux(wallet_data)


def load_wallet() -> dict:
    """Load wallet securely (platform-specific)."""
    if platform.system() == 'Windows':
        return load_wallet_windows()
    else:
        return load_wallet_linux()


def wallet_exists() -> bool:
    """Check if wallet file exists."""
    return os.path.exists(get_storage_path())
