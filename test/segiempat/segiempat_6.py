def segiempat(n):
    ret = ''
    c1 = '*'
    c2 = '#'
    if (n==1):
        ret = c1
    elif (n==2):
        ret = c1+c1+'\n'+c1+c1
    elif (n>2):
        for i in range(n):
            ret += c1
        ret += '\n'
        for j in range(n-2):
            ret += c1
            for k in range(n-2):
                ret += c2
            ret += c1
        for i in range(n):
            ret += c1
    return ret