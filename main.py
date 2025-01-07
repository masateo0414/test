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
    if "@" in  mention:
        return re.search(r'\@(.+?)\>', mention).group(1)
    else:
        return mention

def addJosu(age):
    if age == 11 or age == 12 or age == 13:
        return f"{age}th"
    elif age % 10 == 1:
        return f"{age}st"
    elif age % 10 == 2:
        return f"{age}nd"
    elif age % 10 == 3:
        return f"{age}rd"
    else:
        return f"{age}th"

# // MARK: call
@bot.command()
async def call(ctx):
    await ctx.send("マ！")

# // MARK: help
@bot.command()
async def send_bot_help(self):
    await self.get_destination().send("https://discord.com/channels/1133831716507754536/1217748515288121426")

# // MARK: shout
@bot.command()
async def shout(ctx,*arg):
    quiz = f_shout.normal()
    sh_col = discord.Colour.green()

    if len(arg) > 0 and arg[0] == "hard":
        quiz = f_shout.hard()
        sh_col = discord.Colour.red()

    await ctx.send(embed=discord.Embed(title=":boom:SPRINT SHOUT", description="**【○に文字を入れて言葉を完成させよ】**\n# {}".format(quiz), color=sh_col))

# // MARK: coin
@bot.command()
async def coin(ctx):
    if random.randint(1,2) == 1:
        coin_deme = "<:sei:1133968046915076116>"
    else:
        coin_deme = "<:si:1133966404001996881>"

    embed = discord.Embed(title=":coin:COIN TOSS", description="# {}".format(coin_deme), color=0xffcc00)
    await ctx.send(embed=embed)

# // MARK: dice
@bot.command()
async def dice(ctx,*arg):
    if len(arg) > 0:
        di_max = arg[0]
        di_res = func.convCustomEmoji(f_dice.roll(di_max))

    if len(arg) == 0:
        di_max = "2d6"
        di_res = func.convCustomEmoji(f_dice.roll(di_max))

    if len(di_max) > 200:
        di_max = "KUSODEKA"
        di_res = "# デカすぎます"

    if len(di_res) > 4096:
        di_max = "KUSODEKA"
        di_res = "# デカすぎます"

    embed = discord.Embed(title=":game_die:DICES( {} )".format(di_max), description=f"**<@{ctx.author.id}>**\n{di_res}", color=0xffcc00)
    await ctx.send(embed=embed)  

# // MARK: rand
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


# // MARK: login
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

# // MARK: memory
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

# // MARK: sv
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
    
    # tag - ゲマタグ追加
    if arg[0] == "tag":
        if len(arg) != 2:
            embed = discord.Embed(title="<:savar:1218331362415870032>SAVAR BANK", description=f"ERROR!", color=0x0074e1)
            await ctx.send(embed=embed)
            return
        
        tag = arg[1]
        userID = str(ctx.author.id)

        ws_tag = workbook.worksheet("tag")
        tag_list = ws_tag.col_values(1)

        if tag in tag_list:
            tag_id = ws_tag.cell((tag_list.index(tag))+1, 2,).value
            embed = discord.Embed(title=":memo:GAMER TAG RESISTRATION", description=
            f"**:warning:\"{tag}\" はすでに <@{tag_id}> によって登録されています**\n"
            f"(そんなわけない場合は、Masateoに連絡してください)", color=0x0074e1)
            await ctx.send(embed=embed)
            return     
        
        ws_tag.update_cell(len(tag_list)+1, 1, tag)
        ws_tag.update_cell(len(tag_list)+1, 2, userID)

        embed = discord.Embed(title=":memo:GAMER TAG RESISTRATION", description=
        f":white_check_mark:ゲーマータグを登録しました:\n"
        f"## <@{userID}> : {tag}", color=0x0074e1)
        await ctx.send(embed=embed)

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

