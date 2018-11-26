import tempfile
from contextlib import suppress
from os.path import join
from random import choice, randint

from discord import HTTPException, Message, Embed, Channel, Client, Colour, Embed, Message, Emoji, Reaction
from discord.client import WaitedReaction
from discord.ext.commands import Bot, BucketType, command, cooldown

from HollowText import create_image_file
from utils import is_emoji, is_int, is_mod, make_embed, precepts, text_embed



# noinspection PyUnusedFunction
class Memes:
    def __init__(self, bot):
        self.bot: Bot = bot

    @command()
    @cooldown(1, 5, BucketType.user)
    async def about(self):
        await self.bot.say("56 but bot v1.0 by 56.\nBrought to you by nugget in collaboration with the mothposters!")

    @command()
    @cooldown(1, 5, BucketType.user)
    async def precept(self, *args):
        """Gives zote's precepts"""
        if args:
            if is_int(args[0]):
                await self.bot.say(embed=text_embed(str(int(args[0])) + ": " + precepts[int(args[0]) - 1]))
            else:
                rand = randint(0, len(precepts))
                await self.bot.say(embed=text_embed(str(rand) + ": " + precepts[rand - 1]))
        else:
            rand = randint(1, len(precepts))
            await self.bot.say(embed=text_embed(str(rand) + ": " + precepts[rand - 1]))

    @command()
    @cooldown(1, 5, BucketType.user)
    async def neglect(self):
        """Shows an image of neglect"""
        from data import zote
        await self.bot.say(embed=zote)

    @command(aliases=["XD", "xD", "Xd"])
    @cooldown(1, 5, BucketType.user)
    async def xd(self, f: str, b: str):
        """XD out of emoji."""
        if is_emoji(f) and is_emoji(b):
            await self.bot.say_embed(
                f"{f}{b*2}{b}{f}{b}{f*2}{f}{b}\n{b}{f}{b}{f}{b*2}{f}{b*2}{f}\n{b*2}{f}{b*2}"
                f"{b}{f}{b*2}{f}\n{b}{f}{b}{f}{b*2}{f}{b*2}{f}\n{f}{b*2}{b}{f}{b}{f*2}{f}{b}")
        else:
            await self.bot.say_embed("Invalid emoji")

    @command(pass_context=True)
    async def ban(self, ctx):
        """Ban image. Mod-only."""
        if not is_mod(ctx): return
        from data import ban_hammer
        await self.bot.say(embed=ban_hammer)

    @command()
    @cooldown(1, 5, BucketType.user)
    async def udungo(self, u_dungo=""):
        """u dungo"""
        from data import dungo_orig, dungo
        if u_dungo.lower() == "orig" or u_dungo.lower() == "original":
            await self.bot.say(embed=dungo_orig)
        else:
            await self.bot.say(embed=dungo)

    @command(aliases=["KDT", "Kdt"])
    @cooldown(1, 5, BucketType.user)
    async def kdt(self):
        """KDT"""
        from data import KDT
        await self.bot.say(embed=choice(KDT))

    @command(aliases=["Finchmeister", "finch", "Finch", "sln"])
    async def finchmeister(self):
        """Disappointment."""
        await self.bot.say(embed=make_embed("Disappointment",
                                            "https://cdn.discordapp.com/attachments/421554516023050261"
                                            "/450123677359669248 "
                                            "/unknown.png"))

    async def image_maker(self, channel: xd, message: str, it = 0):
        """Outputs text as stiched images of Hollow Knight letters, if it fails split it in two and try again"""
        path = join(tempfile.gettempdir(), "meme.png")
        try:
            create_image_file(message, path)
            await self.bot.send_file(channel, path)
        except (SystemError, HTTPException, MemoryError) as e:
            try:
                if (it > 5): return
                await self.image_maker(channel, message[:len(message) // 2], it = it + 1)
                await self.image_maker(channel, message[len(message) // 2:], it = it + 1)
            except RecursionError:
                return

    @command(aliases=["htext", "htxt", "hollowtext", "hollowText", "hktext"], pass_context=True)
    @cooldown(1, 5, BucketType.user)
    async def hollow_text(self, ctx, *, message: str):
        """Outputs text as stiched images of Hollow Knight letters"""
        await self.image_maker(ctx.message.channel, message)

    @command()
    async def delet_meme(self, msg):
        x = "❌"
        chk = "✅"

        delet_channel = self.bot.get_channel("516676649627156481")
        channel = self.bot.get_channel("516675581622878209")
        try:
            k: Message = await self.bot.get_message(channel, msg)
        except Exception as ex:
            await self.bot.say("Unable to delete <#516675581622878209> meme.")
            return

        e = Embed(title="Delete?")

        if k.attachments:
            e.set_image(url=k.attachments[0]["url"])
        if k.embeds:
            with (suppress(IndexError, KeyError)):
                e.set_image(url=k.embeds[0]["image"]["url"])

        msg = await self.bot.send_message(delet_channel, embed=e)

        await self.bot.add_reaction(msg, chk)
        await self.bot.add_reaction(msg, x)

        while True:
            r: WaitedReaction = await self.bot.wait_for_reaction([x, chk])

            if r is None:
                continue

            if r.reaction.emoji != chk and r.reaction.emoji != x:
                continue

            if r.reaction.count >= 4 or (any([role.permissions.manage_messages for role in r.user.roles]) and r.reaction.count >= 2):
                if r.reaction.emoji == chk:
                    await self.bot.delete_message(k)
                await self.bot.delete_message(msg)
                return


# noinspection PyUnusedFunction
def setup(bot):
    bot.add_cog(Memes(bot))
