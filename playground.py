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
# s.add(And(a>b, b>c, a>=c))
# s.add(t)
# s.add(b>c)
# s.add(d>c)
# print(type(a))
# print(type(t.__rmul__(t2)))
# print(type(t*t2))
# print(type(And(a>b, b>c)))
# s.add(Or(And(And(a>=b, a>=c), Or(a<=b, a<=c)), And(And(a>b, a>c), Or(a<b, a<c))))
s.add(arr)
print(s.check())
print(s.model())
# x = And(t, t2, t3)
# x = And(t3, x)
# print(arr)