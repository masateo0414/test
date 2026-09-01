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
import f_sniper
import f_slot

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



intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!!", intents=intents, help_command=None)

#intents = discord.Intents.default()
#intents.message_content = True
#intents.messages = True
#intents.guilds = True
#intents.members = True
#client = discord.Client(intents=intents)


# Botを通すやつ
@bot.check
async def global_allow_bots(ctx):
    return True  # 全てのメッセージを許可（Botも含む）

#真鯖のguild(未解決)
global guild
guild = bot.get_guild(1133831716507754536)

#MasateoのID
global masateo_id
masateo_id = 414755451419230208
#本当のゲリ
ch_test_id = 1150788907953299586
#地下労働施設
global chika_id
chika_id = 1220089357113888844

#datebase
global dbch_id 
dbch_id = 1217820622755987566
#old_now初期化
old_now = ""

#slotのやつ
ws_slot = workbook.worksheet("slot")
user_achievements = {}

# // MARK: on_ready
# 起動したときに起こるイベント
@bot.event
async def on_ready():
    print("準備完了")
    try:
        await bot.tree.sync()
        print("tree sync ok")

        # スプレッドシートからの実績読み込み
        load_achievements()
        print("load_achievements ok")

        # 0時定期更新タスクの起動
        if not daily_reset_task.is_running():
            daily_reset_task.start()
            print("0:00_loop started")

        # 突然喋るタスクの起動
        if not random_talk_task.is_running():
            random_talk_task.start()
            print("10sec_loop started")

    except Exception as e:
        print("ERROR in on_ready:", e)

# // MARK: any function
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

#slotのやつら
def load_achievements():
    """起動時にスプシから全ユーザーの実績を読み込む"""
    global user_achievements
    records = ws_slot.get_all_records()
    for row in records:
        uid = int(row["user_id"])
        ids = (
            set(row["unlocked_ids"].split(","))
            if row.get("unlocked_ids")
            else set()
        )
        user_achievements[uid] = ids


def save_achievement(user_id, user_name, p_id):
    # p_id が None や空の場合は実績保存しない
    if not p_id:
        return False

    # 初期化チェック
    if user_id not in user_achievements:
        user_achievements[user_id] = set()

    str_p_id = str(p_id)
    is_new = str_p_id not in user_achievements[user_id]

    if is_new:
        user_achievements[user_id].add(str_p_id)

    # 過去に入り込んでしまった None や非文字列をすべて除去・文字列化して安全に連結
    clean_set = {str(x) for x in user_achievements[user_id] if x is not None}
    user_achievements[user_id] = clean_set  # 汚染されたデータをきれいなデータで上書き
    
    unlocked_str = ",".join(clean_set)

    try:
        cell = ws_slot.find(str(user_id))
        ws_slot.update_cell(cell.row, 2, user_name)
        ws_slot.update_cell(cell.row, 3, unlocked_str)
    except:
        ws_slot.append_row([str(user_id), user_name, unlocked_str])

    return is_new


# --- コレクション表示UI ---
class SlotAchvView(discord.ui.View):

    def __init__(self, author, unlocked_ids, per_page=10):  # 1ページ10件に設定
        super().__init__(timeout=60)
        self.author = author
        self.unlocked_ids = unlocked_ids
        self.per_page = per_page
        self.current_page = 0
        self.patterns = f_slot.WINNING_PATTERNS
        self.total_pages = (
            len(self.patterns) + self.per_page - 1
        ) // self.per_page

    def create_embed(self):
        unlocked_count = len(self.unlocked_ids)
        total_count = len(self.patterns)

        start_idx = self.current_page * self.per_page
        end_idx = start_idx + self.per_page
        page_items = self.patterns[start_idx:end_idx]

        description = f"## {unlocked_count}/{total_count} \n\n"

        for i, (p_id, emojis, rate, title, rarity) in enumerate(page_items):
            # No.01, No.02 のように全体での通し番号を計算
            no_num = start_idx + i + 1
            no_str = f"No.{no_num:02d}"

            # 絵文字リストをスペース区切りで結合（可変対応）
            emoji_str = "".join(emojis)

            if p_id in self.unlocked_ids:
                description += f"✅ **{no_str} [ {rarity} ] {title}** \n ┗ {emoji_str}\n"
            else:
                description += f"🔒 **{no_str} [ {rarity} ] ？**\n ┗ ❓❓❓\n"

        embed = discord.Embed(
            title=f"🏆 Achievements",
            description=description,
            color=0x00FF7F,
        )
        embed.set_author(
                    name=f"{self.author.display_name}",
                    icon_url=self.author.display_avatar.url
                )
        embed.set_footer(
            text=f"PAGE {self.current_page + 1}/{self.total_pages}"
        )
        return embed

    @discord.ui.button(label="◀ PREV", style=discord.ButtonStyle.secondary)
    async def prev_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                "コラッ！他人のボタンを勝手に押さない", ephemeral=True
            )
            return

        # 最初のページなら最後のページへループ、それ以外は1つ戻る
        if self.current_page > 0:
            self.current_page -= 1
        else:
            self.current_page = self.total_pages - 1

        await interaction.response.edit_message(
            embed=self.create_embed(), view=self
        )

    @discord.ui.button(label="NEXT ▶", style=discord.ButtonStyle.secondary)
    async def next_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                "コラッ！他人のボタンを勝手に押さない", ephemeral=True
            )
            return

        # 最後のページなら最初のページへループ、それ以外は1つ進む
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
        else:
            self.current_page = 0

        await interaction.response.edit_message(
            embed=self.create_embed(), view=self
        )
    

