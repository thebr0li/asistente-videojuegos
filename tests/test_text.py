"""Tests de las utilidades de texto compartidas."""

import unittest

from shared.text import clean_text, contains_keyword, normalize, remove_words


class NormalizeTest(unittest.TestCase):
    def test_pasa_a_minusculas(self):
        self.assertEqual(normalize("QUE HORA ES"), "que hora es")

    def test_saca_las_tildes(self):
        self.assertEqual(normalize("qué día es hoy"), "que dia es hoy")

    def test_conserva_las_enes(self):
        self.assertEqual(normalize("mañana"), "manana")

    def test_no_toca_el_texto_sin_tildes(self):
        self.assertEqual(normalize("salir"), "salir")


class ContainsKeywordTest(unittest.TestCase):
    def test_encuentra_la_palabra(self):
        self.assertTrue(contains_keyword("que hora es", "hora"))

    def test_ignora_mayusculas_y_tildes(self):
        self.assertTrue(contains_keyword("Qué Día es HOY", "que dia"))
        self.assertTrue(contains_keyword("precio de la acción de nvidia", "accion"))

    def test_no_encuentra_lo_que_no_esta(self):
        self.assertFalse(contains_keyword("hola que tal", "hora"))


class RemoveWordsTest(unittest.TestCase):
    def test_saca_las_palabras(self):
        self.assertEqual(remove_words("busca en wikipedia lionel messi", ["wikipedia", "busca"]), "en lionel messi")

    def test_respeta_los_limites_de_palabra(self):
        self.assertEqual(remove_words("mis componentes", ["pon"]), "mis componentes")

    def test_no_toca_palabras_mas_largas(self):
        self.assertEqual(remove_words("reproductores", ["pon"]), "reproductores")

    def test_ignora_las_mayusculas(self):
        self.assertEqual(remove_words("SALIR ahora", ["salir"]), "ahora")

    def test_limpia_los_espacios_sobrantes(self):
        self.assertEqual(remove_words("  reproduce   la cancion ", ["reproduce", "la"]), "cancion")

    def test_un_texto_sin_las_palabras_queda_igual(self):
        self.assertEqual(remove_words("bohemian rhapsody", ["pon"]), "bohemian rhapsody")


class CleanTextTest(unittest.TestCase):
    def test_saca_el_espacio_invisible(self):
        self.assertEqual(clean_text("\u200bResumen"), "Resumen")

    def test_une_las_lineas(self):
        self.assertEqual(clean_text("primera\nsegunda"), "primera segunda")

    def test_recorta_los_extremos(self):
        self.assertEqual(clean_text("  resumen  "), "resumen")


if __name__ == "__main__":
    unittest.main()
