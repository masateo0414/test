import random

# 丸の位置セット
ms_p = ["oxooo","ooxoo","oooxo","oooox",
        "oxooo","ooxoo","oooxo","oooox",
        "oxooo","ooxoo","oooxo","oooox",
        "oxooo","ooxoo","oooxo","oooox",
        "xoxoo","xooxo",
        "oxoxo",
        "oxoooo","ooxooo","oooxoo","ooooxo","ooooox",
        "oxoooo","ooxooo","oooxoo","ooooxo","ooooox",
        "oxoooo","ooxooo","oooxoo","ooooxo","ooooox",
        "oxoooo","ooxooo","oooxoo","ooooxo","ooooox",
        "xoxooo","xooxoo","xoooxo",
        "oxoxoo","oxooxo",
        "ooxoxo",
        "oxooooo","ooxoooo","oooxooo","ooooxoo","oooooxo","oooooox",
        "oxooooo","ooxoooo","oooxooo","ooooxoo","oooooxo","oooooox",
        "oxooooo","ooxoooo","oooxooo","ooooxoo","oooooxo","oooooox",
        "oxoxooo","oxooxoo","oxoooxo","oxoooox",
        "ooxoxoo","ooxooxo",
        "oooxoxo",
        "oxoooooo","ooxooooo","oooxoooo","ooooxooo","oooooxoo","ooooooxo","ooooooox",
        "oxoooooo","ooxooooo","oooxoooo","ooooxooo","oooooxoo","ooooooxo","ooooooox",
        "oxooxooo","oxoooxoo","oxooooxo",
        "ooxooxoo","ooxoooxo",
        "oooxooxo"]

ms_ph = ["xoxoo","xooxo","xooox",
        "oxoxo","oxoox",
        "ooxox",
        "xoxooo","xooxoo","xoooxo","xoooox",
        "oxoxoo","oxooxo","oxooox",
        "ooxoxo","ooxoox",
        "oooxox",
        "xoxoooo","xooxooo","xoooxoo","xooooxo","xooooox",
        "oxoxooo","oxooxoo","oxoooxo","oxoooox",
        "ooxoxoo","ooxooxo","ooxooox",
        "oooxoxo","oooxoox",
        "ooooxox",
        "oxoxoooo","oxooxooo","oxoooxoo","oxooooxo","oxooooox",
        "ooxoxooo","ooxooxoo","ooxoooxo","ooxoooox",
        "oooxoxoo","oooxooxo","oooxooox",
        "ooooxoox"]

# ランダム文字セット
ms_l = "あいいいいいうううううえおかかかかかききききくくくくけけここここさしししししすすすせそたたたたたちつててててとととととななななにににににぬねのののののははははひふへほままみむめもやゆよらりりりるるるれれれれろわわわわんんんんんががぎぎぐげごござざじじずずぜぞだだでででどどばばびぶべぼぼゃゃゅゅょょっっ"


def normal():
    ms_q = ""
    
    for p in random.choice(ms_p):
        if p == "o":
            ms_q += "○"
        else:
            ms_q += random.choice(ms_l)
    
    return ms_q

def hard():
    ms_q = ""
    
    for p in random.choice(ms_ph):
        if p == "o":
            ms_q += "○"
        else:
            ms_q += random.choice(ms_l)
    
    return ms_q

