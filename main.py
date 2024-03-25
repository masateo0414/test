import discord
import os
import re
import random
import pickle
import datetime
import gspread
import asyncio  
from oauth2client.service_account import ServiceAccountCredentials
from discord.ext import commands
from discord.ext import tasks
from dotenv import load_dotenv
import func
import f_shout
import f_dice
import f_login
import f_reply

load_dotenv()

# --- このへんスプシ連携の準備(丸写し)

#2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

#認証情報設定
#ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
credentials = ServiceAccountCredentials.from_json_keyfile_name('masababot-db-426b2ba80ff6.json', scope)

#OAuth2の資格情報を使用してGoogle APIにログインします。
gc = gspread.authorize(credentials)

#共有設定したスプレッドシートキーを変数[SPREADSHEET_KEY]に格納→そのキーでスプシを開く
global workbook
SPREADSHEET_KEY = os.getenv("SPREADSHEET_KEY")
workbook = gc.open_by_key(SPREADSHEET_KEY)

# --- スプシ連携ここまで



bot = commands.Bot(command_prefix="!!", intents=discord.Intents.all())

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

#真鯖のguild(未解決)
global guild
guild = client.get_guild(1133831716507754536)
#MasateoのID
global masateo_id
masateo_id = 414755451419230208
#本当のゲリ
testch_id = 1150788907953299586
#地下労働施設
global chika_id
chika_id = 1220089357113888844

#datebase
global dbch_id 
dbch_id = 1217820622755987566
#old_now初期化
old_now = ""

#起動したときに起こるイベント
@bot.event
async def on_ready():
    print("準備完了")
    await bot.tree.sync()
    loop.start()

#^^v お役立ちfunc v^^

def pickID(mention):
    return re.search(r'\@(.+?)\>', mention).group(1)

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

#!!rand
@bot.command()
async def rand(ctx,*arg):
    if len(arg) != 2:
        embed = discord.Embed(title=":1234:RANDOM NUMBER GENERATER", description="**:x:生成する乱数を`!!rand (最小値) (最大値)`で指定してください**", color=0x00dfa5)
        await ctx.send(embed=embed)
        return
    
    min = int(arg[0])
    max = int(arg[1])

    if min > max:
        embed = discord.Embed(title=":1234:RANDOM NUMBER GENERATER", description="**:x:最小値が最大値よりも大きいです**", color=0x00dfa5)
        await ctx.send(embed=embed)        
    
    res = random.randint(min, max)
    if len(str(res)) > 500:
        embed = discord.Embed(title=":1234:RANDOM NUMBER GENERATER", description="**:x:デカすぎます**", color=0x00dfa5)
        await ctx.send(embed=embed) 
        
    embed = discord.Embed(title=f":1234:RANDOM NUMBER GENERATER({min} - {max})", description=f"# {f_dice.numToEmoji(res)}", color=0x00dfa5)
    await ctx.send(embed=embed)      


#!!login
@bot.command()
async def login(ctx):
    ws_login = workbook.worksheet("login")
    login_list = ws_login.col_values(1)

    if str(ctx.author.id) in login_list and ctx.author.id != masateo_id:
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
        
        # savarボーナス
        sv_list = ws_login.col_values(3)
        add_sv = int(random.choice(sv_list))
        now_sv = svAdd(ctx.author.id, add_sv)
        
        today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y/%m/%d")
        embed = discord.Embed(title=":gift:LOGIN BOUNS", 
        
        description=
        f"**<@{ctx.author.id}>\n{today}\n今日のログインボーナスはこちら:bangbang::star2:\n"
        f"## <:savar:1218331362415870032>{add_sv:,}\n"
        f"TOTAL ▶ <:savar:1218331362415870032>{now_sv:,}**\n\n"
        ":sparkle::sparkle::sparkle::sparkle::sparkle::sparkle::sparkle::sparkle::sparkle::sparkle::sparkle::sparkle::sparkle::sparkle:\n"
        f"{bonus_txt}\n",
        color=0x00f230)

        if im_url != "":
            embed.set_image(url=im_url)
        await ctx.send(embed=embed) 
        ws_login.update_cell(len(login_list)+1, 1, str(ctx.author.id))
        ws_login.update_cell(len(login_list)+1, 2, ctx.author.name)

