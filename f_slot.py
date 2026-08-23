import random

# 絵文字の定義
E_SEVEN = "<:seven_sp:1150817444894617640>"
E_CHINKO = "<:chinko:1134001412695674891>"
E_OGNK = "<:ognk:1133854076182986793>"
E_DEKA = "<:deka:1134020757983330304>"
E_ERO = "<:ero:1133855884540383333>"
E_KANSYA = "<:kansya:1134217544937508955>"
E_YOU = "<:you:1134512789340291142>"
E_A = "<:a_:1134523410584698900>"
E_E = "<:e_:1134422095330279444>"
E_NN = "<:n_:1135530206661197984>"
E_HA = "<:ha:1152244906547494933>"
E_OWARI = "<:owari:1136232461542633504>"
E_SEI = "<:sei:1133968046915076116>"
E_SI = "<:si:1133966404001996881>"
E_SOU = "<:sou:1133969434793492510>"
E_UTSU = "<:utsu:1133951952754057246>"
E_II = "<:ii:1134043430289416243>"
E_KUSA = "<:kusa:1134039196391182448>"
E_WIN = "<:win:1135077422824427562>"
E_OGNK_YOKO = "<:ognk_yoko:1134506538325778593>"
E_HATENA = "<:question:1149724448405065809>"
E_AJI = "<:aji:1133981540842479629>"
E_SHINGI = "<:shingi:1135535797785874453>"
E_SUMAN = "<:suman:1134611029003862169>"
E_5000 = "<:gosen:1152534375448199239>"
E_CHOEN = "<:tyoen:1152534407140343818>"
E_HOSHI = "<:hoshii:1152179242617020447>"
E_RT = "<:retweet:1150065394699223101>"
E_WARA = "<:wara:1133856183443259432>"
E_DICE1 = "<:dice_1:1278521756176613428>"
E_DICE2 = "<:dice_2:1278521805279330394>"
E_DICE3 = "<:dice_3:1278521883142389880>"
E_DICE4 = "<:dice_4:1278521923139145818>"
E_DICE5 = "<:dice_5:1278521957935218708>"
E_DICE6 = "<:dice_6:1278521991791640639>"
E_AKIYAMA = "<:Akiyama:1396571856932438047>"
E_PIPE = "<:pipeline_punch:1171463822750515230>"
E_SUKKIRI = "<:sukkiri:1133966569106575361>"
E_SAMBO = "<:sambo:1379177841484103830>"
E_NEDU = "<:nedu:1141406784746180678>"
E_HIGH = "<:high_level:1221782684242542653>"
E_REIWA = "<:reiwa_roman:1379179260601700372>"
E_OI = "<:oi:1155008695516803253>"
E_NOGNK = "<:nognk:1168519628440477766>"
E_UKETSU = "<:uketsu:1379181302493745292>"
E_LOGO = "<:masaba_logo:1152542177470193774>"
E_MASABA = "<:masaba:1133967448853450832>"
E_AHO = "<:aho:1168437457969229824>"
E_KAMI = "<:kami:1161339802340298793>"
E_BABA = "<:baba:1134513176210317382>"
E_IS = "<:is:1134512504844849162>"
E_NE = "<:ne:1336286119599538196>"
E_OGNK_L = "<:ognk_l:1161359198408429650>"
E_OGNK_R = "<:ognk_r:1161359236375261214>"
E_SANSEN = "<:sansen:1161337784569692393>"
E_TAI = "<:tai:1204746447988457472>"
E_HO = "<:ho:1204746491541856266>"
E_AA = "<:aa:1344751685578526730>"
E_HAA = "<:haa:1344750841000628305>"
E_K = "<:K_:1154137051655045253>"
E_O = "<:O_:1154137054536548352>"
E_N = "<:N_:1154137056092622979>"  # ※小文字のn_と被るため _1 を付与しています
E_G = "<:G_:1154137058957332590>"
E_SHAPEZ1 = "<:Shapez:1257333654317699072>"
E_SHAPEZ2 = "<:blueprint:1257691511429136475>"
E_SHAPEZ3 = "<:nankadaijinayatu:1257703168461246640>"
E_BAKARI = "<:bakarizumu:1204460557676187751>"
E_TABAKO = "<:TOBACCO:1262397030207328398>"
E_KUSURI = "<:kusuri:1379178130777833554>"
E_SAKE = "<:alcohol:1161352654899925104>"
E_SAVAR = "<:savar:1218331362415870032>"
E_MASATEO = "<:msto:1149730665076637776>"
E_7 = "7 "
E_HAMSA = ":hamsa:"
E_EYE = ":eye:"
E_GAMING = "<a:gaming:1231223018043347044>"
BLANK = "　　"
U3000 = "ㅤ"

