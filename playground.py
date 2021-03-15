from z3 import *

a = Real('a')
b = Real('b')
# c = Real('c')
s = Solver()
s.add('a>b')
# s.add(Or(And(And(a>=b, a>=c), Or(a<=b, a<=c)), And(And(a>b, a>c), Or(a<b, a<c))))
print(s.check())
print(s.model())