# // MARK: help
@bot.command()
async def help(ctx, *arg):
    if len(arg) == 0:
        embed = discord.Embed(title=":grey_question:HELP",
                        description=f"# ´・-・)っhttps://discordapp.com/channels/1133831716507754536/1217748515288121426",
                        color=0xdddddd)
        
        await ctx.send(embed=embed)
    
    else:
        doc = func.helpDocument(arg[0])
        if doc == "NF":
            embed = discord.Embed(title=":grey_question:HELP",
                description=f"そんなコマンドないと思う\n"
                "# ´・-・)っhttps://discordapp.com/channels/1133831716507754536/1217748515288121426",
                color=0xdddddd)
        else:
            embed = discord.Embed(title=":grey_question:HELP",
                description=doc,
                color=0xdddddd)
        
        await ctx.send(embed=embed)

# // MARK: call
@bot.command()
async def call(ctx):
    await ctx.send("マ！<a:gaming:1231223018043347044>")

# // MARK: shout
@bot.command()
async def shout(ctx,*arg):
    quiz = f_shout.normal()
    sh_col = discord.Colour.green()

    if len(arg) > 0 and arg[0] == "hard":
        quiz = f_shout.hard()
        sh_col = discord.Colour.red()

    await ctx.send(embed=discord.Embed(title=":boom:SPRINT SHOUT", description="**【○に文字を入れて言葉を完成させよ】**\n# {}".format(quiz), color=sh_col))

