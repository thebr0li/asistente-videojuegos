from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from shared.command import Command, KeywordCommand

if TYPE_CHECKING:
    from app.session import Context

STOCKS_KEYWORDS = ("accion", "bolsa")

TICKERS = {
    "nvidia": "NVDA",
    "amd": "AMD",
    "intel": "INTC",
    "sony": "SONY",
    "microsoft": "MSFT",
    "logitech": "LOGI",
    "corsair": "CRSR",
    "electronic arts": "EA",
    "ea": "EA",
    "take two": "TTWO",
}


def find_company(text: str) -> str:
    """La empresa es lo que el usuario dice despues de la ultima 'de'."""
    return text.rsplit("de", 1)[-1].strip().lower()


def stocks_commands(last_price: Callable[[str], float | None]) -> list[Command]:
    def answer(context: Context, text: str) -> None:
        company = find_company(text)
        ticker = TICKERS.get(company)
        if ticker is None:
            context.voice.say("No tengo informacion sobre la accion de " + company)
            return

        price = last_price(ticker)
        if price is None:
            context.voice.say("No pude encontrar la informacion de la accion")
            return

        context.voice.say(f"El precio de {company} es {price} dolares")

    return [KeywordCommand("stocks.price", STOCKS_KEYWORDS, answer)]
