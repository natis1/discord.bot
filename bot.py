#!/bin/env python3

import asyncio
import pickle
import traceback
from contextlib import suppress
from datetime import datetime as dt
from os.path import isfile
from random import choice, randint
from typing import Dict, List

import discord
from discord import Channel, Colour, Embed, Forbidden, HTTPException, Permissions, Message, Emoji, Reaction
from discord.client import WaitedReaction
from discord.ext.commands import BadArgument, Bot, BucketType, CommandNotFound, CommandOnCooldown, Context, \
    MissingRequiredArgument, command, cooldown, when_mentioned_or
from discord.ext.commands.bot import _get_variable

from data import conrad_urls
from utils import is_mod, make_embed, first, first_or_default


class FiftySix(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for i in self._cogs:
            try:
                self.load_extension(f'cogs.{i}')
            except Exception as e:
                print(e)

        for i in self.cmds:
            self.add_command(getattr(self, i))

    async def say_embed(self, message):
        """Says stuff in a fancy embed."""
        embed = Embed()
        embed.colour = Colour.red()
        embed.description = message
        await self.say(embed=embed)

    async def say(self, *args, **kwargs):
        """self.say but it logs in a channel"""
        try:
            await super().say(*args, **kwargs)
        except Exception as e:
            if isinstance(e, Forbidden):
                # While this may look dumb ("just let the error float up")
                # The reason we do this is because
                # we want to allow the command to continue it's execution
                # even when the bot can't say what it wanted to
                # e.g adding to queue -- the bot says Adding to Queue
                # before adding to the queue
                ctx: Context = _get_variable('ctx')

                try:
                    channel = ctx.message.channel
                    await self.send_message(channel, "Bot is missing permissions for command {command}.")
                except Forbidden:  # ree
                    author = ctx.message.author
                    await self.send_message(author, f"Command {ctx.command} failed due to missing permissions.")
                return

            await self.send_message(self.get_channel("467063734800744448"), e)

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

    async def get_commands(self):
        def make_cmd(_key):
            @cooldown(1, 5, BucketType.user)
            async def cmd():
                url = choice(self.command_messages[_key])
                await self.say(embed=make_embed(_key, url))

            return cmd

        for i, j in self.command_channels.items():
            await self.load_command(i, j)
            self.command(name=i)(make_cmd(i))

    async def load_command(self, key, val, to_reload=False):
        if isfile(key[:-3]) and not to_reload:
            self.command_messages[key] = pickle.load(open(key[:-3], 'rb'))
            return

        if isfile(key) and not to_reload:
            self.command_messages[key] = pickle.load(open(key, 'rb'))
            return

        self.command_messages[key] = []
        async for k in self.logs_from(self.get_channel(val), before=dt.utcnow(), limit=10000):
            if k.attachments:
                self.command_messages[key].append(k.attachments[0]['url'])
            if k.embeds:
                with(suppress(IndexError, KeyError)):
                    self.command_messages[key].append(k.embeds[0]['image']['url'])

        with open(key[:-3], 'wb') as f:
            pickle.dump(self.command_messages[key], f)

    @command(pass_context=True)
    async def reload(self, ctx, r_command):
        if not is_mod(ctx): return

        if r_command == "all":
            for i in self.command_channels.keys():
                await self.load_command(i, self.command_channels[i], True)
            return

        await self.load_command(r_command, self.command_channels[r_command], True)

    _cogs: List[str] = \
        [
            "voice",
            "roles",
            "dev",
            "mod",
            "memes",
            "util"
        ]

    cmds: List[str] = \
        [
            "reload",
            "say_in",
            "conrad",
            "get_embed",
            "undo",
            "repeat",
            "invite",
            "dice",
            "delet_meme",
        ]

    async def on_ready(self):
        # TODO: Maybe add some more cool stuff?
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

        await self.get_commands()

        self.edit_profile(username="56 but bot")

    @command(pass_context=True)
    async def say_in(self, ctx, channel: Channel, *, msg: str):
        """Say a message in a given channel"""
        if not is_mod(ctx): return
        await self.send_message(channel, msg)

    @command()
    @cooldown(1, 10, BucketType.user)
    async def conrad(self):
        """Conrad."""
        await self.say(embed=make_embed("conrad", choice(conrad_urls)))

    @command(name="embed", hidden=False, pass_context=True, aliases=["em"])
    async def get_embed(self, ctx, *args):
        """Gets embed information about a message, used for debugging"""
        m = await self.get_message(ctx.message.channel, args[0])
        for e in m.embeds:
            await self.say(f"```{e}```")

    @command(pass_context=True, aliases=["↩"])
    async def undo(self, ctx):
        """Undo your last bot command. Only works for commands which output images/text"""
        message = ctx.message
        bot_msg = None
        async for m in self.logs_from(message.channel, around=message, limit=30):
            if m.author == self.user and bot_msg is None:
                bot_msg = m
            if bot_msg is not None and message.author == m.author:
                await self.delete_messages([bot_msg, m, message])

    repeatServers = ["401524346155434005"]

    @command(pass_context=True)
    async def repeat(self, ctx, times: int, *, content: str):
        """Repeats a message multiple times."""
        if str(ctx.message.author) == "56#1363":
            for i in range(times):
                await self.say(content)
            return
        if ctx.message.server.id in self.repeatServers and times <= 16:
            for i in range(times):
                await self.say_embed(content)

    server_log: Dict[str, str] = \
        {
            # "server_id": "channel_id"
            "452692088731992074": "453037865811836929",
            "445366035584122891": "447236501332426752",
            "453268588585811970": "453276465690312743",
            "459911387490025493": "460616352865189930",
        }

    async def on_message_delete(self, msg):
        """Log message deletes to respective log channels as specified in server_log dict"""
        if msg.server.id not in self.server_log.keys(): return
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

        await self.send_message(self.get_channel(self.server_log[msg.server.id]), embed=embedded)

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

    @command()
    async def invite(self):
        """Gives out an invite for the bot"""
        permissions = Permissions()

        for i in self.requiredPerms:
            setattr(permissions, i, True)

        await self.say(f"<{discord.utils.oauth_url('410926210017656852', permissions=permissions)}>")

    server_prefix: Dict[str, str] = \
        {
            "280800571760574464": ";",
            "453375619799973898": "&"
        }

    void_server = "453739385683312650"
    void_channel = "459925254559629312"

    async def add_role(self, server, role_name, member):
        sroles = list(server.roles)

        added_role = first(sroles, lambda x: x.name == role_name)
        wanderer = first_or_default(sroles, lambda x: x.name == "Wanderers")

        roles = [added_role] + [x for x in member.roles if x != wanderer]
        await self.replace_roles(member, *roles)

    async def on_message(self, message):
        if message.server and message.server.id in self.server_prefix and message.content:
            if message.content[0] == self.server_prefix[message.server.id]:
                message.content = "!" + message.content[1:]
            elif message.content[0] == "!":
                return

        if message.content[:9] == "oxyl play":
            message.content = "!play" + message.content[9:]

        # Normal running of commands
        await self.process_commands(message)

        if message.server.id == self.void_server or message.channel.id == self.void_channel:
            # Delete void server messages after 6.9420 seconds
            await asyncio.sleep(6.9420)
            await self.delet_this(message, 0)

    multi_server = "459911387490025493"

    async def on_member_join(self, member):
        """Automatically gives void role to new members on void server"""
        if member.server.id == self.void_server:
            await self.add_roles(member, member.server.role_hierarchy[2])
        elif member.server.id != self.multi_server:
            return
        await self.add_roles(member, list(filter(lambda x: x.name == "Wanderers", member.server.roles))[0])

    # noinspection PyUnusedLocal
    async def on_command(self, cmd, ctx):
        if ctx.message.author == (await self.application_info()).owner:
            ctx.command.reset_cooldown(ctx)

    @command(aliases=["roll"])
    async def dice(self, x: str):
        x = x.lower()

        if "d" not in x:
            await self.say(f"{x} is not a valid dice type.")
            return

        try:
            num = int(float(x.split("d")[::-1][0]))
            if num > 5000:
                await self.say("Can't go above 5000")
                return
            elif num <= 0:
                await self.say("Number cannot be equal to or below 0")
                return
        except ValueError:
            await self.say(f"{x.split('d')[::-1][0]} is not a valid number")
            return

        try:
            y = [int(i) for i in x.split("d")]

            if y[0] > 300:
                await self.say("Dice amount cannot go over 300.")
                return

            dlist = [y[1] for _ in range(y[0])]
        except (ValueError, TypeError):
            dlist = [x]

        # Roll Dice
        ret = [randint(1, int(x.split("d")[::-1][0])) for _ in dlist]
        await self.say(ret if len(ret) == 1 else repr(ret) + f" = {sum(ret)}")

    async def delet_this(self, message, num):
        """
        Attempts to delete a message,
        if it fails with a NotFound exception then it assumes the message is gone
        if it fails with a HTTPException, retry up to 15 more times (cause it could be due to Discord being spotty)
        """
        try:
            await self.delete_message(message)
        except discord.errors.NotFound:
            pass
        except discord.errors.HTTPException:
            if num > 15: return
            await self.delet_this(message, num + 1)

    @command()
    async def delet_meme(self, channel, msg):
        x = "❌"

        delet_channel = self.get_channel("474594963359924235")

        channel: Channel = self.get_channel(self.command_channels[channel])
        k: Message = await self.get_message(channel, msg)

        e = Embed(title="Delete?")

        if k.attachments:
            e.set_image(url=k.attachments[0]['url'])
        if k.embeds:
            with(suppress(IndexError, KeyError)):
                e.set_image(url=k.embeds[0]['image']['url'])

        msg = await self.send_message(delet_channel, embed=e)

        self.add_reaction(msg,    x)
        self.add_reaction(msg, "✅")

        while True:
            r: WaitedReaction = await self.wait_for_reaction(emoji=x)

            if r is None:
                continue

            if r.reaction.emoji != "✅" and r.reaction.emoji != x:
                continue

            if r.reaction.count >= 2:
                if r.reaction.emoji == "✅":
                    await self.delete_message(k)
                await self.delete_message(msg)
                return

    async def on_command_error(self, e, ctx: Context):
        if isinstance(e, (CommandNotFound, CommandOnCooldown, MissingRequiredArgument, BadArgument)):
            return

        if isinstance(e, Forbidden):
            try:
                await self.send_message(ctx.message.channel, "Bot is missing permissions.")
            except Forbidden:  # ree
                await self.send_message(ctx.message.author, f"Command {ctx.command} failed due to missing permissions.")
            return

        if isinstance(e, HTTPException):
            # Might be due to the message being too long :(
            print(ctx.message.content)
            print(ctx.message.embeds)
            return

        tb = traceback.format_exception(type(e), e.__cause__, e.__traceback__)
        embed = discord.Embed()
        embed.title = '**__Command Error__**'
        embed.description = 'Shard: **{0}**'.format(self.shard_id)
        embed.add_field(name='Command', value='{0}'.format(ctx.command.name))
        embed.add_field(name='Message', value=ctx.message.clean_content, inline=False)
        embed.add_field(name='Server',
                        value='{0.name} <{0.id}>'.format(
                            ctx.message.server) if ctx.message.server else 'Private Message')
        embed.add_field(name='Type', value='__{0}__'.format(type(e)))
        embed.add_field(name='File', value=str(e.__traceback__.tb_frame.f_code.co_filename) + '\nLine: **{0}**'.format(
            e.__traceback__.tb_lineno), inline=False)
        embed.add_field(name='Traceback', value=f"```py\n{(''.join(tb))}```", inline=False)
        embed.set_author(name='{0} <{0.id}>'.format(ctx.message.author), icon_url=ctx.message.author.avatar_url)
        embed.colour = discord.Color.red()
        embed.timestamp = dt.now()
        print(''.join(tb))
        await self.send_message(self.get_channel("467063734800744448"), embed=embed)


bot = FiftySix(command_prefix=when_mentioned_or('!'), description="56 but bot")

if __name__ == "__main__":
    from config import key

    # noinspection PyBroadException
    try:
        bot.run(key, reconnect=True)
    except Exception as error:
        print(f"Bot Errored due to {error}, Restarting.")