# // MARK: sniper
@bot.command()
async def sniper(ctx):
    letter = f_sniper.getLetter()
    odai = f_sniper.getOdai()

    embed = discord.Embed(title=":gun:WORD SNIPER",
                        description=f"# 「{letter[0]}」\n"
                                    f"**から始まる**\n"
                                    f"# 「{odai}」\n"
                                    f"**といえば？( {letter[1]} pt )**",
                        color=0xffa500)
    
    await ctx.send(embed=embed)

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
        embed = discord.Embed(
            title="<:savar:1218331362415870032>SAVAR BANK",
            description="ERROR!",
            color=0x0074E1,
        )
        await ctx.send(embed=embed)
        return

    # show - 確認
    if arg[0] == "show":
        id = str(ctx.author.id) if len(arg) == 1 else pickID(arg[1])
        sv = svRead(id)

        embed = discord.Embed(
            title="<:savar:1218331362415870032>SAVAR BANK",
            description=f"**<@{id}>\n所持Savar:**\n# <:savar:1218331362415870032>{sv:,}",
            color=0x0074E1,
        )
        await ctx.send(embed=embed)

    # give - 譲渡
    elif arg[0] == "give":
        if len(arg) != 3:
            embed = discord.Embed(
                title="<:savar:1218331362415870032>SAVAR BANK",
                description="ERROR!",
                color=0x0074E1,
            )
            await ctx.send(embed=embed)
            return

        fromID = str(ctx.author.id)
        toID = pickID(arg[1])
        add = int(arg[2])

        if add < 1:
            embed = discord.Embed(
                title="<:savar:1218331362415870032>SAVAR BANK",
                description="**:x:譲渡する金額は1以上を指定してください**",
                color=0x0074E1,
            )
            await ctx.send(embed=embed)
            return

        # 事前チェック
        current_from_sv = svRead(fromID)
        if current_from_sv < add:
            embed = discord.Embed(
                title="<:savar:1218331362415870032>SAVAR BANK",
                description="**:x:所持Savarを超える金額は譲渡できません**",
                color=0x0074E1,
            )
            await ctx.send(embed=embed)
            return

        from_sv = svAdd(fromID, -add)
        to_sv = svAdd(toID, add)

        embed = discord.Embed(
            title="<:savar:1218331362415870032>SAVAR BANK",
            description=(
                f"**:white_check_mark:以下の通りSavarが移動しました:**\n\n"
                f"from : **<@{fromID}>**\n"
                f"<:savar:1218331362415870032>{from_sv + add:,} ▶ **<:savar:1218331362415870032>{from_sv:,}**\n"
                f"## ⇓ <:savar:1218331362415870032>{add:,} ⇓\n"
                f"to : **<@{toID}>**\n"
                f"<:savar:1218331362415870032>{to_sv - add:,} ▶ **<:savar:1218331362415870032>{to_sv:,}**\n"
            ),
            color=0x0074E1,
        )
        await ctx.send(embed=embed)

        if (
            int(toID) == 1371392422390665236
        ):  # 行き先がsumikaBotなら、両替コマンドを送信
            await ctx.send(f"--hc exchange {fromID} {add}")
        return

    # add - 追加
    elif arg[0] == "add":
        if ctx.author.id != masateo_id:
            return

        if len(arg) != 3:
            embed = discord.Embed(
                title="<:savar:1218331362415870032>SAVAR BANK",
                description="ERROR!",
                color=0x0074E1,
            )
            await ctx.send(embed=embed)
            return

        toID = pickID(arg[1])
        add = int(arg[2])

        to_sv = svAdd(toID, add)

        embed = discord.Embed(
            title="<:savar:1218331362415870032>SAVAR BANK",
            description=(
                f"to : **<@{toID}>**\n"
                f"## + <:savar:1218331362415870032>{add:,}\n"
                f"<:savar:1218331362415870032>{to_sv - add:,} ▶ **<:savar:1218331362415870032>{to_sv:,}**\n"
            ),
            color=0x0074E1,
        )
        await ctx.send(embed=embed)
        return

    # tag - ゲマタグ追加
    elif arg[0] == "tag":
        if len(arg) != 2:
            embed = discord.Embed(
                title="<:savar:1218331362415870032>SAVAR BANK",
                description="ERROR!",
                color=0x0074E1,
            )
            await ctx.send(embed=embed)
            return

        tag = arg[1]
        userID = str(ctx.author.id)

        ws_tag = workbook.worksheet("tag")
        rows = ws_tag.get_all_values()  # 一括取得

        # タグの重複チェック
        for row in rows:
            if len(row) > 0 and row[0] == tag:
                tag_id = row[1] if len(row) > 1 else "不明"
                embed = discord.Embed(
                    title=":memo:GAMER TAG RESISTRATION",
                    description=(
                        f"**:warning:\"{tag}\" はすでに <@{tag_id}> によって登録されています**\n"
                        f"(そんなわけない場合は、Masateoに連絡してください)"
                    ),
                    color=0x0074E1,
                )
                await ctx.send(embed=embed)
                return

        # 追加（append_rowで1回の通信に削減）
        ws_tag.append_row([tag, userID])

        embed = discord.Embed(
            title=":memo:GAMER TAG RESISTRATION",
            description=f":white_check_mark:ゲーマータグを登録しました:\n## <@{userID}> : {tag}",
            color=0x0074E1,
        )
        await ctx.send(embed=embed)


# --- savar CRUD関数（最適化版） ---

ws_savar = workbook.worksheet("savar")

def svCreate(id):
    """新規ユーザー作成（API通信：1回）"""
    user = bot.get_user(int(id))
    user_name = user.name if user else "Unknown"

    # append_row で1行まとめて書き込む（旧: 4回の通信 ➔ 新: 1回）
    ws_savar.append_row([str(id), user_name, 0])


def svRead(id):
    """所持数取得（API通信：1回）"""
    rows = ws_savar.get_all_values()  # 全データを1回で取得

    for row in rows:
        if len(row) > 0 and row[0] == str(id):
            return int(row[2])

    # 見つからない場合は新規作成
    svCreate(id)
    return 0


