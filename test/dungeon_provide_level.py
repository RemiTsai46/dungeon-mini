import math
charlv = 1
upgradeRequiredDust = 200
dungeonLevel = 1
DungeonDropDust = 3500
OwnedDust = 3500

def lvup(curlv, reqDust):
    curlv += 1
    reqDust += 40*2**((curlv+1)//20)
    return curlv, reqDust

for i in range(dungeonLevel,201):
    while OwnedDust >= upgradeRequiredDust*4:
        OwnedDust -= upgradeRequiredDust*4
        charlv, upgradeRequiredDust = lvup(charlv, upgradeRequiredDust)
    print(f"Level {i}: Lv.{charlv}")
    DungeonDropDust += 15*2**((i+1)//20)
    OwnedDust += DungeonDropDust
