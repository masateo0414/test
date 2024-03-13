import discord
import os
from discord.ext import commands

bot = commands.Bot(command_prefix="!!", intents=discord.Intents.all())


#起動したときに起こるイベント
@bot.event
async def on_ready():
    print("準備完了")
    await bot.tree.sync()


#!!ping
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)