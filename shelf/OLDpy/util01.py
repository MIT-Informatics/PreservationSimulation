#!/usr/bin/python
# util.py

import random
from NewTraceFac import TRC,trace,tracef
from math import sqrt
import itertools


# U t i l i t i e s 
#------------------

def makeexpo(mean):
    ''' fn makeexpo(mean)
        return integer from exponential distribution with mean
    '''
    interval = int(random.expovariate(1.0/abs(mean)))
    return interval

def makeunif(lo,hi):
    ''' fn makeinfo(lo,hi)
        return integer from uniform distribution in range
    '''
    interval = int(random.uniform(lo,hi))
    return interval
    
def makennnorm(mean,sdev=0):
    ''' makennnorm(mean)
        return non-neg gaussian with mean and sd sqrt(mean)
        not because there's any science in that, just because.  
    '''
    if sdev == 0: sdev =  sqrt(mean)
    x = random.gauss(mean,sdev)
    return abs(x)


# f n I n t P l e a s e 
@tracef("INTP",level=5)
def fnIntPlease(oldval):
    ''' fnIntPlease()
        If it looks like an integer and walks like an integer, . . . 
    '''
    try:
        newval = int(oldval)
    except:
        newval = oldval
    return newval


# END
