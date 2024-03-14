import discord
import os
import random
import pickle
import datetime
from discord.ext import commands
from discord.ext import tasks
from dotenv import load_dotenv
import func
import f_shout
import f_dice
import f_login

load_dotenv()

bot = commands.Bot(command_prefix="!!", intents=discord.Intents.all())

#MasateoのID
masateo_id = 414755451419230208
#本当のゲリ
testch_id = 1150788907953299586
#old_now初期化
old_now = ""

#起動したときに起こるイベント
@bot.event
async def on_ready():
    print("準備完了")
    await bot.tree.sync()
    loop.start()


#!!call
@bot.command()
async def call(ctx):
    await ctx.send("マ！")

#!!shout
@bot.command()
async def shout(ctx,*arg):
    quiz = f_shout.normal()
    sh_col = discord.Colour.green()

    if len(arg) > 0 and arg[0] == "hard":
        quiz = f_shout.hard()
        sh_col = discord.Colour.red()

    await ctx.send(arg)
    await ctx.send(embed=discord.Embed(title=":boom:SPRINT SHOUT", description="**【○に文字を入れて言葉を完成させよ】**\n# {}".format(quiz), color=sh_col))

#!!coin
@bot.command()
async def coin(ctx):
    if random.randint(1,2) == 1:
        coin_deme = "<:sei:1133968046915076116>"
    else:
        coin_deme = "<:si:1133966404001996881>"

    embed = discord.Embed(title=":coin:COIN TOSS", description="# {}".format(coin_deme), color=0xffcc00)
    await ctx.send(embed=embed)

#!!dice
@bot.command()
async def dice(ctx,*arg):
    if len(arg) > 0:
        di_max = arg[0]
        di_res = f_dice.roll(di_max)

    if len(arg) == 0:
        di_max = "2d6"
        di_res = f_dice.roll(di_max)

    if len(di_max) > 200:
        di_max = "KUSODEKA"
        di_res = "# デカすぎます"

    if len(di_res) > 5000:
        di_max = "KUSODEKA"
        di_res = "# デカすぎます"

    embed = discord.Embed(title=":game_die:DICES( {} )".format(di_max), description=di_res, color=0xffcc00)
    await ctx.send(embed=embed)  

#!!login
@bot.command()
async def login(ctx):
    with open("login.pkl", "rb") as f:
        login_list = pickle.load(f)
    print(login_list)

    if ctx.author.id in login_list and ctx.author.id != masateo_id:
        embed = discord.Embed(title=":gift:LOGIN BOUNS", description="**<@{}>\n今日のログインボーナスは取得済みです**".format(ctx.author.id), color=0x00f230)
        await ctx.send(embed=embed)         

    else:
        bonus = func.convCustomEmoji(f_login.getBonus())
        im_url = ""
        if "https" in bonus:
            im_url = bonus
            bonus_txt = ""
        else:
            bonus_txt = "\n# {}".format(bonus)

        give = -1
        if ctx.author.id == give:
            bonus = "自分しか書き込めないテキストチャンネル"
            bonus_txt = "\n# {}".format(bonus)
        
        today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y/%m/%d")
        embed = discord.Embed(title=":gift:LOGIN BOUNS", 
        description="**<@{0}>\n{1}\n今日のログインボーナスはこちら:bangbang::star2:**\n:sparkle::sparkle::sparkle::sparkle::sparkle::sparkle::sparkle::sparkle::sparkle::sparkle::sparkle::sparkle::sparkle::sparkle:{2}".format(ctx.author.id, today, bonus_txt), color=0x00f230)
        if im_url != "":
            embed.set_image(url=im_url)
        await ctx.send(embed=embed) 
        login_list.append(ctx.author.id)
        with open("login.pkl","wb") as f:
            pickle.dump(login_list, f)

#!!login_listreset
@bot.command()
async def login_listreset(ctx):
    login_list = []
    with open("login.pkl","wb") as f:
        pickle.dump(login_list, f)

# error syori
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        embed = discord.Embed(title=":question:UNKNOWN COMMAND", description="# そんなコマンドはない", color=0xff0000)
        await ctx.send(embed=embed)
    else:
        raise error



#ログインリセット用ループ処理
@tasks.loop(seconds=10)
async def loop():
    global old_now,testch_id
    #print("loop")
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%H:%M")
    channel = bot.get_channel(testch_id)
    #await channel.send(now)

    # 00:00 - login reset
    if old_now != now and now == "00:00":
        await channel.send("login reset")
        login_list = []
        with open("login.pkl","wb") as f:
            pickle.dump(login_list, f)
    
    # 現在時刻更新
    old_now = now


TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)