# // MARK: bomb
@bot.command()
async def bomb(ctx,arg):
    # 競合を弾きたい
    log_list = [msg async for msg in ctx.channel.history(limit=2)]
    if log_list[1].content.startswith("!!bomb"):
        await ctx.send("ﾏ-")
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
        embed = discord.Embed(title=f":boom:{len(now_list)} BOMB GAME (ver.3)", description=outtext, color=0x600000)
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
        embed = discord.Embed(title=f":boom:{len(now_list)} BOMB GAME (ver.3)", description=cleartext, color=0x600000)
        await ctx.send(embed=embed)

        # 賞金
        if len(now_list) % 3 == -1:
            jackpot = int(ws.acell("A4").value)
            hero_log = ws.col_values(5)
            hero_log.reverse()
            txt = f"# <:3000fever:1163376520975351818>JACKPOT<:3000fever:1163376520975351818>\n" + jackpotGive(hero_log, jackpot)
            ws.update_acell("A4", 100000)
        else:
            bonus = 4000 * len(now_list)
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


# // MARK: work
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


# // MARK: dojo
@bot.command()
async def dojo(ctx):

    forDojoCh = [1289226276443521034, 1150788907953299586]
    if ctx.channel.id not in forDojoCh:
        embed = discord.Embed(title=":x:ERROR", description="# このチャンネルでは使えません", color=0xff0000)
        await ctx.send(embed=embed)
        return

    ws_dojo = workbook.worksheet("dojo")

    yaku_list = ["ヒフミ","目無し","1の目","2の目","3の目","4の目","5の目","6の目",
                "シゴロ","6のアラシ","5のアラシ","4のアラシ","3のアラシ","2のアラシ","ピンゾロ"]
    rank_list = ["カス","素人","一般人","四段","五段","六段","七段","八段",
                "名人初段","名人二段","名人三段","名人四段","名人五段","名人六段","名人七段","名人八段",
                "超人初段","超人二段","超人三段","超人四段","超人五段","超人六段","超人七段","超人八段",
                "達人初段","達人二段","達人三段","達人四段","達人五段","達人六段","達人七段","達人八段",
                "神"]
    border = 3
    rankup = 0
    d_res = ""

    # セーブデータ読み込み
    id_list = ws_dojo.col_values(1)
    if str(ctx.author.id) in id_list:
        lineind = id_list.index(str(ctx.author.id))+1

        level = int(ws_dojo.cell(lineind, 3,).value)
        border = level % 8
        if border == 0 : border = 8
        maxlife = int(7 - (level - border) / 4)
        star = int(ws_dojo.cell(lineind, 4,).value)
        life = int(ws_dojo.cell(lineind, 5,).value)
    else:
        lineind = len(id_list)+1

        await rankUpdate(f"<@{ctx.author.id}>", "【一般人】")
        ws_dojo.update([[str(ctx.author.id), ctx.author.name, 3, 0, 7]],f"A{lineind}:E{lineind}")

        level = 3
        border = 3
        star = 0
        maxlife = 7
        life = 7
    
    rank = f"{rank_list[level-1]}{"★"*star}"

    # ふるよー
    a = random.randint(1,6)
    d_res += f":dice_{a}: "
    b = random.randint(1,6)
    d_res += f":dice_{b}: "
    c = random.randint(1,6)
    d_res += f":dice_{c}: "

    d_list = (a,b,c)
    d_res = func.convCustomEmoji(d_res)


    # 出目判定
    if a!=b and b!=c and c!=a and a+b+c == 6:
        result = -1
    elif d_list.count(1) == 2:
        result = a+b+c -2
    elif d_list.count(2) == 2:
        result = a+b+c -4
    elif d_list.count(3) == 2:
        result = a+b+c -6
    elif d_list.count(4) == 2:
        result = a+b+c -8
    elif d_list.count(5) == 2:
        result = a+b+c -10
    elif d_list.count(6) == 2:
        result = a+b+c -12
    elif a!=b and b!=c and c!=a and a+b+c == 15:
        result = 7
    elif a==b==c:
        result = 7 -a +7
    else:
        result = 0

    # 成否処理
    rankupStar = [3,3,3,3,2,2,1,1]
    # ションベン
    if random.randrange(1,500) == 1:
        rankup = -1

        d_res = ":basket: :white_small_square::white_small_square::white_small_square:"
        yaku = f"ションベン　▶　<:aho:1168437457969229824>"
        syohai = f"<:ikunai:1134046737338732624>:bangbang:"
        now_life = life
    # ピンゾロ
    elif result == 13:
        syohai = f":star2: 即飛び級昇格!!!!"
        now_life = life
        yaku = f"{yaku_list[result+1]}　▶　<:kami:1161339802340298793><:kati:1155023087172067360>"

        rankup = 2
        print("rankUp2")
    # アラシ
    elif result >= 8 and result <= 12:
        syohai = f":star2: 即昇格!!!"
        now_life = life
        yaku = f"{yaku_list[result+1]}　▶　<:deka:1134020757983330304><:kati:1155023087172067360>"

        rankup = 1
        print("rankUp")
    # 123
    elif result == -1:
        syohai = "<:si:1133966404001996881>:bangbang:"
        now_life = 0
        yaku = f"{yaku_list[result+1]}　▶　<:deka:1134020757983330304><:make:1155023139416326205>"
    # 通常勝ち
    elif result >= border:
        star += 1
        syohai = f":star2: CLEAR!!\n## {rank_list[level-1]}{"★"*(star-1)} ▶ {rank_list[level-1]}{"★"*star}"
        now_life = life
        yaku = f"{yaku_list[result+1]}　▶　<:kati:1155023087172067360>"

        if star == rankupStar[border-1]:
            rankup = 1
            print("rankUp")
        else:
            ws_dojo.update([[star, maxlife]],f"D{lineind}:E{lineind}")
            await rankUpdate(f"<@{ctx.author.id}>", f"【{rank_list[level-1]}{"★"*star}】")
    # 通常負け
    else:
        syohai = "MISS..."
        now_life = life -1
        yaku = f"{yaku_list[result+1]}　▶　<:make:1155023139416326205>"

        ws_dojo.update_cell(lineind, 5, now_life)


    yaku_border = yaku_list[border+1]

    embed = discord.Embed(title=":hut:CHINCHIRO DOJO", 
                    description=f"### {rank} <@{ctx.author.id}>\n"
                                f"{rank_list[level]} 昇格条件: **★ {rankupStar[border-1]}つ**\n"
                                f"★獲得条件: **{yaku_border}** 以上\n"
                                f"―――――――――――――――――\n"
                                f"# {d_res}\n"
                                f"## {yaku}\n"
                                f"# {syohai}\n"
                                f"{":heart:"*now_life}{":black_heart:"*(maxlife-now_life)}",
                        color=0xee3700)
    await ctx.send(embed=embed) 

    # 降格処理
    if now_life <= 0:
        star -= 1

        # ★0なら
        if star == -1:
            if level == 1:
                ws_dojo.update_cell(lineind, 4, 7)            

                embed = discord.Embed(title=":hut:CHINCHIRO DOJO", 
                            description=f"## <@{ctx.author.id}> 本当にカス\n"
                                        f"**ライフリセット！いい加減にしろ**",
                                color=0x880000)
                await ctx.send(embed=embed) 
            else:
                await rankUpdate(f"<@{ctx.author.id}>", f"【{rank_list[level-2]}】")
                if border == 1:
                    ws_dojo.update([[level-1, 0, maxlife+2]],f"C{lineind}:E{lineind}")
                else:
                    ws_dojo.update([[level-1, 0, maxlife]],f"C{lineind}:E{lineind}")
                
                embed = discord.Embed(title=":hut:CHINCHIRO DOJO", 
                            description=f"# :arrow_heading_down:降格:anger:\n"
                                        f"## <@{ctx.author.id}> {rank_list[level-1]} ▶ {rank_list[level-2]}\n"
                                        f"**ライフリセット！再挑戦しよう**",
                                color=0x880000)
                await ctx.send(embed=embed) 
        # ★があるなら
        else:
            await rankUpdate(f"<@{ctx.author.id}>", f"【{rank_list[level-1]}{"★"*star}】")
            ws_dojo.update([[star, maxlife]],f"D{lineind}:E{lineind}")

            embed = discord.Embed(title=":hut:CHINCHIRO DOJO", 
                        description=f"# :skull_crossbones: LOST\n"
                                    f"## <@{ctx.author.id}> {rank_list[level-1]}{"★"*(star+1)} ▶ {rank_list[level-1]}{"★"*star}\n"
                                    f"**ライフリセット！再挑戦しよう**",
                            color=0x880000)
            await ctx.send(embed=embed) 

    
    # 昇格処理
    if rankup == 1:
        if border == 8:
            ws_dojo.update([[level+1, 0, maxlife-2]],f"C{lineind}:E{lineind}")
        else:
            ws_dojo.update([[level+1, 0, maxlife]],f"C{lineind}:E{lineind}")
        
        await rankUpdate(f"<@{ctx.author.id}>", f"【{rank_list[level]}】")

        embed = discord.Embed(title=":hut:CHINCHIRO DOJO", 
                    description=f"# :arrow_heading_up:昇格!!\n"
                                f"## <@{ctx.author.id}> {rank_list[level-1]} ▶ {rank_list[level]}\n"
                                f"**ライフリセット！**",
                        color=0xff3300)
        await ctx.send(embed=embed) 
    elif rankup == 2:
        if border > 6:
            ws_dojo.update([[level+2, 0, maxlife-2]],f"C{lineind}:E{lineind}")
        else:
            ws_dojo.update([[level+2, 0, maxlife]],f"C{lineind}:E{lineind}")
        
        await rankUpdate(f"<@{ctx.author.id}>", f"【{rank_list[level+1]}】")

        embed = discord.Embed(title=":hut:CHINCHIRO DOJO", 
                    description=f"# :arrow_heading_up::arrow_heading_up:飛び級昇格!!\n"
                                f"## <@{ctx.author.id}> {rank_list[level-1]} ▶ {rank_list[level+1]}\n"
                                f"**ライフリセット！**",
                        color=0xff3300)
        await ctx.send(embed=embed) 
    elif rankup == -1:
        if level == 1:
            ws_dojo.update_cell(lineind, 4, 7)            

            embed = discord.Embed(title=":hut:CHINCHIRO DOJO", 
                        description=f"## <@{ctx.author.id}> 本当にカス\n"
                                    f"**ライフリセット！いい加減にしろ**",
                            color=0x880000)
            await ctx.send(embed=embed) 
        else:
            await rankUpdate(f"<@{ctx.author.id}>", f"【{rank_list[level-2]}】")
            if border == 1:
                ws_dojo.update([[level-1, 0, maxlife+2]],f"C{lineind}:E{lineind}")
            else:
                ws_dojo.update([[level-1, 0, maxlife]],f"C{lineind}:E{lineind}")
            
            embed = discord.Embed(title=":hut:CHINCHIRO DOJO", 
                        description=f"# :arrow_heading_down:降格:anger:\n"
                                    f"## <@{ctx.author.id}> {rank_list[level-1]} ▶ {rank_list[level-2]}\n"
                                    f"**ライフリセット！再挑戦しよう**",
                            color=0x880000)
            await ctx.send(embed=embed) 

