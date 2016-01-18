#!/usr/bin/python
# util.py
# Recovered, we hope, after commit/delete screw-up.  

import random
from NewTraceFac import TRC,trace,tracef,NTRC,ntrace,ntracef
from math import sqrt, log
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
        Return non-neg gaussian with mean and sd sqrt(mean)
        not because there's any science in that, just because.  
        If sd arg os zerp. then the result is always the mean.  
    '''
    if sdev == 0: 
        x = mean
    else:
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
            TRC.tracef(3,"DOC","proc CalcDocSize rand|%s| cum|%s| pct|%s| mean|%s| sd|%s| siz|%s|" % (nPctRandom,nPctCum,nPercent,nMean,nSdev,nDocSize))
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

# f n f H a l f l i f e 2 E x p o n e n t i a l l i f e 
@tracef("UTIL",level=5)
def fnfHalflife2Exponentiallife(myfHalflife):
    ''' Convert half-life number to mean exponential lifetime
        for use by makeexpo().
        '''
    fExplife = float(myfHalflife) / log(2.0)
    return fExplife

# f n f C a l c T r a n s f e r T i m e 
@tracef("UTIL",level=5)
def fnfCalcTransferTime(mynDocSize,mynBandwidth):
    ''' Convert doc size in MB and bandwidth in Mb/s 
        to part of an hour that it takes to transmit.  
    '''
    fPartialHours = float(mynDocSize)   \
    * 10                                \
    / float(mynBandwidth)               \
    / float(G.fSecondsPerHour)
    return fPartialHours


#  f n l S o r t I D L i s t 
@tracef("UTIL")
def fnlSortIDList(mylIDs):
    '''\
    Sort a list of IDs of the sort we use here.
    Sort by the numeric integer part, ignoring the 
    alpha class designator, which is always the same
    (one character long) in a list of this sort.
    '''
    """             Found newer, easier way, below.
    lFinal= list()
    lNew = [ fniNumberFromID(id), id) for id in mylIDs ]
    lNew.sort()
    lFinal[:] = [ tup[1] for tup in lNew ]
    return lFinal
    """
    return sorted(mylIDs, key=fniNumberFromID)

# f n i N u m b e r F r o m I D 
@tracef("UTIL",level=5)
def fniNumberFromID(sSomeID):
    '''\
    All IDs are one letter followed by an integer.
    Remove the first letter, convert the rest to int.  
    Intended to be used as the key function in .sort()
    or sorted().
    '''
    return int(sSomeID[1:])


#END
