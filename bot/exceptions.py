"""Application-specific exception types."""


class ValidationError(Exception):
    """Raised when CLI input fails validation."""


class BinanceAPIError(Exception):
    """Raised when Binance returns an error response."""

