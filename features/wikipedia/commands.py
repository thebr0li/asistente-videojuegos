from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from features.wikipedia.errors import AmbiguousQuery, LookupFailed
from shared.command import Command, KeywordCommand
from shared.text import clean_text, remove_words

if TYPE_CHECKING:
    from app.session import Context

WIKIPEDIA_KEYWORDS = ("wikipedia",)
QUERY_NOISE = ("busca en wikipedia", "buscar en wikipedia", "wikipedia", "busca", "buscar")


def find_query(text: str) -> str:
    """Saca las palabras del comando y deja el tema a consultar."""
    return remove_words(text, QUERY_NOISE)


def wikipedia_commands(summarize: Callable[[str], str | None]) -> list[Command]:
    def answer(context: Context, text: str) -> None:
        context.voice.say("Buscando en wikipedia")

        try:
            summary = summarize(find_query(text))
        except AmbiguousQuery as error:
            context.voice.say("Hay varias opciones: " + ", ".join(error.options[:3]))
            return
        except LookupFailed:
            context.voice.say("No pude buscar en wikipedia en este momento")
            return

        if not summary:
            context.voice.say("No encontre informacion sobre eso")
            return

        context.voice.say(clean_text(summary))

    return [KeywordCommand("wikipedia.summary", WIKIPEDIA_KEYWORDS, answer)]