# 段位表更新
async def rankUpdate(user, rank):
    rank_dic = [["神","a"],
                ["超人八段","b"],
                ["超人七段","c"],
                ["超人六段","d"],
                ["超人五段","e"],
                ["超人四段","f"],
                ["超人三段","g"],
                ["超人二段","h"],
                ["超人初段","i"],
                ["名人八段","j"],
                ["名人七段","k"],
                ["名人六段","l"],
                ["名人五段","m"],
                ["名人四段","n"],
                ["名人三段","o"],
                ["名人二段","p"],
                ["名人初段","q"],
                ["八段","r"],
                ["七段","s"],
                ["六段","t"],
                ["五段","u"],
                ["四段","v"],
                ["一般人","w"],
                ["素人","x"],
                ["カス","y"]]
    
    channel = bot.get_channel(1289170232782622751) #段位表
    messages = [message async for message in channel.history(limit=1)]
    rank_mes = messages[-1]
    rank_lists = rank_mes.content.replace("**","").split("\n")
    rank_list = []
    for i in range(len(rank_lists)):
        rank_set = rank_lists[i].split(" ")
        rank_list.append(rank_set)

    # あったら更新、なければ追加
    flag = 0
    for i in range(len(rank_list)):
        if user == rank_list[i][1]:
            rank_list[i][0] = rank
            flag = 1
    if flag == 0:
        rank_list.append([rank,user])
        
    # まわりくどソート
    for j in range(len(rank_list)):
        for k in range(len(rank_dic)):
            rank_list[j][0] = rank_list[j][0].replace(rank_dic[k][0],rank_dic[k][1])
    rank_list.sort()
    for j in range(len(rank_list)):
        for k in range(len(rank_dic)):
            rank_list[j][0] = rank_list[j][0].replace(rank_dic[k][1],rank_dic[k][0])
    
    # txtにもどす
    new_mes = ""
    for set in rank_list:
        new_mes += f"**{set[0]} {set[1]}**\n"
    new_mes = new_mes[:-1]
    await rank_mes.edit(content=new_mes)

