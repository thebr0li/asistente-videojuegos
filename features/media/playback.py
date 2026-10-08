from __future__ import annotations

import pywhatkit


def play_on_youtube(query: str) -> bool:
    """Reproduce una cancion en YouTube. Devuelve False si no se pudo."""
    try:
        pywhatkit.playonyt(query)
        return True
    except Exception:
        return False


def search_on_internet(query: str) -> bool:
    """Abre una busqueda en el navegador. Devuelve False si no se pudo."""
    try:
        pywhatkit.search(query)
        return True
    except Exception:
        return False
