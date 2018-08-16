import tempfile
from os.path import join
from random import choice, randint

from discord import HTTPException
from discord.ext.commands import Bot, BucketType, command, cooldown

from HollowText import create_image_file
from utils import is_emoji, is_int, is_mod, make_embed, precepts, text_embed


# noinspection PyUnusedFunction
class Memes:
    def __init__(self, bot):
        self.bot: Bot = bot

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

    async def image_maker(self, channel: xd, message: str):
        """Outputs text as stiched images of Hollow Knight letters, if it fails split it in two and try again"""
        path = join(tempfile.gettempdir(), "meme.png")
        create_image_file(message, path)
        try:
            await self.bot.send_file(channel, path)
        except HTTPException as e:
            await self.image_maker(channel, message[:len(message) // 2])
            await self.image_maker(channel, message[len(message) // 2:])

    @command(aliases=["htext", "htxt", "hollowtext", "hollowText", "hktext"], pass_context=True)
    @cooldown(1, 5, BucketType.user)
    async def hollow_text(self, ctx, *, message: str):
        """Outputs text as stiched images of Hollow Knight letters"""
        await self.image_maker(ctx.message.channel, message)


# noinspection PyUnusedFunction
def setup(bot):
    bot.add_cog(Memes(bot))