#!!memory
@bot.command()
async def memory(ctx,*arg):
    if len(arg) != 1:
        embed = discord.Embed(title=":memo:TEACH WORD", description=f"`!!memory`と半角スペースのあとに、おぼえさせたい言葉をひとつ入力してください", color=0x3d77ff)
        await ctx.send(embed=embed)
    else:
        ws_reply = workbook.worksheet("reply")
        mem_list = ws_reply.col_values(2)
        ws_reply.update_cell(len(mem_list)+1, 2, arg[0])

        embed = discord.Embed(title=":memo:TEACH WORD", description=f":white_check_mark:真鯖botは以下の言葉をおぼえました\n## {arg[0]}", color=0x3d77ff)
        await ctx.send(embed=embed)

#!!sv
@bot.command()
async def sv(ctx, *arg):
    if len(arg) == 0:
        embed = discord.Embed(title="<:savar:1218331362415870032>SAVAR BANK", description=f"ERROR!", color=0x0074e1)
        await ctx.send(embed=embed)
        return

    ws = workbook.worksheet("savar")

    # show - 確認
    if arg[0] == "show":
        # デフォルトは自分の、指定がある場合はid抽出
        if len(arg) == 1:
            id = str(ctx.author.id)    
        else:
            id = pickID(arg[1])  

        sv = svRead(id)
        
        embed = discord.Embed(title="<:savar:1218331362415870032>SAVAR BANK", description=f"**<@{id}>\n所持Savar:**\n# <:savar:1218331362415870032>{sv:,}", color=0x0074e1)
        await ctx.send(embed=embed)
    
    # give - 譲渡
    if arg[0] == "give":
        if len(arg) != 3:
            embed = discord.Embed(title="<:savar:1218331362415870032>SAVAR BANK", description=f"ERROR!", color=0x0074e1)
            await ctx.send(embed=embed)
            return
        
        fromID = ctx.author.id
        toID = pickID(arg[1])
        add = int(arg[2])

        if add < 1:
            embed = discord.Embed(title="<:savar:1218331362415870032>SAVAR BANK", description=f"**:x:譲渡する金額は1以上を指定してください**", color=0x0074e1)
            await ctx.send(embed=embed)
            return
        elif svRead(fromID) < add:
            embed = discord.Embed(title="<:savar:1218331362415870032>SAVAR BANK", description=f"**:x:所持Savarを超える金額は譲渡できません**", color=0x0074e1)
            await ctx.send(embed=embed)
            return

        from_sv = svAdd(fromID, add*(-1))
        to_sv = svAdd(toID, add)

        embed = discord.Embed(title="<:savar:1218331362415870032>SAVAR BANK", description=
        f"**:white_check_mark:以下の通りSavarが移動しました:**\n\n"
        f"from : **<@{fromID}>**\n"
        f"<:savar:1218331362415870032>{from_sv + add:,} ▶ **<:savar:1218331362415870032>{from_sv:,}**\n"
        f"## ⇓ <:savar:1218331362415870032>{add:,} ⇓\n"
        f"to : **<@{toID}>**\n"
        f"<:savar:1218331362415870032>{to_sv - add:,} ▶ **<:savar:1218331362415870032>{to_sv:,}**\n", color=0x0074e1)
        await ctx.send(embed=embed)
        return

    # add - 追加
    if arg[0] == "add":
        if ctx.author.id != masateo_id:
            return
        
        if len(arg) != 3:
            embed = discord.Embed(title="<:savar:1218331362415870032>SAVAR BANK", description=f"ERROR!", color=0x0074e1)
            await ctx.send(embed=embed)
            return
        
        toID = pickID(arg[1])
        add = int(arg[2])
        
        to_sv = svAdd(toID, add)

        embed = discord.Embed(title="<:savar:1218331362415870032>SAVAR BANK", description=
        f"to : **<@{toID}>**\n"
        f"## + <:savar:1218331362415870032>{add:,}\n"
        f"<:savar:1218331362415870032>{to_sv - add:,} ▶ **<:savar:1218331362415870032>{to_sv:,}**\n", color=0x0074e1)
        await ctx.send(embed=embed)
        return


# savar CRUDなど
def svCreate(id):
    ws = workbook.worksheet("savar")

    user = bot.get_user(int(id))

    list = ws.col_values(1)
    ws.update_cell(len(list)+1, 1, str(id))
    ws.update_cell(len(list)+1, 2, user.name)
    ws.update_cell(len(list)+1, 3, 0)


def svRead(id):
    ws = workbook.worksheet("savar")

    list = ws.col_values(1)
    if str(id) in list:
        sv = int(ws.cell(list.index(str(id))+1, 3,).value)
    else:
        svCreate(id)
        sv = 0
    
    return sv

def svAdd(id,add):
    ws = workbook.worksheet("savar")

    list = ws.col_values(1)

    if not str(id) in list:
        svCreate(id)
        list = ws.col_values(1)
    
    add_row = list.index(str(id))+1
    sv = int(ws.cell(add_row, 3,).value)
    ws.update_cell(add_row, 3, sv+add)
    return sv+add

