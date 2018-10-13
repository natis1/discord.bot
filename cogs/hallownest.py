from discord import Server
from discord.ext.commands import Bot
from discord.utils import get


# noinspection PyUnusedFunction
class Hallownest:
    def __init__(self, bot):
        self.hallownest: Server = None
        self.bot: Bot = bot

    async def on_ready(self):
        self.hallownest = self.bot.get_server("459911387490025493")

    async def on_member_join(self, member):
        """Wanderer role"""
        if member.server != self.hallownest:
            return

        await self.bot.add_roles(member, get(member.server.roles, name="Wanderers"))


# noinspection PyUnusedFunction
def setup(bot):
    bot.add_cog(Hallownest(bot))
