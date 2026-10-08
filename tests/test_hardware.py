"""Tests del dominio de hardware: lectura de componentes y compatibilidad."""

import unittest

from features.hardware.compatibility import check_compatibility
from features.hardware.data import CPUS, GAMES, GPUS
from features.hardware.models import DetectedParts, HardwareProfile, Spec
from features.hardware.parser import (
    build_profile,
    detect_parts,
    find_cpu,
    find_game,
    find_gpu,
    find_ram,
)


class HardwareParserTest(unittest.TestCase):
    def test_detecta_los_componentes_en_una_frase(self):
        parts = detect_parts("tengo una rtx 3060, un ryzen 5 y 16 de ram")

        self.assertEqual(parts.gpu_model, "rtx 3060")
        self.assertEqual(parts.cpu_model, "ryzen 5")
        self.assertEqual(parts.ram, 16)

    def test_detecta_solo_la_grafica(self):
        self.assertEqual(detect_parts("gpu rtx 3060").gpu_model, "rtx 3060")

    def test_detecta_solo_la_ram(self):
        self.assertEqual(detect_parts("ram 16").ram, 16)

    def test_detecta_la_ram_con_unidades(self):
        self.assertEqual(detect_parts("16 gb de ram").ram, 16)

    def test_detecta_solo_el_procesador(self):
        self.assertEqual(detect_parts("procesador ryzen 7").cpu_model, "ryzen 7")

    def test_una_frase_sin_componentes_no_detecta_nada(self):
        self.assertTrue(detect_parts("hola, que tal").is_empty)

    def test_arma_el_equipo_con_los_tres_componentes(self):
        profile = build_profile(detect_parts("tengo una rtx 3060, un ryzen 5 y 16 de ram"))

        self.assertEqual(profile, HardwareProfile(ram=16, vram=12, gpu_level=7, cpu_level=5))

    def test_no_se_arma_el_equipo_si_falta_un_componente(self):
        self.assertIsNone(build_profile(DetectedParts(gpu_model="rtx 3060", ram=16)))

    def test_lista_los_componentes_que_faltan(self):
        parts = DetectedParts(gpu_model="rtx 3060")

        self.assertEqual(parts.missing_components, ("cpu", "ram"))

    def test_detecta_el_juego_de_la_base(self):
        self.assertEqual(find_game("me corre cyberpunk 2077"), "cyberpunk 2077")

    def test_no_detecta_juegos_desconocidos(self):
        self.assertIsNone(find_game("me corre cricket 24"))


class RamParsingTest(unittest.TestCase):
    def test_lecturas_de_ram(self):
        casos = {
            "16 de ram": 16,
            "16 gb de ram": 16,
            "8 gigas de ram": 8,
            "8 giga ram": 8,
            "ram 16": 16,
            "ram: 16": 16,
            "ram tengo 16": 16,
            "mi ram es de 64 gb": 64,
            "16gb ram": 16,
            "tengo 16 de ram y una rtx 3060": 16,
        }

        for texto, esperado in casos.items():
            with self.subTest(texto=texto):
                self.assertEqual(find_ram(texto), esperado)

    def test_sin_ram_devuelve_none(self):
        for texto in ("hola que tal", "tengo una rtx 3060", ""):
            with self.subTest(texto=texto):
                self.assertIsNone(find_ram(texto))


class ModelCatalogTest(unittest.TestCase):
    def test_todas_las_gpus_de_la_base_se_detectan(self):
        for modelo in GPUS:
            with self.subTest(modelo=modelo):
                self.assertEqual(find_gpu(f"tengo una {modelo}"), modelo)

    def test_todos_los_procesadores_de_la_base_se_detectan(self):
        for modelo in CPUS:
            with self.subTest(modelo=modelo):
                self.assertEqual(find_cpu(f"tengo un {modelo}"), modelo)

    def test_todos_los_juegos_de_la_base_se_detectan(self):
        for juego in GAMES:
            with self.subTest(juego=juego):
                self.assertEqual(find_game(f"me corre {juego}"), juego)

    def test_una_gpu_que_no_esta_en_la_base_no_se_detecta(self):
        self.assertIsNone(find_gpu("tengo una rtx 9080"))

    def test_un_procesador_que_no_esta_en_la_base_no_se_detecta(self):
        self.assertIsNone(find_cpu("tengo un pentium g4560"))

    def test_un_modelo_desconocido_que_containe_uno_conocido_lo_usa(self):
        self.assertEqual(find_cpu("tengo un ryzen 5 7800x3d"), "ryzen 5")

    def test_toda_gpu_detectada_permite_armacel_equipo(self):
        for modelo, spec in GPUS.items():
            with self.subTest(modelo=modelo):
                perfil = build_profile(DetectedParts(gpu_model=modelo, cpu_model="ryzen 5", ram=8))
                self.assertEqual(perfil.gpu_level, spec.level)
                self.assertEqual(perfil.vram, spec.vram)