#!!bomb
@bot.command()
async def bomb(ctx,arg):
    # 競合を弾きたい
    log_list = [msg async for msg in ctx.channel.history(limit=2)]
    if log_list[1].content.startswith("!!bomb"):
        await ctx.send("ﾏ")
        return
    # 地下ではNG
    if ctx.channel.id == 1220089357113888844:
        return
    
    ws = workbook.worksheet("bomb")
    flag = ws.acell("A3").value

    if arg == "newgame":
        # 終わってなかったらerror
        if flag != "end":
            embed = discord.Embed(title=f":bomb:n BOMB GAME (ver.3)", description="**:x:まだ前の爆弾が解除されていません**", color=0x600000)
            await ctx.send(embed=embed)
            return            
        moto = ws.col_values(3)
        ws.update('B1',motoTrans(moto))
        ws.update_acell("A3","play")
        ws.batch_clear(["E:E"])
        new_list = ws.col_values(2)
        print(new_list)
        embed = discord.Embed(title=f":bomb:{len(moto)} BOMB GAME (ver.3)", description=bombText(new_list), color=0x600000)
        await ctx.send(embed=embed)
        return

    # そもそも爆破済みなら押せない
    if flag == "end":
        embed = discord.Embed(title=f":bomb:n BOMB GAME (ver.3)", description="**:x:爆発済、もしくは解除済です\n(`!!bomb newgame`で新しくゲームを開始できます)**", color=0x600000)
        await ctx.send(embed=embed)
        return       
    try:
        push_num = int(arg)
    # このへん例外処理
    except ValueError:
        embed = discord.Embed(title=f":bomb:n BOMB GAME (ver.3)", description="**:x:存在しないボタンです**", color=0x600000)
        await ctx.send(embed=embed)
        return
    now_list = ws.col_values(2)
    if push_num > len(now_list) or push_num < 1:
        embed = discord.Embed(title=f":bomb:n BOMB GAME (ver.3)", description="**:x:存在しないボタンです**", color=0x600000)
        await ctx.send(embed=embed)  
        return

    # もう押されてたら
    if not str(push_num) in now_list:
        embed = discord.Embed(title=f":bomb:{len(now_list)} BOMB GAME (ver.3)", description=f"**:x:({push_num})は既に押されています**", color=0x600000)
        await ctx.send(embed=embed)
        return
    
    # 1/nひいたか判定
    nokori = int(ws.acell("A2").value)
    if random.randrange(nokori) == 0:
        # jackpot = int(ws.acell("A4").value)
        # 罰金決める
        if nokori == 2:
            minus = 1500 * len(now_list) * (-1)
        else:
            minus = 150 * (len(now_list) - nokori +1) * (-1)
        # 徴収
        now_sv = svAdd(ctx.author.id, minus)

        #outtext = f"## ({push_num}) ▶ OUT!\n# :boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom:\n# <@{ctx.author.id}> <:si:1133966404001996881>:bangbang::bangbang::bangbang:\n# :boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom:\n\n**JACKPOT : <:savar:1218331362415870032>{jackpot-minus:,}**"
        outtext = f"## ({push_num}) ▶ OUT!\n# :boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom:\n# <@{ctx.author.id}> <:si:1133966404001996881>:bangbang::bangbang::bangbang:\n# :boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom::boom:"
        embed = discord.Embed(title=f":boom:{len(now_list)} BOMB GAME (ver.2)", description=outtext, color=0x600000)
        await ctx.send(embed=embed)

        embed = discord.Embed(title=f":bomb:{len(now_list)} BOMB GAME (ver.3)",
            description=f"## <:savar:1218331362415870032>{minus*(-1):,} LOST\n"
            f"<:savar:1218331362415870032>{now_sv - minus:,} ▶ **<:savar:1218331362415870032>{now_sv:,}**", color=0x600000)
        await ctx.send(embed=embed)

        ws.update_acell("A3","end")
        # ws.update_acell("A4", jackpot-minus)
        return

    # セーフなら押した処理
    ws.update_acell(f"B{push_num}", "x")
    ws.update_acell(f"E{len(now_list) - nokori +1}", str(ctx.author.id))
    new_list = ws.col_values(2)
    embed = discord.Embed(title=f":bomb:{len(new_list)} BOMB GAME (ver.3)", description=f"## ({push_num}) ▶ SAFE!\n{bombText(new_list)}", color=0x600000)
    await ctx.send(embed=embed)
    # ボタン2個だったならclaer
    if nokori == 2:
        cleartext = f"# :sparkles::sparkles::sparkles::sparkles::sparkles::sparkles::sparkles::sparkles::sparkles::sparkles::sparkles::sparkles::sparkles::sparkles::sparkles:\n# ALL CLEARED!!!!\n# :sparkles::sparkles::sparkles::sparkles::sparkles::sparkles::sparkles::sparkles::sparkles::sparkles::sparkles::sparkles::sparkles::sparkles::sparkles:\n**:warning:次の爆弾のボタンが1つ増えました({len(now_list)+1}個)**"
        embed = discord.Embed(title=f":boom:{len(now_list)} BOMB GAME (ver.2)", description=cleartext, color=0x600000)
        await ctx.send(embed=embed)

        # 賞金
        if len(now_list) % 3 == -1:
            jackpot = int(ws.acell("A4").value)
            hero_log = ws.col_values(5)
            hero_log.reverse()
            txt = f"# <:3000fever:1163376520975351818>JACKPOT<:3000fever:1163376520975351818>\n" + jackpotGive(hero_log, jackpot)
            ws.update_acell("A4", 100000)
        else:
            bonus = 2500 * len(now_list)
            hero_log = ws.col_values(5)
            hero_log.reverse()
            txt = jackpotGive(hero_log, bonus)            

        embed = discord.Embed(title=f":bomb:{len(now_list)} BOMB GAME (ver.3)",description=f"**1枚→1Savarと換金できるチケットを配布します**\n{txt}", color=0x600000)
        await ctx.send(embed=embed)
        ws.update_acell("A1", len(now_list)+1)
        ws.update_acell("A3","end")
        return


