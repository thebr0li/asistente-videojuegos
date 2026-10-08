"""Tests de los mensajes que dependen del reloj."""

import datetime
import unittest

from features.datetime.time import WEEKDAYS, describe_day, describe_time, greeting_for


def momento(dia=6, mes=10, anio=2026, hora=12, minuto=0):
    return datetime.datetime(anio, mes, dia, hora, minuto)


SEMANA = {
    0: (5, "Lunes"),
    1: (6, "Martes"),
    2: (7, "Miercoles"),
    3: (8, "Jueves"),
    4: (9, "Viernes"),
    5: (10, "Sabado"),
    6: (11, "Domingo"),
}


class DescribeTimeTest(unittest.TestCase):
    def test_dice_la_hora_y_los_minutos(self):
        self.assertEqual(describe_time(momento(hora=14, minuto=35)), "En este momento son las 14 horas con 35 minutos")

    def test_no_rellena_con_ceros(self):
        self.assertEqual(describe_time(momento(hora=9, minuto=5)), "En este momento son las 9 horas con 5 minutos")

    def test_medianoche(self):
        self.assertEqual(describe_time(momento(hora=0, minuto=0)), "En este momento son las 0 horas con 0 minutos")


class DescribeDayTest(unittest.TestCase):
    def test_nombre_de_cada_dia_de_la_semana(self):
        for dia, (fecha, nombre) in SEMANA.items():
            with self.subTest(dia=dia):
                self.assertEqual(describe_day(momento(dia=fecha)), f"Hoy es {nombre}")

    def test_los_siete_dias_estan_cubiertos(self):
        self.assertEqual(sorted(WEEKDAYS), list(range(7)))


class GreetingForTest(unittest.TestCase):
    def test_saluda_segun_la_hora(self):
        casos = [
            (3, "Buenas noches"),
            (5, "Buenas noches"),
            (6, "Buen dia"),
            (12, "Buen dia"),
            (13, "Buenas tardes"),
            (20, "Buenas tardes"),
            (21, "Buenas noches"),
            (23, "Buenas noches"),
        ]

        for hora, saludo in casos:
            with self.subTest(hora=hora):
                self.assertEqual(greeting_for(momento(hora=hora)), f"{saludo}, en que te puedo ayudar?")


if __name__ == "__main__":
    unittest.main()
