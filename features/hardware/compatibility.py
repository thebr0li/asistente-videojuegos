"""Regla de compatibilidad. Devuelve texto: no habla ni guarda nada."""

from features.hardware.data import GAMES
from features.hardware.models import HardwareProfile

UNKNOWN_GAME_MESSAGE = "No tengo ese juego en mi base de datos"


def check_compatibility(profile: HardwareProfile, game: str) -> str:
    requirements = GAMES.get(game)
    if requirements is None:
        return UNKNOWN_GAME_MESSAGE

    if requirements.recommended.is_met_by(profile):
        return f"Si, {game} te corre en calidad alta (recomendado)"
    if requirements.minimum.is_met_by(profile):
        return f"Si, {game} te corre, pero en calidad baja (minimo)"
    return f"No, no te corre {game} con esos componentes"
