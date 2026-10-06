from __future__ import annotations

import pyjokes


def tell_joke() -> str:
    return pyjokes.get_joke("es")