WIN_RATE = 0.35

# 重みの合計が 100 になるように設定
RARITY_WEIGHTS = {
    "USR": 0.1,  # 当たり1,000回に1回の幻枠 (0.1%)
    "SSR": 1.0,  # 激レア (2.0%)
    "SR": 12.0,  # 中当り (10.9%)
    "R": 40.0,  # 小当り・主軸 (37.0%)
    "N": 46.9,  # 元返し系 (50.0%)
}

# 1. 当たりの目リスト（絵文字の個数は1個でも4個でも可変！）
WINNING_PATTERNS = [
    ("seven_3", (E_SEVEN, E_SEVEN, E_SEVEN), 3, "シンプル大当たり:bangbang:", "R"),
    ("chinko_3", (E_CHINKO, E_CHINKO, E_CHINKO), 3, "大ちんこ祭り 開幕:bangbang:", "R"),
    ("ognk_3", (E_OGNK, E_OGNK, E_OGNK), 5, "オーガニック", "R"),
    ("deka_3", (E_DEKA, E_DEKA, E_DEKA), 4, "クソデカ大当たり:bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang:", "R"),
    ("ero_3", (E_ERO, E_ERO, E_ERO), 3, "ドスケベ", "R"),
    ("kansya_3", (E_KANSYA, E_KANSYA, E_KANSYA), 3, ":sparkles:大感謝祭:sparkles:", "R"),
    ("you_3", (E_YOU, E_YOU, E_YOU), 1.7, "お前お前お前:bangbang::bangbang::bangbang::index_pointing_at_the_viewer::index_pointing_at_the_viewer::index_pointing_at_the_viewer::index_pointing_at_the_viewer::index_pointing_at_the_viewer::index_pointing_at_the_viewer:", "R"),
    ("a_3", (E_A, E_A, E_A), 1.7, "ああああああああああああああ:bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang:", "R"),
    ("e_3", (E_E, E_E, E_E), 1.7, "えええええええええええええ:interrobang::interrobang::interrobang::interrobang::interrobang::interrobang::interrobang::interrobang::interrobang::interrobang::interrobang::interrobang::interrobang:", "R"),
    ("n_3", (E_NN, E_NN, E_NN), 1.2, "ウンコがでない:sob:", "R"),
    ("ha_3", (E_HA, E_HA, E_HA), 1.2, "(乾いた笑い)", "R"),
    ("owari_3", (E_OWARI, E_OWARI, E_OWARI), 1, "終　　了", "R"),
    ("sei_3", (E_SEI, E_SEI, E_SEI), 3, "イキスギ", "R"),
    ("si_3", (E_SI, E_SI, E_SI), 0.4, "ドカ死", "R"),
    ("sou_3", (E_SOU, E_SOU, E_SOU), 5, "人生最高ウルトラハッピー:sparkles:", "R"),
    ("utsu_3", (E_UTSU, E_UTSU, E_UTSU), 1, "架空の通貨を支払ってこんなスロット回して一体何が得られるというのだろうね", "R"),
    ("ii_3", (E_II, E_II, E_II), 3, "良すぎます", "R"),
    ("kusa_3", (E_KUSA, E_KUSA, E_KUSA), 3, "大　草　原　不　可　避", "R"),
    ("win_3", (E_WIN, E_WIN, E_WIN), 3, "優勝:bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang:", "R"),
    ("ognk_yoko_3", (E_OGNK_YOKO, E_OGNK_YOKO, E_OGNK_YOKO), 1.5, "それは…今年も、CMの後です！", "R"),
    ("hatena_3", (E_HATENA, E_HATENA, E_HATENA), 1.5, "？", "R"),
    ("aji_3", (E_AJI, E_AJI, E_AJI), 3, "満天☆青空レストラン", "R"),
    ("shingi_3", (E_SHINGI, E_SHINGI, E_SHINGI), 1.2, "大当たり……？", "R"),
    ("suman_3", (E_SUMAN, E_SUMAN, E_SUMAN), 1.3, "この度は誠に申し訳ありませんでした", "R"),
    ("5000_3", (E_5000, E_5000, E_5000), 5, "五千億五千万五千", "R"),
    ("choen_3", (E_CHOEN, E_CHOEN, E_CHOEN), 3, "バカ大金持ち", "R"),
    ("hoshi_3", (E_HOSHI, E_HOSHI, E_HOSHI), 2, "貪欲", "R"),
    ("rt_3", (E_RT, E_RT, E_RT), 3, "300億RP　鬼 バ ズ 達 成", "R"),
    ("wara_3", (E_WARA, E_WARA, E_WARA), 1.5, "うおw", "R"),
    ("dice1_3", (E_DICE1, E_DICE1, E_DICE1), 5, ":fire: ピンゾロ :fire:", "R"),
    ("akiyama_3", (E_AKIYAMA, E_AKIYAMA, E_AKIYAMA), 7, "ライアーゲーム事務局　倒産", "SR"),
    ("pipe_3", (E_PIPE, E_PIPE, E_PIPE), 7, "*Unleash The Beast!*", "SR"),
    ("sukkiri_3", (E_SUKKIRI, E_SUKKIRI, E_SUKKIRI), 7, "IQ15000", "SR"),
    ("seven_normal_3", (E_7, E_7, E_7), 1.5, "大当たり(無料版)", "SR"),
    ("sambo_3", (E_SAMBO, E_SAMBO, E_SAMBO), 8, "俺はね:bangbang:この真鯖にいる人たちにね:bangbang:どうしても伝えたいワケですよ:bangbang:何が大事かを歌いたいワケですよ:bangbang:行きますよ:bangbang:行きますよ:bangbang:世　界　は　そ　れ　を　愛　と　呼　ぶ　ん　だ　ぜ", "SR"),
    ("nedu_3", (E_NEDU, E_NEDU, E_NEDU), 7, "整 い ま く り ま し た", "SR"),
    ("high_3", (E_HIGH, E_HIGH, E_HIGH), 7, "かなりサイコーでーす！", "SR"),
    ("reiwa_3", (E_REIWA, E_REIWA, E_REIWA), 7, "令和ロマン V3達成", "SR"),
    ("hamsa_3", (E_HAMSA, E_HAMSA, E_HAMSA), 6, ":hamsa::hamsa::hamsa::hamsa::hamsa::hamsa::hamsa::hamsa::hamsa::hamsa::hamsa:", "SR"),
    ("oi_3", (E_OI, E_OI, E_OI), 3, "死ぬわアイツ", "SR"),
    ("nognk_3", (E_NOGNK, E_NOGNK, E_NOGNK), 0, "SCP-240-JP 0匹のオーガニック", "SR"),
    ("uketsu_3", (E_UKETSU, E_UKETSU, E_UKETSU), 5, "人間ぶっ殺しゾーン", "SR"),
    ("logo_3", (E_LOGO, E_LOGO, E_LOGO), 20, ":sparkles::sparkles::sparkles: 真鯖大当たり :sparkles::sparkles::sparkles:", "SSR"),
    ("masaba_3", (E_MASABA, E_MASABA, E_MASABA), 5, "鮮魚コーナー", "SR"),
    ("aho_3", (E_AHO, E_AHO, E_AHO), 5, "ﾎﾟェ！^^", "SR"),
    ("kami_3", (E_KAMI, E_KAMI, E_KAMI), 30, "*G O D*", "SSR"),
    ("babaisyou", (E_BABA, E_IS, E_YOU), 1.7, "BABA IS YOU", "R"),
    ("babaisognk", (E_BABA, E_IS, E_OGNK), 0.7, "違います", "N"),
    ("babaiswin", (E_BABA, E_IS, E_WIN), 2, ":sparkles:CONGRATURATIONS!", "R"),
    ("aen", (E_A, E_E, E_NN), 1.6, "亜鉛(元素記号:Zn / 原子番号:30 / 融点:419.5℃ / 沸点:907℃ / 原子量:65.38u / 電子配置:[Ar]3d_10 4s_2)", "R"),
    ("ahan", (E_A, E_HA, E_NN), 1.2, "「イマ」というほうき星 君と二人追いかけてた Oh Yeah", "N"),
    ("nehan", (E_NE, E_HA, E_NN), 1.2, ":pray::lotus: 涅槃 :lotus::pray:", "N"),
    ("dekachin", (E_DEKA, E_DEKA, E_CHINKO), 1.2, "ドデカマラ:bangbang:", "N"),
    ("dekachinkansya", (E_DEKA, E_CHINKO, E_KANSYA), 1.2, "デカいちんこに感謝を", "N"),
    ("bkb", (E_BABA, E_KUSA, E_BABA), 1.1, "BKB ヒィヤ", "N"),
    ("nama_an", (E_SEI, E_A, E_NN), 1.5, " :tea::beans: 生あん :beans::tea:", "R"),
    ("zeppinchinko", (E_II, E_CHINKO, E_AJI), 1.8, ":sparkles:絶品ちんぽ:sparkles:", "R"),
    ("kusahae", (E_KUSA, E_SEI, E_E), 1.2, "wwwwwwwwwwwwwwwwwww", "N"),
    ("sisou", (E_SI, E_IS, E_SOU), 0.7, "思想ヤバすぎる", "N"),
    ("syusin", (E_OWARI, E_SI, E_NN), 1.1, "就寝:zzz:", "N"),
    ("sou_utsu", (E_SOU, E_UTSU, E_SOU), 1, "躁鬱オセロ", "N"),
    ("og_kansya", (E_OGNK, E_OGNK_YOKO, E_KANSYA), 1.5, "感謝できてえらい", "N"),
    ("og_suman", (E_OGNK, E_OGNK_YOKO, E_SUMAN), 1.5, "謝れてえらい", "N"),
    ("og_a", (E_OGNK, E_A, E_HATENA), 0.5, "キレちゃった", "N"),
    ("og_e", (E_OGNK, E_E, E_HATENA), 0.7, "難聴", "N"),
    ("og_n", (E_OGNK, E_NN, E_HATENA), 1.3, "何かに気付いた――", "N"),
    ("og_iie", (E_OGNK, E_II, E_E), 0.7, "違うらしい", "N"),
    ("og_roll", (E_OGNK, E_OGNK_YOKO, E_RT), 2, "ローリンガール / Wowaka", "R"),
    ("og_utsu", (E_OGNK_YOKO, E_UTSU, E_UTSU), 1.5, "がんばって……(オーガニックさんを、応援してあげよう)", "R"),
    ("og_kami", (E_OGNK, E_HA, E_KAMI), 2, "そうかも", "R"),
    ("og_sansen", (E_OGNK_L, E_OGNK_R, E_SANSEN), 7, "オーガニック 参戦！", "SR"),
    ("og_taiho", (E_TAI, E_OGNK, E_HO), 5, "オーガニック　逮捕", "SR"),
    ("og_tanpin", (E_OGNK,), 5, "オーガニック(単品)", "SR"),
    ("og_long", (E_OGNK_L, E_OGNK_R, E_OGNK_L, E_OGNK_R, E_OGNK_L, E_OGNK_R), 10, "LONGオーガニック", "SR"),
    ("og_kango", (E_OGNK_L, BLANK, E_OGNK_R), 5, "勘合貿易", "SR"),
    ("og_gaming", (E_GAMING, E_GAMING, E_GAMING), 50, "*C R A Z Y　O G A N I C　F E V E R*", "SSR"),
    ("reach", (E_SEVEN, E_HATENA, E_SEVEN), 1, ":fire: リーチ:bangbang: :fire:", "N"),
    ("5000choen_hoshi", (E_5000, E_CHOEN, E_HOSHI), 2.5, "5000兆円 欲しい！", "R"),
    ("7choen_hoshi", (E_SEVEN, E_CHOEN, E_HOSHI), 1.2, "やや控えめ", "N"),
    ("77choen", (E_SEVEN, E_SEVEN, E_CHOEN), 1.2, "77兆円(日本国家予算の68%)", "N"),
    ("domoto", (E_5000, E_CHOEN, E_WIN), 3, "胴元殺し", "N"),
    ("higuchi", (E_5000, E_E, E_NN), 1.5, "津田梅子", "N"),
    ("iichinko", (E_II, E_CHINKO, E_HOSHI), 1.2, "わかる", "N"),
    ("hifumi", (E_DICE1, E_DICE2, E_DICE3), -2, "ヒフミ", "R"),
    ("shigoro", (E_DICE4, E_DICE5, E_DICE6), 2, "シゴロ", "R"),
    ("nana_aa", (E_AA, E_A, E_A), 1.5, "僕が、ななまがりの面白いほうで、", "R"),
    ("nana_haa", (E_HAA, E_HA, E_A), 3, "こいつが、超面白いほうです", "R"),
    ("kong", (E_K, E_O, E_N, E_G), 2, "Kステージ 解放:bangbang:", "R"),
    ("ong", (E_O, E_N, E_G), 2.5, "【ﾃﾚﾚﾚﾚﾚﾚﾚ､ZIP!のリズムで言える】ジュジュジュジュジュジュジュディ・", "R"),
    ("uoooo", (E_II, E_SOU, E_CHINKO), 3, "ウオオオオオオオオオオオ最高最高最高最高最高最高最高最高イクイクイクイクイクイクイクイク:bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang::bangbang:", "R"),
    ("shapez", (E_SHAPEZ1, E_SHAPEZ2, E_SHAPEZ3), 1.5, "shapez", "N"),
    ("happy", (E_BAKARI, E_HAA, E_REIWA), 1.5, "みんなたのしそう", "N"),
    ("toyoko", (E_TABAKO, E_KUSURI, E_SAKE), 0.5, "トー横", "N"),
    ("eron", (E_SAVAR, E_5000, E_5000), 3, "イーロン・マスク", "R"),
    ("eye", (U3000, BLANK, BLANK, E_EYE), 1, "　　み　つ け         た", "SR"),
    ("syuen", (E_OWARI, E_E, E_NN), 0.5, "♰ 終 焉(アポカリプス) ♰", "N"),
    ("hitomania", (E_A, E_A, E_SUMAN, E_NE), 1, "人マニア / 原口沙輔", "N"),
    ("pinzoro_10", (E_DICE1,E_DICE1,E_DICE1,E_DICE1,E_DICE1,E_DICE1,E_DICE1,E_DICE1,E_DICE1,E_DICE1), 100, "ス ー パ ー ウ ル ト ラ ア ル テ ィ メ ッ ト ピ ン ゾ ロ", "USR"),
    ("masateo", (E_MASATEO, E_MASATEO, E_MASATEO), 414, "どうも！Masateoです", "USR"),
    ("jackpot", (E_SEVEN, E_CHINKO, E_DEKA, E_ERO, E_KANSYA, E_OWARI, E_SEI, E_SI, E_SOU, E_UTSU, E_II, E_KUSA, E_WIN, E_AJI, E_SHINGI, E_SUMAN, E_HOSHI, E_RT, E_WARA, E_DICE1, E_AKIYAMA, E_PIPE, E_SUKKIRI, E_SAMBO, E_NEDU, E_HIGH, E_REIWA, E_LOGO, E_AHO, E_KAMI, E_BABA, E_SANSEN, E_HAA, E_SHAPEZ1, E_BAKARI, E_TABAKO, E_KUSURI, E_SAKE, E_SAVAR, E_HAMSA, E_GAMING, E_MASATEO), 1000, "真　鯖　ウ　ル　ト　ラ　F　I　N　A　L　ジ　ャ　ッ　ク　ポ　ッ　ト　・　E　X　T　R　E　M　E", "USR")
]

