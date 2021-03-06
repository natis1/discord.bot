from collections import Awaitable
from types import GeneratorType

from discord.ext.commands import Bot, command


# noinspection PyUnusedFunction
class Developer:
    def __init__(self, bot):
        self.bot: Bot = bot

    @command(pass_context=True, aliases=["die"])
    async def kill(self, ctx):
        """Developer only command. Don't bother."""
        # Kills the bot
        if (str(ctx.message.author) != "56#1363" or str(ctx.message.author) != "Avenging Angle#0272"): return
        print("Please kill the bot by sshing to radiance.host and attaching to the tmux session it is running it.")

    @command(pass_context=True, aliases=["ctx", "eval"])
    async def eval_ctx(self, ctx, *, msg: str):
        """Developer only command. Don't bother."""
        # Runs code
        # Used for debugging.
        if str(ctx.message.author) != "56#1363" and str(ctx.message.author) != "Avenging_Angle#0272": return
        try:
            a = eval(msg)

            if isinstance(a, (Awaitable, GeneratorType)):
                a = await a

            if a is not None:
                await self.bot.say(a)

        except Exception as e:
            await self.bot.say(e)

    @command(pass_context=True, aliases=["exec"])
    async def exec_ctx(self, ctx, *, msg: str):
        """Developer only command. Don't bother."""
        # Runs code
        # Used for debugging.
        if str(ctx.message.author) != "56#1363" and str(ctx.message.author) != "Avenging_Angle#0272": return
        try:
            await self.bot.say(await exec(msg))
        except Exception as e:
            await self.bot.say(e)

    @command(pass_context=True)
    async def reload_cog(self, ctx, cog: str):
        if (str(ctx.message.author) != "56#1363" or str(ctx.message.author) != "Avenging Angle#0272"): return
        print(f"Reloading cog {cog}")
        self.bot.unload_extension(f"cogs.{cog}")
        print(f"Unloading cog {cog}")
        self.bot.load_extension(f"cogs.{cog}")
        print(f"Loading cog {cog}")


# noinspection PyUnusedFunction
def setup(bot):
    bot.add_cog(Developer(bot))
