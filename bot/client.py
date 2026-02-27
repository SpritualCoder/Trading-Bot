"""
Binance Futures Testnet REST client.
Handles signing, sending requests, and basic error handling.
"""

import hashlib
import hmac
import time
from decimal import Decimal
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

from bot.logging_config import get_logger


logger = get_logger("client")

TESTNET_BASE_URL = "https://testnet.binancefuture.com"
DEFAULT_TIMEOUT = 10  # seconds


class BinanceAPIError(Exception):
    """Raised when Binance returns an API-level error."""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Binance API error {code}: {message}")


class BinanceClient:
    """
    Minimal wrapper around Binance Futures Testnet API.
    Responsible for signing and sending requests.
    """

    def __init__(self, api_key: str, api_secret: str, base_url: str = TESTNET_BASE_URL):
        if not api_key or not api_secret:
            raise ValueError("API key and secret must not be empty.")

        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")

        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-MBX-APIKEY": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )

        logger.info("BinanceClient initialized | base_url=%s", self.base_url)

    def _sign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Attach HMAC-SHA256 signature."""
        query_string = urlencode(params)

        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        params["signature"] = signature
        return params

    def _timestamp(self) -> int:
        return int(time.time() * 1000)

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False,
    ) -> Dict[str, Any]:
        """
        Send HTTP request and return JSON response.
        Centralized request + error handling.
        """

        params = params or {}

        if signed:
            params["timestamp"] = self._timestamp()
            params = self._sign(params)

        url = f"{self.base_url}{endpoint}"

        logger.debug(
            "REQUEST %s %s | params=%s",
            method.upper(),
            endpoint,
            {k: v for k, v in params.items() if k != "signature"},
        )

        try:
            response = self.session.request(
                method,
                url,
                params=params if method.upper() == "GET" else None,
                data=params if method.upper() != "GET" else None,
                timeout=DEFAULT_TIMEOUT,
            )

        except requests.exceptions.ConnectionError as exc:
            logger.error("Connection error: %s", exc)
            raise ConnectionError(f"Cannot reach Binance API: {exc}") from exc

        except requests.exceptions.Timeout as exc:
            logger.error("Timeout after %ss: %s", DEFAULT_TIMEOUT, exc)
            raise TimeoutError(f"Request timed out after {DEFAULT_TIMEOUT}s.") from exc

        except requests.exceptions.RequestException as exc:
            logger.error("Unexpected request error: %s", exc)
            raise

        logger.debug(
            "RESPONSE %s %s | status=%s | body=%s",
            method.upper(),
            endpoint,
            response.status_code,
            response.text[:500],
        )

        try:
            data = response.json()
        except ValueError:
            logger.error("Invalid JSON response: %s", response.text[:200])
            raise BinanceAPIError(
                -1, f"Non-JSON response (HTTP {response.status_code})"
            )

        # Handle Binance-specific error structure
        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            if data["code"] < 0:
                raise BinanceAPIError(
                    data["code"], data.get("msg", "Unknown error")
                )

        if not response.ok:
            raise BinanceAPIError(
                response.status_code,
                data.get("msg", response.text[:200])
                if isinstance(data, dict)
                else str(data),
            )

        return data

    # ----------------------------------------------------------
    # Public API methods
    # ----------------------------------------------------------

    def get_exchange_info(self) -> Dict[str, Any]:
        """Return exchange metadata."""
        return self._request("GET", "/fapi/v1/exchangeInfo")

    def get_account(self) -> Dict[str, Any]:
        """Return futures account details."""
        return self._request("GET", "/fapi/v2/account", signed=True)

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Decimal,
        price: Optional[Decimal] = None,
        stop_price: Optional[Decimal] = None,
        time_in_force: str = "GTC",
        reduce_only: bool = False,
    ) -> Dict[str, Any]:
        """
        Place an order and return the response.
        """

        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": str(quantity),
        }

        if order_type == "LIMIT":
            params["timeInForce"] = time_in_force
            params["price"] = str(price)

        elif order_type in ("STOP", "TAKE_PROFIT"):
            params["timeInForce"] = time_in_force
            params["price"] = str(price)
            params["stopPrice"] = str(stop_price)

        elif order_type in ("STOP_MARKET", "TAKE_PROFIT_MARKET"):
            params["stopPrice"] = str(stop_price)

        if reduce_only:
            params["reduceOnly"] = "true"

        logger.info(
            "Placing order | symbol=%s side=%s type=%s qty=%s price=%s stopPrice=%s",
            symbol,
            side,
            order_type,
            quantity,
            price,
            stop_price,
        )

        response = self._request(
            "POST",
            "/fapi/v1/order",
            params=params,
            signed=True,
        )

        logger.info(
            "Order placed | orderId=%s status=%s",
            response.get("orderId"),
            response.get("status"),
        )

        return response

    def get_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Fetch a specific order."""
        return self._request(
            "GET",
            "/fapi/v1/order",
            params={"symbol": symbol, "orderId": order_id},
            signed=True,
        )

    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Cancel an existing order."""
        return self._request(
            "DELETE",
            "/fapi/v1/order",
            params={"symbol": symbol, "orderId": order_id},
            signed=True,
        )