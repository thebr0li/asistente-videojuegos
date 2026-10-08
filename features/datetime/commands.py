from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from features.datetime.time import describe_day, describe_time
from shared.command import Command, KeywordCommand

if TYPE_CHECKING:
    from app.session import Context

HOUR_KEYWORDS = ("hora",)
DAY_KEYWORDS = ("que dia", "dia es", "dia de hoy", "fecha")


def datetime_commands() -> list[Command]:
    return [
        KeywordCommand("datetime.hour", HOUR_KEYWORDS, tell_time),
        KeywordCommand("datetime.day", DAY_KEYWORDS, tell_day),
    ]


def tell_time(context: Context, _text: str) -> None:
    context.voice.say(describe_time(datetime.datetime.now()))


def tell_day(context: Context, _text: str) -> None:
    context.voice.say(describe_day(datetime.datetime.now()))
