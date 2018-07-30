#!/bin/env python3

import asyncio
import pickle
import re
import tempfile
import traceback
from collections import AsyncIterable
from contextlib import suppress
from copy import deepcopy
from datetime import datetime as dt, timedelta
from os.path import isfile, join
from random import choice, randint
from typing import Callable, Dict

import discord
from dateparser import parse
from discord import Channel, Colour, Embed, Member, Message, Permissions, Server, User, errors
from discord.ext import commands
from discord.ext.commands import Bot, CommandOnCooldown
from emoji import UNICODE_EMOJI

from HollowText import create_image_file

bot = Bot(command_prefix='!', description="56 but bot")

reg = re.compile('<:\w*:\w*>', re.IGNORECASE)
reg2 = re.compile(':\w*:', re.IGNORECASE)
with open('precepts') as f:
    precepts = [x.strip('\n') for x in f.readlines()]
conrad = ["https://cdn.discordapp.com/attachments/297468195026239489/410229029841534996/Nice.png",
          "https://image.prntscr.com/image/QkwXy2XnTMKN9IFSKWxnAg.png",
          'https://cdn.discordapp.com/attachments/297468195026239489/410229255084179466/DeepinScreenshot_select'
          '-area_20180205192432.png']
regInd = "	🇦	🇧	🇨	🇩	🇪	🇫	🇬	🇭	🇮	🇯	🇰	🇱	🇲	🇳	🇴	🇵	🇶	🇷	🇸	🇹	🇺	🇻	🇼	🇽	🇾🇿"


def get_utc_date(string: str, tz: str = "") -> dt:
    """Gets a UTC datetime object from a string"""
    data_settings = \
        {
            'TO_TIMEZONE':              'UTC',
            'RETURN_AS_TIMEZONE_AWARE': False,
            'PREFER_DATES_FROM':        'past'
        }
    if tz:
        data_settings['TIMEZONE'] = tz

    return parse(string, settings=data_settings)


async def say_embed(self, message):
    """Says stuff in a fancy embed."""
    embed = Embed()
    embed.colour = Colour.red()
    embed.description = message
    await self.say(embed=embed)


Bot.say_embed = say_embed

origSay = Bot.say


async def say(self, *args, **kwargs):
    """Bot.say but it logs in a channel"""
    try:
        await origSay(self, *args, **kwargs)
    # TODO: Permissions
    except Exception as e:
        await bot.send_message(bot.get_channel(""), e)


Bot.say = say


def is_mod(ctx):
    """Tells if the command user is a mod given a ctx for a message."""
    if str(ctx.message.author) == "56#1363": return True
    if str(ctx.message.author) == "PrehistoricBanana#0003": return True
    if any([role.permissions.manage_messages for role in ctx.message.author.roles]): return True


def is_emoji(emoji: str):
    """Returns whether or not a string is emoji"""
    if emoji in UNICODE_EMOJI or reg.match(emoji) or reg2.match(
            emoji) or emoji in regInd:
        return True
    else:
        return False


def is_int(s) -> bool:
    """Returns whether or not a number is an integer."""
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()


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


command_channels: Dict[str, str] = \
    {
        "meta":      "467382508397527050",
        "56pls":     "465897058562211855",
        "bananapls": "465900714422435851",
        "faerenpls": "465897072743415838",
        "finchpls":  "466634821334990859",
        "paperspls": "465897086425104384",
        "jonnypls":  "serialized"
    }

command_messages: Dict[str, list] = { }


async def get_commands():
    def make_cmd(key):
        async def command():
            url = choice(command_messages[key])
            await bot.say(embed=make_embed(key, url))

        return command

    for i, j in command_channels.items():
        await load_command(i, j)
        bot.command(name=i)(make_cmd(i))


