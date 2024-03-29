import discord
from discord.ext import commands
import asyncio
import datetime 
import youtube_dl
from youtubesearchpython import VideosSearch
client = commands.Bot(command_prefix="+", intents=discord.Intents.all())
 

@client.event
async def on_ready():
    print("Bot is Online")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Music is ❤!"))
sent_users = {}
empty_array = []
@client.event
async def on_message(message):
    guild=client.get_guild(779532880959242250)

    if message.author == client.user:
        return
    if message.guild and message.channel.id in sent_users.values() and not message.content.startswith("+"):
        for id, channel_id in sent_users.items():
            if message.channel.id == channel_id:
                user_id = id
        user=await client.fetch_user(user_id)
        embed=discord.Embed(
            description=f"{message.content}",
            color=0x42f542)
        embed.set_author(name=message.author,icon_url=message.author.avatar_url)
        embed.set_footer(text="Moderation Team")
        embed.timestamp=datetime.datetime.utcnow()
        if message.attachments != empty_array:
            files = message.attachments
            for file in files:
                embed.set_image(url=file.url)
        await user.send(embed=embed)
    if str(message.channel.type)=="private" and message.author.id in sent_users:
        embed=discord.Embed(
            description=f"{message.content}",
            color=0x42f542)
        embed.set_author(name=message.author,icon_url=message.author.avatar_url)
        embed.set_footer(text="Client")
        embed.timestamp=datetime.datetime.utcnow()
        if message.attachments != empty_array:
            files = message.attachments
            for file in files:
                embed.set_image(url=file.url)
        channel=client.get_channel(sent_users[message.author.id])
        await channel.send(embed=embed)
    if str(message.channel.type)=="private" and message.author.id not in sent_users:
        embed=discord.Embed(
            title="Confirm Thread Creation",
            description='''This system is meant for directly contacting the server Moderators. Confirming a thread without a valid reason will not be tolerated at all.
React to confirm a thread.''',
            color=0x03bafc)
        msg=await message.channel.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        def check(reaction, user):
            return user == message.author and str(reaction.emoji) in ["✅","❌"]

        try:
            reaction, user = await client.wait_for('reaction_add', timeout=10.0, check=check)
            await msg.remove_reaction("❌",client.user)
            await msg.remove_reaction("✅",client.user)
            if str(reaction.emoji)=="✅":

                embed=discord.Embed(
                    title="Ticket Opened",
                    color=0x42f542
                )
                embed.add_field(name="Created By :",value=message.author,inline=False)
                channel = discord.utils.get(guild.channels, name="modmail-logs")
                await channel.send(embed=embed)
                category = discord.utils.get(guild.categories, name="modmail")
                channel_name=(((str(message.author)).replace(" ","-")).replace("#","-")).lower()
                modmail_channel=await guild.create_text_channel(channel_name, category=category)
                await modmail_channel.set_permissions(guild.default_role, read_messages=False)
                embed=discord.Embed(
                    title="New ticket",
                    description="Type messages in this channel to reply. Messages starting with ``+`` will be ignored and and can be used for staff discussions. To close the thread use ``+close`` and ``+delete`` to delete the client channel.",
                    color=0xfcba03)
                member = guild.get_member(message.author.id)
                mention = []
                for role in member.roles:
                    if role.name != "@everyone":
                        mention.append(role.mention)

                b = ", ".join(mention)
                embed.add_field(name="Nickname:",value=member.nick,inline=False)
                embed.add_field(name="Roles:",value=b,inline=False)
                embed.add_field(name="User ID:",value=message.author.id,inline=False)
                embed.set_thumbnail(url=member.avatar_url)
                embed.set_footer(text=message.author)
                embed.timestamp=datetime.datetime.utcnow()
                await modmail_channel.send(embed=embed)
                embed=discord.Embed(
                    description=f"{message.content}",
                    color=0x42f542)
                embed.set_author(name=message.author,icon_url=message.author.avatar_url)
                embed.set_footer(text="Client")
                embed.timestamp=datetime.datetime.utcnow()
                if message.attachments != empty_array:
                    files = message.attachments
                    for file in files:
                        embed.set_image(url=file.url)
                await modmail_channel.send(embed=embed)
                sent_users[message.author.id]=modmail_channel.id

                embed=discord.Embed(
                    title="Thread Created",
                    description="Thank you for your report! The moderation team will get back to you as soon as possible.",
                    color=0x42f542)
                embed.set_footer(text="Your message has been sent")
                embed.timestamp=datetime.datetime.utcnow()
                await message.channel.send(embed=embed)
            if str(reaction.emoji)=="❌":
                embed=discord.Embed(
                    title="Cancelled",
                    color=0xff3c00)
                embed.set_footer(text="Replying will create a New Thread")
                embed.timestamp=datetime.datetime.utcnow()
                await msg.delete()
                await message.channel.send(embed=embed)

        except asyncio.TimeoutError:
            await msg.delete()
            await message.channel.send("Timeout Error... Try Again!")

    await client.process_commands(message)
