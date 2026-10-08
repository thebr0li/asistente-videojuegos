"""Tests de la seleccion de voz.

Se prueban los metodos de `VoiceService` con un motor falso, asi que los tests
no necesitan pyttsx3 ni un sistema de sonido.
"""

import unittest


class FakeVoiceEntry:
    def __init__(self, voice_id: str, languages: tuple[str, ...] = ()) -> None:
        self.id = voice_id
        self.languages = languages


class FakeEngine:
    """Motor minimo que imita la cola de pyttsx3: setProperty encola y
    runAndWait aplica."""

    def __init__(self, voices: tuple[str, ...], rejects: tuple[str, ...] = ()) -> None:
        self.voices = [FakeVoiceEntry(v) for v in voices]
        self._rejects = rejects
        self._pending: list[str] = []
        self._active = ""

    def getProperty(self, name: str):
        if name == "voices":
            return self.voices
        if name == "voice":
            return self._active
        raise KeyError(name)

    def setProperty(self, _name: str, value: str) -> None:
        self._pending.append(value if value not in self._rejects else "rechazada")

    def say(self, message: str) -> None:
        pass

    def runAndWait(self) -> None:
        while self._pending:
            self._active = self._pending.pop(0)


def build_service(voices: tuple[str, ...] = (), rejects: tuple[str, ...] = ()):
    from shared.voice import VoiceService

    service = VoiceService.__new__(VoiceService)
    service._engine = FakeEngine(voices, rejects)
    return service


def with_voice(voice_id: str, languages: tuple[str, ...] = ()) -> FakeVoiceEntry:
    return FakeVoiceEntry(voice_id, languages)


class VoiceSelectionTest(unittest.TestCase):
    def test_usa_la_voz_de_windows_si_esta_instalada(self):
        windows_voice = (
            r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices"
            r"\Tokens\TTS_MS_ES-ES_HELENA_11.0"
        )
        service = build_service((windows_voice,))

        self.assertEqual(service._select_spanish_voice((windows_voice,)), windows_voice)

    def test_cae_a_la_voz_de_macos_si_la_de_windows_no_esta(self):
        windows_voice = r"HKEY_LOCAL_MACHINE\voz-que-no-existe"
        macos_voice = "com.apple.voice.compact.es-ES.Monica"
        service = build_service((macos_voice,))

        self.assertEqual(service._select_spanish_voice((windows_voice, macos_voice)), macos_voice)

    def test_prueba_las_candidatas_en_orden(self):
        primera = "com.apple.voice.compact.es-ES.Primera"
        segunda = "com.apple.voice.compact.es-ES.Segunda"
        service = build_service((primera, segunda))

        self.assertEqual(service._select_spanish_voice((primera, segunda)), primera)

    def test_salta_las_candidatas_que_el_motor_rechaza(self):
        rechazada = "com.apple.voice.compact.es-ES.Rechazada"
        aceptada = "com.apple.voice.compact.es-ES.Aceptada"
        service = build_service((rechazada, aceptada), rejects=(rechazada,))

        self.assertEqual(service._select_spanish_voice((rechazada, aceptada)), aceptada)

    def test_si_ninguna_candidata_existe_busca_una_en_espanol_del_sistema(self):
        engine = FakeEngine(())
        engine.voices.append(with_voice("com.apple.voice.compact.en-US.Alex", ("en_US",)))
        engine.voices.append(with_voice("com.apple.voice.compact.es-ES.DelSistema", ("es_ES",)))
        service = build_service()
        service._engine = engine

        self.assertEqual(
            service._select_spanish_voice(("voz-inexistente",)),
            "com.apple.voice.compact.es-ES.DelSistema",
        )

    def test_no_elige_una_voz_en_otro_idioma(self):
        engine = FakeEngine(())
        engine.voices.append(with_voice("com.apple.voice.compact.en-US.Alex", ("en_US",)))
        service = build_service()
        service._engine = engine

        self.assertIsNone(service._select_spanish_voice(("voz-inexistente",)))

    def test_devuelve_none_si_no_hay_ninguna_voz_en_espanol(self):
        self.assertIsNone(build_service()._select_spanish_voice(("voz-inexistente",)))

    def test_la_voz_queda_activa_despues_de_procesar_la_cola(self):
        voz = "com.apple.voice.compact.es-ES.Monica"
        service = build_service((voz,))

        self.assertTrue(service._activate(voz))
        self.assertEqual(service._engine.getProperty("voice"), voz)

    def test_activar_deja_la_voz_seleccionada_para_hablar(self):
        voz = "com.apple.voice.compact.es-ES.Monica"
        service = build_service((voz,))
        service._activate(voz)

        self.assertEqual(service._engine.getProperty("voice"), voz)

    def test_ignora_las_candidatas_que_no_estan_instaladas(self):
        instalada = "com.apple.voice.compact.es-ES.Instalada"
        service = build_service((instalada,))

        self.assertEqual(
            service._available_voices(("com.apple.voice.compact.es-ES.Ausente", instalada)),
            (instalada,),
        )

    def test_si_ninguna_candidata_esta_instalada_no_inventa_una(self):
        engine = FakeEngine(())
        engine.voices.append(with_voice("com.apple.voice.compact.en-US.Alex", ("en_US",)))
        service = build_service()
        service._engine = engine

        self.assertEqual(service._available_voices(("com.apple.voice.compact.es-ES.Ausente",)), ())


if __name__ == "__main__":
    unittest.main()
