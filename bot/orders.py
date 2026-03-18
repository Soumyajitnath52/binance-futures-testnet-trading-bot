"""Order orchestration logic."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from bot.client import BinanceFuturesClient


class OrderService:
    """Application service responsible for order placement."""

    def __init__(self, client: BinanceFuturesClient) -> None:
        self.client = client

    def place_order(
        self,
        *,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
            "newOrderRespType": "RESULT",
        }

        if order_type == "LIMIT":
            params["price"] = price
            params["timeInForce"] = "GTC"

        response = self.client.place_order(params)
        response["avgPriceComputed"] = self._compute_avg_price(response)
        return response

    @staticmethod
    def _compute_avg_price(response: dict[str, Any]) -> str | None:
        avg_price = response.get("avgPrice")
        if avg_price and avg_price != "0.00000":
            return str(avg_price)

        executed_qty = response.get("executedQty")
        cum_quote = response.get("cumQuote")
        if not executed_qty or not cum_quote:
            return None

        try:
            qty = Decimal(str(executed_qty))
            quote = Decimal(str(cum_quote))
        except InvalidOperation:
            return None

        if qty <= 0:
            return None

        return format((quote / qty).normalize(), "f")