# // MARK: test
#!!login_listreset
@bot.command()
async def login_listreset(ctx):
    worksheet = workbook.sheet1
    worksheet.batch_clear(["A:B"])

#test~
@bot.command()
async def dbTest(ctx):
    channel = bot.get_channel(1289170232782622751) #datebase
    embed = discord.Embed(title=":hut:CHINCHIRO DOJO: RANK LIST", 
            description=f"**【五段】 <@159985870458322944>**\n"
                        f"**【四段】 <@235148962103951360>**\n"
                        f"**【一般人】 <@414755451419230208>**",
                color=0xee3700)
    await channel.send(f"**【名人二段】 <@610826378971185152>**\n"
                        f"**【七段】 <@1001800888001773588>**\n"
                        f"**【六段★】 <@836563535722446850>**\n"
                        f"**【四段★★】 <@778974168410226708>**\n"
                        f"**【四段★】 <@699110927957622804>**\n"
                        f"**【四段】 <@398044353207205892>**\n"
                        f"**【一般人★★】 <@515090484889255938>**\n")

@bot.command()
async def dbTest2(ctx,*arg):
    await rankUpdate(arg[0],arg[1])
    # embed = discord.Embed(title=f":birthday:BIRTHDAY REMINDER",
    #                description=
    #                f"## 2024/09/28\n# <@562955628268486696>\n# :confetti_ball:HAPPY 19th BIRTHDAY!!:tada:",
    #                color=0xff6000)
    #channel = bot.get_channel(1133837604991811665) #ノーマル雑談
    #await channel.send(embed=embed)
    



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



