from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from features.hardware.compatibility import UNKNOWN_GAME_MESSAGE, check_compatibility
from features.hardware.models import DetectedParts
from features.hardware.parser import build_profile, detect_parts, find_game
from shared.command import Command, KeywordCommand
from shared.text import contains_keyword

if TYPE_CHECKING:
    from app.session import Context

COMPONENT_KEYWORDS = ("componentes", "mi pc", "mi equipo")
GAME_KEYWORDS = ("me corre", "corre")


def report_detected(parts: DetectedParts) -> None:
    if parts.gpu_model is not None:
        print("Grafica detectada:", parts.gpu_model)
    if parts.cpu_model is not None:
        print("Procesador detectado:", parts.cpu_model)
    if parts.ram is not None:
        print("Ram detectada:", parts.ram, "GB")


def hardware_commands() -> list[Command]:
    return [
        KeywordCommand("hardware.game", GAME_KEYWORDS, answer_game),
        RecordComponents(),
    ]


def answer_game(context: Context, text: str) -> None:
    game = find_game(text)
    if game is None:
        context.voice.say(UNKNOWN_GAME_MESSAGE)
        return

    profile = context.session.hardware
    if profile is None:
        context.voice.say("Primero decime tus componentes")
        return

    context.voice.say(check_compatibility(profile, game))


@dataclass(frozen=True)
class RecordComponents:
    """Guarda los componentes que aparecen en el pedido y pide los que faltan."""

    name: str = "hardware.components"
    ends_session: bool = False

    def matches(self, text: str) -> bool:
        if not detect_parts(text).is_empty:
            return True
        return any(contains_keyword(text, keyword) for keyword in COMPONENT_KEYWORDS)

    def execute(self, context: Context, text: str) -> None:
        parts = detect_parts(text)
        report_detected(parts)

        context.session.record_parts(parts)
        missing = context.session.detected.missing_components
        if missing:
            context.voice.say("Anote. Todavia me falta " + ", ".join(missing))
            return

        context.session.hardware = build_profile(context.session.detected)
        context.voice.say("Perfecto, ya tengo tu equipo completo")