async def load_command(key, val, to_reload=False):
    global command_messages

    if isfile(key[:-3]) and not to_reload:
        command_messages[key] = pickle.load(open(key[:-3], 'rb'))
        return

    if isfile(key) and not to_reload:
        command_messages[key] = pickle.load(open(key, 'rb'))
        return

    command_messages[key] = []
    async for k in bot.logs_from(bot.get_channel(val), before=dt.utcnow(), limit=10000):
        if k.attachments:
            command_messages[key].append(k.attachments[0]['url'])
        if k.embeds:
            with(suppress(IndexError, KeyError)):
                command_messages[key].append(k.embeds[0]['image']['url'])

    with open(key[:-3], 'wb') as f:
        pickle.dump(command_messages[key], f)


@bot.command(pass_context=True)
async def reload(ctx, command):
    if not is_mod(ctx): return

    if command == "all":
        for i in command_channels.keys():
            await load_command(i, command_channels[i], True)
        return

    await load_command(command, command_channels[command], True)


@bot.event
async def on_ready():
    # TODO: Maybe add some more cool stuff?
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    #bot.load_extension('cogs.roles')
    #bot.load_extension('cogs.voice')
    bot.edit_profile(username="56 but bot")

    msglist = []
    for i in bot.logs_from(bot.get_channel("427640085555707904"), before=dt.utcnow(), limit=10000):
        msglist.append(i)

    embeds = []
    i: Message
    for i in msglist[::-1]:
        embed = Embed()
        embed.set_author(name=get_nick(i.author), icon_url=get_avatar(i.author))
        if len(i.attachments) == 1:
            embed.set_image(url=i.attachments[0]["url"])
        elif len(i.attachments) > 1:
            for ind, j in enumerate(i.attachments):
                aembed = deepcopy(embed)
                aembed.description = f"Image {ind+1}/{len(i.attachments)}"
                aembed.set_image(url=j["url"])
                embeds.append(aembed)
        if i.embeds:
            with(suppress(IndexError, KeyError)):
                aembed = deepcopy(embed)
                aembed.set_image(url=i.embeds[0]['image']['url'])
                embeds.append(aembed)
        embed.description = i.content
        if embed.description or embed.image.url:
            print(embed.image)
            print(type(embed.image))
            embeds.append(embed)

    with open('hkannounce', 'wb') as f:
        pickle.dump(embeds, f)

    #await get_commands()


@bot.command(pass_context=True)
async def say_in(ctx, channel: Channel, *msg: str):
    """Say a message in a given channel"""
    if not is_mod(ctx): return
    await bot.send_message(channel, msg)


@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def conrad(*args):
    """Conrad."""
    await bot.say(embed=make_embed("conrad", choice(conrad)))


@bot.command(name="embed", hidden=False, pass_context=True, aliases=["em"])
async def get_embed(ctx, *args):
    """Gets embed information about a message, used for debugging"""
    m = await bot.get_message(ctx.message.channel, args[0])
    for e in m.embeds:
        await bot.say(f"```{e}```")


@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def precept(*args):
    """Gives zote's precepts"""
    if args:
        if is_int(args[0]):
            await bot.say(embed=text_embed(str(int(args[0])) + ": " + precepts[int(args[0]) - 1]))
        else:
            rand = randint(0, len(precepts))
            await bot.say(embed=text_embed(str(rand) + ": " + precepts[rand - 1]))
    else:
        rand = randint(1, len(precepts))
        await bot.say(embed=text_embed(str(rand) + ": " + precepts[rand - 1]))


@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def neglect():
    """Shows an image of neglect"""
    from data import zote
    await bot.say(embed=zote)


@bot.command(aliases=["XD", "xD", "Xd"])
@commands.cooldown(1, 10, commands.BucketType.user)
async def xd(f: str, b: str):
    """XD out of emoji."""
    if is_emoji(f) and is_emoji(b):
        await bot.say_embed(
            f"{f}{b*2}{b}{f}{b}{f*2}{f}{b}\n{b}{f}{b}{f}{b*2}{f}{b*2}{f}\n{b*2}{f}{b*2}"
            f"{b}{f}{b*2}{f}\n{b}{f}{b}{f}{b*2}{f}{b*2}{f}\n{f}{b*2}{b}{f}{b}{f*2}{f}{b}")
    else:
        await bot.say_embed("Invalid emoji")