# // MARK: on_message
#特定のメッセージに反応する
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # 1 : しゃべる
    if bot.user in message.mentions:
        ws_reply = workbook.worksheet("reply")

        #特定の言葉に反応する
        reply = f_reply.aiduti(message.content)
        #ない場合は適当に喋る
        if reply == None:
            reply = randomSpeak(ws_reply)


        #送信！
        await message.reply(reply)
    
    # 2 : ServerBot -> MasabaBotの連携
    if message.author.id == 1287447200611176500:
        if message.content.startswith("[change]"):
            change_list = message.content.replace("[change] ","").split(",")
            tag = change_list[0]
            amount = int(change_list[1])

            ws_tag = workbook.worksheet("tag")
            tag_list = ws_tag.col_values(1)

            if tag in tag_list:
                tag_id = ws_tag.cell((tag_list.index(tag))+1, 2,).value
                now_sv = svAdd(tag_id, amount)
                embed = discord.Embed(title=f"<:savar:1218331362415870032>SAVAR BANK",
                description=
                f"## {amount:,} MinePointを <:savar:1218331362415870032>{amount:,} に変換しました\n"
                f"<@{tag_id}> <:savar:1218331362415870032>{now_sv - amount:,} ▶ **<:savar:1218331362415870032>{now_sv:,}**"
                , color=0x0074e1)
                await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(title="<:savar:1218331362415870032>SAVAR BANK", description=
                f"## :x:ゲーマータグが登録されていません\n"
                f"**・`!!sv tag (ゲーマータグ)`でゲーマータグを登録してください**\n"
                f"**・Switch勢の方は、ゲーマータグではなくアカウント名で登録するとうまくいくと思います**", color=0x0074e1)
                await message.channel.send(embed=embed)
                await message.channel.send(f"変換が正しく行われませんでした")
                await message.channel.send(f"/scoreboard players add {tag} minepoint {amount}")
                await message.channel.send(f"/scoreboard players add {tag} change_minepoint {amount}")


    # 3 : ちんこ検知
    chinkoes = ["ちんこ","chinko","tinko","チンコ","ﾁﾝｺ","ちんぽ","chimpo","chinpo","tinpo","チンポ","ﾁﾝﾁﾝ","ちんちん","chinchin","tintin","チンチン","ﾁﾝﾁﾝ","珍棒","珍珍","ちんぼう","チンボウ","ぽこちん","pokochin","pokotin","ポコチン","ﾎﾟｺﾁﾝ","肉棒","陰茎","ぺにす","ペニス","ﾍﾟﾆｽ","まら","マラ","ﾏﾗ","魔羅","penis","てぃんてぃん","ティンティン","ティムポ","ちーんこ","チーンコ"]
    if message.content.lower() in chinkoes or any(s in message.content.lower() for s in chinkoes):
        chinkoEmoji = "<:chinko:1134001412695674891>"
        await message.add_reaction(chinkoEmoji)
    
    #フレームワーク移行のための
    await bot.process_commands(message)


