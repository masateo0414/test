import random

# 絵文字の定義
E_FEVER = "<:gogo:1162986210906611794>"
E_SAVAR = "<:savar:1218331362415870032>"
E_KATTI = "<:kati:1155023087172067360>"
E_SI = "<:si:1133966404001996881>"
E_SEI = "<:sei:1133968046915076116>"
E_AHO = "<:aho:1168437457969229824>"

# 1. レア度ごとの出現割合（当たりが出た際の内訳比率）
# 合計が100になるように設定
RARITY_WEIGHTS = {
    "SSR": 3,  # 当たりのうち 3%
    "SR": 12,  # 当たりのうち 12%
    "R": 25,  # 当たりのうち 25%
    "N": 60,  # 当たりのうち 60%
}

# 2. 当たりの目リスト（weight を排除して5項目に！）
# フォーマット: ( id, (絵文字1, 2, 3), 配当倍率, "タイトル", "レア度" )
WINNING_PATTERNS = [
    # --- SSR (何個増やしてもSSRグループ全体で3%の枠を分け合う) ---
    ("fever_3000", (E_FEVER, E_FEVER, E_FEVER), 50.0, "超FEVER 3000", "SSR"),
    ("jackpot_7", (E_SEI, E_SEI, E_SEI), 50.0, "アルティメット正義", "SSR"),
    # --- SR ---
    ("kati_3", (E_KATTI, E_KATTI, E_KATTI), 15.0, "大勝利の刻", "SR"),
    ("sei_si", (E_SEI, E_SI, E_KATTI), 15.0, "正義の勝利", "SR"),
    # --- R ---
    ("aho_trio", (E_AHO, E_AHO, E_AHO), 3.0, "アホトリオ揃い", "R"),
    ("si_combo", (E_SI, E_SI, E_SI), 3.0, "シ・シ・シ", "R"),
    # --- N ---
    ("aho_double", (E_AHO, E_AHO, E_SI), 1.5, "プチアホ", "N"),
    ("savar_single", (E_SAVAR, E_AHO, E_SI), 1.0, "セーフ！", "N"),
]

LOSE_EMOJIS = [E_FEVER, E_SAVAR, E_KATTI, E_SI, E_SEI, E_AHO]
WIN_RATE = 0.30  # 全体の勝率は30%固定


def spin():
    """スロットを1回回す"""
    # --- 【当たり】の処理 ---
    if random.random() < WIN_RATE:
        # 1. 存在するレア度ごとに役をグループ分けする
        patterns_by_rarity = {}
        for pattern in WINNING_PATTERNS:
            rarity = pattern[4]
            if rarity not in patterns_by_rarity:
                patterns_by_rarity[rarity] = []
            patterns_by_rarity[rarity].append(pattern)

        # 2. 現在登録されているレア度とその重みを取得
        available_rarities = list(patterns_by_rarity.keys())
        rarity_weights = [
            RARITY_WEIGHTS.get(r, 10) for r in available_rarities
        ]

        # 3. レア度を1つ抽選
        selected_rarity = random.choices(
            available_rarities, weights=rarity_weights, k=1
        )[0]

        # 4. 選ばれたレア度の中にある役からランダムで1つ選ぶ（均等確率）
        selected = random.choice(patterns_by_rarity[selected_rarity])

        # (p_id, res_emojis, payout_rate, title, rarity)
        return (
            selected[0],
            list(selected[1]),
            selected[2],
            selected[3],
            selected[4],
        )

# --- 【ハズレ】の処理 ---
    else:
        winning_combos = [p[1] for p in WINNING_PATTERNS]
        while True:
            res_emojis = random.choices(LOSE_EMOJIS, k=3)

            # 1. 当たり役に登録されている並びではないか
            is_winning_combo = tuple(res_emojis) in winning_combos

            # 2. 3つすべて同じ絵文字（ゾロ目）になっていないか
            is_three_of_a_kind = res_emojis[0] == res_emojis[1] == res_emojis[2]

            # どちらにも該当しない場合のみ確定
            if not is_winning_combo and not is_three_of_a_kind:
                break

        return None, res_emojis, 0.0, "", ""