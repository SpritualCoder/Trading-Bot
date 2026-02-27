"""
Handles order placement and formatting of order responses.

Acts as a bridge between:
CLI layer  →  Validation  →  Binance client
"""

from decimal import Decimal
from typing import Any, Dict, Optional

from bot.client import BinanceClient, BinanceAPIError
from bot.logging_config import get_logger
from bot.validators import validate_order_inputs, ValidationError


logger = get_logger("orders")


def _fmt(value: Any, default: str = "N/A") -> str:
    """
    Convert a value to string.
    If empty or zero-like, return a default placeholder.
    """
    if value in (None, "", "0", 0):
        return default
    return str(value)


def format_order_response(response: Dict[str, Any]) -> str:
    """
    Format Binance order response into a readable block.

    Works for:
    - Newly placed orders
    - Fetched existing orders
    """

    order_type = response.get("type") or response.get("origType")

    lines = []
    lines.append("")
    lines.append("====================================================")
    lines.append("                  ORDER DETAILS                     ")
    lines.append("====================================================")
    lines.append(f"Order ID        : {_fmt(response.get('orderId'))}")
    lines.append(f"Client Order ID : {_fmt(response.get('clientOrderId'))}")
    lines.append(f"Symbol          : {_fmt(response.get('symbol'))}")
    lines.append(f"Side            : {_fmt(response.get('side'))}")
    lines.append(f"Type            : {_fmt(order_type)}")
    lines.append(f"Status          : {_fmt(response.get('status'))}")
    lines.append(f"Quantity        : {_fmt(response.get('origQty'))}")
    lines.append(f"Executed Qty    : {_fmt(response.get('executedQty'))}")
    lines.append(f"Average Price   : {_fmt(response.get('avgPrice'))}")
    lines.append(f"Price           : {_fmt(response.get('price'))}")
    lines.append(f"Stop Price      : {_fmt(response.get('stopPrice'))}")
    lines.append(f"Time in Force   : {_fmt(response.get('timeInForce'))}")
    lines.append(f"Reduce Only     : {response.get('reduceOnly', False)}")
    lines.append(f"Last Update     : {_fmt(response.get('updateTime'))}")
    lines.append("----------------------------------------------------")

    return "\n".join(lines)


def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str] = None,
    stop_price: Optional[str] = None,
    time_in_force: str = "GTC",
    reduce_only: bool = False,
) -> Dict[str, Any]:
    """
    Validate inputs and forward the order to Binance.

    Returns:
        Raw response dictionary from the Binance API.

    Raises:
        ValidationError
        BinanceAPIError
    """

    # -------------------------
    # Step 1: Validate inputs
    # -------------------------
    validated = validate_order_inputs(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
        stop_price=stop_price,
    )

    # -------------------------
    # Step 2: Log what we're about to do
    # -------------------------
    logger.info(
        "Placing order | symbol=%s side=%s type=%s qty=%s price=%s stopPrice=%s",
        validated["symbol"],
        validated["side"],
        validated["order_type"],
        validated["quantity"],
        validated["price"],
        validated["stop_price"],
    )

    # -------------------------
    # Step 3: Send to Binance
    # -------------------------
    response = client.place_order(
        symbol=validated["symbol"],
        side=validated["side"],
        order_type=validated["order_type"],
        quantity=validated["quantity"],
        price=validated["price"],
        stop_price=validated["stop_price"],
        time_in_force=time_in_force,
        reduce_only=reduce_only,
    )

    return response