@bot.command(pass_context=True)
async def ban(ctx):
    """Ban image. Mod-only."""
    if not is_mod(ctx): return
    from data import ban_hammer
    await bot.say(embed=ban_hammer)


@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def udungo(u_dungo=""):
    """u dungo"""
    from data import dungo_orig, dungo
    if u_dungo.lower() == "orig" or u_dungo.lower() == "original":
        await bot.say(embed=dungo_orig)
    else:
        await bot.say(embed=dungo)


@bot.command(aliases=["KDT", "Kdt"])
@commands.cooldown(1, 10, commands.BucketType.user)
async def kdt():
    """KDT"""
    from data import KDT
    await bot.say(embed=choice(KDT))


@bot.command(aliases=["Finchmeister", "finch", "Finch", "sln"])
async def finchmeister():
    """Disappointment."""
    await bot.say(embed=make_embed("Disappointment",
                                   "https://cdn.discordapp.com/attachments/421554516023050261/450123677359669248"
                                   "/unknown.png"))


async def image_maker(channel: Channel, message: str):
    """Outputs text as stiched images of Hollow Knight letters, if it fails split it in two and try again"""
    path = join(tempfile.gettempdir(), "meme.png")
    create_image_file(message, path, scaling=True)
    try:
        await bot.send_file(channel, path)
    except errors.HTTPException as e:
        await image_maker(channel, message[:len(message) // 2])
        await image_maker(channel, message[len(message) // 2:])


@bot.command(aliases=["htext", "htxt", "hollowtext", "hollowText", "hktext"], pass_context=True)
@commands.cooldown(1, 10, commands.BucketType.user)
async def hollow_text(ctx, *, message: str):
    """Outputs text as stiched images of Hollow Knight letters"""
    await image_maker(ctx.message.channel, message)


@bot.command(pass_context=True, aliases=["↩"])
async def undo(ctx):
    """Undo your last bot command. Only works for commands which output images/text"""
    message = ctx.message
    bot_msg = None
    async for m in bot.logs_from(message.channel, around=message, limit=30):
        if m.author == bot.user and bot_msg is None:
            bot_msg = m
        if bot_msg is not None and message.author == m.author:
            await bot.delete_messages([bot_msg, m, message])

repeatServers = ["401524346155434005"]


@bot.command(pass_context=True)
async def repeat(ctx, times: int, *, content: str):
    """Repeats a message multiple times."""
    if str(ctx.message.author) == "56#1363":
        for i in range(times):
            await bot.say(content)
        return
    if ctx.message.server.id in repeatServers and times <= 16:
        for i in range(times):
            await bot.say_embed(content)


@bot.command(pass_context=True, aliases=["death", "purge"])
async def clear(ctx, num: int, user: User = None):
    """Clear the given number of messages. Optional user param."""
    if not is_mod(ctx): return
    counter = 0

    def check_user(msg: Message):
        nonlocal counter
        if counter < num + 1 and user is None:
            counter += 1
            return True
        elif counter < num + 1 and msg.author == user:
            counter += 1
            return True
        return False

    try:
        await bot.purge_from(ctx.message.channel,
                             around=ctx.message,
                             limit=101,
                             before=ctx.message.timestamp + timedelta(seconds=5),
                             check=check_user)
    except Exception as e:
        await bot.say(e)


@bot.command(pass_context=True, aliases=["deleteTime", "delTime"])
async def del_time(ctx, after, before=None):
    """Deletes messages given a time at which to start and an optional time at which to end"""
    if not is_mod(ctx): return
    args = {}

    if before: args['before'] = get_utc_date(before)
    args['after'] = get_utc_date(after)

    try:
        print(args['after'])
        await bot.purge_from(ctx.message.channel, **args, limit=4000)
    except Exception as e:
        await bot.say(e)


@bot.command(pass_context=True, aliases=["deleteTimeUser", "delTimeUser"])
async def del_time_user(ctx, after, user: User):
    """Deletes messages given a time at which to start and an optional time at which to end"""
    if not is_mod(ctx): return
    args = {}

    def check_user(msg: Message):
        return msg.author == user

    args['after'] = get_utc_date(after)

    try:
        print(args['after'])
        await bot.purge_from(ctx.message.channel, **args, limit=4000, check=check_user)
    except Exception as e:
        await bot.say(e)


@bot.command(pass_context=True, aliases=["deleteTimeTZ", "delTimeTZ"])
async def del_time_tz(ctx, tzi, after, before=None):
    """Deletes messages given a time zone, a time at which to start, and an optional time at which to end"""
    if not is_mod(ctx): return
    args = {}

    if before: args['before'] = get_utc_date(before, tzi)
    args['after'] = get_utc_date(after, tzi)

    try:
        print(args['after'])
        await bot.purge_from(ctx.message.channel, **args, limit=4000)
    except Exception as e:
        await bot.say(e)


@bot.command(pass_context=True, aliases=["die"])
async def kill(ctx):
    """Developer only command. Don't bother."""
    # Kills the bot
    if str(ctx.message.author) != "56#1363": return
    exit(0)


@bot.command(pass_context=True, aliases=["ctx", "eval"])
async def eval_ctx(ctx, *, msg: str):
    """Developer only command. Don't bother."""
    # Runs code
    # Used for debugging.
    if str(ctx.message.author) != "56#1363": return
    try:
        await bot.say(await eval(msg))
    except Exception as e:
        await bot.say(e)


@bot.command(pass_context=True, aliases=["exec"])
async def exec_ctx(ctx, *, msg: str):
    """Developer only command. Don't bother."""
    # Runs code
    # Used for debugging.
    if str(ctx.message.author) != "56#1363": return
    try:
        await bot.say(await exec(msg))
    except Exception as e:
        await bot.say(e)


@bot.command(pass_context=True, aliases=["delete"])
async def delete_this(ctx, msg_id: str, channel_id=None):
    """Delete a message by id"""
    if not is_mod(ctx): return
    channel = bot.get_channel(channel_id) if channel_id else ctx.message.channel
    await bot.delete_message(await bot.get_message(channel, msg_id))
    await bot.delete_message(ctx.message)


server_log: Dict[str, str] = \
    {
        # "server_id": "channel_id"
        "452692088731992074": "453037865811836929",
        "445366035584122891": "447236501332426752",
        "453268588585811970": "453276465690312743",
        "459911387490025493": "460616352865189930",
    }


@bot.event
async def on_message_delete(msg):
    return
    """Log message deletes to respective log channels as specified in server_log dict"""
    if msg.server.id not in server_log.keys(): return
    embedded = Embed(title=f"Message deleted in {str(msg.channel)}",
                     description=msg.content,
                     timestamp=msg.timestamp,
                     colour=Colour.red())
    embedded.set_author(name=msg.author.name + "#" + msg.author.discriminator, icon_url=msg.author.avatar_url)

    has_image = False
    for ind, i in enumerate(msg.attachments):
        embedded.add_field(name=f"Image {ind}", value=str(i['url']))

    for e in msg.embeds:
        for i, j in e.items():
            embedded.add_field(name=f"Deleted {i}", value=str(j), inline=True)

            if i != "image": continue
            if not has_image:
                embedded.set_image(url=j['url'])
                has_image = True
            else:
                embedded.add_field(name=f"Image {ind}", value=str(j['url']))

    await bot.send_message(bot.get_channel(server_log[msg.server.id]), embed=embedded)


@bot.command(pass_context=True, aliases=["memberCount"])
async def membercount(ctx):
    """Display server members"""
    embedded = Embed(title="Server Members",
                     colour=Colour.red())
    embedded.set_author(name=ctx.message.server.name, icon_url=ctx.message.server.icon_url)
    bots = list(filter(lambda x: x.bot, ctx.message.server.members))
    total = len(ctx.message.server.members)
    embedded.add_field(name="All", value=str(total))
    embedded.add_field(name="Bots", value=str(len(bots)))
    embedded.add_field(name="Humans", value=str(total - len(bots)))
    await bot.say(embed=embedded)


# Bot required permissions
requiredPerms = \
    [
        "administrator",
        "manage_channels",
        "add_reactions",
        "read_messages",
        "send_messages",
        "manage_messages",
        "embed_links",
        "attach_files",
        "read_message_history",
        "external_emojis",
        "connect",
        "speak"
    ]


@bot.command()
async def invite():
    """Gives out an invite for the bot"""
    permissions = Permissions()

    for i in requiredPerms:
        setattr(permissions, i, True)

    await bot.say(f"<{discord.utils.oauth_url('410926210017656852', permissions=permissions)}>")


# Predefined bot responses to certain messages
predefined: Dict[str, str] = \
    {
        "angle":           "is bad at hk",
        "avenging angle":  "needs easy mode to play hk",
        "faeren":          "does not want to be called gay",
        "nth":             "karoeke",
        "papers":          "Yeah, I wish Papers was here too",
        "perdungo":        "also not having 56 but bot respond to my name is a good thing\n"
                           "means I'm not known enough to be hated",
        "danny":           "I am too gay for 56's standards",
        "molamola":        "<:hollowgay:460403705036931072>",
        "banana":          "🍌",
        "goldenlightning": "I bet I'm not gay enough for 56 to add a response for 56 but bot when someone says my "
                           "name <:grimmdab:459946281457156116> "

    }

server_prefix: Dict[str, str] = \
    {
        "280800571760574464": ";",
        "453375619799973898": "&"
    }

void_server = "453739385683312650"
void_channel = "459925254559629312"


@bot.event
async def on_message(message):
    return

    if message.content.lower() in predefined:
        # Predefined bot responses from dict
        await bot.send_message(message.channel, predefined[message.content.lower()])

    if message.server.id in server_prefix and message.content:
        if message.content[0] == server_prefix[message.server.id]:
            message.content = "!" + message.content[1:]
        elif message.content[0] == "!":
            return

    if message.content[:9] == "oxyl play":
        message.content = "!play" + message.content[9:]

    # Normal running of commands
    await bot.process_commands(message)

    if message.server.id == void_server or message.channel.id == void_channel:
        # Delete void server messages after 6.9420 seconds
        await asyncio.sleep(6.9420)
        await delet_this(message, 0)


multi_server = "459911387490025493"


@bot.event
async def on_member_join(member):
    """Automatically gives void role to new members on void server"""
    if member.server.id == void_server:
        await bot.add_roles(member, member.server.role_hierarchy[2])
    elif member.server.id != multi_server:
        return
    await bot.add_roles(member, list(filter(lambda x: x.name == "Wanderers", member.server.roles))[0])


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


@bot.command(pass_context=True)
async def copy_channel(ctx, server: str, co_channel: str, to_channel: Channel, to_filter=None, limit=10000):
    if not is_mod(ctx): return
    server: Server = bot.get_server(server)
    print(server.name)
    channel: Channel = server.get_channel(co_channel)
    if to_filter == "image":
        def to_filter(msg: Message):
            if msg.attachments or msg.embeds:
                return True
    else:
        # noinspection PyUnusedLocal
        def to_filter(msg: Message):
            return True

    msglist = []
    async for i in afilter(bot.logs_from(channel, before=dt.utcnow(), limit=limit), to_filter):
        msglist.append(i)

    i: Message
    for i in msglist[::-1]:
        embed = Embed()
        embed.set_author(name=get_nick(i.author), icon_url=get_avatar(i.author))

        if len(i.attachments) == 1:
            embed.set_image(url=i.attachments[0]["url"])
        elif len(i.attachments) > 1:
            for ind, j in enumerate(i.attachments):
                aembed = deepcopy(embed)
                aembed.description = f"Image {ind+1}/{len(i.attachments)}"
                aembed.set_image(url=j["url"])

                await bot.send_message(to_channel, embed=aembed)

        if i.embeds:
            with(suppress(IndexError, KeyError)):
                aembed = deepcopy(embed)
                aembed.set_image(url=i.embeds[0]['image']['url'])

                await bot.send_message(to_channel, embed=aembed)

        embed.description = i.content
        if embed.description or embed.image.url:
            print(embed.image)
            print(type(embed.image))
            await bot.send_message(to_channel, embed=embed)


@bot.command(pass_context=True)
async def list_role_ids(ctx):
    server = ctx.message.server
    embed = Embed()
    for i in server.roles:
        embed.add_field(name=str(i), value=str(i.id))
    await bot.say(embed=embed)


def first(iterable, cond: Callable = lambda x: True):
    return next(x for x in iterable if cond(x))


def first_or_default(iterable, cond: Callable = lambda x: True):
    return next((x for x in iterable if cond(x)), None)


@bot.command(aliases=["roll"])
async def dice(x: str):
    x = x.lower()

    try:
        num = int(x.split("d")[::-1][0])
        if num > 5000:
            await bot.say("Can't go above 5000")
            return
        elif num <= 0:
            await bot.say("Number cannot be equal to or below 0")
            return
    except ValueError:
        await bot.say(f"{x.split('d')[::-1][0]} is not a valid number")

    try:
        y = [int(i) for i in x.split("d")]

        if y[0] > 300:
            await bot.say("Dice amount cannot go over 300.")
            return

        dlist = [y[1] for _ in range(y[0])]
    except (ValueError, TypeError):
        dlist = [x]

    # Roll Dice
    ret = [randint(1, int(x.split("d")[::-1][0])) for i in dlist]
    await bot.say(ret if len(ret) == 1 else repr(ret) + f" = {sum(ret)}")


async def delet_this(message, num):
    """
    Attempts to delete a message,
    if it fails with a NotFound exception then it assumes the message is gone
    if it fails with a HTTPException, it'll retry up to 15 more times
    """
    try:
        await bot.delete_message(message)
    except discord.errors.NotFound:
        pass
    except discord.errors.HTTPException:
        if num > 15: return
        await delet_this(message, num + 1)


@bot.event
async def on_command_error(e, ctx):
    from discord.ext.commands import CommandNotFound

    if isinstance(e, CommandNotFound):
        return

    if isinstance(e, CommandOnCooldown):
        return

    tb = traceback.format_exception(type(e), e.__cause__, e.__traceback__)
    embed = discord.Embed()
    embed.title = '**__Command Error__**'
    embed.description = 'Shard: **{0}**'.format(bot.shard_id)
    embed.add_field(name='Command', value='{0}'.format(ctx.command.name))
    embed.add_field(name='Message', value=ctx.message.clean_content, inline=False)
    embed.add_field(name='Server', value='{0.name} <{0.id}>'.format(ctx.message.server) if ctx.message.server else 'Private Message')
    embed.add_field(name='Type', value='__{0}__'.format(type(e)))
    embed.add_field(name='File', value=str(e.__traceback__.tb_frame.f_code.co_filename)+'\nLine: **{0}**'.format(e.__traceback__.tb_lineno), inline=False)
    embed.add_field(name='Traceback', value=f"```py\n{(''.join(tb))}```", inline=False)
    embed.set_author(name='{0} <{0.id}>'.format(ctx.message.author), icon_url=ctx.message.author.avatar_url)
    embed.colour = discord.Color.red()
    embed.timestamp = dt.now()
    await bot.send_message(bot.get_channel("467063734800744448"), embed=embed)

#if __name__ == "__main__":
bot.run("ybham6@", reconnect=True)
