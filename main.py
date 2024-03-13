import discord
import os
import random
from discord.ext import commands
import f_shout

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

#!!shout
@bot.command()
async def shout(ctx,*arg):
    if arg == "hard":
        quiz = f_shout.hard()
        sh_col = discord.Colour.red()
    else:
        quiz = f_shout.normal()
        sh_col = discord.Colour.green()

    await ctx.send(arg)
    await ctx.send(embed=discord.Embed(title=":boom:SPRINT SHOUT", description="**【○に文字を入れて言葉を完成させよ】**\n# {}".format(quiz), color=sh_col))


TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)