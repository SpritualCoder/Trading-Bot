#!/usr/bin/env python3
import os
import sys
import argparse
from pathlib import Path

# Ensure local modules are accessible
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try loading .env if available
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

from bot.logging_config import setup_logging, get_logger
from bot.client import BinanceClient, BinanceAPIError
from bot.orders import place_order, format_order_response
from bot.validators import ValidationError


BANNER = """
========================================================
      Binance Futures Testnet - Trading Bot
========================================================
"""


def _get_client() -> BinanceClient:
    """Create Binance client from environment variables."""
    api_key = os.environ.get("BINANCE_TESTNET_API_KEY", "").strip()
    api_secret = os.environ.get("BINANCE_TESTNET_API_SECRET", "").strip()

    if not api_key or not api_secret:
        print("\n[ERROR] API credentials not found.")
        print("Please add the following to your .env file:")
        print("  BINANCE_TESTNET_API_KEY=your_key")
        print("  BINANCE_TESTNET_API_SECRET=your_secret\n")
        sys.exit(1)

    return BinanceClient(api_key=api_key, api_secret=api_secret)


def _print_request_summary(symbol, side, order_type, quantity, price, stop_price) -> None:
    """Print a small summary before placing the order."""
    print("\n----------- Order Summary -----------")
    print(f"Symbol   : {symbol.upper()}")
    print(f"Side     : {side.upper()}")
    print(f"Type     : {order_type.upper()}")
    print(f"Quantity : {quantity}")

    if price:
        print(f"Price    : {price}")
    if stop_price:
        print(f"Stop     : {stop_price}")

    print("-------------------------------------\n")


def run_order(symbol, side, order_type, quantity, price=None, stop_price=None) -> None:
    """
    Validate inputs, send order request,
    and print the final response.
    """
    logger = get_logger("cli")

    _print_request_summary(symbol, side, order_type, quantity, price, stop_price)
    client = _get_client()

    try:
        response = place_order(
            client=client,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=str(quantity),
            price=str(price) if price else None,
            stop_price=str(stop_price) if stop_price else None,
        )

    except ValidationError as exc:
        logger.error("Validation error: %s", exc)
        print(f"\n[VALIDATION ERROR] {exc}")
        sys.exit(2)

    except BinanceAPIError as exc:
        logger.error("API error (%s): %s", exc.code, exc.message)
        print(f"\n[API ERROR] Code {exc.code}: {exc.message}")
        sys.exit(3)

    except (ConnectionError, TimeoutError) as exc:
        logger.error("Network issue: %s", exc)
        print(f"\n[NETWORK ERROR] {exc}")
        sys.exit(4)

    print(format_order_response(response))
    print("\nOrder placed successfully ✔\n")



def interactive_mode() -> None:
    print(BANNER)
    print("Interactive Mode (Press Ctrl+C to exit)\n")

    try:
        symbol = input("Symbol (default BTCUSDT): ").strip()
        if not symbol:
            symbol = "BTCUSDT"

        print("\nChoose Side:")
        print("1. BUY")
        print("2. SELL")
        side_choice = input("Enter 1 or 2: ").strip()
        side = "SELL" if side_choice == "2" else "BUY"

        print("\nChoose Order Type:")
        print("1. MARKET")
        print("2. LIMIT")
        print("3. STOP_MARKET")
        type_choice = input("Enter 1/2/3: ").strip()

        order_type = {
            "1": "MARKET",
            "2": "LIMIT",
            "3": "STOP_MARKET"
        }.get(type_choice, "MARKET")

        quantity = input("\nQuantity (e.g., 0.01): ").strip()

        price = None
        stop_price = None

        if order_type == "LIMIT":
            price = input("Limit Price: ").strip()

        elif order_type == "STOP_MARKET":
            stop_price = input("Stop Price: ").strip()

        run_order(symbol, side, order_type, quantity, price, stop_price)

    except KeyboardInterrupt:
        print("\nExiting... Bye!\n")
        sys.exit(0)

    except ValueError as exc:
        print(f"\nInvalid input: {exc}")
        sys.exit(2)



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading-bot",
        description="Binance Futures Testnet Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument("--symbol", required=True, help="Trading pair (e.g., BTCUSDT)")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL"], help="BUY or SELL")
    parser.add_argument(
        "--type",
        required=True,
        choices=["MARKET", "LIMIT", "STOP_MARKET"],
        metavar="MARKET|LIMIT|STOP_MARKET",
        help="Order type"
    )
    parser.add_argument("--quantity", required=True, type=float, help="Order quantity")
    parser.add_argument("--price", type=float, default=None, help="Limit price (for LIMIT)")
    parser.add_argument(
        "--stop-price",
        type=float,
        default=None,
        dest="stop_price",
        help="Stop price (for STOP_MARKET)"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )

    return parser


def main() -> None:
    setup_logging("INFO")

    # If no CLI arguments → interactive mode
    if len(sys.argv) == 1:
        interactive_mode()
        return

    parser = build_parser()
    args = parser.parse_args()

    setup_logging(args.log_level)
    get_logger("cli").info("Started via CLI flags")

    print(BANNER)

    run_order(
        args.symbol,
        args.side,
        args.type,
        args.quantity,
        args.price,
        args.stop_price
    )


if __name__ == "__main__":
    main()