import discord
from discord.ext import commands
import os
from src.tts import TTS

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

token = os.environ["DISCORD_TOKEN"]

if __name__ == "__main__":

    TTS = TTS()

    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user}')
        if TTS.model is None:
            TTS.load()
        print(f'Model Loaded')


    @bot.hybrid_command(name="tts")
    async def tts(ctx):

        if ctx.author.voice:
            if ctx.voice_client:
                await ctx.voice_client.disconnect()
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.send(f"Joined {ctx.author.voice.channel}")
        else:
            await ctx.send("You are not in a voice channel")

        @bot.event
        async def on_message(message):
            if message.author == bot.user:
                return
            else:
                TTS.gen(message.content)
                voice_client = ctx.voice_client
                source = discord.FFmpegPCMAudio("sample.wav")
                play(voice_client, source)

    def play(voice_client, source):
        if source is not None:
            voice_client.play(source)


    @bot.hybrid_command()
    async def leave(ctx):
        if ctx.author.voice:
            if ctx.voice_client.is_connected():
                await ctx.voice_client.disconnect()
                await ctx.send(f"Disconnected from {ctx.author.voice.channel}")
        else:
            await ctx.send("I'm not in a voice channel")

    class Speaker(commands.Cog):
        def __init__(self, bot):
            self.bot = bot

        @commands.hybrid_group()
        async def speaker(self, ctx, name: str,  attachment: discord.Attachment):
            if name is None:
                await ctx.send("Please provide a name for the speaker")
            else:
                if "audio" in attachment.content_type:
                    if f"{name}.pt" == TTS.speaker[0]:
                        await ctx.send("Speaker already loaded")
                        return
                    elif f"{name}.pt" in TTS.speakers:
                        TTS.load_speaker(name)
                    else:
                        audio_bytes = await attachment.read()
                        TTS.save_speaker(name, audio_bytes)
                        TTS.load_speaker(name)
                    await ctx.send("Speaker loaded")
                else:
                    await ctx.send("Please upload a voice message")

        @speaker.command()
        async def list(self, ctx):
            await ctx.send(f"Speakers: {TTS.speakers}")

        @speaker.command()
        async def save(self, ctx, name: str, attachment: discord.Attachment):
            if name is None:
                await ctx.send("Please provide a name for the speaker")
            else:
                if "audio" in attachment.content_type:
                    audio_bytes = await attachment.read()
                    TTS.save_speaker(name, audio_bytes)
                    await ctx.send(f"Speaker {name} saved")
                else:
                    await ctx.send("Please upload a voice message")

        @speaker.command()
        async def load(self, ctx, name: str):
            if name is None:
                await ctx.send("Please provide a name for the speaker")
            else:
                if f"{name}.pt" == TTS.speaker[0]:
                    await ctx.send("Speaker already loaded")
                    return
                elif f"{name}.pt" in TTS.speakers:
                    TTS.load_speaker(name)
                    await ctx.send(f"Speaker {name} loaded")
                else:
                    await ctx.send("Speaker not found")


    async def setup(bot):
        await bot.add_cog(Speaker(bot))

    try:
        bot.run(token)
    except:
        pass