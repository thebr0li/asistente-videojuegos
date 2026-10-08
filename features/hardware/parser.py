"""Lectura de hardware a partir del texto del usuario.

Solo logica pura: recibe una frase y devuelve informacion del dominio, sin
hablar con el microfono ni con el usuario.
"""

from __future__ import annotations

import re
from collections.abc import Collection

from features.hardware.data import CPUS, GAMES, GPUS
from features.hardware.models import DetectedParts, HardwareProfile

RAM_PATTERNS = (
    re.compile(r"(\d+)\s*(?:gb|gigas?)?\s*(?:de\s*)?ram"),
    re.compile(r"ram\D{0,12}?(\d+)"),
)


def find_ram(text: str) -> int | None:
    """Busca la cantidad de RAM, por ejemplo "16 de ram" o "8gb de ram"."""
    for pattern in RAM_PATTERNS:
        match = pattern.search(text)
        if match:
            return int(match.group(1))
    return None


def find_gpu(text: str) -> str | None:
    """Busca el modelo de la placa de video en la frase."""
    return find_model(text, GPUS)


def find_cpu(text: str) -> str | None:
    """Busca el modelo del procesador en la frase."""
    return find_model(text, CPUS)


def find_game(text: str) -> str | None:
    """Busca el nombre de un juego cargado en la base."""
    return find_model(text, GAMES)


def detect_parts(text: str) -> DetectedParts:
    """Devuelve los componentes que aparecen en la frase, aunque sean parciales."""
    return DetectedParts(
        gpu_model=find_gpu(text),
        cpu_model=find_cpu(text),
        ram=find_ram(text),
    )


def build_profile(parts: DetectedParts) -> HardwareProfile | None:
    """Arma el equipo del usuario, o None si todavia falta algun componente."""
    gpu = GPUS.get(parts.gpu_model or "")
    cpu = CPUS.get(parts.cpu_model or "")
    if gpu is None or cpu is None or parts.ram is None:
        return None
    return HardwareProfile(ram=parts.ram, vram=gpu.vram, gpu_level=gpu.level, cpu_level=cpu)


def find_model(text: str, catalog: Collection[str]) -> str | None:
    """Primer modelo del catalogo cuyo nombre aparece en la frase."""
    for model in catalog:
        if model in text:
            return model
    return None
