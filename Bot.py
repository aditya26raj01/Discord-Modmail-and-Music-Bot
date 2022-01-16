import discord
from discord.ext import commands
import youtube_dl
from youtubesearchpython import VideosSearch

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@client.event
async def on_ready():
    print("Bot is Online")


def audio_finder(song_name):
    videosSearch = VideosSearch(song_name , limit = 2)
    link=videosSearch.result()['result'][0]['link']
    
    ydl_opts = {'format': 'bestaudio/best',"quiet":True, "geo-bypass":True,"no-playlist":True,"flat-playlist":True}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=False)
    
    URL = info['formats'][0]['url']
    title = videosSearch.result()['result'][0]['title']
    duration = videosSearch.result()['result'][0]['duration']
    thumbnail = videosSearch.result()['result'][0]['thumbnails'][0]["url"]
    return URL, title, duration, thumbnail, link


def audio_player(voice):
    if len(songs) >0:    
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        voice.play(discord.FFmpegPCMAudio(songs[0]["url"], **FFMPEG_OPTIONS), after = lambda e: audio_player(voice))
        songs.pop(0)

songs = []

@client.command(aliases=["p"])
async def play(ctx,*,song_name : str):
    channel = ctx.author.voice.channel
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice:
        await channel.connect()
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    
    await ctx.send(f"🔎Searching for **{song_name}**")
    
    url , title, duration, thumbnail, link = audio_finder(song_name)

    song_detail={"url":url,"title":title,"duration":duration,"thumbnail":thumbnail,"send":ctx.channel,"author":ctx.author,"link":link}
    
    songs.append(song_detail)
    
    if not voice.is_playing():
        audio_player(voice)

        embed=discord.Embed(title = "Now Playing",description=f'''[{title}]({link})\n`Duration:` {duration}\n\n`Requested By:` {ctx.author}''', color = 0x32db3e)
        
        embed.set_thumbnail(url=thumbnail)
        await ctx.send(embed=embed)
    else:
        
        embed=discord.Embed(title = "Added To Queue",description=f'''[{title}]({link})\n`Duration:` {duration}\n\n`Requested By:` {ctx.author}\n\n`Position in Queue:` {len(songs)}''', color = 0x4287f5)
        
        embed.set_thumbnail(url=thumbnail)
        await ctx.send(embed=embed)

@client.command(aliases=["q"])
async def queue(ctx):
    y=""
    if len(songs)>0:
        for i in range(1,len(songs)+1):
            x =f'''`{i}.` [{songs[i-1]["title"]}]({songs[i-1]["link"]})\nDuration: {songs[i-1]["duration"]} **|** Requested By: {songs[i-1]["author"]}\n\n'''
            y=y+x
        embed=discord.Embed(
            title="Upcoming Songs",
            color = 0xFFFF00,
            description= f"{y}")
        await ctx.send(embed=embed)
    else:
        await ctx.send("Queue is Empty.")

@client.command(aliases=["s"])
async def skip(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        
        if len(songs)>0:
            voice.pause()
            audio_player(voice)
            await ctx.send("⏭ **Skipped**")
        else:
            await ctx.send("Queue is empty")

@client.command(aliases=["rm"])
async def remove(ctx, song : str):
    if len(songs)>=int(song):
        delted = songs.pop(int(song)-1)
        await ctx.send(f'''`{delted["title"]}` has been removed from Queue.''')
    else:
        await ctx.send("Song doesnt exist.")

@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        voice.stop()
        songs.clear()
        await ctx.send("**🛑 Stopped\nQueue has been Cleared!!**")

@client.command(aliases=["dc","leave"])
async def disconnect(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        voice.stop()
        songs.clear()
        await voice.disconnect()
        await ctx.send("**📬 Disconnected**")

@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        voice.pause()
        await ctx.send("**⏸️ Paused**")

@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_paused():
        voice.resume()
        await ctx.send("**▶️ Resumed**")

client.run("ODQ4NTQ5NDAxNTMzNjEyMDYy.YLOPNg.-ReUjCsZGnJV8he1trdDeT1AoAI")
