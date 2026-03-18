"""Validation helpers for CLI inputs."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from bot.exceptions import ValidationError

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


def validate_symbol(symbol: str) -> str:
    value = (symbol or "").strip().upper()
    if not value:
        raise ValidationError("Symbol is required.")
    if not value.isalnum():
        raise ValidationError("Symbol must be alphanumeric, e.g. BTCUSDT.")
    return value


def validate_side(side: str) -> str:
    value = (side or "").strip().upper()
    if value not in VALID_SIDES:
        raise ValidationError("Side must be BUY or SELL.")
    return value


def validate_order_type(order_type: str) -> str:
    value = (order_type or "").strip().upper()
    if value not in VALID_ORDER_TYPES:
        raise ValidationError("Order type must be MARKET or LIMIT.")
    return value


def validate_positive_number(raw_value: str | float | int, field_name: str) -> str:
    if raw_value is None or str(raw_value).strip() == "":
        raise ValidationError(f"{field_name} is required.")

    try:
        value = Decimal(str(raw_value))
    except InvalidOperation as exc:
        raise ValidationError(f"{field_name} must be a valid number.") from exc

    if value <= 0:
        raise ValidationError(f"{field_name} must be greater than zero.")

    normalized = format(value.normalize(), "f")
    return normalized.rstrip("0").rstrip(".") if "." in normalized else normalized


def validate_order_inputs(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str | float | int,
    price: str | float | int | None,
) -> dict[str, str | None]:
    validated_type = validate_order_type(order_type)
    validated_price = None

    if validated_type == "LIMIT":
        validated_price = validate_positive_number(price, "Price")
    elif price not in (None, ""):
        raise ValidationError("Price is only allowed for LIMIT orders.")

    return {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": validated_type,
        "quantity": validate_positive_number(quantity, "Quantity"),
        "price": validated_price,
    }