def svAdd(id, add):
    """Savar加算・減算（API通信：読み1回 ＋ 書き1回）"""
    rows = ws_savar.get_all_values()

    target_row = None
    current_sv = 0

    for idx, row in enumerate(rows):
        if len(row) > 0 and row[0] == str(id):
            target_row = idx + 1  # シートの行番号は1始まり
            current_sv = int(row[2])
            break

    # ユーザーが存在しない場合
    if target_row is None:
        svCreate(id)
        # 新規作成直後は 0 + add
        new_sv = add
        # 追加された最後の行を取得
        target_row = len(rows) + 1
    else:
        new_sv = current_sv + add

    # 金額セルだけを更新（API 1回）
    ws_savar.update_cell(target_row, 3, new_sv)
    return new_sv

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

            gain = random.randint(400,800)
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

        #await rankUpdate(f"<@{ctx.author.id}>", "【一般人】")
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
            #await rankUpdate(f"<@{ctx.author.id}>", f"【{rank_list[level-1]}{"★"*star}】")
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
                #await rankUpdate(f"<@{ctx.author.id}>", f"【{rank_list[level-2]}】")
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
            #await rankUpdate(f"<@{ctx.author.id}>", f"【{rank_list[level-1]}{"★"*star}】")
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
        
        #await rankUpdate(f"<@{ctx.author.id}>", f"【{rank_list[level]}】")

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
        
        #await rankUpdate(f"<@{ctx.author.id}>", f"【{rank_list[level+1]}】")

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
            #await rankUpdate(f"<@{ctx.author.id}>", f"【{rank_list[level-2]}】")
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


# // MARK: slot
@bot.command()
async def slot(ctx, arg: str = "100", target: discord.User = None):
    # 開発者以外には準備中メッセージを表示
    # if ctx.author.id != masateo_id:
    #     embed = discord.Embed(
    #         title=":slot_machine:NEW MASABA SLOT",
    #         description="### 🛠️ UNDER CONSTRUCTION...",
    #         color=0xFFA500,
    #     )
    #     await ctx.send(embed=embed)
    #     return

# ★ 1. 実績表示コマンドはチャンネル制限の前に実行
    if arg.lower() in ["achv", "list", "図鑑"]:
        # 閲覧対象ユーザーの決定
        if target and target != ctx.author:
            # サーバー主または開発者(masateo_id)のみ許可
            is_owner = ctx.guild and (ctx.author.id == ctx.guild.owner_id)
            is_dev = ctx.author.id == masateo_id
            
            if not (is_owner or is_dev):
                await ctx.send("❌ 他人の実績を閲覧できるのはサーバー主のみです。")
                return
            target_user = target
        else:
            target_user = ctx.author

        unlocked = user_achievements.get(target_user.id, set())

        # 【デバッグ用】コンソールにデータ差分を出力して原因特定
        all_pattern_ids = set(p[0] for p in f_slot.WINNING_PATTERNS)
        invalid_ids = unlocked - all_pattern_ids

        print(f"=== [DEBUG] {target_user.display_name} (ID:{target_user.id}) ===")
        print(f"・メモリ上の実績数: {len(unlocked)} 個")
        if invalid_ids:
            print(f"⚠️ WINNING_PATTERNS に存在しないID ({len(invalid_ids)}個): {invalid_ids}")
        print("==========================================")

        # SlotAchvView に対象ユーザーを渡して Embed 生成
        view = SlotAchvView(target_user, unlocked)
        await ctx.send(embed=view.create_embed(), view=view)
        return

    # ★ 2. スロット専用チャンネルチェック (通常のスロットプレイ時のみ適用)
    SLOT_CHANNEL_ID = 1540964066045206599  # Dedicated channel ID

    if ctx.channel.id != SLOT_CHANNEL_ID and ctx.author.id != masateo_id:
        embed = discord.Embed(
            title=":slot_machine:NEW MASABA SLOT",
            description=f"## :x: ここでは回せません\n<#{SLOT_CHANNEL_ID}> へ",
            color=0xFFA500
        )
        await ctx.send(embed=embed)
        return

    # --- 実績表示コマンド: !!slot achv ---
    if arg.lower() in ["achv", "list"]:
        unlocked = user_achievements.get(ctx.author.id, set())
        view = SlotAchvView(ctx.author, unlocked)
        await ctx.send(embed=view.create_embed(), view=view)
        return

