level = 1
dgdd = 3500
for i in range(level,201):
    print(i, dgdd)
    dgdd += 15*2**((i+1)//20)
