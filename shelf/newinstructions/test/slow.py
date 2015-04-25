#!/usr/bin/python

from time import sleep
from sys import argv

if len(argv) > 1:
    sleep(int(argv[1]))
else:
    sleep(5)
if len(argv) > 2:
    print(argv[2])

