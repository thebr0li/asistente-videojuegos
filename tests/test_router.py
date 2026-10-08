"""Tests del router: cada pedido tiene que caer en la feature correcta.

Ningun test necesita microfono, parlantes, navegador ni internet: las
dependencias se reemplazan por dobles de prueba.
"""

import io
import unittest
from contextlib import redirect_stdout

from app.session import Context, Session
from features.hardware.models import HardwareProfile
from features.media.commands import find_song
from features.stocks.commands import TICKERS, find_company
from features.wikipedia.commands import find_query
from tests.doubles import (
    FakeVoice,
    MediaStub,
    PricesStub,
    WikipediaStub,
    build_test_router,
)


class RouterTestCase(unittest.TestCase):
    """Base con el router armado con dobles: solo helpers, sin tests."""

    def setUp(self) -> None:
        self.summaries = WikipediaStub()
        self.media = MediaStub()
        self.prices = PricesStub()
        self.router = build_test_router(
            wikipedia=self.summaries,
            media=self.media,
            prices=self.prices,
        )
        self.voice = FakeVoice()
        self.session = Session()
        self.context = Context(session=self.session, voice=self.voice)
        self.detected_output = io.StringIO()

    def command_for(self, text):
        return self.router.resolve(text)

    def command_name(self, text):
        command = self.command_for(text)
        return None if command is None else command.name

    def run_command(self, text):
        command = self.command_for(text)
        self.assertIsNotNone(command, f"ningun comando reconoce: {text}")
        with redirect_stdout(io.StringIO()) as self.detected_output:
            command.execute(self.context, text)

    @property
    def last_message(self):
        return self.voice.messages[-1]


