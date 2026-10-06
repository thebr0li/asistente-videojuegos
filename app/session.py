"""Estado de la conversacion: lo que el asistente recuerda del usuario."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from features.hardware.models import DetectedParts, HardwareProfile

if TYPE_CHECKING:
    from shared.voice import VoiceService


@dataclass
class Session:
    """Lo que el asistente recuerda del usuario durante la conversacion."""

    hardware: HardwareProfile | None = None
    detected: DetectedParts = field(default_factory=DetectedParts)

    def record_parts(self, parts: DetectedParts) -> None:
        self.detected.merge(parts)


@dataclass(frozen=True)
class Context:
    """Lo que un comando necesita para responder."""

    session: Session
    voice: VoiceService
