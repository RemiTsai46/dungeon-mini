import math
lv = 1
rqead = 200
for i in range(lv,201):
    print(i, rqead)
    rqead += 40*2**((i+1)//20)
