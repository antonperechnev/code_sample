with open('t.txt') as f:
    f.read(2)
    n = 1
    s = 0
    while n <= 8:
        for i in f.readlines():
            s += i[n:].count('1')
            n += 2
    print(s)
