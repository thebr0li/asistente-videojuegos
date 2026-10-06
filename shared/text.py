"""Utilidades para trabajar con el texto reconocido por el microfono."""

import re
import unicodedata
from collections.abc import Iterable

ZERO_WIDTH_SPACE = "\u200b"


def normalize(text: str) -> str:
    """Pasa el texto a minusculas sin tildes para poder compararlo."""
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def contains_keyword(text: str, keyword: str) -> bool:
    """Indica si el texto contiene la palabra, ignorando tildes y mayusculas."""
    return normalize(keyword) in normalize(text)


def remove_words(text: str, words: Iterable[str]) -> str:
    """Saca del texto las palabras indicadas y limpia los espacios sobrantes."""
    for word in words:
        text = re.sub(rf"\b{re.escape(word)}\s*", " ", text, flags=re.IGNORECASE)
    return " ".join(text.split())


def clean_text(text: str) -> str:
    """Deja el texto en una sola linea, listo para ser leído en voz alta."""
    return text.replace(ZERO_WIDTH_SPACE, "").replace("\n", " ").strip()
