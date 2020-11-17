# case.py
#!/usr/bin/env python3
# encoding: utf-8

def output(s):
    print(s)

def add(x, y):
    x += y
    output(str(x))
    return x

def sub(x, y):
    x -= y
    output(str(x))
    return x

a = 2
b = 3

sum = add(a, b)

if sum < 10:
    print('sum < 10')
elif sum > 10:
    print('sum > 10')

for i in range(sum):
    print(i)

while b < a:
    print(b)
    b += 1
