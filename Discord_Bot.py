import discord
from discord.ext import commands
import random
import keep_alive
import os
import ffmpeg
import youtube_dl
import nacl

client = commands.Bot(command_prefix='!')

client.remove_command("help")


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game("a"))


@client.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            embed = discord.Embed(
                title="Thank you for adding wedonnobot to your server!",
                description=
                "Im a music+text bot, use !help to see a list of commands!\nTo add me to another server: https://bit.ly/wedonno",
                colour=discord.Colour.red())
            embed.set_image(
                url=
                "https://media.discordapp.net/attachments/787385063284932630/820979172511449118/kaki.png?width=676&height=676"
            )
            await channel.send(embed=embed)

        break


@client.command()
async def ping(ctx):
    await ctx.send(
        f'Ping: {round(client.latency * 1000)}ms. My developers ping is twice as much, damn hot.'
    )


#AUDIOCOMMANDS


@client.command(aliases=['8ball', 'ball', '8b'])
async def _8ball(ctx, *, question):
    responses = [
        "It is certain.", "It is decidedly so.", "Without a doubt.",
        "Yes - definitely.", "You may rely on it.", "As I see it, yes.",
        "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
        "Reply hazy, try again.", "Ask again later.",
        "Better not tell you now.", "Cannot predict now.",
        "Concentrate and ask again.", "Don't count on it.", "My reply is no.",
        "My sources say no.", "Outlook not so good.", "Very doubtful."
    ]
    await ctx.send(f'You asked: {question}\nAnswer: {random.choice(responses)}'
                   )


@client.command(aliases=['delete', 'remove', 'rm'])
async def clear(ctx, amount=6):
    await ctx.channel.purge(limit=amount)


@client.command()
async def join(ctx):
    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name='General')
    await voiceChannel.connect()
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)


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
    'source_address':
    '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {'options': '-vn'}

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
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options),
                   data=data)


@client.command(aliases=['p', 'playsong'])
async def play(ctx, url: str):
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send(
            "Wait for the current playing music to end or use the 'stop' command"
        )
    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name='General')
    await voiceChannel.connect()
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format':
        'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                os.rename(file, "song.mp3")
            voice.play(discord.FFmpegPCMAudio("song.mp3"))
            embed = discord.Embed(colour=discord.Colour.orange())

    def find_string(txt, str1):
        if file.count("-") > 1:
          return txt.find(str1, txt.find(str1) + 1)
        return(file)

    x = find_string(file, "-")
    fixed_name = file[:x]
    embed.set_author(name="Playing: " + fixed_name)
    await ctx.send(embed=embed)


@client.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(
        color=discord.Colour.orange(),
        description=
        "My prefix here is ! so use it to send commands! Here is the list of the commands you can use on me"
    )
    embed.set_author(name="Help")
        )
    embed.add_field(name="!ping", value="Returns my ping.", inline=False)
    embed.add_field(name="!mandarin",
                    value="Shows the lyrics of the best song to ever exist.",
                    inline=False)
    embed.add_field(name="!play",
                    value="Plays a song from the url you entered.",
                    inline=False)
    embed.add_field(name="!pause",
                    value="Pauses the current track",
                    inline=False)
    embed.add_field(name="!leave",
                    value="Disconnects from the channel.",
                    inline=False)
    embed.add_field(name="!stop",
                    value="Stops the current track/queue",
                    inline=False)
    embed.add_field(name="!resume",
                    value="Resumes the paused track.",
                    inline=False)
    embed.add_field(name="!8ball",
                    value="Ask a question, and get an answer!",
                    inline=False)
    embed.add_field(name="!clear",
                    value="Deletes the last 5 messeges",
                    inline=False)
    embed.add_field(
        name="!help",
        value="If you arrived here, i guess you know what it does.",
        inline=False)

    await ctx.send(embed=embed)


keep_alive.keep_alive()
client.run(
    "ODIwNzMxODE5NDE0NTE5ODc4.G26jXc.XRJe5pdQFCaxGLgW5NdF16iSwAME4Nfh-mDnEs")
