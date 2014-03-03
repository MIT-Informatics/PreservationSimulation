#!/usr/bin/python

import random
from NewTraceFac07 import TRC,trace,tracef
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
    
def makennnorm(mean):
    ''' makennnorm(mean)
        return non-neg gaussian with mean and sd sqrt(mean)
        not because there's any science in that, just because.  
     '''
    x = random.gauss(mean,sqrt(mean))
    return abs(x)
    

# END
