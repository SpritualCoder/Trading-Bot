#Basic input validation for trading bot CLI parameters.

from decimal import Decimal, InvalidOperation
from typing import Optional


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {
    "MARKET",
    "LIMIT",
    "STOP_MARKET",
    "STOP",
    "TAKE_PROFIT",
    "TAKE_PROFIT_MARKET",
}


class ValidationError(ValueError):
    #Raised when user input is invalid.
    pass


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()

    if not symbol or not symbol.isalnum():
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Use alphanumeric format like BTCUSDT."
        )

    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()

    if side not in VALID_SIDES:
        allowed = ", ".join(sorted(VALID_SIDES))
        raise ValidationError(f"Invalid side '{side}'. Allowed: {allowed}.")

    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()

    if order_type not in VALID_ORDER_TYPES:
        allowed = ", ".join(sorted(VALID_ORDER_TYPES))
        raise ValidationError(f"Invalid order type '{order_type}'. Allowed: {allowed}.")

    return order_type


def validate_quantity(quantity: str) -> Decimal:
    try:
        qty = Decimal(str(quantity))
    except InvalidOperation:
        raise ValidationError(
            f"Invalid quantity '{quantity}'. It must be a positive number."
        )

    if qty <= 0:
        raise ValidationError(f"Quantity must be greater than zero (got {qty}).")

    return qty


def validate_price(price: Optional[str]) -> Optional[Decimal]:
    if price is None:
        return None

    try:
        value = Decimal(str(price))
    except InvalidOperation:
        raise ValidationError(
            f"Invalid price '{price}'. It must be a positive number."
        )

    if value <= 0:
        raise ValidationError(f"Price must be greater than zero (got {value}).")

    return value


def validate_order_inputs(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str] = None,
    stop_price: Optional[str] = None,
) -> dict:
    """
    Validate all order inputs and return cleaned values.
    """

    validated = {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": validate_order_type(order_type),
        "quantity": validate_quantity(quantity),
        "price": None,
        "stop_price": None,
    }

    ot = validated["order_type"]

    if ot == "LIMIT":
        if price is None:
            raise ValidationError("Price is required for LIMIT orders.")
        validated["price"] = validate_price(price)

    elif ot in ("STOP", "TAKE_PROFIT"):
        if price is None:
            raise ValidationError(f"Limit price is required for {ot} orders.")
        if stop_price is None:
            raise ValidationError(f"Stop price is required for {ot} orders.")

        validated["price"] = validate_price(price)
        validated["stop_price"] = validate_price(stop_price)

    elif ot in ("STOP_MARKET", "TAKE_PROFIT_MARKET"):
        if stop_price is None:
            raise ValidationError(f"Stop price is required for {ot} orders.")

        validated["stop_price"] = validate_price(stop_price)

    return validated