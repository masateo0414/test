import random

emoji_list = [["0",":zero:"],
            ["1",":one:"],
            ["2",":two:"],
            ["3",":three:"],
            ["4",":four:"],
            ["5",":five:"],
            ["6",":six:"],
            ["7",":seven:"],
            ["8",":eight:"],
            ["9",":nine:"],
            ["-",":no_entry:"]]

dice_list = [["1",":dice_1:"],
            ["2",":dice_2:"],
            ["3",":dice_3:"],
            ["4",":dice_4:"],
            ["5",":dice_5:"],
            ["6",":dice_6:"]]

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

#    res = str(sum(deme_list))
#    for j in range(10):
#        res = res.replace(numToEmoji[j][0],numToEmoji[j][1])

    if max == 6:
        return f"{numsToDices(deme_list)} →\n# {numToEmoji(sum(deme_list))}"
    else:
        return "**{0}** →\n# {1}".format(deme_list, numToEmoji(sum(deme_list)))

def numToEmoji(num):
    emoji = str(num)
    for j in range(11):
        emoji = emoji.replace(emoji_list[j][0],emoji_list[j][1])
    return emoji

def numsToDices(nums):
    dices = "#"
    for j in range(len(nums)):
        dices += f" :dice_{nums[j]}:"
    return dices