LOSE_EMOJIS = [E_SEVEN, E_CHINKO, E_OGNK, E_DEKA, E_ERO, E_KANSYA, E_YOU, E_A, E_E, E_NN, E_HA, E_OWARI, E_SEI, E_SI, E_SOU, E_UTSU, E_II, E_KUSA, E_WIN, E_OGNK_YOKO, E_HATENA, E_AJI, E_SHINGI, E_SUMAN, E_5000, E_CHOEN, E_HOSHI, E_RT, E_WARA, E_DICE1, E_DICE2, E_DICE3, E_DICE4, E_DICE5, E_DICE6, E_AKIYAMA, E_PIPE, E_SUKKIRI, E_SAMBO, E_NEDU, E_HIGH, E_REIWA, E_OI, E_LOGO, E_AHO, E_KAMI, E_BABA, E_IS, E_NE, E_SANSEN, E_TAI, E_HO, E_HAA, E_K, E_O, E_N, E_G, E_SHAPEZ1, E_BAKARI]



def spin():
    """スロット実行"""
    if random.random() < WIN_RATE:
        patterns_by_rarity = {}
        for pattern in WINNING_PATTERNS:
            rarity = pattern[4]
            if rarity not in patterns_by_rarity:
                patterns_by_rarity[rarity] = []
            patterns_by_rarity[rarity].append(pattern)

        available_rarities = list(patterns_by_rarity.keys())
        rarity_weights = [
            RARITY_WEIGHTS.get(r, 10) for r in available_rarities
        ]

        selected_rarity = random.choices(
            available_rarities, weights=rarity_weights, k=1
        )[0]

        candidates = patterns_by_rarity[selected_rarity]

        # レアリティ内の役ごとに重みを計算（基本は1、高額倍率は重みを下げる例）
        pattern_weights = []
        for p in candidates:
            multiplier = p[2]  # selected[2] が倍率
            if selected_rarity == "USR":
                if multiplier >= 1000:
                    pattern_weights.append(2)   # 1000倍は重み1（約10%）
                elif multiplier >= 400:
                    pattern_weights.append(3)   # 414倍は重み2（約20%）
                else:
                    pattern_weights.append(5)   # 100倍は重み7（約70%）
            else:
                pattern_weights.append(1)      # 他のレアリティは均等

        # 重み付きで1つ選択
        selected = random.choices(candidates, weights=pattern_weights, k=1)[0]

        return (
            selected[0],
            list(selected[1]),
            selected[2],
            selected[3],
            selected[4],
        )

    else:
        # ハズレ時は標準の3個のランダム出目を生成
        winning_combos = [p[1] for p in WINNING_PATTERNS]
        while True:
            res_emojis = random.choices(LOSE_EMOJIS, k=3)
            is_winning_combo = tuple(res_emojis) in winning_combos
            is_three_of_a_kind = (
                res_emojis[0] == res_emojis[1] == res_emojis[2]
            )

            if not is_winning_combo and not is_three_of_a_kind:
                break
        return None, res_emojis, 0.0, "", ""

def get_pattern(target):
    """指定された番号(1始まり) または ID文字列から役を取得する (デバッグ用)"""
    # 1. 数字で指定された場合 (例: 1 -> 1番目の役)
    if str(target).isdigit():
        idx = int(target) - 1  # 1始まりを0始まりインデックスに変換
        if 0 <= idx < len(WINNING_PATTERNS):
            selected = WINNING_PATTERNS[idx]
            return (
                selected[0],
                list(selected[1]),
                selected[2],
                selected[3],
                selected[4],
            )
        return None

    # 2. 文字列IDで指定された場合 (例: "seven_3")
    for pattern in WINNING_PATTERNS:
        if str(pattern[0]) == str(target):
            return (
                pattern[0],
                list(pattern[1]),
                pattern[2],
                pattern[3],
                pattern[4],
            )
    return None