from datetime import datetime, timedelta
from pytz import timezone
from discord.ext.commands import Bot, command
from utils import get_utc_date, is_mod
from dateparser import parse
from discord import Channel, Client, Colour, Embed, Message, Emoji, Reaction
from discord.utils import get
from copy import deepcopy

# noinspection PyUnusedFunction
class Time:
    def __init__(self, bot):
        self.bot: Bot = bot
        self.timers= {}
        return

    @command()
    async def now(self, tz="UTC"):
        fmt = "%H:%M:%S"
        try:
            now_tz = datetime.now(timezone(tz))
            stime = now_tz.strftime(fmt)
            if (int(stime[:2]) > 22) or (int(stime[:2]) < 6):
                await self.bot.say("Current time in " + tz + " is " + now_tz.strftime(fmt) + "\n\nPeople living here should really be sleeping!")
            else:
                await self.bot.say("Current time in " + tz + " is " + now_tz.strftime(fmt))
        except:
            await self.bot.say("Invalid timezone " + tz + " see https://en.wikipedia.org/wiki/List_of_tz_database_time_zones")
        return

    def strfdelta(self, tdelta, fmt):
        d = {"days": tdelta.days}
        d["hours"], rem = divmod(tdelta.seconds, 3600)
        d["minutes"], d["seconds"] = divmod(rem, 60)
        return fmt.format(**d)


    @command(pass_context=True)
    async def show_events(self, ctx):
        eventstr = ""
        itimers = deepcopy(self.timers)
        for key in sorted(itimers, key=itimers.get):
            if (datetime.now(timezone("UTC")) - timedelta(hours=1)) > itimers[key]:
                del self.timers[key]
            elif (datetime.now(timezone("UTC")) > itimers[key]):
                eventstr += "\n" + key + "\t|\t" + itimers[key].strftime("%m-%d %H:%M") + "\t|\t" + "NOW!"
            else:
                diff = itimers[key] - datetime.now(timezone("UTC"))
                eventstr += "\n" + key + "\t|\t" + itimers[key].strftime("%m-%d %H:%M") + "\t|\t" + self.strfdelta(diff, "{days} days {hours}:{minutes}:{seconds}")
        embedded = Embed(title="Event | Time | ETA",
                         colour=Colour.green(),
                         description=eventstr)
        embedded.set_author(name=ctx.message.server.name, icon_url=ctx.message.server.icon_url)

        await self.bot.say(embed=embedded)
        return

    @command(pass_context=True)
    async def create_event(self, ctx, event_name, date):
        if ctx.message.server.id != '459911387490025493':
            return
        if not is_mod(ctx):
            return
        dt = parse(date)
        if event_name in self.timers:
            if not is_mod(ctx):
                return
        else:
            self.timers[event_name] = dt.astimezone(timezone("UTC"))
            await self.bot.say("Added event: " + event_name + " at time: " + dt.strftime("%Y-%m-%d %H:%M:%S %Z%z"))
            return

    @command(pass_context=True)
    async def delete_event(self, ctx, event_name):
        if ctx.message.server.id != '459911387490025493':
            return
        if not is_mod(ctx):
            return
        if event_name in self.timers:
            del self.timers[event_name]
            await self.bot.say("Deleted event: " + event_name)
            return



# noinspection PyUnusedFunction
def setup(bot):
    bot.add_cog(Time(bot))
