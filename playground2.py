from z3 import *

a = Real('a')
b = Real('b')
c = Real('c')
d = Real('a')
e = Real('e')
s = Solver()
t = a>b
t2 = b>c
t3 = d>e
n = (t,)
n += (t2,)
n2 = (t3, t2)
arr = [t, t2]
arr2 = [t3]
y = Or(And(n), Not(And(n2)))
# x = Or(And(a, Not(b)), And(b, Not(a)))
# s.add(y)
s.add(a==d)
s.add(a!=c)
# print(n)
# print(type(n))
# arr.append(t3)
# print(arr)
# s.add(arr)
print(s)
print(s.check())
print(repr(s.check())=='sat')
m = s.model()
print(m)
# print(len(m))
# print(type(m[m[1]]))
# print(int(m[m[0]].as_decimal(0)))
# x = And(t, t2, t3)
# x = And(t3, x)