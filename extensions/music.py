import discord, youtube_dl, asyncio, sys
from utils.database import DatabaseTool
from discord.ext import commands
from functools import partial
from datetime import timedelta, datetime
from async_timeout import timeout

# based off: https://gist.github.com/EvieePy/ab667b74e9758433b3eb806c53a19f34

ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True, #
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ytdl = youtube_dl.YoutubeDL(ytdlopts)

class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)

        self.requester = requester

        self.title = data.get('title')
        self.webpage_url = data.get('webpage_url')
        self.duration = data.get('duration')
        self.thumbnail = data.get('thumbnail')

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=True)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        await ctx.send(f"> Added `{data['title']}` to the queue.")

        return cls(discord.FFmpegPCMAudio(ytdl.prepare_filename(data)), data=data, requester=ctx.author)

class MusicPlayer:

    def __init__(self, ctx):
        self.bot = ctx.bot

        self.guild = ctx.guild
        self.channel = ctx.channel
        self.voice_client = None

        self.cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.volume = 1.f

        self.current = None
        self.np = None

        self.play_timestamp = None

        ctx.bot.loop.create_task(self.player_loop())

    def destroy(self, guild):
        return self.bot.loop.create_task(self.cog.cleanup(guild))

    def create_now_playing_embed(self, for_player_loop=False):
        source = self.voice_client.source

        embed = discord.Embed(
            title="Now Playing",
            description=f"[{source.title}]({source.webpage_url})"
        )
        embed.color = 0x2F3136

        # todo: if not lazy stop using tiemdate.timedelta, cringe lol

        # .177000
        song_duration = int(source.duration)

        embed.add_field(name="Requester", value=f"`{source.requester}`")
        if for_player_loop:
            embed.add_field(name="Duration", value=f"`{timedelta(seconds=song_duration)}`")
        else:
            time_passed = int((datetime.now() - self.play_timestamp).total_seconds())
            embed.add_field(name="Duration", value=f"`{timedelta(seconds=time_passed)} / {timedelta(seconds=song_duration)}`")

        embed.set_thumbnail(url=source.thumbnail)

        return embed

    async def player_loop(self):
        await self.bot.wait_until_ready()
        self.voice_client = self.guild.voice_client

        while not self.bot.is_closed():
            self.next.clear()
            
            if self.current is None: # makes no sense but breaks if this check isn't here
                try:
                    async with timeout(240):
                        source = await self.queue.get()
                except asyncio.TimeoutError:
                    return self.destroy(self.guild)

            source.volume = self.volume
            self.current = source

            self.guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            self.play_timestamp = datetime.now()
            self.np = await self.channel.send(embed=self.create_now_playing_embed(True))

            await self.next.wait()

            source.cleanup()

            self.current = None
            self.np = None

    async def connect(self, channel):
        if self.voice_client:
            if self.voice_client.channel.id == channel.id:
                await self.channel.send("> I'm already connected to your channel.")
                return

        try:
            await channel.connect()
            await self.channel.send("> Connected.")
        except asyncio.TimeoutError:
            await self.channel.send("> Connection failed. Timed out.")            

    async def disconnect(self):
        self.destroy(self.guild)

    async def pause(self):
        if self.voice_client.is_paused():
            await self.channel.send("> The song is already paused.")
            return
        elif not self.voice_client.is_playing():
            await self.channel.send("> I'm not playing anything.")
            return

        elif not self.voice_client.is_connected():
            await self.channel.send("> I'm not connected to a Voice Channel.")
            return

        self.voice_client.pause()
        await self.channel.send("> Paused.")

    async def resume(self):
        if self.voice_client.is_playing():
            await self.channel.send("> I'm already playing a song.")
            return

        if not self.voice_client.is_connected():
            await self.channel.send("> I'm not connected to a Voice Channel.")
            return

        self.voice_client.resume()
        await self.channel.send("> Resumed.")

    async def stop_current_song(self):
        if self.voice_client.is_paused():
            self.voice_client.resume()

        if self.voice_client.is_playing():
            self.voice_client.stop()

    async def change_volume(self, new_volume: float):
        if not 0 < new_volume < 101:
            await self.channel.send("> Invalid value.")
            return

        new_volume = new_volume / 100

        if self.voice_client.is_playing():
            self.volume = new_volume
            self.voice_client.source.volume = new_volume
            await self.channel.send(f"> Volume set to **{new_volume * 100}%**")
        else:
            await self.channel.send("> Couldn't set Volume.")

class MusicCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        self.skip_votes = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    def get_player(self, ctx):
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    # todo:
    # - display the queue
    # - add a way to index items from the queue and move or remove them
    # - add a database-based dj list -> rework database
    # - add force skip for moderators and djs

    @commands.command(aliases=["join", "summon"])
    async def connect(self, ctx):
        """Connects to your Voice Channel."""
        await self.get_player(ctx).connect(ctx.author.voice.channel)

    @commands.command(aliases=["stop", "dc"])
    async def disconnect(self, ctx):
        """Disconnects from the Voice Channel."""
        await self.get_player(ctx).disconnect()  

    @commands.command(aliases=["p"], usage="song")
    async def play(self, ctx, *, search: str):
        """Queues up a song to play."""
        if not ctx.voice_client:
            await ctx.invoke(self.connect)

        source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
        await self.get_player(ctx).queue.put(source)

    @commands.command()
    async def pause(self, ctx):
        """Pauses the Song."""
        await self.get_player(ctx).pause()

    @commands.command()
    async def resume(self, ctx):
        """Resumes the Song."""
        await self.get_player(ctx).resume()

    @commands.command(aliases=["s"])
    async def skip(self, ctx):
        """Stars a vote to Skip the current Song."""
        try:
            self.skip_votes[ctx.guild.id] += 1
        except KeyError:
            self.skip_votes[ctx.guild.id] = 1
        
        member_count = 0
        for member in ctx.voice_client.channel.members:
            if member.bot == False:
                member_count += 1

        member_dj_status = DatabaseTool(ctx.guild).get_member_data(ctx.author)[2]

        if member_dj_status == 0:
            if member_count / self.skip_votes[ctx.guild.id] <= 2:
                await self.get_player(ctx).stop_current_song()
                await ctx.send("Skipping.")
            else:
                await ctx.send(f"**{self.skip_votes[ctx.guild.id]}/{member_count}** members have voted to skip.")
        else:
            await self.get_player(ctx).stop_current_song()
            await ctx.send("**[DJ]** Skipping.")

    @commands.command(aliases=["vol"], usage="volume")
    async def volume(self, ctx, new_volume: float):
        """Changes the Song volume."""
        await self.get_player(ctx).change_volume(new_volume)

    @commands.command(name="nowplaying", aliases=["np", "now playing", "current"])
    async def now_playing(self, ctx):
        """Displays the currently playing Song."""
        if self.get_player(ctx).np is None:
            await ctx.send("I'm not playing anything.")
        else:
            await ctx.send(embed=self.get_player(ctx).create_now_playing_embed())

    @commands.command()
    @commands.has_permissions(kick_members=True) # mod check
    async def dj(self, ctx, member: discord.Member):
        """Moderator command, changes the DJ status of a member."""
        member_dj_status = DatabaseTool(ctx.guild).get_member_data(member)[2]

        if member_dj_status == 0:
            DatabaseTool(ctx.guild).update_member_data(member, "dj_status", 1)
            await ctx.send(f"{member.mention} is now a DJ.")
        else:
            DatabaseTool(ctx.guild).update_member_data(member, "dj_status", 0)
            await ctx.send(f"{member.mention} is no longer a DJ.")

    async def cog_check(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            return await ctx.send("You are not able to use Music commands in DMs")

        return True

def setup(bot):
    bot.add_cog(MusicCommands(bot))
