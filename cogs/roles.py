from itertools import chain

from discord import Embed, Member
from discord.ext.commands import Bot, command
from discord.utils import get

from utils import first, first_or_default, is_mod, opt_str


class Roles:
    def __init__(self, bot):
        self.bot: Bot = bot

    # (A,l, i, a, s, e, s): "Role"
    roles = \
        {
            ("moths", "radiance", "moth", "mothkin"):             "Mothkin",
            ("lifeblood", "wheelchair", "♿"):                     "Lifeblood",
            ("grimm", "grimmkin"):                                "Grimmkin",
            ("pale king", "palace resident", "palace residents"): "Palace Residents",
            ("hiveling", "bee"):                                  "Hiveling",
            ("void", "Void"):                                     "Void",
            ("moss", "mosskin", "unn"):                           "Mosskin",
            ("mantis", "mantis youth"):                           "Mantis",
            ("archiver", "archivers", "monomon"):                 "Archivers",
            ("weavers", "faeren", "spidesr"):                     "Weavers"

        }

    @command(pass_context=True)
    async def role(self, ctx, *, role: str = "show_roles"):
        server = ctx.message.server
        user = ctx.message.author
        role = role.lower()
        show = role == "show_roles"

        if not get(user.roles, name="Wanderers") and not show:
            await self.bot.say("You already have a role, u dungo")
            return

        if role in chain(*self.roles):
            await self.bot.add_role(server, self.roles[first(self.roles, lambda x: role in x)], user)
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

    @command(pass_context=True)
    async def player(self, ctx, mem: Member):
        if not is_mod(ctx): return
        await self.bot.add_role(ctx.message.server, "DnD Player", mem)


def setup(bot):
    bot.add_cog(Roles(bot))
