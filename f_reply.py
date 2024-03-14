import random

aiduti_dic = [ ["おはよ", ["おはよう","おはようございます:sunny:","おはよ！","# 押忍","おやすみ～","あさ！"]],
               ["こんにちは", ["こんにちは","ども！","# 押忍","げんき！"]],
               ["こんにちわ", ["こんにちわ","ども！","# 押忍","げんき！"]],
               ["こんばんは", ["こんばんは","フワ～:yawning_face:","# 押忍","よる！"]],
               ["こんばんわ", ["こんばんは","フワ～:yawning_face:","# 押忍","よる！"]],
               ["ありがと", ["どういたしまして","いいよ","エヘ！","ウィ"]],
               ["ごめん", ["許す","いいよお","# *NO PROBLEM*","許しません"]],
               ["すまん", ["許す","いいよお","# *NO PROBLEM*","許しません"]],
               ["すみません", ["許す","いいよお","# *NO PROBLEM*","許しません"]],
               ["さよなら", ["！？","ばいばい","やだ～","乙した！"]],
               ["じゃあね", ["！？","ばいばい","やだ～","乙した！"]],
                ["ちんこ", ["ちんこ！","ちんこ！！","<:chinko:1134001412695674891>","草","そういうのやめよう"]],
                ["チンコ", ["ちんこ！","ちんこ！！","<:chinko:1134001412695674891>","草","そういうのやめよう"]],
                ["ちんぽ", ["ちんぽ！","ちんぽ！！","<:chinko:1134001412695674891>","草","そういうのやめよう"]],
                ["チンポ", ["ちんぽ！","ちんぽ！！","<:chinko:1134001412695674891>","草","そういうのやめよう"]] ]

randomRep_dic = ["ms",
              "ms！",
              "ms……",
              "msを",
              "msかも",
              "msです",
              "msだね",
              "えーと、ms",
              "msですか？",
              "それはms",
              "# ms"]

randomSay_dic = ["ms",
                 "ms！",
                 "ms……",
                 "msを",
                 "ms！ms！",
                 "msかも",
                 "msです",
                 "あ～msms",
                 "あ！msだ",
                 "やばい　ms",
                 "msの時間",
                 "msがきてる",
                 "# ms",
                 
                 "わあ",
                 "うーん",
                 "マ",
                 "あ～",
                 "# マ！"]

randomSays_dic = ["ms1のms2",
                  "ms1と、ms2",
                  "ms1みたいなms2"]

def aiduti(msg):
    #たまに話を聞かない
    if random.randrange(10) == 0:
        return None
    
    for list in aiduti_dic:
        if list[0] in msg:
            reply = random.choice(list[1])
            return reply
    return None

def randomReply(list):
    meisi = random.choice(list)
    reply = random.choice(randomRep_dic).replace("ms",meisi)
    return reply

def randomSay(list):
    meisi = random.choice(list)
    meisi2 = random.choice(list)

    if random.randrange(5) > 0:
        reply = random.choice(randomSay_dic).replace("ms",meisi)
    else:
        reply = random.choice(randomSays_dic).replace("ms1",meisi).replace("ms2",meisi2)
    return reply
