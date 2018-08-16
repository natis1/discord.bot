from contextlib import suppress
from copy import deepcopy
from datetime import datetime as dt

from discord import Channel, Colour, Embed, Message
from discord.ext.commands import Bot, command

from utils import afilter, get_avatar, get_nick, is_mod


# noinspection PyUnusedFunction
class Util:
    def __init__(self, bot):
        self.bot: Bot = bot

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
