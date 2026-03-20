level = 1
dgsd = 20
total_dgsd = 20
for i in range(level,201):
    # print(i, dgsd)
    dgsd += 5*2**((i+1)//20)
    if i % 20 == 0:
        print(i, "total", total_dgsd)
        total_dgsd = 0
    total_dgsd += dgsd