class DetectedPartsTest(unittest.TestCase):
    def test_una_parte_sin_todo_marca_los_tres_faltantes(self):
        self.assertEqual(DetectedParts().missing_components, ("gpu", "cpu", "ram"))

    def test_una_parte_completa_no_tiene_faltantes(self):
        parts = DetectedParts(gpu_model="rtx 3060", cpu_model="ryzen 5", ram=16)

        self.assertEqual(parts.missing_components, ())

    def test_es_vacia_solo_si_no_tiene_nada(self):
        self.assertTrue(DetectedParts().is_empty)
        self.assertFalse(DetectedParts(gpu_model="rtx 3060").is_empty)
        self.assertFalse(DetectedParts(cpu_model="ryzen 5").is_empty)
        self.assertFalse(DetectedParts(ram=16).is_empty)

    def test_los_componentes_se_van_acumulando(self):
        parts = DetectedParts(gpu_model="rtx 3060")
        parts.merge(detect_parts("tengo 16 de ram"))

        self.assertEqual(parts.missing_components, ("cpu",))

    def test_lo_nuevo_reemplaza_lo_anterior(self):
        parts = DetectedParts(ram=8)
        parts.merge(detect_parts("tengo 16 de ram"))

        self.assertEqual(parts.ram, 16)

    def test_mergear_vacio_no_pisa_nada(self):
        parts = DetectedParts(gpu_model="rtx 3060", cpu_model="ryzen 5", ram=16)
        parts.merge(DetectedParts())

        self.assertEqual(parts, DetectedParts("rtx 3060", "ryzen 5", 16))


class SpecTest(unittest.TestCase):
    def perfil(self, ram=8, vram=4, gpu_level=5, cpu_level=5):
        return HardwareProfile(ram=ram, vram=vram, gpu_level=gpu_level, cpu_level=cpu_level)

    def test_se_cumple_con_valores_iguales(self):
        self.assertTrue(Spec(ram=8, vram=4, gpu=5, cpu=5).is_met_by(self.perfil()))

    def test_no_se_cumple_si_cualquier_valor_queda_por_debajo(self):
        for campo in ("ram", "vram", "gpu_level", "cpu_level"):
            with self.subTest(campo=campo):
                perfil = self.perfil(**{campo: 1})
                self.assertFalse(Spec(ram=8, vram=4, gpu=5, cpu=5).is_met_by(perfil))

    def test_sobra_un_solo_valor_no_alcanza_el_requisito(self):
        self.assertFalse(Spec(ram=8, vram=4, gpu=5, cpu=6).is_met_by(self.perfil(cpu_level=5)))

    def test_alcanza_cualquier_requisito_menor_o_igual(self):
        for campo in ("ram", "vram", "gpu_level", "cpu_level"):
            with self.subTest(campo=campo):
                perfil = self.perfil(**{campo: 99})
                self.assertTrue(Spec(ram=8, vram=4, gpu=5, cpu=5).is_met_by(perfil))


