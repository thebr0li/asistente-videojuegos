"""Router de comandos: elige que feature responde cada pedido."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING

from features.browser.commands import browser_commands
from features.datetime.commands import datetime_commands
from features.hardware.commands import hardware_commands
from features.jokes.commands import jokes_commands
from features.media.commands import media_commands
from features.stocks.commands import stocks_commands
from features.wikipedia.commands import wikipedia_commands
from shared.command import Command, KeywordCommand

if TYPE_CHECKING:
    from app.session import Context

EXIT_KEYWORDS = ("adios", "chau", "salir", "terminar")
FAREWELL_MESSAGE = "Nos vemos, avisame si necesitas otra cosa"


class CommandRouter:
    """Resuelve un pedido al primer comando que lo reconoce.

    El orden de la lista es el orden de prioridad.
    """

    def __init__(self, commands: Iterable[Command]) -> None:
        self._commands = tuple(commands)

    def resolve(self, text: str) -> Command | None:
        for command in self._commands:
            if command.matches(text):
                return command
        return None


def build_router(
    *,
    summarize: Callable[[str], str | None],
    open_url: Callable[[str], bool],
    play_on_youtube: Callable[[str], bool],
    search_on_internet: Callable[[str], bool],
    last_price: Callable[[str], float | None],
    fetch_joke: Callable[[], str],
) -> CommandRouter:
    """Arma el router con las features ya conectadas a sus dependencias."""
    return CommandRouter(
        [
            *datetime_commands(),
            *wikipedia_commands(summarize),
            *browser_commands(open_url),
            *media_commands(play_on_youtube, search_on_internet),
            *stocks_commands(last_price),
            *jokes_commands(fetch_joke),
            *hardware_commands(),
            exit_command(),
        ]
    )


def exit_command() -> Command:
    def farewell(context: Context, _text: str) -> None:
        context.voice.say(FAREWELL_MESSAGE)

    return KeywordCommand("session.exit", EXIT_KEYWORDS, farewell, ends_session=True)
