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

# Functions to generate random deviates for several distributions.

# m a k e e x p o 
@tracef("UTIL",level=4)
def makeexpo(mean):
    ''' fn makeexpo(mean)
        return integer from exponential distribution with mean
    '''
    #interval = int(random.expovariate(1.0/abs(mean)))
    interval = (random.expovariate(1.0/abs(mean)))
    return interval

# m a k e u n i f 
@tracef("UTIL",level=4)
def makeunif(lo,hi):
    ''' fn makeinfo(lo,hi)
        return integer from uniform distribution in range
    '''
    interval = int(random.uniform(lo,hi))
    return interval
    
# m a k e n n n o r m 
@tracef("UTIL",level=4)
def makennnorm(mean,sdev=0):
    ''' makennnorm(mean)
        Return non-neg gaussian with mean and sd sqrt(mean)
         not because there's any science in that, just because.  
        If sd arg is zero. then the result is always the mean. 
        If you think that the folding at zero gives extra weight
         to the lower tail, then change it to, maybe, truncate
         the tail.  
    '''
    return abs(random.gauss(mean, sdev) if sdev > 0 else mean)

# Functions to random deviates for various event streams:
#  sector, server, glitch, and shock lifetimes.  

# m a k e s o m e r a n d 
@tracef("UTIL",level=4)
def makesomerand(mysDistn, myParam1, myParam2=0):
    '''
    Make a random number of some kind, specified by first arg.
    '''
    if mysDistn == "exponential":
        return makeexpo(myParam1)
    elif mysDistn == "normal":
        return makennnorm(myParam1,myParam2)
    elif mysDistn == "uniform":
        return makeunif(myParam1,myParam2)
    else:
        raise ValueError, "Unknown distribution type |%s|" % mysDistn
            
# m a k e s e r v e r l i f e 
@tracef("UTIL",level=4)
def makeserverlife(mynHalf, myParam=0):
    '''
    Today, server lifetimes are exponential.
    '''
    return makesomerand("exponential", fnfHalflife2Exponentiallife(mynHalf))

# m a k e s e c t o r l i f e 
@tracef("UTIL",level=4)
def makesectorlife(mynHalf, myParam=0):
    '''
    Today, sector lifetimes are exponential.
    '''
    return makesomerand("exponential", fnfHalflife2Exponentiallife(mynHalf))

# m a k e g l i t c h l i f e 
@tracef("UTIL",level=4)
def makeglitchlife(mynHalf, myParam=0):
    '''
    Today, glitch lifetimes are exponential.
    '''
    return makesomerand("exponential", fnfHalflife2Exponentiallife(mynHalf))

# m a k e s h o c k l i f e 
@tracef("UTIL",level=4)
def makeshocklife(mynHalf, myParam=0):
    '''
    Today, shock lifetimes are exponential.
    '''
    return makesomerand("exponential", fnfHalflife2Exponentiallife(mynHalf))

# General calculations.

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
    Value returned as an int so it doesn't matter if I
     remembered to put in the leading zeros.  
    '''
    return int(sSomeID[1:])


#END