@client.command()
async def close(ctx,*,reason="No Reason Provided!",has_role="Admin"):
    if str(ctx.channel.category) != "modmail":
        return
    for id, channel_id in sent_users.items():
        if ctx.channel.id == channel_id:
            user_id = id
    guild=client.get_guild(779532880959242250)
    sent_users.pop(user_id)
    user=await client.fetch_user(user_id)
    embed=discord.Embed(
        title="Ticket Closed",
        color=0xff3c00)

    embed.add_field(name="Created By :",value=user,inline=False)
    embed.add_field(name="Closed By :",value=ctx.author,inline=False)
    channel = discord.utils.get(guild.channels, name="modmail-logs")
    await channel.send(embed=embed)

    embed=discord.Embed(
        title="Thread Closed",
        description=f"{reason}",
        colour=0xff3c00)
    embed.set_footer(text="Replying will create a New Thread")
    embed.timestamp=datetime.datetime.utcnow()

    user=await client.fetch_user(user_id)
    await user.send(embed=embed)
    await ctx.send(f"Mail with <@{user_id}> is closed now.")
@client.command()
async def delete(ctx,has_role="Admin"):
    if str(ctx.channel.category) != "modmail":
        return
    if str(ctx.channel) != "modmail-logs":
        await ctx.channel.delete()
@client.command()
async def setup(ctx,has_role="Admin"):
    guild=client.get_guild(779532880959242250)
    category = discord.utils.get(guild.categories, name = "modmail")
    if category:
        await ctx.send("Setup Already Complete")
        return

    cat = await guild.create_category("modmail")
    await cat.set_permissions(guild.default_role, read_messages=False)
    category = discord.utils.get(guild.categories, name="modmail")
    await guild.create_text_channel("modmail-logs", category=category)
    await ctx.send("Setup Complete")
@client.command()
async def cleardm(ctx,id,has_role="Admin"):
    msg = await ctx.channel.send("Deletion Started...")
    messages_to_remove = 1000
    async for message in client.get_user(int(id)).history(limit=messages_to_remove):
        if message.author.id == client.user.id:
            await message.delete()
        await asyncio.sleep(0.5)
    await msg.delete()
    await ctx.channel.send("Done")
# ---------------------------------------------------------------------------------


def audio_finder(song_name):
    videosSearch = VideosSearch(song_name, limit=2)
    link = videosSearch.result()['result'][0]['link']

    ydl_opts = {'format': 'bestaudio/best', "quiet": True,
                "geo-bypass": True, "no-playlist": True, "flat-playlist": True}

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=False)

    URL = info['formats'][0]['url']
    title = videosSearch.result()['result'][0]['title']
    duration = videosSearch.result()['result'][0]['duration']
    thumbnail = videosSearch.result()['result'][0]['thumbnails'][0]["url"]
    return URL, title, duration, thumbnail, link


songs = []


def audio_player(voice):
    if len(songs) > 0:
        #FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        FFMPEG_OPTIONS = {'options': '-vn', "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"}
        #FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        voice.play(discord.FFmpegPCMAudio(
            songs[0]["url"], **FFMPEG_OPTIONS), after=lambda e: audio_player(voice))
        songs.pop(0)


