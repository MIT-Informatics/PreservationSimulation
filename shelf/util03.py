#!/usr/bin/python
# util.py

import random
from NewTraceFac import TRC,trace,tracef
from math import sqrt
import itertools
from globaldata import *


# U t i l i t i e s 
#------------------

@tracef("UTIL",level=4)
def makeexpo(mean):
    ''' fn makeexpo(mean)
        return integer from exponential distribution with mean
    '''
    #interval = int(random.expovariate(1.0/abs(mean)))
    interval = (random.expovariate(1.0/abs(mean)))
    return interval

@tracef("UTIL",level=4)
def makeunif(lo,hi):
    ''' fn makeinfo(lo,hi)
        return integer from uniform distribution in range
    '''
    interval = int(random.uniform(lo,hi))
    return interval
    
@tracef("UTIL",level=4)
def makennnorm(mean,sdev=0):
    ''' makennnorm(mean)
        return non-neg gaussian with mean and sd sqrt(mean)
        not because there's any science in that, just because.  
    '''
    if sdev == 0: sdev =  sqrt(mean)
    x = random.gauss(mean,sdev)
    return abs(x)


# f n I n t P l e a s e 
@tracef("UTIL",level=5)
def fnIntPlease(oldval):
    ''' fnIntPlease()
        If it looks like an integer and walks like an integer, . . . 
    '''
    try:
        newval = int(oldval)
    except:
        newval = oldval
    return newval

# f n n C a l c D o c S i z e ( ) 
@tracef("UTIL",level=4)
def fnnCalcDocSize(mynLevel):
    lPercents = G.dDocParams[mynLevel]
    nPctRandom = makeunif(0,100)
    nPctCum = 0
    for lTriple in lPercents:
        (nPercent,nMean,nSdev) = lTriple
        nPctCum += nPercent
        if nPctRandom <= nPctCum:
            nDocSize = int(makennnorm(nMean,nSdev))
            TRC.tracef(3,"DOC","proc CalcDocSize rand|%s| cum|%s| pct|%s| mean|%s| sd|%s|" % (nPctRandom,nPctCum,nPercent,nMean,nSdev))
            break
    return nDocSize

#  f n f C a l c B l o c k L i f e t i m e 
@tracef("UTIL",level=4)
def fnfCalcBlockLifetime(mynSectorLife,mynCapacity):
    ''' Because of the funny way we handle small errors, we have to
        calculate the aggregate block error rate for the shelf.  
        When such an error occurs we then choose the block within
        the shelf that failed.  
        For the moment, simple: real failure rate for a single block
        times the number of blocks on the shelf.  Eventually, we might
        increase this rate if another recent failure has occurred on
        this shelf.
        Actually, calculate this as lifetime.  What is the exponential
        mean lifetime of a block?  Probably something like 1E14 hours
        per bit (1E9 years).  But a megabyte block has about 10E7
        bits, so that reduces the block lifetime to 1E7 hours = 1E2 years.  
        Whoa, way small.  Hmmm.  Now if you have a storage structure of 
        say 10 terabytes = 1E13 bytes = 1E14 bits, then the lifetime of
        *some* block in that storage structure, i.e., the time to failure
        of the first block in that structure, is about one hour.  Whoa.  
        Way too short.  
        Let's redo that with a lifetime of 
        - 1e14 years per bit
        - 1e7 years per megabyte block
        - storage structure of 10TB = 1e13B = 1e7MB
        - time to first failure in structure = 1e7/1e7 = 1 year.  
        Much more plausible.  
        Note that all these parameters are stated as lifetimes in hours.
    '''
    fLife = float(mynSectorLife) / float(mynCapacity)
    return fLife            # returns float


# END
