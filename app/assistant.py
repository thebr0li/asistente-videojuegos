"""Bucle de la conversacion y armado de la aplicacion.

El nucleo y los comandos de cada feature reciben las integraciones externas por
inyeccion de dependencias, asi que se pueden probar sin microfono ni internet.
"""

from __future__ import annotations

import datetime
import sys
from typing import TYPE_CHECKING

from app.router import CommandRouter, build_router
from app.session import Context, Session
from features.datetime.time import greeting_for

if TYPE_CHECKING:
    from shared.voice import VoiceService

GOODBYE_MESSAGE = "Hasta luego"
FALLBACK_MESSAGE = "No entendi el pedido"


class Assistant:
    """Saluda, escucha pedidos y ejecuta el comando que los reconoce."""

    def __init__(self, voice: VoiceService, router: CommandRouter, session: Session | None = None) -> None:
        self._voice = voice
        self._router = router
        self._session = session or Session()

    def run(self) -> None:
        context = Context(session=self._session, voice=self._voice)
        self._voice.say(greeting_for(datetime.datetime.now()))

        try:
            while True:
                text = self._voice.listen()
                if text is None or not text.strip():
                    continue

                text = text.lower()
                print("Comando recibido:", text)
                command = self._router.resolve(text)
                if command is None:
                    self._voice.say(FALLBACK_MESSAGE)
                    continue

                command.execute(context, text)
                if command.ends_session:
                    break
        except KeyboardInterrupt:
            print()
            self._voice.say(GOODBYE_MESSAGE)


def create_assistant() -> Assistant:
    """Conecta las dependencias reales de la aplicacion.

    Las librerias se importan aca y no arriba del archivo para que el nucleo se
    pueda importar sin instalar microfono, navegador ni internet.
    """
    import webbrowser

    from features.jokes.jokes import tell_joke
    from features.media.playback import play_on_youtube, search_on_internet
    from features.stocks.quotes import last_price
    from features.wikipedia import client as wikipedia_client
    from shared.voice import VoiceService

    configure_console()
    wikipedia_client.configure()

    return Assistant(
        voice=VoiceService(),
        router=build_router(
            summarize=wikipedia_client.summarize,
            open_url=webbrowser.open,
            play_on_youtube=play_on_youtube,
            search_on_internet=search_on_internet,
            last_price=last_price,
            fetch_joke=tell_joke,
        ),
    )


def configure_console() -> None:
    """Fuerza UTF-8 en la salida para que los acentos no se rompan en Windows."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main() -> None:
    create_assistant().run()
