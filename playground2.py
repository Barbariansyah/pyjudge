from z3 import *

a = Real('a')
b = Real('b')
c = Real('c')
d = Real('d')
e = Real('e')
s = Solver()
t = a>b
t2 = b>c
t3 = d>e
arr = [t, t2]
arr.append(t3)
print(arr)
print(s.check())
print(s.model())
# x = And(t, t2, t3)
# x = And(t3, x)