class RouterTest(RouterTestCase):
    """Cada pedido por voz cae en la feature correcta."""

    def test_hora_va_a_la_feature_de_fecha(self):
        self.assertEqual(self.command_name("que hora es"), "datetime.hour")

    def test_dia_va_a_la_feature_de_fecha(self):
        self.assertEqual(self.command_name("que dia es hoy"), "datetime.day")

    def test_fecha_va_a_la_feature_de_fecha(self):
        self.assertEqual(self.command_name("que fecha es"), "datetime.day")

    def test_wikipedia_va_a_la_feature_de_wikipedia(self):
        self.assertEqual(self.command_name("busca en wikipedia lionel messi"), "wikipedia.summary")

    def test_youtube_va_a_la_feature_de_navegador(self):
        self.assertEqual(self.command_name("abrir youtube"), "browser.youtube")

    def test_google_va_a_la_feature_de_navegador(self):
        self.assertEqual(self.command_name("abrir google"), "browser.google")

    def test_busqueda_en_internet_va_a_la_feature_de_multimedia(self):
        self.assertEqual(self.command_name("busca en internet requisitos gta 5"), "media.search")

    def test_cancion_va_a_la_feature_de_multimedia(self):
        self.assertEqual(self.command_name("reproducir bohemian rhapsody"), "media.play")

    def test_accion_va_a_la_feature_de_acciones(self):
        self.assertEqual(self.command_name("precio de la accion de nvidia"), "stocks.price")

    def test_chiste_va_a_la_feature_de_chistes(self):
        self.assertEqual(self.command_name("contame un chiste"), "jokes.tell")

    def test_juego_va_a_la_feature_de_hardware(self):
        self.assertEqual(self.command_name("me corre valorant"), "hardware.game")

    def test_componentes_van_a_la_feature_de_hardware(self):
        self.assertEqual(self.command_name("tengo una rtx 3060, un ryzen 5 y 16 de ram"), "hardware.components")

    def test_salir_cierra_la_conversacion(self):
        command = self.command_for("salir")

        self.assertEqual(command.name, "session.exit")
        self.assertTrue(command.ends_session)

    def test_pedido_sin_comando_no_resuelve(self):
        self.assertIsNone(self.command_name("hola, buen dia"))

    def test_el_juego_tiene_prioridad_sobre_los_componentes(self):
        self.assertEqual(self.command_name("me corre valorant con mi rtx 3060"), "hardware.game")

    def test_los_componentes_tienen_prioridad_sobre_salir(self):
        self.assertEqual(self.command_name("salir, tengo una rtx 3060"), "hardware.components")

    def test_wikipedia_avisa_que_esta_buscando_y_lee_el_resumen(self):
        self.run_command("busca en wikipedia lionel messi")

        self.assertEqual(self.summaries.queries, ["lionel messi"])
        self.assertEqual(
            self.voice.messages,
            ["Buscando en wikipedia", "Resumen de lionel messi"],
        )

    def test_wikipedia_ambigua_lista_las_opciones(self):
        self.run_command("busca en wikipedia ambiguo")

        self.assertEqual(self.last_message, "Hay varias opciones: Nintendo, Nintendo Switch, Nintendo 64")

    def test_wikipedia_sin_informacion(self):
        self.run_command("busca en wikipedia sin informacion")

        self.assertEqual(self.last_message, "No encontre informacion sobre eso")

    def test_wikipedia_sin_conexion(self):
        self.run_command("busca en wikipedia sin conexion")

        self.assertEqual(self.last_message, "No pude buscar en wikipedia en este momento")

    def test_acciones_consultan_el_ticker_de_la_empresa(self):
        self.run_command("precio de la accion de nvidia")

        self.assertEqual(self.prices.tickers, ["NVDA"])
        self.assertEqual(self.last_message, "El precio de nvidia es 100.5 dolares")

    def test_acciones_de_una_empresa_sin_datos(self):
        self.run_command("precio de la accion de sony")

        self.assertEqual(self.last_message, "No pude encontrar la informacion de la accion")

    def test_acciones_de_una_empresa_desconocida(self):
        self.run_command("precio de la accion de valve")

        self.assertEqual(self.prices.tickers, [])
        self.assertEqual(self.last_message, "No tengo informacion sobre la accion de valve")

    def test_abrir_youtube_abre_la_pagina(self):
        self.run_command("abrir youtube")

        self.assertEqual(self.media.opened, ["https://www.youtube.com"])
        self.assertEqual(self.last_message, "Abriendo YouTube")

    def test_abrir_google_abre_la_pagina(self):
        self.run_command("abrir google")

        self.assertEqual(self.media.opened, ["https://www.google.com"])
        self.assertEqual(self.last_message, "Abriendo el navegador")

    def test_buscar_en_internet_saca_las_palabras_del_comando(self):
        self.run_command("busca en internet requisitos gta 5")

        self.assertEqual(self.media.searched, ["requisitos gta 5"])

    def test_reproducir_saca_las_palabras_del_comando(self):
        self.run_command("reproducir bohemian rhapsody en youtube")

        self.assertEqual(self.media.played, ["bohemian rhapsody"])

    def test_chiste_se_limpia_antes_de_hablarlo(self):
        self.run_command("contame un chiste")

        self.assertEqual(self.last_message, "Primer chiste con remate")

    def test_componentes_parciales_pide_lo_que_falta(self):
        self.run_command("tengo una rtx 3060")

        self.assertEqual(self.session.detected.gpu_model, "rtx 3060")
        self.assertIsNone(self.session.hardware)
        self.assertEqual(self.last_message, "Anote. Todavia me falta cpu, ram")

    def test_componentes_completos_guardan_el_equipo(self):
        self.run_command("tengo una rtx 3060, un ryzen 5 y 16 de ram")

        self.assertEqual(self.last_message, "Perfecto, ya tengo tu equipo completo")
        self.assertEqual(self.session.hardware, HardwareProfile(ram=16, vram=12, gpu_level=7, cpu_level=5))

    def test_juego_sin_equipo_pide_los_componentes(self):
        self.run_command("me corre cyberpunk 2077")

        self.assertEqual(self.last_message, "Primero decime tus componentes")

    def test_juego_con_equipo_usa_el_perfil_guardado(self):
        self.run_command("tengo una rtx 3060, un ryzen 5 y 16 de ram")
        self.run_command("me corre fortnite")

        self.assertEqual(self.last_message, "Si, fortnite te corre en calidad alta (recomendado)")

    def test_juego_con_equipo_que_solo_alcanza_el_minimo(self):
        self.run_command("tengo una rtx 3060, un ryzen 5 y 16 de ram")
        self.run_command("me corre cyberpunk 2077")

        self.assertEqual(self.last_message, "Si, cyberpunk 2077 te corre, pero en calidad baja (minimo)")

    def test_juego_desconocido(self):
        self.run_command("me corre cricket 24")

        self.assertEqual(self.last_message, "No tengo ese juego en mi base de datos")

class PrioridadDelRouterTest(RouterTestCase):
    """La prioridad se respeta en el orden en que se arman los comandos."""

    def test_la_hora_gana_antes_que_la_fecha(self):
        self.assertEqual(self.command_name("que dia es, que hora es"), "datetime.hour")

    def test_wikipedia_gana_antes_que_el_navegador(self):
        self.assertEqual(self.command_name("busca en wikipedia como abrir youtube"), "wikipedia.summary")

    def test_el_navegador_gana_antes_que_la_multimedia(self):
        self.assertEqual(self.command_name("abrir youtube y reproducir algo"), "browser.youtube")

    def test_la_busqueda_gana_antes_que_la_cancion(self):
        self.assertEqual(self.command_name("busca en internet reproducir cancion"), "media.search")

    def test_la_cancion_gana_antes_que_las_acciones(self):
        self.assertEqual(self.command_name("pon una cancion y el precio de la accion"), "media.play")

    def test_las_acciones_ganan_antes_que_los_chistes(self):
        self.assertEqual(self.command_name("precio de la accion de nvidia y un chiste"), "stocks.price")

    def test_los_chistes_ganan_antes_que_el_hardware(self):
        self.assertEqual(self.command_name("contame un chiste sobre mi rtx 3060"), "jokes.tell")


