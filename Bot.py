import discord
from discord.ext import commands
import asyncio
import datetime

client=commands.Bot(command_prefix="!",intents=discord.Intents.all())

@client.event
async def on_ready():
    print("Bot is Online")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="DM Reports!"))

sent_users={}

@client.event
async def on_message(message):
    guild=client.get_guild(848549758377263104)
    empty_array=[]

    if message.author == client.user:
        return

    if message.guild and message.author != client.user:
        if message.channel.id not in sent_users.values():
            return
            
        for id, channel_id in sent_users.items():
            if message.channel.id == channel_id:
                user_id = id
        user=await client.fetch_user(user_id)

        if message.content.startswith("!"):
            return

        embed=discord.Embed(
            description=f"{message.content}",
            color=0x42f542
        )
        embed.set_author(name=message.author,icon_url=message.author.avatar_url)
        embed.set_footer(text="Moderation Team")
        embed.timestamp=datetime.datetime.utcnow()

        if message.attachments != empty_array:
            files = message.attachments
            for file in files:
                embed.set_image(url=file.url)

        await user.send(embed=embed)

         
    if message.author.id in sent_users and message.author != client.user:
        embed=discord.Embed(
            description=f"{message.content}",
            color=0x42f542
        )
        embed.set_author(name=message.author,icon_url=message.author.avatar_url)
        embed.set_footer(text="Client")
        embed.timestamp=datetime.datetime.utcnow()

        if message.attachments != empty_array:
            files = message.attachments
            for file in files:
                embed.set_image(url=file.url)

        channel=client.get_channel(sent_users[message.author.id])
        await channel.send(embed=embed)

    if message.author.id not in sent_users and message.author != client.user:
        embed=discord.Embed(
            title="Confirm Thread Creation",
            description='''This system is meant for directly contacting the server Moderators. Confirming a thread without a valid reason will not be tolerated at all.

React to confirm a thread.''',
            color=0x03bafc
        )
        msg=await message.channel.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        def check(reaction, user):
            return user == message.author and str(reaction.emoji) in ["✅","❌"]
        
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)

            if str(reaction.emoji)=="✅":
                await msg.remove_reaction("❌",client.user)
                await msg.remove_reaction("✅",client.user)

                name = "modmail"
                category = discord.utils.get(guild.categories, name=name)
                channel_name=(((str(message.author)).replace(" ","-")).replace("#","-")).lower()
                modmail_channel=await guild.create_text_channel(channel_name, category=category)
                await modmail_channel.set_permissions(guild.default_role, read_messages=False)

                embed=discord.Embed(
                    title="New ticket",
                    description="Type messages in this channel to reply. Messages starting with ``!`` will be ignored and and can be used for staff discussions. To close the thread use ``!close`` and ``!delete`` to delete the client channel.``",
                    color=0xfcba03
                )
                embed.set_footer(text=message.author)
                embed.timestamp=datetime.datetime.utcnow()
                await modmail_channel.send(embed=embed)

                embed=discord.Embed(
                    description=f"{message.content}",
                    color=0x42f542
                )
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
                    color=0x42f542
                )
                embed.set_footer(text="Your message has been sent",icon_url="")
                embed.timestamp=datetime.datetime.utcnow()
                await message.channel.send(embed=embed)

        except asyncio.TimeoutError:
            await message.channel.send("Timeout Error... Try Again!")
        

client.run("ODQ4NTQ5NDAxNTMzNjEyMDYy.YLOPNg.cKs5tTQl6v_MLfKuNngBG88b704")