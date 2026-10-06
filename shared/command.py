"""Como se reconoce un pedido y como se ejecuta: lo usan el router y las features."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from shared.text import contains_keyword

if TYPE_CHECKING:
    from app.session import Context

Handler = Callable[["Context", str], None]


class Command(Protocol):
    """Un pedido que el asistente sabe reconocer y ejecutar."""

    name: str
    ends_session: bool

    def matches(self, text: str) -> bool:
        """Indica si este comando responde al pedido."""

    def execute(self, context: Context, text: str) -> None:
        """Realiza la accion del comando."""


@dataclass(frozen=True)
class KeywordCommand:
    """Comando que se reconoce cuando el pedido contiene alguna palabra clave."""

    name: str
    keywords: tuple[str, ...]
    handler: Handler
    ends_session: bool = False

    def matches(self, text: str) -> bool:
        return any(contains_keyword(text, keyword) for keyword in self.keywords)

    def execute(self, context: Context, text: str) -> None:
        self.handler(context, text)
