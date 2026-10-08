from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from shared.command import Command, KeywordCommand

if TYPE_CHECKING:
    from app.session import Context

YOUTUBE_URL = "https://www.youtube.com"
GOOGLE_URL = "https://www.google.com"

YOUTUBE_KEYWORDS = ("abrir youtube",)
GOOGLE_KEYWORDS = ("abrir google", "abrir navegador", "abrir el navegador")


def browser_commands(open_url: Callable[[str], bool]) -> list[Command]:
    def open_youtube(context: Context, _text: str) -> None:
        context.voice.say("Abriendo YouTube")
        open_url(YOUTUBE_URL)

    def open_google(context: Context, _text: str) -> None:
        context.voice.say("Abriendo el navegador")
        open_url(GOOGLE_URL)

    return [
        KeywordCommand("browser.youtube", YOUTUBE_KEYWORDS, open_youtube),
        KeywordCommand("browser.google", GOOGLE_KEYWORDS, open_google),
    ]
