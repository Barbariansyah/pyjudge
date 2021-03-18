def max_3_2(a, b, c):
    if a >= b + c and a >= c:
        return a
    elif b >= a and b >= c:
        return b
    else:
        return c