# 雑転置
def motoTrans(bef):
    aft = []
    for num in bef:
        box = []
        box.append(num)
        aft.append(box)
    return aft

# 盤面テキスト生成
def bombText(list):
    blist = ""
    btotal = len(list)
    bcnt = 0

    for i in range((btotal // 10)+1):
        blist += ""
        for j in range(1, 11):
            bnum = 10*i + j
            if bnum > btotal:
                blist += ""
            elif str(bnum) in list:
                blist += f"({bnum})"
                bcnt += 1
            else:
                blist += ":ballot_box_with_check:"
        blist += "\n"

    btxt = f"# 残り {bcnt} 個\n{blist}"
    return btxt

# 賞金分配
def bonusGive(log,bonus):
    hero_list = list(set(log))
    txt = f"# :scales:BONUS LIST\n"

    for hero in hero_list:
        gain = 0
        for i in range(len(log)):
            if log[i] == hero:
                gain += round(bonus / (i+2))
        now_sv = svAdd(hero, gain)
        txt += f"## <@{hero}> <:savar:1218331362415870032>{gain:,} <:get:1179307754893082724>\n"\
                f"<:savar:1218331362415870032>{now_sv - gain:,} ▶ **<:savar:1218331362415870032>{now_sv:,}**\n\n"

    return txt

def jackpotGive(log,jackpot):
    hero_list = list(set(log))
    txt = f"# :scales:BONUS LIST\n"
    pro_sum = 0
    for n in range(2,len(log)+2):
        pro_sum += 1/n

    for hero in hero_list:
        gain = 0
        for i in range(len(log)):
            if log[i] == hero:
                gain += round(jackpot * 1/(i+2) / pro_sum)
        # now_sv = svAdd(hero, gain)
        txt += f"## <@{hero}> :tickets:{gain:,} <:get:1179307754893082724>\n"\
                # f"<:savar:1218331362415870032>{now_sv - gain:,} ▶ **<:savar:1218331362415870032>{now_sv:,}**\n\n"

    return txt


#!!work
@bot.command()
async def work(ctx):
    # check用
    def replyCheck(msg):
        return msg.author == ctx.author and msg.content.isdigit()

    if ctx.channel.id != 1220089357113888844 and ctx.author.id != masateo_id:
        return
    
    # 問題生成
    mode = random.randrange(4)
    if mode == 0:
        num1 = random.randint(1,999)
        num2 = random.randint(1,999)
        ans = num1 + num2
        txt = f"{num1} + {num2} ="
    
    if mode == 1:
        ans = random.randint(1,999)
        num2 = random.randint(1,999)
        num1 = num2 + ans
        txt = f"{num1} - {num2} ="
    
    if mode == 2:
        num1 = random.randint(2,99)
        num2 = random.randint(2,99)
        ans = num1 * num2
        txt = f"{num1} × {num2} =" 

    if mode == 3:
        ans = random.randint(5,99)
        num2 = random.randint(3,99)
        num1 = num2 * ans
        txt = f"{num1} ÷ {num2} ="  
    
    embed = discord.Embed(title=f":pick:WORK FOR MONEY",
        description=f"<@{ctx.author.id}>\n# {txt} ？", color=0x000030)
    await ctx.send(embed=embed)

    try:
        reply = await ctx.bot.wait_for(
            'message', check=replyCheck, timeout=45
        )   
        if reply.content == str(ans):
            embed = discord.Embed(title=f":pick:WORK FOR MONEY",
                description=
                f"<@{ctx.author.id}>\n# <:seikai:1164184120105107557> {txt} {ans}\n",
                color=0x000030)
            await ctx.send(embed=embed)

            gain = random.randint(100,400)
            now_sv = svAdd(ctx.author.id, gain)
            embed = discord.Embed(title=f":pick:WORK FOR MONEY",
                description=
                f"## <:savar:1218331362415870032>{gain:,} 返済\n"
                f"<:savar:1218331362415870032>{now_sv - gain:,} ▶ **<:savar:1218331362415870032>{now_sv:,}**"
                , color=0x000030)
            await ctx.send(embed=embed)

            # 返済完了なら解放
            saimu_role = ctx.guild.get_role(1220102866501369917)
            if now_sv > -1:
                await ctx.author.remove_roles(saimu_role)
                embed = discord.Embed(title=f":pick:WORK FOR MONEY",
                    description=f"## <@{ctx.author.id}>\n# :sparkles::sparkles: 解 放 :sparkles::sparkles:", color=0x000030)
                await ctx.send(embed=embed)                
        else:
            embed = discord.Embed(title=f":pick:WORK FOR MONEY",
                description=f"<@{ctx.author.id}>\n## アホ\n# <:huseikai:1164186420483723305> {txt} {ans}", color=0x000030)
            await ctx.send(embed=embed)
    except asyncio.TimeoutError:
        embed = discord.Embed(title=f":pick:WORK FOR MONEY",
            description=f"<@{ctx.author.id}>\n## 遅い\n# {txt} {ans}", color=0x000030)
        await ctx.send(embed=embed)





#!!login_listreset
@bot.command()
async def login_listreset(ctx):
    worksheet = workbook.sheet1
    worksheet.batch_clear(["A:B"])

#test~
@bot.command()
async def svTest(ctx,*arg):
    svAdd(str(masateo_id), int(arg[0]))
    await ctx.send( svRead(str(masateo_id)) )

#test~
@bot.command()
async def talkToNormal(ctx):
    ws_reply = workbook.worksheet("reply")
    meisi_list = ws_reply.col_values(2)
    randomRep_dic = ws_reply.col_values(3)
    randomRep_dic2 = ws_reply.col_values(4)
    reply = f_reply.randomSay(meisi_list, randomRep_dic, randomRep_dic2)
    channel = bot.get_channel(1133837604991811665) #ノーマル雑談
    await channel.send(reply)



#返信機能
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if bot.user in message.mentions:
        ws_reply = workbook.worksheet("reply")

        #特定の言葉に反応する
        reply = f_reply.aiduti(message.content)
        #ない場合は適当に喋る
        if reply == None:
            reply = randomSpeak(ws_reply)


        #送信！
        await message.reply(reply)
    
    #フレームワーク移行のための
    await bot.process_commands(message)


# 適当発言生成
def randomSpeak(ws):
    if random.randrange(5) < 2:
        aiduti_list = ws.col_values(1)
        reply = aiduti_list[random.randrange(len(aiduti_list))]
    else:
        meisi_list = ws.col_values(2)
        randomRep_dic = ws.col_values(3)
        randomRep_dic2 = ws.col_values(4)
        reply = f_reply.randomSay(meisi_list, randomRep_dic, randomRep_dic2)
    return reply

# -------------------------------------------------------------------------------------------
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
        worksheet = workbook.worksheet("login")
        worksheet.batch_clear(["A:B"])
    
    # 現在時刻更新
    old_now = now

    # 突然喋る
    if random.randrange(20000) == 0:
        ws_reply = workbook.worksheet("reply")
        meisi_list = ws_reply.col_values(2)
        randomRep_dic = ws_reply.col_values(3)
        randomRep_dic2 = ws_reply.col_values(4)
        reply = f_reply.randomSay(meisi_list, randomRep_dic, randomRep_dic2)

        channel = bot.get_channel(1133837604991811665) #ノーマル雑談
        # channel = bot.get_channel(testch_id)
        await channel.send(reply)


TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)