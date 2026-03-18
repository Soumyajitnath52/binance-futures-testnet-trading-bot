"""Low-level Binance Futures Testnet REST client."""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import time
from typing import Any
from urllib.parse import urlencode

try:
    import requests
    from requests import Response, Session
    from requests.exceptions import RequestException
except ModuleNotFoundError as exc:
    raise ImportError(
        "Missing dependency: requests. Install with 'pip install -r requirements.txt'"
    ) from exc

from bot.exceptions import BinanceAPIError


class BinanceFuturesClient:
    """Minimal signed REST client for Binance USDT-M Futures Testnet."""

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        base_url: str = "https://testnet.binancefuture.com",
        timeout: int = 15,
        session: Session | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("BINANCE_API_KEY")
        self.api_secret = api_secret or os.getenv("BINANCE_API_SECRET")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.logger = logging.getLogger(self.__class__.__name__)

        if not self.api_key or not self.api_secret:
            raise ValueError(
                "Missing Binance credentials. Set BINANCE_API_KEY and "
                "BINANCE_API_SECRET environment variables."
            )

    def place_order(self, params: dict[str, Any]) -> dict[str, Any]:
        """Create an order on Binance Futures Testnet."""
        return self._request("POST", "/fapi/v1/order", signed=True, params=params)

    def get_server_time(self) -> dict[str, Any]:
        """Fetch Binance server time."""
        return self._request("GET", "/fapi/v1/time", signed=False)

    def _request(
        self,
        method: str,
        path: str,
        *,
        signed: bool = False,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        params = dict(params or {})
        headers = {"X-MBX-APIKEY": self.api_key}
        url = f"{self.base_url}{path}"

        if signed:
            params["timestamp"] = int(time.time() * 1000)
            params["recvWindow"] = 5000
            params["signature"] = self._sign(params)

        self.logger.info(
            "Sending request | method=%s | path=%s | params=%s",
            method,
            path,
            self._redact_params(params),
        )

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params if method.upper() == "GET" else None,
                data=params if method.upper() != "GET" else None,
                timeout=self.timeout,
            )
        except RequestException as exc:
            self.logger.exception("Network error while calling Binance: %s", exc)
            raise BinanceAPIError(f"Network error while calling Binance: {exc}") from exc

        return self._handle_response(response)

    def _handle_response(self, response: Response) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            self.logger.exception(
                "Received non-JSON response | status=%s | text=%s",
                response.status_code,
                response.text,
            )
            raise BinanceAPIError(
                f"Binance returned a non-JSON response with status {response.status_code}."
            ) from exc

        self.logger.info(
            "Received response | status=%s | body=%s",
            response.status_code,
            payload,
        )

        if response.ok:
            return payload

        message = payload.get("msg", "Unknown Binance API error")
        code = payload.get("code", "N/A")
        raise BinanceAPIError(f"Binance API error {code}: {message}")

    def _sign(self, params: dict[str, Any]) -> str:
        query = urlencode(params, doseq=True)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    @staticmethod
    def _redact_params(params: dict[str, Any]) -> dict[str, Any]:
        redacted = dict(params)
        if "signature" in redacted:
            redacted["signature"] = "***"
        return redacted

