from datetime import timedelta

from discord import Message, User
from discord.ext.commands import Bot, command

from utils import get_utc_date, is_mod


class Moderator:
    def __init__(self, bot):
        self.bot: Bot = bot

    @command(pass_context=True, aliases=["death", "purge"])
    async def clear(self, ctx, num: int, user: User = None):
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
            await self.bot.purge_from(ctx.message.channel,
                                      around=ctx.message,
                                      limit=101,
                                      before=ctx.message.timestamp + timedelta(seconds=5),
                                      check=check_user)
        except Exception as e:
            await self.bot.say(e)

    @command(pass_context=True, aliases=["deleteTime", "delTime"])
    async def del_time(self, ctx, after, before=None):
        """Deletes messages given a time at which to start and an optional time at which to end"""
        if not is_mod(ctx): return
        args = {}

        if before: args['before'] = get_utc_date(before)
        args['after'] = get_utc_date(after)

        try:
            print(args['after'])
            await self.bot.purge_from(ctx.message.channel, **args, limit=4000)
        except Exception as e:
            await self.bot.say(e)

    @command(pass_context=True, aliases=["deleteTimeUser", "delTimeUser"])
    async def del_time_user(self, ctx, after, user: User):
        """Deletes messages given a time at which to start and an optional time at which to end"""
        if not is_mod(ctx): return
        args = {}

        def check_user(msg: Message):
            return msg.author == user

        args['after'] = get_utc_date(after)

        try:
            await self.bot.purge_from(ctx.message.channel, **args, limit=4000, check=check_user)
        except Exception as e:
            await self.bot.say(e)

    @command(pass_context=True, aliases=["deleteTimeTZ", "delTimeTZ"])
    async def del_time_tz(self, ctx, tzi, after, before=None):
        """Deletes messages given a time zone, a time at which to start, and an optional time at which to end"""
        if not is_mod(ctx): return
        args = {}

        if before: args['before'] = get_utc_date(before, tzi)
        args['after'] = get_utc_date(after, tzi)

        try:
            await self.bot.purge_from(ctx.message.channel, **args, limit=4000)
        except Exception as e:
            await self.bot.say(e)

    @command(pass_context=True, aliases=["delete"])
    async def delete_this(self, ctx, msg_id: str, channel_id=None):
        """Delete a message by id"""
        if not is_mod(ctx): return
        channel = self.bot.get_channel(channel_id) if channel_id else ctx.message.channel
        await self.bot.delete_message(await self.bot.get_message(channel, msg_id))
        await self.bot.delete_message(ctx.message)


def setup(bot):
    bot.add_cog(Moderator(bot))
