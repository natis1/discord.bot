#!/bin/env python3

import re
from collections import AsyncIterable
from typing import Callable

from dateparser import parse
from discord import Colour, Embed, Member
from emoji import UNICODE_EMOJI
from datetime import datetime as dt

reg = re.compile("<:\w*:\w*>", re.IGNORECASE)
reg2 = re.compile(":\w*:", re.IGNORECASE)
with open("precepts") as f:
    precepts = [x.strip("\n") for x in f.readlines()]
regInd = "	🇦	🇧	🇨	🇩	🇪	🇫	🇬	🇭	🇮	🇯	🇰	🇱	🇲	🇳	🇴	🇵	🇶	🇷	🇸	🇹	🇺	🇻	🇼	🇽	🇾🇿"


def get_utc_date(string: str, tz: str = "") -> dt:
    """Gets a UTC datetime object from a string"""
    data_settings = {
        "TO_TIMEZONE": "UTC",
        "RETURN_AS_TIMEZONE_AWARE": False,
        "PREFER_DATES_FROM": "past",
    }
    if tz:
        data_settings["TIMEZONE"] = tz

    return parse(string, settings=data_settings)


async def say_embed(self, message):
    """Says stuff in a fancy embed."""
    embed = Embed()
    embed.colour = Colour.red()
    embed.description = message
    await self.say(embed=embed)


def is_mod(ctx):
    """Tells if the command user is a mod given a ctx for a message."""
    if str(ctx.message.author) == "56#1363":
        return True
    if str(ctx.message.author) == "Avenging Angle#0272":
        return True
    if any([role.permissions.manage_messages for role in ctx.message.author.roles]):
        return True


def is_emoji(emoji: str):
    """Returns whether or not a string is emoji"""
    if (
        emoji in UNICODE_EMOJI
        or reg.match(emoji)
        or reg2.match(emoji)
        or emoji in regInd
    ):
        return True
    else:
        return False


def is_int(s) -> bool:
    """Returns whether or not a number is an integer."""
    if s[0] in ("-", "+"):
        return s[1:].isdigit()
    return s.isdigit()


def opt_str(b: bool, s: str) -> str:
    return s if b else ""


# noinspection PyDunderSlots
def make_embed(desc: str, url: str) -> Embed:
    embed = Embed()
    embed.set_image(url=url)
    embed.colour = Colour.red()
    embed.colour = Colour(0xff0000)
    embed.description = desc
    return embed


# noinspection PyDunderSlots
def text_embed(desc: str) -> Embed:
    embed = Embed()
    embed.colour = Colour.red()
    embed.colour = Colour(0xff0000)
    embed.description = desc
    return embed


def get_nick(m: Member):
    try:
        return m.name or m.name
    except AttributeError:
        return m.name


def get_avatar(m: Member):
    try:
        return m.avatar_url or m.default_avatar_url
    except AttributeError:
        return m.default_avatar_url


async def afilter(gen: AsyncIterable, method: Callable):
    async for i in gen:
        if method(i):
            yield i


def first(iterable, cond: Callable = lambda x: True):
    return next(x for x in iterable if cond(x))


def first_or_default(iterable, cond: Callable = lambda x: True):
    return next((x for x in iterable if cond(x)), None)
