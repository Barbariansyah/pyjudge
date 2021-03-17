from z3 import *

a = Real('a')
b = Real('b')
c = Real('c')
s = Solver()
t = a>b
# s.add(And(a>b, b>c, a>=c))
s.add(t)
s.add(b>c)
print(type(a))
print(type(t))
print(type(a>b))
# s.add(Or(And(And(a>=b, a>=c), Or(a<=b, a<=c)), And(And(a>b, a>c), Or(a<b, a<c))))
print(s.check())
print(s.model())