# 適当発言生成
def randomSpeak(ws):
    if random.randrange(6) < 2:
        aiduti_list = ws.col_values(1)
        reply = aiduti_list[random.randrange(len(aiduti_list))]
    else:
        meisi_list = ws.col_values(2)
        randomRep_dic = ws.col_values(3)
        randomRep_dic2 = ws.col_values(4)
        reply = f_reply.randomSay(meisi_list, randomRep_dic, randomRep_dic2)
    return reply






# -------------------------------------------------------------------------------------------

# // MARK: sh-error
@bot.command()
async def sh(ctx):
    await ctx.send("たぶん、ビックリマークがいっこ多いぞ")

# // MARK: on_command_error
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        embed = discord.Embed(title=":question:UNKNOWN COMMAND", description="# そんなコマンドはない", color=0xff0000)
        await ctx.send(embed=embed)
    else:
        raise error



# // MARK: loop
#ログインリセット用ループ処理
@tasks.loop(seconds=10)
async def loop():
    global old_now,testch_id
    #print("loop")
    dt_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    now = dt_now.strftime("%H:%M")
    todate = dt_now.strftime("%Y/%m/%d")
    channel = bot.get_channel(testch_id)
    normal = bot.get_channel(1133837604991811665) #ノーマル雑談
    #await channel.send(now)

    # 00:00 events
    if old_now != now and now == "00:00":
    # if True:

        # login reset
        await channel.send(f"{todate}こうしんおっけー！！")
        worksheet = workbook.worksheet("login")
        worksheet.batch_clear(["A:B"])

        # birthday
        today = dt_now.strftime("%m%d")
        print(today)
        toyear = dt_now.year
        ws_birth = workbook.worksheet("birth")
        birthday_list = ws_birth.col_values(3)

        for i in range(len(birthday_list)):
            if today == birthday_list[i][-4:]:
                birth_userid = ws_birth.cell(i+1,1).value
                birth_year = birthday_list[i][:4]

                if birth_year == "0000":
                    embed = discord.Embed(title=f":birthday:BIRTHDAY REMINDER",
                    description=
                    f"## {todate}\n# <@{birth_userid}>\n# :confetti_ball:HAPPY BIRTHDAY!!:tada:",
                    color=0xff6000)
                else:
                    age = toyear - int(birth_year)
                    embed = discord.Embed(title=f":birthday:BIRTHDAY REMINDER",
                    description=
                    f"## {todate}\n# <@{birth_userid}>\n# :confetti_ball:HAPPY {addJosu(age)} BIRTHDAY!!:tada:",
                    color=0xff6000)
                
                await normal.send(embed=embed)

    
    # 現在時刻更新
    old_now = now

    # 突然喋る
    if random.randrange(50000) == 0:
        ws_reply = workbook.worksheet("reply")
        meisi_list = ws_reply.col_values(2)
        randomRep_dic = ws_reply.col_values(3)
        randomRep_dic2 = ws_reply.col_values(4)
        reply = f_reply.randomSay(meisi_list, randomRep_dic, randomRep_dic2)

        # channel = bot.get_channel(testch_id)
        await normal.send(reply)


TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)