class RouterSinComandoTest(unittest.TestCase):
    def setUp(self) -> None:
        self.router = build_test_router()

    def test_un_pedido_vacio_no_resuelve(self):
        for text in ("", "   ", "xyz abc 123"):
            with self.subTest(text=text):
                self.assertIsNone(self.router.resolve(text))


class BusquedaDeTextoTest(unittest.TestCase):
    """Las funciones que limpian el pedido antes de consultar afuera."""

    def test_find_query(self):
        casos = {
            "busca en wikipedia lionel messi": "lionel messi",
            "buscar en wikipedia lionel messi": "lionel messi",
            "wikipedia lionel messi": "lionel messi",
            "busca lionel messi": "lionel messi",
        }

        for pedido, consulta in casos.items():
            with self.subTest(pedido=pedido):
                self.assertEqual(find_query(pedido), consulta)

    def test_find_song(self):
        casos = {
            "reproducir bohemian rhapsody": "bohemian rhapsody",
            "reproduce bohemian rhapsody": "bohemian rhapsody",
            "reproducime bohemian rhapsody": "bohemian rhapsody",
            "poner bohemian rhapsody": "bohemian rhapsody",
            "poneme bohemian rhapsody": "bohemian rhapsody",
            "pon bohemian rhapsody": "bohemian rhapsody",
            "bohemian rhapsody en youtube": "bohemian rhapsody",
            "reproducir la cancion siempre en mi corazon": "la siempre en mi corazon",
        }

        for pedido, cancion in casos.items():
            with self.subTest(pedido=pedido):
                self.assertEqual(find_song(pedido), cancion)

    def test_find_company(self):
        casos = {
            "precio de la accion de nvidia": "nvidia",
            "el precio de la accion de nvidia": "nvidia",
            "quiero saber el precio de la accion de amd": "amd",
            "el precio de la accion de electronic arts": "electronic arts",
            "cuanto vale la accion de take two": "take two",
            "accion de sony": "sony",
            "precio de la ACCION de Microsoft": "microsoft",
        }

        for pedido, empresa in casos.items():
            with self.subTest(pedido=pedido):
                self.assertEqual(find_company(pedido), empresa)

    def test_find_company_devuelve_un_ticker_conocido(self):
        for empresa in TICKERS:
            with self.subTest(empresa=empresa):
                self.assertIn(find_company(f"precio de la accion de {empresa}"), TICKERS)


class AccionesTest(RouterTestCase):
    def test_todas_las_empresas_terminan_en_precio_o_en_error(self):
        for empresa in TICKERS:
            with self.subTest(empresa=empresa):
                self.voice.messages.clear()
                self.prices.tickers.clear()
                self.run_command(f"precio de la accion de {empresa}")
                self.assertEqual(len(self.prices.tickers), 1)
                self.assertTrue(
                    self.last_message.startswith("El precio de ")
                    or self.last_message == "No pude encontrar la informacion de la accion"
                )


class MediaFalloTest(unittest.TestCase):
    """Si YouTube o Google no abren, el asistente lo avisa y no se cae."""

    def setUp(self) -> None:
        self.voice = FakeVoice()
        self.context = Context(session=Session(), voice=self.voice)
        self.router = build_test_router(media=MediaStub(failing=True))

    def test_avisa_si_no_reproduce_la_cancion(self):
        command = self.router.resolve("reproducir bohemian rhapsody")
        command.execute(self.context, "reproducir bohemian rhapsody")

        self.assertEqual(
            self.voice.messages,
            ["Reproduciendo bohemian rhapsody en YouTube", "No pude reproducir la cancion en YouTube"],
        )

    def test_avisa_si_no_puede_buscar_en_internet(self):
        command = self.router.resolve("busca en internet requisitos gta 5")
        command.execute(self.context, "busca en internet requisitos gta 5")

        self.assertEqual(
            self.voice.messages,
            ["Buscando en internet", "No pude buscar en internet en este momento"],
        )

    def test_reproducir_sin_cancion_ignora_el_error(self):
        command = self.router.resolve("reproducir")
        command.execute(self.context, "reproducir")

        self.assertEqual(self.voice.messages, ["Que cancion queres que reproduzca?"])


if __name__ == "__main__":
    unittest.main()
