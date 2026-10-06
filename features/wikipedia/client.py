"""Cliente de Wikipedia: busca la pagina y devuelve su resumen."""

from __future__ import annotations

import wikipedia

from features.wikipedia.errors import AmbiguousQuery, LookupFailed

LANGUAGE = "es"
USER_AGENT = "AsistenteGamer/1.0 (asistente educativo de videojuegos)"


def configure() -> None:
    wikipedia.set_lang(LANGUAGE)
    wikipedia.set_user_agent(USER_AGENT)


def summarize(query: str) -> str | None:
    """Devuelve el resumen de la pagina mas cercana, o None si no hay pagina."""
    try:
        results = wikipedia.search(query)
        if not results:
            return None
        return wikipedia.summary(results[0], sentences=2)
    except wikipedia.exceptions.DisambiguationError as error:
        raise AmbiguousQuery(error.options) from error
    except wikipedia.exceptions.PageError:
        return None
    except Exception as error:
        raise LookupFailed(str(error)) from error
