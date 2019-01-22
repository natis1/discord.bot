from itertools import chain

import discord
from discord import Embed, Member, Color, Colour
from discord.ext.commands import Bot, command
from discord.utils import get

from utils import first, first_or_default, is_mod, opt_str


# noinspection PyUnusedFunction
class Roles:
    def __init__(self, bot):
        self.bot: Bot = bot

    # (A,l, i, a, s, e, s): "Role"
    roles = \
        {
            ("moths", "radiance", "moth", "mothkin", "modder", "ascended"): "Moths",
            ("grimm", "grimmkin", "artist", "gamer"):                       "Grimmkin",
            ("pale king", "palace resident", "palace residents"):           "Palace Residents",
            ("hiveling", "bee", "bees", "memer"):                           "Bees",
            ("void", "vessel", "friend"):                                   "Void",
            ("moss", "mosskin", "unn", "plant"):                            "Moss",
            ("mantis", "mantis youth"):                                     "Mantis",
        }

    ranks = \
        {
            ("venting", "angry", "serious"):         "Venting",
            ("dnd", "dnd player", "nerd", "rper"):   "DnD Player",
            ("game night", "gamer"):                 "Game Night",
        }

    realroles = ["Moths", "Grimmkin", "Void", "Palace Residents", "Bees", "Moss", "Mantis"]

    @command(pass_context=True)
    async def factioninfo(self, ctx):
        s = ctx.message.server
        u = ctx.message.author

        e = Embed()
        e.title = "Faction Members:\n"

        for r in self.realroles:
            role = get(s.roles, name=r)
            e.add_field(name=r, value=len([x for x in s.members if role in x.roles]))

        await self.bot.say(embed=e)

    @command(pass_context=True)
    async def rank(self, ctx, *, rank: str = "show_ranks"):
        server = ctx.message.server
        user = ctx.message.author
        rank = rank.lower()
        show = rank == "show_ranks"
        ranktoadd = show
        if rank in chain(*self.ranks):
            ranktoadd = self.ranks[first(self.ranks, lambda x: rank in x)]

        if (not ranktoadd == show) and not get(user.roles, name=ranktoadd):
            await self.bot.add_rank(server, ranktoadd, user)
            await self.bot.say("Adding " + ranktoadd + "!")
            return

        if (not ranktoadd == show) and get(user.roles, name=ranktoadd):
            await self.bot.remove_rank(server, ranktoadd, user)
            await self.bot.say("Removing " + ranktoadd + "!")
            return

        valid_roles = "Valid ranks are: \n" + "\n".join(self.ranks.values())
        await self.bot.say(opt_str(not show, "Invalid Rank\n") + valid_roles)

    @command(pass_context=True)
    async def role(self, ctx, *, role: str = "show_roles"):
        server = ctx.message.server
        user = ctx.message.author
        role = role.lower()
        show = role == "show_roles"

        if not get(user.roles, name="Wanderers") and not show and role in chain(*self.roles):
            await self.bot.say("You already have a role, ask a staff member to switch!")
            return

        if role in chain(*self.roles):
            await self.bot.add_role(server, self.roles[first(self.roles, lambda x: role in x)], user)
            embedded = Embed(
                title=f"{str(user.name)}\#{str(user.discriminator)}",
                description=f"**<@{str(user.id)}> joined the** `" + self.roles[first(self.roles, lambda x: role in x)] + "`",
                colour=Colour.red(),
            )
            await self.bot.send_message(
                self.bot.get_channel(self.bot.audit_log[server.id]), embed=embedded
            )
            return

        valid_roles = "Valid roles are: \n" + "\n".join(self.roles.values())
        await self.bot.say(opt_str(not show, "Invalid Role\n") + valid_roles)

    @command(pass_context=True)
    async def in_role(self, ctx, *, role):
        role = role.title() if role == role.lower() else role

        s = ctx.message.server
        role = get(s.roles, name=role)

        if role is None:
            await self.bot.say("Role not found in server")
            return

        e = Embed()
        e.title = role.name
        e.description = repr([x.mention for x in s.members if role in x.roles])

        await self.bot.say(embed=e)

    @command(pass_context=True)
    async def roleping(self, ctx, *, role):
        if not is_mod(ctx): return

        role = role.title() if role == role.lower() else role
        s = ctx.message.server

        role = get(s.roles, name=role)

        if role is None:
            await self.bot.say("Role not found in server")
            return

        await self.bot.say(repr([x.mention for x in s.members if role in x.roles]))


#    @command(pass_context=True)
#    async def player(self, ctx, mem: Member):
#        if not is_mod(ctx): return
#        await self.bot.add_role(ctx.message.server, "DnD Player", mem)


# noinspection PyUnusedFunction
def setup(bot):
    bot.add_cog(Roles(bot))
