"""Quick auth debug script — run this to test your keys directly."""
import os
import time
import hmac
import hashlib
from urllib.parse import urlencode
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

import requests

api_key = os.environ.get("BINANCE_TESTNET_API_KEY", "").strip()
api_secret = os.environ.get("BINANCE_TESTNET_API_SECRET", "").strip()

print(f"API Key    : {api_key[:8]}...{api_key[-4:]} (length: {len(api_key)})")
print(f"API Secret : {api_secret[:8]}...{api_secret[-4:]} (length: {len(api_secret)})")

# Test a simple signed request — get account balance
params = {"timestamp": int(time.time() * 1000)}
query_string = urlencode(params)
signature = hmac.new(
    api_secret.encode("utf-8"),
    query_string.encode("utf-8"),
    hashlib.sha256,
).hexdigest()
params["signature"] = signature

url = "https://testnet.binancefuture.com/fapi/v2/balance"
headers = {"X-MBX-APIKEY": api_key}

print("\nSending test request to Binance Futures Testnet...")
response = requests.get(url, params=params, headers=headers, timeout=10)
print(f"Status Code : {response.status_code}")
print(f"Response    : {response.text[:300]}")