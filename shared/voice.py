"""Voz del asistente: texto a voz (pyttsx3) y escucha (speech_recognition)."""

from contextlib import suppress

import pyttsx3
import speech_recognition as sr

SPANISH_VOICE = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ES-ES_HELENA_11.0"
SPANISH_LANGUAGE = "es-ES"
PAUSE_THRESHOLD = 0.8


class VoiceService:
    """Habla los mensajes y transcribe lo que dice el usuario.

    El motor de voz y el reconocedor se crean aca y no al importar el modulo.
    """

    def __init__(self, voice_id: str = SPANISH_VOICE, language: str = SPANISH_LANGUAGE) -> None:
        self._engine = pyttsx3.init()
        self._language = language
        self._recognizer = sr.Recognizer()
        self._recognizer.pause_threshold = PAUSE_THRESHOLD
        self._select_voice(voice_id)

    def _select_voice(self, voice_id: str) -> None:
        with suppress(Exception):
            self._engine.setProperty("voice", voice_id)

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
