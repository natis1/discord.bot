import asyncio
import re
from typing import Dict, List

from discord import Channel, Embed
from discord.ext.commands import Bot, command
from discord.voice_client import StreamPlayer


# noinspection PyUnusedFunction
class Voice:
    def __init__(self, bot):
        self.bot: Bot = bot
        self.players: Dict[Channel, StreamPlayer] = {}
        self.queue: List[str] = []

    url_regex = re.compile("^(https?):/(/www.|/)youtu(be.com|\.be)/[^\s/$.?#].[^\s]*$")

    @command(pass_context=True)
    async def play(self, ctx, *, url_query: str = ""):
        """Plays a song if given a url, otherwise resumes a paused song if there is one"""

        vc = ctx.message.author.voice.voice_channel

        if self.players.get(vc) and url_query == "":
            self.players.get(vc).resume()
            return

        if not re.match(self.url_regex, url_query):
            url_query = 'ytsearch:' + url_query

        if vc is None:
            await self.bot.say("You're not in a voice channel")
            return

        player = self.players.get(vc)
        if player is not None and player.is_playing() and not player.is_done():
            await self.bot.say("Adding to queue.")
            self.queue.append(url_query)
            return

        voice = self.get_voice(ctx) or await self.bot.join_voice_channel(vc)

        await self.play_video(ctx, voice, url_query)

    async def play_video(self, ctx, voice, url):
        self.players[voice.channel] = await voice.create_ytdl_player(url, after=lambda: self.play_next(ctx))
        player = self.players[voice.channel]

        if player.duration >= 36000:
            await self.bot.send_message(ctx.message.channel, f"Video {player.title} has been disabled due to abuse")
            player.stop()
            await self.play_queue(ctx)
        else:
            player.start()

    async def play_queue(self, ctx):
        voice = self.get_voice(ctx)

        if len(self.queue) == 0:
            await voice.disconnect()
            return

        # So we don't keep trying to play a video that's too long
        query = self.queue[0]
        self.queue.remove(self.queue[0])

        await self.play_video(ctx, voice, query)

    def play_next(self, ctx):
        asyncio.run_coroutine_threadsafe(self.play_queue(ctx), self.bot.loop).result()

    @staticmethod
    def get_voice(ctx):
        return ctx.message.server.voice_client

    def get_player(self, ctx):
        return self.players.get(ctx.message.author.voice.voice_channel)

    @command(pass_context=True, aliases=["queue", "q"])
    async def queue_check(self, ctx):
        embed = Embed()
        embed.title = "Queue"
        embed.description = f"```\nNow Playing: {self.get_player(ctx) and self.get_player(ctx).title}\n"
        for ind, i in enumerate(self.queue):
            embed.description += f"{str(ind + 1)}. {i}\n"
        embed.description += "\n```"
        await self.bot.say(embed=embed)

    @command(pass_context=True, aliases=["nowplaying"])
    async def now_playing(self, ctx):
        embed = Embed()
        embed.title = "Now Playing"
        embed.description = self.get_player(ctx) and self.get_player(ctx).title
        await self.bot.say(embed=embed)

    @command(pass_context=True)
    async def skip(self, ctx):
        """Skip a song"""
        self.get_player(ctx) and self.get_player(ctx).stop()

    @command(pass_context=True)
    async def pause(self, ctx):
        """Pause the music"""
        self.get_player(ctx) and self.get_player(ctx).pause()

    @command(pass_context=True)
    async def volume(self, ctx, vol: int):
        """Set player volume"""
        if self.get_player(ctx) is None: return
        self.get_player(ctx).volume = vol

    @command(pass_context=True, aliases=["disconnect, leave"])
    async def stop(self, ctx):
        voice = self.get_voice(ctx)
        voice and await voice.disconnect()


# noinspection PyUnusedFunction
def setup(bot):
    bot.add_cog(Voice(bot))