@client.command(aliases=["p"])
async def play(ctx, *, song_name: str):
    if str(ctx.channel) != "commands":
        await ctx.send("All Music Commands only in Commands channel only.")
        return
    if ctx.author.voice and str(ctx.author.voice.channel) == "music":
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if not voice:
            voiceChannel = discord.utils.get(
                ctx.guild.voice_channels, name='music')
            await voiceChannel.connect()
            voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
            await ctx.send(f"🔎Searching for **{song_name}**")
        try:
            url, title, duration, thumbnail, link = audio_finder(song_name)
            song_detail = {"url": url, "title": title, "duration": duration,"thumbnail": thumbnail, "send": ctx.channel, "author": ctx.author, "link": link}
            songs.append(song_detail)
            if not voice.is_playing():
                audio_player(voice)
                embed = discord.Embed(
                    title="Now Playing",
                    description=f'''[{title}]({link})\n`Duration:` {duration}\n\n`Requested By:` {ctx.author}''',
                    color=0x32db3e
                )
                embed.set_thumbnail(url=thumbnail)
                await ctx.send(embed=embed)
            else:

                embed = discord.Embed(
                    title="Added To Queue",
                    description=f'''[{title}]({link})\n
`Duration:` {duration}\n\n`Requested By:` {ctx.author}\n\n`Position in Queue:` {len(songs)}''',
                    color=0x4287f5
                )
                embed.set_thumbnail(url=thumbnail)
                await ctx.send(embed=embed)
        except:
            await ctx.send("An error occured! Try again!")

    else:
        await ctx.send("Please connect to **music** channel to play music, then try again.")


@client.command(aliases=["rm"])
async def remove(ctx, song: str):
    if str(ctx.channel) != "commands":
        await ctx.send("All Music Commands only in Commands channel only.")
        return
    if ctx.author.voice and str(ctx.author.voice.channel) == "music":
        if len(songs) >= int(song):
            delted = songs.pop(int(song)-1)
            await ctx.send(f'''`{delted["title"]}` has been removed from Queue.''')
        else:
            await ctx.send("Song doesnt exist.")
    else:
        await ctx.send("Please connect to **music** channel to play music, then try again.")


@client.command(aliases=["q"])
async def queue(ctx):
    if str(ctx.channel) != "commands":
        await ctx.send("All Music Commands only in Commands channel only.")
        return
    y = ""
    if len(songs) > 0:
        for i in range(1, len(songs)+1):
            x = f'''`{i}.` [{songs[i-1]["title"]}]({songs[i-1]["link"]})\nDuration: {songs[i-1]["duration"]} **|** Requested By: {songs[i-1]["author"]}\n\n'''
            y = y+x
        embed = discord.Embed(
            title="Upcoming Songs",
            color=0xFFFF00,
            description=f"{y}")
        await ctx.send(embed=embed)
    else:
        await ctx.send("Queue is Empty.")


@client.command(aliases=["s"])
async def skip(ctx):
    if str(ctx.channel) != "commands":
        await ctx.send("All Music Commands only in Commands channel only.")
        return
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():

        if len(songs) > 0:
            voice.pause()
            audio_player(voice)
            await ctx.send("⏭ **Skipped**")
        else:
            await ctx.send("Queue is empty")


@client.command()
async def stop(ctx):
    if str(ctx.channel) != "commands":
        await ctx.send("All Music Commands only in Commands channel only.")
        return
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        voice.stop()
        songs.clear()
        await ctx.send("**🛑 Stopped**")


@client.command(aliases=["dc", "leave"])
async def disconnect(ctx):
    if str(ctx.channel) != "commands":
        await ctx.send("All Music Commands only in Commands channel only.")
        return
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        voice.stop()
        songs.clear()
        await voice.disconnect()
        await ctx.send("**📬 Disconnected**")


@client.command()
async def pause(ctx):
    if str(ctx.channel) != "commands":
        await ctx.send("All Music Commands only in Commands channel only.")
        return
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        voice.pause()
        await ctx.send("**⏸️ Paused**")


@client.command()
async def resume(ctx):
    if str(ctx.channel) != "commands":
        await ctx.send("All Music Commands only in Commands channel only.")
        return
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_paused():
        voice.resume()
        await ctx.send("**▶️ Resumed**")

client.run("bot_token")
