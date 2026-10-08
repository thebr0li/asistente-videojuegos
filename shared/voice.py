"""Voz del asistente: texto a voz (pyttsx3) y escucha (speech_recognition)."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, cast

import pyttsx3
import speech_recognition as sr

SPANISH_LANGUAGE = "es-ES"
PAUSE_THRESHOLD = 0.8

# Se prueban en orden. La de Windows es la del proyecto; las de macOS son el
# plan B para que el asistente siga hablando en espanol fuera de Windows.
VOICE_CANDIDATES = (
    r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ES-ES_HELENA_11.0",
    "com.apple.voice.compact.es-ES.Monica",
    "com.apple.speech.synthesis.voice.Monica",
    "com.apple.eloquence.es-ES.Shelley",
)
SPANISH_PREFIX = "es"


class VoiceService:
    """Habla los mensajes y transcribe lo que dice el usuario.

    El motor de voz y el reconocedor se crean aca y no al importar el modulo.
    """

    def __init__(
        self,
        voice_ids: tuple[str, ...] = VOICE_CANDIDATES,
        language: str = SPANISH_LANGUAGE,
    ) -> None:
        self._engine = pyttsx3.init()
        self._language = language
        self._recognizer = sr.Recognizer()
        self._recognizer.pause_threshold = PAUSE_THRESHOLD
        self.voice_id = self._select_spanish_voice(voice_ids)

    def _select_spanish_voice(self, voice_ids: tuple[str, ...]) -> str | None:
        for voice_id in self._available_voices(voice_ids):
            if self._activate(voice_id):
                return voice_id
        return None

    def _activate(self, voice_id: str) -> bool:
        """Prende la voz y verifica que el motor la tome.

        `setProperty` encola el comando: la voz recien queda activa despues de
        procesar la cola, asi que hay que hablar una vez para que se aplique.
        """
        try:
            self._engine.setProperty("voice", voice_id)
            self._engine.say("")
            self._engine.runAndWait()
            return self._engine.getProperty("voice") == voice_id
        except Exception:
            return False

    def _installed_voices(self) -> tuple[str, ...]:
        voices = cast(Iterable[Any], self._engine.getProperty("voices") or ())
        return tuple(str(voice.id) for voice in voices)

    def _available_voices(self, voice_ids: tuple[str, ...]) -> tuple[str, ...]:
        """Las voces pedidas que existen, y si no hay ninguna, las del sistema."""
        installed = self._installed_voices()
        wanted = tuple(voice_id for voice_id in voice_ids if voice_id in installed)
        return wanted or self._spanish_system_voices()

    def _spanish_system_voices(self) -> tuple[str, ...]:
        voices = cast(Iterable[Any], self._engine.getProperty("voices") or ())
        return tuple(str(voice.id) for voice in voices if self._is_spanish(voice))

    def _is_spanish(self, voice) -> bool:
        languages = getattr(voice, "languages", None) or ()
        return any(str(language).startswith(SPANISH_PREFIX) for language in languages)

    def say(self, message: str) -> None:
        print("Asistente:", message)
        self._engine.say(message)
        self._engine.runAndWait()

    def listen(self) -> str | None:
        """Escucha una frase y la transcribe, o devuelve None si no la entendio."""
        with sr.Microphone() as source:
            print("Ya puedes hablar")
            audio = self._recognizer.listen(source)

        try:
            heard = self._recognizer.recognize_google(audio, language=self._language)
        except sr.UnknownValueError:
            print("Ups, no entendi")
            return None
        except sr.RequestError:
            print("Ups, no hay servicio")
            return None

        print("Dijiste:", heard)
        return heard
