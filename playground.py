from z3 import *

a = Real('a')
b = Real('b')
c = Real('c')
d = Real('a')
s = Solver()
t = a>b
t2 = b>c
# s.add(And(a>b, b>c, a>=c))
s.add(t)
s.add(b>c)
s.add(d>c)
# print(type(a))
# print(type(t.__rmul__(t2)))
# print(type(t*t2))
# print(type(And(a>b, b>c)))
# s.add(Or(And(And(a>=b, a>=c), Or(a<=b, a<=c)), And(And(a>b, a>c), Or(a<b, a<c))))
print(s.check())
print(s.model())