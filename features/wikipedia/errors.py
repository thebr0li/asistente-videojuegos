"""Errores de dominio de la busqueda en Wikipedia.

Se definen aca para que los comandos puedan distinguirlos sin importar la
libreria `wikipedia`.
"""

from __future__ import annotations


class AmbiguousQuery(Exception):
    """La consulta tiene varias paginas posibles."""

    def __init__(self, options: list[str]) -> None:
        super().__init__(", ".join(options))
        self.options = options


class LookupFailed(Exception):
    """No se pudo consultar Wikipedia por red o por limite de peticiones."""
