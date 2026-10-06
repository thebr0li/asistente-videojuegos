from __future__ import annotations

import yfinance as yf


def last_price(ticker: str) -> float | None:
    """Ultimo precio de una accion, o None si no se pudo consultar."""
    try:
        quote = yf.Ticker(ticker)
        price = quote.info.get("regularMarketPrice")
        if price is None:
            price = quote.fast_info["last_price"]
        return round(float(price), 2)
    except Exception:
        return None
