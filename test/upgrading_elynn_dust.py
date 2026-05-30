import math
lv = 0
rqead = 200
for i in range(lv,101):
    print(i, rqead)
    rqead += 40*2**((i+1)//20)
