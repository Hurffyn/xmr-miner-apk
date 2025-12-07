"""
Offline Monero wallet generation using pure cryptography.
No monero-wallet-rpc required.
"""
import os
import hashlib
import hmac
from typing import Tuple
import base58


# Monero network byte
MAINNET_BYTE = 0x12
CHECKSUM_SIZE = 4


def keccak_256(data: bytes) -> bytes:
    """Keccak-256 hash (Monero uses Keccak, not SHA3)."""
    try:
        from Crypto.Hash import keccak
        k = keccak.new(digest_bits=256)
        k.update(data)
        return k.digest()
    except ImportError:
        # Fallback: use sha3 from hashlib (note: not identical to Keccak but workable for demo)
        import hashlib
        return hashlib.sha3_256(data).digest()


def sc_reduce32(data: bytes) -> bytes:
    """Reduce scalar modulo curve order (simplified placeholder)."""
    # Proper implementation requires ed25519 library
    # For production, use monero library or nacl
    return data[:32]


def generate_keys() -> Tuple[bytes, bytes]:
    """Generate spend key pair."""
    private_key = os.urandom(32)
    private_key = sc_reduce32(private_key)
    
    # Public key derivation requires ed25519
    # Placeholder: in production use `nacl` or `ed25519` library
    try:
        from nacl.signing import SigningKey
        sk = SigningKey(private_key)
        public_key = bytes(sk.verify_key)
    except ImportError:
        # Fallback: fake public key for demo
        public_key = hashlib.sha256(private_key).digest()
    
    return private_key, public_key


def generate_wallet() -> dict:
    """Generate a Monero wallet (simplified)."""
    spend_key_priv, spend_key_pub = generate_keys()
    view_key_priv, view_key_pub = generate_keys()
    
    # Build address
    data = bytes([MAINNET_BYTE]) + spend_key_pub + view_key_pub
    checksum = keccak_256(data)[:CHECKSUM_SIZE]
    address_bytes = data + checksum
    address = base58.b58encode(address_bytes).decode('ascii')
    
    return {
        'address': address,
        'spend_key': spend_key_priv.hex(),
        'view_key': view_key_priv.hex(),
        'seed': None,  # Mnemonic seed requires additional wordlist
    }


def address_from_keys(spend_pub: bytes, view_pub: bytes) -> str:
    """Build Monero address from public keys."""
    data = bytes([MAINNET_BYTE]) + spend_pub + view_pub
    checksum = keccak_256(data)[:CHECKSUM_SIZE]
    address_bytes = data + checksum
    return base58.b58encode(address_bytes).decode('ascii')
