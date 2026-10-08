from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from shared.command import Command, KeywordCommand
from shared.text import remove_words

if TYPE_CHECKING:
    from app.session import Context

SEARCH_KEYWORDS = ("busca en internet", "buscar en internet")
SEARCH_NOISE = ("buscar en internet", "busca en internet")

PLAY_KEYWORDS = ("reproducir", "reproduce", "poner", "pone", "cancion")
SONG_NOISE = (
    "reproducir",
    "reproduce",
    "reproducime",
    "poner",
    "poneme",
    "pon",
    "pone",
    "en youtube",
    "cancion",
    "canción",
)


def find_song(text: str) -> str:
    """Saca las palabras del comando y deja el nombre de la cancion."""
    return remove_words(text, SONG_NOISE)


def media_commands(
    play_on_youtube: Callable[[str], bool],
    search_on_internet: Callable[[str], bool],
) -> list[Command]:
    def search(context: Context, text: str) -> None:
        context.voice.say("Buscando en internet")
        if not search_on_internet(remove_words(text, SEARCH_NOISE)):
            context.voice.say("No pude buscar en internet en este momento")

    def play(context: Context, text: str) -> None:
        song = find_song(text)
        if not song:
            context.voice.say("Que cancion queres que reproduzca?")
            return

        context.voice.say("Reproduciendo " + song + " en YouTube")
        if not play_on_youtube(song):
            context.voice.say("No pude reproducir la cancion en YouTube")

    return [
        KeywordCommand("media.search", SEARCH_KEYWORDS, search),
        KeywordCommand("media.play", PLAY_KEYWORDS, play),
    ]
