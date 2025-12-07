import requests

from . import config


def fetch_price(fiat: str = None) -> float:
    fiat = fiat or config.FIAT_CODE
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={config.COINGECKO_ID}&vs_currencies={fiat}"
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    data = r.json()
    return float(data[config.COINGECKO_ID][fiat])
