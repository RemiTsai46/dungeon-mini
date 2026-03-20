level = 1
dged = 5000
for i in range(level,201):
    print(i, dged)
    dged += 25*2**((i+1)//20)
