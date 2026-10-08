"""Test del bucle del asistente con una voz guionizada.

Se verifica el flujo completo (saludo, pedidos, fallback, despedida) sin
microfono, parlantes ni conexion a internet.
"""

import io
import sys
import unittest
from contextlib import redirect_stdout

from app import assistant as app_assistant
from app.assistant import GOODBYE_MESSAGE, Assistant, configure_console, main
from app.router import FAREWELL_MESSAGE
from app.session import Session
from features.hardware.models import HardwareProfile
from tests.doubles import ScriptedVoice, build_test_router


class AssistantTestCase(unittest.TestCase):
    def build(self, inputs, session=None):
        voice = ScriptedVoice(inputs)
        session = session or Session()
        assistant = Assistant(voice=voice, router=build_test_router(), session=session)
        return voice, assistant, session

    def run_assistant(self, inputs, session=None):
        voice, assistant, _ = self.build(inputs, session)
        with redirect_stdout(io.StringIO()) as output:
            assistant.run()
        return voice, output.getvalue()

    def test_saluda_antes_de_escuchar(self):
        voice, _ = self.run_assistant(["salir"])

        self.assertEqual(len(voice.messages), 2)
        self.assertTrue(voice.messages[0].endswith(", en que te puedo ayudar?"))
        self.assertEqual(voice.messages[1], FAREWELL_MESSAGE)

    def test_saluda_segun_la_hora(self):
        voice, _ = self.run_assistant(["salir"])

        self.assertRegex(voice.messages[0], r"^(Buenas noches|Buen dia|Buenas tardes), en que te puedo ayudar\?")

    def test_responde_y_se_despide(self):
        voice, _ = self.run_assistant(["que hora es", "salir"])

        self.assertRegex(voice.messages[1], r"^En este momento son las \d+ horas con \d+ minutos$")
        self.assertEqual(voice.messages[2], FAREWELL_MESSAGE)

    def test_pedido_sin_entender_cae_en_el_fallback(self):
        voice, _ = self.run_assistant(["hola buen dia"])

        self.assertEqual(voice.messages[1], "No entendi el pedido")

    def test_sigue_esperando_cuando_no_entiende_la_voz(self):
        voice, _ = self.run_assistant([None, "que dia es hoy", "salir"])

        self.assertRegex(voice.messages[1], r"^Hoy es (Lunes|Martes|Miercoles|Jueves|Viernes|Sabado|Domingo)$")
        self.assertEqual(voice.messages[2], FAREWELL_MESSAGE)

    def test_ignora_las_entradas_vacias(self):
        voice, _ = self.run_assistant(["", "   ", "salir"])

        self.assertEqual(voice.messages[1], FAREWELL_MESSAGE)

    def test_pasa_el_pedido_en_minusculas(self):
        voice, _ = self.run_assistant(["QUE HORA ES"])

        self.assertEqual(voice.inputs_heard, ["QUE HORA ES"])
        self.assertRegex(voice.messages[1], r"^En este momento son las \d+ horas")

    def test_salir_cierra_el_bucle(self):
        voice, _ = self.run_assistant(["salir", "que hora es"])

        self.assertEqual(voice.messages[-1], FAREWELL_MESSAGE)
        self.assertEqual(voice.heard, 1)

    def test_despedida_por_control_c(self):
        voice, _ = self.run_assistant(["que hora es"])

        self.assertEqual(voice.messages[-1], GOODBYE_MESSAGE)

    def test_imprime_el_pedido_recibido(self):
        _, output = self.run_assistant(["que hora es"])

        self.assertIn("Comando recibido: que hora es", output)

    def test_usa_el_equipo_guardado_durante_la_conversacion(self):
        session = Session()
        voice, _ = self.run_assistant(
            ["tengo una rtx 3060, un ryzen 5 y 16 de ram", "me corre gta 5", "salir"], session
        )

        self.assertEqual(session.hardware, HardwareProfile(ram=16, vram=12, gpu_level=7, cpu_level=5))
        self.assertEqual(voice.messages[-2], "Si, gta 5 te corre en calidad alta (recomendado)")

    def test_componentes_de_a_uno_completan_el_equipo(self):
        voice, _ = self.run_assistant(["tengo una rtx 3060", "un ryzen 5", "16 gb de ram", "salir"])

        self.assertEqual(voice.messages[-4], "Anote. Todavia me falta cpu, ram")
        self.assertEqual(voice.messages[-3], "Anote. Todavia me falta ram")
        self.assertEqual(voice.messages[-2], "Perfecto, ya tengo tu equipo completo")


class FakeAssistant:
    def run(self) -> None:
        return None


class ConfiguracionTest(unittest.TestCase):
    def test_configure_console_no_falla_si_stdout_no_tiene_reconfigure(self):
        class SinReconfigure:
            pass

        original, sys.stdout = sys.stdout, SinReconfigure()
        try:
            configure_console()
        finally:
            sys.stdout = original

    def test_configure_console_fuerza_utf8(self):
        configurado = {}

        class ConReconfigure:
            def reconfigure(self, **kwargs):
                configurado.update(kwargs)

        original, sys.stdout = sys.stdout, ConReconfigure()
        try:
            configure_console()
        finally:
            sys.stdout = original

        self.assertEqual(configurado, {"encoding": "utf-8", "errors": "replace"})

    def test_main_crea_el_asistente_y_lo_ejecuta(self):
        ejecutados = []

        class SpyAssistant:
            def run(self):
                ejecutados.append(True)

        original = app_assistant.create_assistant
        app_assistant.create_assistant = lambda: SpyAssistant()
        try:
            main()
        finally:
            app_assistant.create_assistant = original

        self.assertEqual(ejecutados, [True])



if __name__ == "__main__":
    unittest.main()
