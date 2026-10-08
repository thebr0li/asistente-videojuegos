from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from shared.command import Command, KeywordCommand
from shared.text import clean_text

if TYPE_CHECKING:
    from app.session import Context

JOKE_KEYWORDS = ("chiste",)


def jokes_commands(tell_joke: Callable[[], str]) -> list[Command]:
    def answer(context: Context, _text: str) -> None:
        context.voice.say(clean_text(tell_joke()))

    return [KeywordCommand("jokes.tell", JOKE_KEYWORDS, answer)]
