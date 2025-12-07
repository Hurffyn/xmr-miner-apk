"""
Lightweight wrapper around `monero` Python library for local wallet generation.
Install with: pip install monero
"""
from monero.wallet import Wallet
from monero.backends.jsonrpc import JSONRPCWallet


def create_local_wallet(name: str = "local-wallet", host: str = "localhost", port: int = 18083):
    """
    Creates or opens a local monero-wallet-rpc instance.
    NOTE: This requires a running monero-wallet-rpc; for pure offline keygen,
    integrate a Cryptonote keygen library instead.
    """
    wallet = Wallet(JSONRPCWallet(host=host, port=port, user="", password=""))
    return wallet