class CompatibilityTest(unittest.TestCase):
    def test_equipo_por_debajo_del_minimo(self):
        equipo = HardwareProfile(ram=2, vram=1, gpu_level=1, cpu_level=1)

        self.assertEqual(
            check_compatibility(equipo, "cyberpunk 2077"),
            "No, no te corre cyberpunk 2077 con esos componentes",
        )

    def test_equipo_que_solo_cumple_el_minimo(self):
        equipo = HardwareProfile(ram=4, vram=1, gpu_level=2, cpu_level=2)

        self.assertEqual(
            check_compatibility(equipo, "valorant"),
            "Si, valorant te corre, pero en calidad baja (minimo)",
        )

    def test_equipo_que_cumple_lo_recomendado(self):
        equipo = HardwareProfile(ram=8, vram=2, gpu_level=3, cpu_level=3)

        self.assertEqual(
            check_compatibility(equipo, "valorant"),
            "Si, valorant te corre en calidad alta (recomendado)",
        )

    def test_juego_que_no_esta_en_la_base(self):
        equipo = HardwareProfile(ram=32, vram=24, gpu_level=10, cpu_level=9)

        self.assertEqual(
            check_compatibility(equipo, "cricket 24"),
            "No tengo ese juego en mi base de datos",
        )

    def test_todo_juego_alcanza_un_veredicto(self):
        for juego in GAMES:
            with self.subTest(juego=juego):
                self.assertTrue(check_compatibility(HardwareProfile(32, 24, 10, 9), juego))

    def test_cada_dimension_por_debajo_del_minimo_impide_correr(self):
        for juego, requisitos in GAMES.items():
            for campo in ("ram", "vram", "gpu", "cpu"):
                with self.subTest(juego=juego, campo=campo):
                    minimo = requisitos.minimum
                    apenas = (
                        minimo.ram - 1 if campo == "ram" else minimo.ram,
                        minimo.vram - 1 if campo == "vram" else minimo.vram,
                        minimo.gpu - 1 if campo == "gpu" else minimo.gpu,
                        minimo.cpu - 1 if campo == "cpu" else minimo.cpu,
                    )
                    equipo = HardwareProfile(*apenas)
                    self.assertEqual(
                        check_compatibility(equipo, juego),
                        f"No, no te corre {juego} con esos componentes",
                    )

    def test_el_minimo_siempre_alcanza_el_minimo(self):
        for juego, requisitos in GAMES.items():
            with self.subTest(juego=juego):
                equipo = HardwareProfile(
                    ram=requisitos.minimum.ram,
                    vram=requisitos.minimum.vram,
                    gpu_level=requisitos.minimum.gpu,
                    cpu_level=requisitos.minimum.cpu,
                )
                self.assertIn("te corre", check_compatibility(equipo, juego))

    def test_cumplir_lo_recomendado_da_calidad_alta(self):
        for juego, requisitos in GAMES.items():
            with self.subTest(juego=juego):
                equipo = HardwareProfile(
                    ram=requisitos.recommended.ram,
                    vram=requisitos.recommended.vram,
                    gpu_level=requisitos.recommended.gpu,
                    cpu_level=requisitos.recommended.cpu,
                )
                self.assertEqual(
                    check_compatibility(equipo, juego),
                    f"Si, {juego} te corre en calidad alta (recomendado)",
                )


class DataIntegrityTest(unittest.TestCase):
    def test_lo_recomendado_es_mayor_o_igual_a_lo_minimo(self):
        for juego, requisitos in GAMES.items():
            with self.subTest(juego=juego):
                for campo in ("ram", "vram", "gpu", "cpu"):
                    with self.subTest(campo=campo):
                        self.assertGreaterEqual(
                            getattr(requisitos.recommended, campo),
                            getattr(requisitos.minimum, campo),
                        )

    def test_los_valores_son_positivos(self):
        for juego, requisitos in GAMES.items():
            with self.subTest(juego=juego):
                for nivel in (requisitos.minimum, requisitos.recommended):
                    for campo in ("ram", "vram", "gpu", "cpu"):
                        with self.subTest(campo=campo):
                            self.assertGreater(getattr(nivel, campo), 0)

    def test_los_niveles_de_componentes_estan_en_rango(self):
        for modelo, spec in GPUS.items():
            with self.subTest(modelo=modelo):
                self.assertGreaterEqual(spec.level, 1)
                self.assertLessEqual(spec.level, 10)
                self.assertGreater(spec.vram, 0)

        for modelo, nivel in CPUS.items():
            with self.subTest(modelo=modelo):
                self.assertGreaterEqual(nivel, 1)
                self.assertLessEqual(nivel, 10)

    def test_un_componente_maximo_alcanza_el_recomendado_de_cualquier_juego(self):
        equipo = HardwareProfile(ram=64, vram=24, gpu_level=10, cpu_level=9)

        for juego, requisitos in GAMES.items():
            with self.subTest(juego=juego):
                self.assertTrue(requisitos.recommended.is_met_by(equipo))


if __name__ == "__main__":
    unittest.main()
