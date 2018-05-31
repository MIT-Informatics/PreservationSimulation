from __future__ import print_function
# fib.py

from sys import argv

def fib(n):
    if n <= 2:
        return 1
    else:
        return fib(n-1) + fib(n-2)

if "__main__" == __name__:
    if len(argv) > 1:
        print(fib(int(argv[1])))
    else:
        print(fib(1))

#END
