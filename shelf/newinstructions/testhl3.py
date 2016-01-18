#!/usr/bin/python
# testhl3.py
# Test that the lifetime-to-halflife calculation in util.py is correct.
# For any reasonable value of half-life, do half of the generated lifetimes
#  actually fall under the half-life value?
# The correct calculation, btw, is 
#   <mean exponential lifetime> = <half-lifetime> / ln(2)

import util
from NewTraceFac import NTRC,ntrace,ntracef
import math
import sys

@ntrace
def main(mynSamples, mysHl, myfThresh):
    explife = util.fnfHalflife2Exponentiallife(float(mysHl))
    #explife = float(mysHl)
    #explife = float(mysHl) * math.log(2.0)
    #explife = float(mysHl) / math.log(2.0)
    #explife = float(mysHl) / 2.0
    nDeaths = 0
    for iSample in xrange(mynSamples):
        fNextSample = util.makeexpo(explife)
        if fNextSample <= float(myfThresh):
            nDeaths += 1
        NTRC.ntrace(3,"proc sample %s val %s deaths %s" % (iSample, fNextSample, nDeaths))
    print mynSamples, mysHl, myfThresh, nDeaths

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print '''Usage: testhl2 nsamples half-life'''
        sys.exit(1)
    else:
        nSamples = int(sys.argv[1])
        fHalflife = float(sys.argv[2])
        fThresh = float(sys.argv[3]) if len(sys.argv) > 3 else fHalflife
        main(nSamples, fHalflife, fThresh)

#END
