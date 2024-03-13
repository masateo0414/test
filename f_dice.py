import random

numToEmoji = [["0",":zero:"],
            ["1",":one:"],
            ["2",":two:"],
            ["3",":three:"],
            ["4",":four:"],
            ["5",":five:"],
            ["6",":six:"],
            ["7",":seven:"],
            ["8",":eight:"],
            ["9",":nine:"]]

def roll(mx):
    deme_list = []
    try:
        cnt, max = list(map(int, mx.split("d")))
    except:
        return "**:x:「[ダイスの数(1以上)]d[ダイスの最大値(1以上)]」と指定してください**"

    if cnt < 1 or max < 1:
        return "**:x:「[ダイスの数(1以上)]d[ダイスの最大値(1以上)]」と指定してください**"

    for i in range(cnt):
        deme = random.randint(1,max)
        deme_list.append(deme)

    res = str(sum(deme_list))
    for j in range(10):
        res = res.replace(numToEmoji[j][0],numToEmoji[j][1])

    return "**{0}** →\n# {1}".format(deme_list, res)