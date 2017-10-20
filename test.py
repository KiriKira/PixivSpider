def countdown(n):
    print ("Counting down from", n)
    while n >= 0:
        newvalue = (yield n)
        print('newvalue:',newvalue)
        print('n:',n)
        if newvalue is not None:
            n = newvalue
        else:
            n -= 1

c = countdown(5)
for x in c:
    print ('x:',x)
    if x == 5:
        c.send(3)
        c.send(2)