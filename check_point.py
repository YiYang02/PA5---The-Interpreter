def ret_two(a):
    return a, 10

v1 = None; s2 = None
for i in range(5):
    v1, s2 = ret_two(99 + i)
print(v1)
print(s2)