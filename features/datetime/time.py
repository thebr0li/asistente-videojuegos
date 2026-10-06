"""Mensajes que dependen del reloj."""

from __future__ import annotations

import datetime

WEEKDAYS = {0: "Lunes", 1: "Martes", 2: "Miercoles", 3: "Jueves", 4: "Viernes", 5: "Sabado", 6: "Domingo"}

NIGHT_UNTIL = 6
NIGHT_FROM = 20
AFTERNOON_FROM = 13


def describe_time(moment: datetime.datetime) -> str:
    return f"En este momento son las {moment.hour} horas con {moment.minute} minutos"


def describe_day(moment: datetime.datetime) -> str:
    return "Hoy es " + WEEKDAYS[moment.weekday()]


def greeting_for(moment: datetime.datetime) -> str:
    if moment.hour < NIGHT_UNTIL or moment.hour > NIGHT_FROM:
        greeting = "Buenas noches"
    elif moment.hour < AFTERNOON_FROM:
        greeting = "Buen dia"
    else:
        greeting = "Buenas tardes"
    return greeting + ", en que te puedo ayudar?"
