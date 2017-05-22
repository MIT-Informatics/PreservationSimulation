#!/usr/bin/python
# extractcpuinfo.py

# Get real info from the OS about how many cores there are on this system.  
# If the user has specified the NCORES environment variable, then
#  permit that to limit the number of cores used below the number available.  
#  (The user may wish to specify a number smaller than the max available
#  in the hardware, to avoid thrashing in case of other loads.)

import os
import sys
import re
from NewTraceFac import NTRC, ntrace, ntracef
import command


# f n d G e t C p u i n f o 
@ntrace
def fndGetCpuinfo():
    cmd = command.CCommand()
    sGetCpuinfo = "cat /proc/cpuinfo"
    lInfo = cmd.doCmdLst(sGetCpuinfo)

    dInfo = dict()
    sCpuinfoRegex = "([^:]+):\s*(.*)"
    for sLine in lInfo:
        oMatch = re.match(sCpuinfoRegex, sLine)
        if oMatch:
            (sKey, sVal) = (oMatch.group(1).rstrip(), oMatch.group(2).rstrip())
            dInfo[sKey] = fnIntPlease(sVal)
    return dInfo

# f n s G e t C p u I d S t r i n g 
@ntrace
def fnsGetCpuIdString(length="short"):
    dInfo = fndGetCpuinfo()
    if length == "long":
        sOut = ("{vendor_id},speed={cpu MHz}"
                ",family={cpu family},model={model},step={stepping}"
                ",cores={cpu cores}"
                .format(**dInfo))
    else:
        sOut = ("{vendor_id}_"
                "fam{cpu family}mod{model}step{stepping}"
                "cor{cpu cores}spd{cpu MHz}"
                .format(**dInfo))
    return sOut

# f n I n t P l e a s e 
@ntracef("INT", level=5)
def fnIntPlease(myString):
    # If it looks like an integer, make it one.
    try:
        return int(myString)
    except ValueError:
        return myString

# m a i n 
@ntrace
def main():
    sArglen = sys.argv[1] if len(sys.argv)>1 else ""
    sCpuId = fnsGetCpuIdString(sArglen)
    print sCpuId
    return 0


# E n t r y   p o i n t 
if __name__ == "__main__":
    sys.exit(main())


# Edit history:
# 20170522  RBL Original version, extracted from broker.py.  
# 
# 
    
#END
