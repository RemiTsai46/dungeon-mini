mastery = 0
ramx = 1000
for i in range(mastery,30):
    print(i, ramx)
    ramx += 1000*2**(i//10)
