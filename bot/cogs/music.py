import discord
from discord.ext import commands
import youtube_dl
from discord.ext import tasks
from discord import user
from discord import guild


q = []

class music(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.command()
    async def join(self,ctx):
        if ctx.author.voice is None:
            await ctx.send("You're not in a voice channel")
        vc = ctx.author.voice.channel
        if ctx.voice_client is None:
            await vc.connect()
        else:
            await ctx.voice_client.move_to(vc)

    @commands.command(aliases=['dc'])
    async def disconnect(self,ctx):
        await ctx.voice_client.disconnect()

    @commands.command()
    async def stop(self,ctx):
        ctx.voice_client.stop()
        await ctx.send("stopped playing")
        
    @commands.command()
    async def t(self,ctx):

        if ctx.author.voice is None:
            await ctx.send("You're not in a voice channel")
        vc = ctx.author.voice.channel

        if (ctx.voice_client.source is not None):
            await ctx.send("yes")
            await ctx.send("playing : {}".format(ctx.voice_client.source))
        else:
            await ctx.send("non")

    @commands.command(aliases=['p'])
    async def play(self,ctx,url):
        if ctx.author.voice is None:
            await ctx.send("You're not in a voice channel")
        vc = ctx.author.voice.channel

        
        if ctx.voice_client is None:
            await vc.connect()

        try:
            ctx.voice_client.stop()
        except:
            pass
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        YDL_OPTIONS = {'format':'bestaudio'}
        vc = ctx.voice_client

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            vc.play(source)

    @commands.command()
    async def pause(self,ctx):
        ctx.voice_client.pause()
        await ctx.send("Audio Paused")

    @commands.command()
    async def resume(self,ctx):
        ctx.voice_client.resume()
        await ctx.send("Audio Resumed")


def setup(client):
    client.add_cog(music(client))