# --- メッセージ整形用ローカル関数 ---
    def build_slot_result(p_id, res, payout_rate, title, rarity, bet):
        gain = int(bet * payout_rate)
        delta = gain - bet
        now_sv = svAdd(ctx.author.id, delta)
        slot_display = "".join(res)

        # A. 何らかの役が成立した場合 (p_id が存在する)
        if p_id is not None:
            is_new = save_achievement(ctx.author.id, ctx.author.name, p_id)
            new_tag = ":new:" if is_new else ""

            # 1. 1倍以上の勝ち（等倍以上）
            if payout_rate >= 1:
                msg = (
                    f"# {slot_display}\n"
                    f"### [{rarity}] {title} {new_tag}\n"
                    f"(+{payout_rate}倍)\n\n"
                    f"**🎉 WIN! +<:savar:1218331362415870032>{gain:,}**"
                )
                color = 0xFFD700  # ゴールド

            # 2. 0倍〜1未満の微妙な当たり (元本割れ・0倍など)
            elif payout_rate >= 0:
                msg = (
                    f"# {slot_display}\n"
                    f"### [{rarity}] {title} {new_tag}\n"
                    f"({payout_rate}倍)\n\n"
                    f"**🤔 WIN? +<:savar:1218331362415870032>{gain:,}**"
                )
                color = 0xE67E22  # オレンジ (微妙な当たり感演出)

            # 3. 特大ハズレ・没収 (マイナス配当)
            else:
                loss_amount = abs(gain)
                msg = (
                    f"# {slot_display}\n"
                    f"### [{rarity}] {title} {new_tag}\n"
                    f"({payout_rate}倍)\n\n"
                    f"**💀 LOSE! -<:savar:1218331362415870032>{loss_amount:,}**"
                )
                color = 0x7400B0  # 紫

        # B. 完全に役が揃わなかった通常ハズレ (p_id が None)
        else:
            msg = f"# {slot_display}\nｻﾞﾝﾈﾝ\n"
            color = 0x808080  # グレー

        return msg, color, now_sv

    # --- 鯖主限定: 特定IDの出目を直接召喚 (例: !!slot p1 や !!slot p15) ---
    if ctx.author.id == masateo_id and arg.lower().startswith("p") and arg[1:].isdigit():
        target_id = int(arg[1:])
        pattern = f_slot.get_pattern(target_id)

        if not pattern:
            await ctx.send(f"**:x: パターンID `{target_id}` は存在しません**")
            return

        p_id, res, payout_rate, title, rarity = pattern
        bet = 100  # デバッグ時の仮賭け金 (100 Savar)

        msg, color, now_sv = build_slot_result(
            p_id, res, payout_rate, title, rarity, bet
        )

        embed = discord.Embed(
            title=":slot_machine:SAVAR SLOT [DEBUG]",
            description=f"{msg}\n\nTOTAL ▶ <:savar:1218331362415870032>{now_sv:,}",
            color=color,
        )
        embed.set_author(
            name=f"{ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )
        await ctx.send(embed=embed)

            # ★ USR当選時のみメンション文字列を設定
        if rarity == "USR":
            await ctx.send(f"# <@{masateo_id}> おいヤバいぞ")
        return

    # --- 通常の賭け金（数値）チェック ---
    if not arg.isdigit():
        embed = discord.Embed(
            title=":slot_machine:NEW MASABA SLOT",
            description="**:x: BET額を指定する場合は、数字のみで入力してください**\n(例: `!!slot 300` )",
            color=0xFFA500,
        )
        embed.set_author(
                    name=f"{ctx.author.display_name}",
                    icon_url=ctx.author.display_avatar.url
                )
        await ctx.send(embed=embed)
        return

    bet = int(arg)

    # BET額の上限・下限チェック (100 ~ 500)
    MIN_BET = 100
    MAX_BET = 500

# 賭け金の下限チェック
    if bet < MIN_BET:
        embed = discord.Embed(
            title=":slot_machine:NEW MASABA SLOT",
            description=f"## :x: 賭け金が小さすぎます\n<:savar:1218331362415870032>{MIN_BET:,} 以上に指定してください",
            color=0xFFA500,
        )
        embed.set_author(
                    name=f"{ctx.author.display_name}",
                    icon_url=ctx.author.display_avatar.url
                )
        await ctx.send(embed=embed)
        return

    # 賭け金の上限チェック
    if bet > MAX_BET:
        embed = discord.Embed(
            title=":slot_machine:NEW MASABA SLOT",
            description=f"## :x: 賭け金が大きすぎます\n上限は <:savar:1218331362415870032>{MAX_BET:,} までです",
            color=0xFFA500,
        )
        embed.set_author(
                    name=f"{ctx.author.display_name}",
                    icon_url=ctx.author.display_avatar.url
                )
        await ctx.send(embed=embed)
        return

    # 所持金チェック
    user_sv = svRead(ctx.author.id)
    if user_sv < bet:
        embed = discord.Embed(
            title=":slot_machine:NEW MASABA SLOT",
            description="## :x: Savarが足りませ～ん",
            color=0xFFA500,
        )
        embed.set_author(
                    name=f"{ctx.author.display_name}",
                    icon_url=ctx.author.display_avatar.url
                )
        await ctx.send(embed=embed)
        return

    # スロット実行
    p_id, res, payout_rate, title, rarity = f_slot.spin()

    msg, color, now_sv = build_slot_result(
        p_id, res, payout_rate, title, rarity, bet
    )

    embed = discord.Embed(
        title=":slot_machine:NEW MASABA SLOT",
        description=f"{msg}\n\nTOTAL ▶ <:savar:1218331362415870032>{now_sv:,}",
        color=color,
    )
    embed.set_author(
                name=f"{ctx.author.display_name}",
                icon_url=ctx.author.display_avatar.url
            )
    await ctx.send(embed=embed)

    # ★ USR当選時のみメンション文字列を設定
    if rarity == "USR":
        await ctx.send(f"# <@{masateo_id}> おいヤバいぞ")

@bot.command(name="slot_reload")
async def slot_reload(ctx):
    if ctx.author.id != masateo_id: return

    try:
        load_achievements()  # 既存の読み込み関数を再実行
        embed = discord.Embed(
            title=":gear: SLOT SYSTEM RELOAD",
            description="スプシの情報をリロードしますた",
            color=0x00FF00
        )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ {e}")

# // MARK: test
# !!login_listreset
@bot.command()
async def login_reset(ctx):
    worksheet = workbook.worksheet("login")
    worksheet.batch_clear(["A:B"])

    embed = discord.Embed(title=":gear:DEBUG: LOGIN RESET",
                        description=f"ログインボーナスの取得状況をリセットしました\n"
                        f"(実行者: <@{ctx.author.id}>)",
                        color=0xdddddd)
        
    await ctx.send(embed=embed)

#test~
# @bot.command()
# async def dbTest(ctx):
#     channel = bot.get_channel(1289170232782622751) #datebase
#     embed = discord.Embed(title=":hut:CHINCHIRO DOJO: RANK LIST", 
#             description=f"**【五段】 <@159985870458322944>**\n"
#                         f"**【四段】 <@235148962103951360>**\n"
#                         f"**【一般人】 <@414755451419230208>**",
#                 color=0xee3700)
#     await channel.send(f"**【名人二段】 <@610826378971185152>**\n"
#                         f"**【七段】 <@1001800888001773588>**\n"
#                         f"**【六段★】 <@836563535722446850>**\n"
#                         f"**【四段★★】 <@778974168410226708>**\n"
#                         f"**【四段★】 <@699110927957622804>**\n"
#                         f"**【四段】 <@398044353207205892>**\n"
#                         f"**【一般人★★】 <@515090484889255938>**\n")

# @bot.command()
# async def dbTest2(ctx,*arg):
#     await rankUpdate(arg[0],arg[1])
    # embed = discord.Embed(title=f":birthday:BIRTHDAY REMINDER",
    #                description=
    #                f"## 2024/09/28\n# <@562955628268486696>\n# :confetti_ball:HAPPY 19th BIRTHDAY!!:tada:",
    #                color=0xff6000)
    #channel = bot.get_channel(1133837604991811665) #ノーマル雑談
    #await channel.send(embed=embed)
    

# @bot.command()
# async def dbTest3(ctx):
#     ch_test = bot.get_channel(1329405973588086826)

#     embed = embed_3ch()
#     await ch_test.send(embed=embed)



#test~
# @bot.command()
# async def talkToNormal(ctx):
#     ws_reply = workbook.worksheet("reply")
#     meisi_list = ws_reply.col_values(2)
#     randomRep_dic = ws_reply.col_values(3)
#     randomRep_dic2 = ws_reply.col_values(4)
#     reply = f_reply.randomSay(meisi_list, randomRep_dic, randomRep_dic2)
#     channel = bot.get_channel(1133837604991811665) #ノーマル雑談
#     await channel.send(reply)



# // MARK: on_message
#特定のメッセージに反応する
@bot.event
async def on_message(message):
    # print(f"on_message受信: {message.content} [from {message.author}, bot={message.author.bot}]")
    
    # 外様IDたち
    sumika_id = 1371392422390665236
    masabasaba_id = 1287447200611176500
    ALLOWED_BOT_IDS = [sumika_id, masabasaba_id]

    # 自分の発言は無視
    if message.author.id == bot.user.id:
        return
    # Botだったとき、そのBotは許可対象でないなら無視
    if message.author.bot and message.author.id not in ALLOWED_BOT_IDS:
        print(f"❌ 許可されてないBotのメッセージなのでスキップ: {message.author}")
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
    if message.author.id == 1287447200611176500: #MasabaServerBotのID
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
    chinkoes = ["ちんこ","chinko","tinko","チンコ","ﾁﾝｺ",
                "ちーんこ","チーンコ","ﾁｰﾝｺ","ちんーこ","チンーコ","ﾁﾝｰｺ",
                "ち～んこ","チ～ンコ",
                "ちんぽ","chimpo","chinpo","tinpo","チンポ",
                "ちーんぽ","チーンポ","ﾁｰﾝﾎﾟ","ちんーぽ","チンーポ","ﾁﾝｰﾎﾟ",
                "ちん～ぽ","チン～ポ",
                "ﾁﾝﾁﾝ","ちんちん","chinchin","tintin","チンチン","ﾁﾝﾁﾝ",
                "珍棒","珍珍","ちんぼう","チンボウ",
                "ぽこちん","pokochin","pokotin","ポコチン","ﾎﾟｺﾁﾝ",
                "肉棒","陰茎","ぺにす","ペニス","ﾍﾟﾆｽ",
                "マラ","ﾏﾗ","魔羅","penis",
                "てぃんてぃん","ティンティン","ティムポ","ちーんこ","チーンコ",
                "男根","いちもつ","イチモツ","ｲﾁﾓﾂ","ファルス"]
    if message.content.lower() in chinkoes or any(s in message.content.lower() for s in chinkoes):
        chinkoEmoji = "<:chinko:1134001412695674891>"
        await message.add_reaction(chinkoEmoji)


    # 4 : 3日チャンネル案追加
    if message.channel.id == 1329405973588086826: # の、案　のID
        if message.content.startswith("【") and message.content.endswith("】"):
            an = message.content.strip("【】")
            ws_3ch = workbook.worksheet("3ch")
            an_list = ws_3ch.col_values(1)

            ws_3ch.update_cell(len(an_list)+1, 1, an)
    
    # 5 : shovel系の勘違いに対して
    if message.content.startswith(("!!sh ","!!shg ","!!shr ","!!shc ","!!shm ","!!shy ")):
        await message.channel.send("たぶん、ビックリマークがいっこ多いぞ")

    # await bot.process_commands(message)

    # ↑これいったんナシで　以下、ctxから無理やり実行するやつ
    ctx = await bot.get_context(message)
    
    if ctx.valid:
        # print(f"[ctx.valid] コマンド: {ctx.command} 実行者: {ctx.author}")
        await bot.invoke(ctx)


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

# コマンド呼び出し確認用
@bot.event
async def on_command(ctx):
    print(f"[on_command] 実行されたコマンド: {ctx.command}, by: {ctx.author} [bot={ctx.author.bot}]")




# -------------------------------------------------------------------------------------------

# // MARK: on_command_error
@bot.event
async def on_command_error(ctx, error):
    print(f"[ERROR] コマンドエラー: {error}")

    # 1. コマンドが存在しない場合
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title=":question:UNKNOWN COMMAND",
            description="# そんなコマンドはない",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
        return

    # 2. コマンド実行中にエラーが発生した場合
    if isinstance(error, commands.CommandInvokeError):
        original = error.original

        # A. Google Sheets APIの制限 (429 / Quota exceeded) を検知
        if isinstance(original, gspread.exceptions.APIError):
            if original.response.status_code == 429 or "Quota exceeded" in str(original):
                embed = discord.Embed(
                    title="⚠️ API LIMIT!",
                    description="## APIの制限に達しました\nスマン！botの使いすぎというやつです\nちょっと待ってからでヨロピ",
                    color=0xc00000
                )
                try:
                    await ctx.send(embed=embed)
                except Exception:
                    pass
                return

        # B. Discord APIの制限 (HTTP 429) を検知
        if isinstance(original, discord.HTTPException) and original.status == 429:
            embed = discord.Embed(
                title="⚠️ DISCORD RATE LIMIT",
                description="## Discordの通信制限が発生しました\n短期間に送信しまくりすぎたのかもしれません\nおちついて♡",
                color=0xc00000
            )
            try:
                await ctx.send(embed=embed)
            except Exception:
                pass
            return

    # 3. その他の予期せぬエラーはそのまま出力
    raise error



# 日本時間（JST）の深夜0:00:00を定義
JST = datetime.timezone(datetime.timedelta(hours=9))
MIDNIGHT = datetime.time(hour=0, minute=0, second=0, tzinfo=JST)


# // MARK: 0:00_loop
@tasks.loop(time=MIDNIGHT)
async def daily_reset_task():
    try:
        dt_now = datetime.datetime.now(JST)
        todate = dt_now.strftime("%Y/%m/%d")
        today_mmdd = dt_now.strftime("%m%d")
        toyear = dt_now.year

        ch_test = bot.get_channel(ch_test_id)
        ch_normal = bot.get_channel(1133837604991811665)  # ノーマル雑談
        ch_an = bot.get_channel(1329405973588086826)  # の、案

        print(f"[00:00 EVENT] {todate} の更新処理を開始します")

        # 1. login reset
        if ch_test:
            await ch_test.send(f"{todate}こうしんおっけー！！")
        ws_login = workbook.worksheet("login")
        ws_login.batch_clear(["A:B"])

        # 2. birthday (get_all_values で一括取得してAPI制限を回避)
        ws_birth = workbook.worksheet("birth")
        all_birth_rows = ws_birth.get_all_values()

        for row in all_birth_rows:
            if len(row) < 3:
                continue
            birth_userid = row[0]  # 1列目: UserID
            b_date_str = row[2]  # 3列目: YYYYMMDD

            if today_mmdd == b_date_str[-4:]:
                birth_year = b_date_str[:4]

                if birth_year == "0000":
                    embed = discord.Embed(
                        title=":birthday:BIRTHDAY REMINDER",
                        description=(
                            f"## {todate}\n# <@{birth_userid}>\n# "
                            ":confetti_ball:HAPPY BIRTHDAY!!:tada:"
                        ),
                        color=0xFF6000,
                    )
                else:
                    age = toyear - int(birth_year)
                    embed = discord.Embed(
                        title=":birthday:BIRTHDAY REMINDER",
                        description=(
                            f"## {todate}\n# <@{birth_userid}>\n# "
                            f":confetti_ball:HAPPY {addJosu(age)} BIRTHDAY!!:tada:"
                        ),
                        color=0xFF6000,
                    )

                if ch_normal:
                    await ch_normal.send(embed=embed)

        # 3. 3days chat
        ws_3ch = workbook.worksheet("3ch")
        flag_3ch = ws_3ch.acell("D1").value

        if flag_3ch == "DERU":
            embed = embed_3ch()
            if ch_an:
                await ch_an.send(embed=embed)
            ws_3ch.update_acell("D1", "DENAI2")
        elif flag_3ch == "DENAI2":
            ws_3ch.update_acell("D1", "DENAI1")
        elif flag_3ch == "DENAI1":
            ws_3ch.update_acell("D1", "DERU")

    except Exception as e:
        print(f"0時更新処理 エラー発生: {e}")


# // MARK: 10sec_loop
@tasks.loop(seconds=10)
async def random_talk_task():
    if random.randrange(50000) == 0:
        try:
            ch_normal = bot.get_channel(1133837604991811665)
            ws_reply = workbook.worksheet("reply")
            meisi_list = ws_reply.col_values(2)
            randomRep_dic = ws_reply.col_values(3)
            randomRep_dic2 = ws_reply.col_values(4)
            reply = f_reply.randomSay(
                meisi_list, randomRep_dic, randomRep_dic2
            )

            if ch_normal:
                await ch_normal.send(reply)
        except Exception as e:
            print(f"突然喋る エラー: {e}")

# 3日チャンネル抽選用
def embed_3ch():
    ws_3ch = workbook.worksheet("3ch")
    an_list = ws_3ch.col_values(1)  # A列を取得
    b_list = ws_3ch.col_values(2)  # B列を取得
    backNo = ws_3ch.acell("B1").value

    # B2以降（インデックス1以降）に "this" が存在するか確認
    if len(b_list) > 1 and "this" in b_list[1:]:
        # 2行目以降で最初に "this" がある行番号（1始まり）を取得
        choice_row = b_list.index("this", 1) + 1
    else:
        # "this" がない場合は従来通りランダム抽出
        choice_row = random.randint(2, len(an_list))

    # 取得済みの A列リストからタイトルを取得（API呼び出しの削減）
    title = an_list[choice_row - 1]

    embed = discord.Embed(
        title=":three:3 DAYS TEXT CHANNEL",
        description=f"# #{backNo}『{title}』",
        color=0x1E90FF,
    )

    ws_3ch.update_acell("B1", int(backNo) + 1)
    ws_3ch.delete_rows(choice_row)  # 該当行を削除

    return embed

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)