"""CLI entry point for the Binance Futures Testnet trading bot."""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Any

from bot.client import BinanceFuturesClient
from bot.exceptions import BinanceAPIError, ValidationError
from bot.logging_config import configure_logging
from bot.orders import OrderService
from bot.validators import validate_order_inputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Place MARKET or LIMIT orders on Binance Futures Testnet."
    )
    parser.add_argument("--symbol", required=True, help="Trading symbol, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, help="BUY or SELL")
    parser.add_argument(
        "--order-type",
        required=True,
        help="MARKET or LIMIT",
    )
    parser.add_argument(
        "--quantity",
        required=True,
        help="Order quantity as a positive number",
    )
    parser.add_argument(
        "--price",
        help="Limit price. Required when --order-type LIMIT is used.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level, e.g. INFO, DEBUG, WARNING",
    )
    return parser


def print_order_summary(order_data: dict[str, Any]) -> None:
    print("Order Request Summary")
    print(f"  Symbol: {order_data['symbol']}")
    print(f"  Side: {order_data['side']}")
    print(f"  Type: {order_data['order_type']}")
    print(f"  Quantity: {order_data['quantity']}")
    print(f"  Price: {order_data['price'] or 'N/A'}")


def print_order_response(response: dict[str, Any]) -> None:
    print("Order Response Details")
    print(f"  Order ID: {response.get('orderId', 'N/A')}")
    print(f"  Status: {response.get('status', 'N/A')}")
    print(f"  Executed Quantity: {response.get('executedQty', 'N/A')}")
    print(f"  Average Price: {response.get('avgPriceComputed') or 'N/A'}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    log_file = configure_logging(args.log_level)
    logger = logging.getLogger("cli")
    logger.info("CLI started. Log file: %s", log_file)

    try:
        order_data = validate_order_inputs(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )

        print_order_summary(order_data)

        client = BinanceFuturesClient()
        order_service = OrderService(client)
        response = order_service.place_order(
            symbol=order_data["symbol"],
            side=order_data["side"],
            order_type=order_data["order_type"],
            quantity=order_data["quantity"],
            price=order_data["price"],
        )

        print_order_response(response)
        print("Success: order placed successfully.")
        logger.info("Order completed successfully | order_id=%s", response.get("orderId"))
        return 0
    except ValidationError as exc:
        logger.error("Validation error: %s", exc)
        print(f"Failure: {exc}")
        return 2
    except ValueError as exc:
        logger.error("Configuration error: %s", exc)
        print(f"Failure: {exc}")
        return 3
    except BinanceAPIError as exc:
        logger.error("Binance API error: %s", exc)
        print(f"Failure: {exc}")
        return 4
    except Exception as exc:  # pragma: no cover - safeguard for CLI usage
        logger.exception("Unexpected error: %s", exc)
        print(f"Failure: unexpected error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

