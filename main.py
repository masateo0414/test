import discord
import os
from discord.ext import commands

bot = commands.Bot(command_prefix="!!", intents=discord.Intents.all())


#起動したときに起こるイベント
@bot.event
async def on_ready():
    print("準備完了")
    await bot.tree.sync()


#!!call
@bot.command()
async def call(ctx):
    await ctx.send("マ！")

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)