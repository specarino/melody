#!/usr/bin/env python3

import discord, youtube_dl, asyncio, os
from discord.ext import commands

defaultVolume = 10

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

ffmpeg_options = {
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['relax', 'study'])
    async def lofi(self, ctx):
        """Streams beats to relax/study to"""

        studyURL = os.getenv('LOFI')
        async with ctx.typing():
            player = await YTDLSource.from_url(studyURL, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        ctx.voice_client.source.volume = defaultVolume/1000
        await ctx.send(f'Now playing: {player.title}')

    @commands.command(aliases=['p', 'stream', 'yt'])
    async def play(self, ctx, *, url):
        """Streams from YouTube URL"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        ctx.voice_client.source.volume = defaultVolume/1000
        await ctx.send(f'Now playing: {player.title}')

    @commands.command(aliases=['vol', 'v'])
    async def volume(self, ctx, volume: int):
        """Changes the volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")
        if volume > 10:
            return await ctx.send("Maximum volume is 10.")
        if volume < 0:
            return await ctx.send("Minimum volume is 0.")

        ctx.voice_client.source.volume = volume/1000
        print(ctx.voice_client.source.volume)
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command(aliases=['disconnect', 'dc'])
    async def stop(self, ctx):
        """Stops and disconnects the bot"""

        await ctx.voice_client.disconnect()

    @lofi.before_invoke
    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(os.getenv('PREFIX')),
    description='melody - a 24/7 lofi radio bot powered by Discord.py',
    intents=intents,
)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

async def main():
    async with bot:
        await bot.add_cog(Music(bot))
        await bot.start(os.getenv('TOKEN'))

asyncio.run(main())