from random import randrange

t = 0
f = 0

for i in range(10000000):
    r = 0
    for _ in range(5):
        if randrange(52) < 25:
            r+=1
    if r == 2:
        t += 1
    else:
        f += 1
    if i%10000 == 0:
        print(t/(t+f))
        
print(t/(t+f))