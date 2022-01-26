import discord
from discord.ext import commands

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@client.event
async def on_ready():
    print("Bot is Online")
        
client.run("ODQ4NTQ5NDAxNTMzNjEyMDYy.YLOPNg.-ReUjCsZGnJV8he1trdDeT1AoAI")
