from contextlib import suppress
from copy import deepcopy
from datetime import datetime as dt

from discord import Channel, Client, Colour, Embed, Message, Emoji, Reaction
from discord.ext.commands import Bot, command
from discord.ext.commands.converter import MemberConverter
from discord.utils import get

from utils import afilter, get_avatar, get_nick, is_mod

import asyncio

# noinspection PyUnusedFunction
class Util:
    def __init__(self, bot):
        self.bot: Bot = bot

    @command(pass_context=True)
    async def unmute(self, ctx, *args):
        member = MemberConverter(ctx, args[0]).convert() if len(args) > 0 and args[0] else ctx.message.author
        server = ctx.message.server
        if server.id not in self.bot.audit_log.keys() or not is_mod(ctx):
            return
        if not get(member.roles, name="Muted"):
            await self.bot.say(f"The user: {str(member.name)}\#{str(member.discriminator)} was not muted.")
            return
        await self.bot.remove_rank(server, "Muted", member)
        e = Embed(
            title=f"Member: {str(member.name)}\#{str(member.discriminator)} unmuted",
            description=member.mention + " " + member.display_name,
            colour=0xFFFF00,
        )
        e.set_author(name=get_nick(member), icon_url=get_avatar(member))
        e.set_thumbnail(url=get_avatar(member))
        await self.bot.send_message(
            self.bot.get_channel(self.bot.audit_log[member.server.id]), embed=e
        )
        emojimeme=get(self.bot.get_all_emojis(), name='gladrad')
        await self.bot.add_reaction(ctx.message, emojimeme )



    async def unmuteinternal(self, server, member, time):
        await asyncio.sleep(int(time) * 60)
        if not get(member.roles, name="Muted"):
            return
        await self.bot.remove_rank(server, "Muted", member)
        e = Embed(
            title=f"Member: {str(member.name)}\#{str(member.discriminator)} unmuted because moths are better than mantises.",
            description=member.mention + " " + member.display_name,
            colour=0xFFFF00,
        )
        e.set_author(name=get_nick(member), icon_url=get_avatar(member))
        e.set_thumbnail(url=get_avatar(member))
        await self.bot.send_message(
            self.bot.get_channel(self.bot.audit_log[member.server.id]), embed=e
        )


    @command(pass_context=True)
    async def mute(self, ctx, *args):
        member = MemberConverter(ctx, args[0]).convert() if len(args) > 0 and args[0] else ctx.message.author
        server = ctx.message.server
        if server.id not in self.bot.audit_log.keys() or not is_mod(ctx):
            return
        if len(args) < 2 or not args[1].isdigit():
            await self.bot.say("Invalid argument. Please specify a user and a time in minutes as a number.")
            return
        if get(member.roles, name="Muted"):
            await self.bot.say(f"The user: {str(member.name)}\#{str(member.discriminator)} was already muted.")
            return
        e = Embed(
            title=f"Member: {str(member.name)}\#{str(member.discriminator)} muted for {args[1]} minute(s)",
            description=member.mention + " " + member.display_name,
            colour=Colour.red(),
        )
        e.set_author(name=get_nick(member), icon_url=get_avatar(member))
        e.set_thumbnail(url=get_avatar(member))
        await self.bot.send_message(
            self.bot.get_channel(self.bot.audit_log[member.server.id]), embed=e
        )
        await self.bot.add_rank(server, "Muted", member)
        emojimeme=get(self.bot.get_all_emojis(), name='jellysad')
        await self.bot.add_reaction(ctx.message, emojimeme )
        await self.unmuteinternal(server, member, args[1])

    @command(pass_context=True)
    async def whois(self, ctx, *args):
        member = MemberConverter(ctx, args[0]).convert() if len(args) > 0 and args[0] else ctx.message.author
        server = ctx.message.server

        e = Embed()
        e.set_author(name=get_nick(member), icon_url=get_avatar(member))
        e.description=member.mention
        e.set_thumbnail(url=get_avatar(member))
        e.add_field(name= "Status", value=member.status)
        e.add_field(name= "Joined", value=member.joined_at.strftime("%a %Y-%m-%d %H:%MUTC"))
        joinpos=1
        for m in server.members:
            if m.joined_at < member.joined_at:
                joinpos += 1

        e.add_field(name= "Join Position", value=str(joinpos))

        e.add_field(name= "Registered", value=member.created_at.strftime("%a %Y-%m-%d %H:%MUTC"))
        roleString = ""
        for rm in member.roles[1:]:
            roleString += rm.mention + "\t"
        e.add_field(name= "Roles (" + str(len(member.roles) - 1) + ")", value=roleString)

        await self.bot.say(embed=e)


    @command(pass_context=True)
    async def avatar(self, ctx, *args):
        urMum = MemberConverter(ctx, args[0]).convert() if len(args) > 0 and args[0] else ctx.message.author
        e = Embed()
        e.set_author(name=get_nick(urMum), icon_url=get_avatar(urMum))
        e.set_image(url=get_avatar(urMum))
        await self.bot.say(embed=e)

    @command(pass_context=True)
    async def copy_channel(self, ctx, from_channel: str, to_channel: Channel, to_filter=None, limit=10000):
        if not is_mod(ctx): return

        from_channel = self.bot.get_channel(from_channel) or self.bot.get_channel(from_channel[2:-1])

        if from_channel is None:
            await self.bot.say("Invalid from_channel")
            return

        if to_filter == "image":
            def to_filter(msg: Message):
                if msg.attachments or msg.embeds:
                    return True
        else:
            # noinspection PyUnusedLocal
            def to_filter(msg: Message):
                return True

        msglist = []
        async for i in afilter(self.bot.logs_from(from_channel, before=dt.utcnow(), limit=limit), to_filter):
            msglist.append(i)

        for i in msglist[::-1]:
            i: Message = i

            embed = Embed()
            embed.set_author(name=get_nick(i.author), icon_url=get_avatar(i.author))

            if len(i.attachments) == 1:
                embed.set_image(url=i.attachments[0]["url"])
            elif len(i.attachments) > 1:
                for ind, j in enumerate(i.attachments):
                    aembed = deepcopy(embed)
                    aembed.description = f"Image {ind+1}/{len(i.attachments)}"
                    aembed.set_image(url=j["url"])

                    await self.bot.send_message(to_channel, embed=aembed)

            if i.embeds:
                with(suppress(IndexError, KeyError)):
                    aembed = deepcopy(embed)
                    aembed.set_image(url=i.embeds[0]['image']['url'])

                    await self.bot.send_message(to_channel, embed=aembed)

            embed.description = i.content
            if embed.description or embed.image.url:
                await self.bot.send_message(to_channel, embed=embed)

    @command(pass_context=True)
    async def list_role_ids(self, ctx):
        server = ctx.message.server
        embed = Embed()
        for i in server.roles:
            embed.add_field(name=str(i), value=str(i.id))
        await self.bot.say(embed=embed)

    @command(pass_context=True, aliases=["memberCount"])
    async def membercount(self, ctx):
        """Display server members"""
        embedded = Embed(title="Server Members",
                         colour=Colour.red())
        embedded.set_author(name=ctx.message.server.name, icon_url=ctx.message.server.icon_url)
        bots = list(filter(lambda x: x.bot, ctx.message.server.members))
        total = len(ctx.message.server.members)
        embedded.add_field(name="All", value=str(total))
        embedded.add_field(name="Bots", value=str(len(bots)))
        embedded.add_field(name="Humans", value=str(total - len(bots)))
        await self.bot.say(embed=embedded)

    @command(pass_context=True, aliases=["sep"])
    async def seperator(self, ctx):
        await self.bot.delete_message(ctx.message)
        await self.bot.say("``` ```")


# noinspection PyUnusedFunction
def setup(bot):
    bot.add_cog(Util(bot))
