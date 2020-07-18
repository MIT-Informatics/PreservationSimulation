#!/usr/bin/python
# brokergetcores.py
from __future__ import print_function

# Get real info from the OS about how many cores there are on this system.  
# If the user has specified the NCORES environment variable, then
#  permit that to limit the number of cores used below the number available.  
#  (The user may wish to specify a number smaller than the max available
#  in the hardware, to avoid thrashing in case of other loads.)

import os
import sys
from NewTraceFac import NTRC, ntrace, ntracef
import command
import multiprocessing


# f n n G e t H W C o r e s 
@ntracef("GETC")
def fnnGetHWCores(default=8):
#    cmd = command.CCommand()
#    sGetCoreCount = "cat /proc/cpuinfo | grep processor | wc -l"
#    sCount = cmd.doCmdStr(sGetCoreCount)
#    try:
#        nCount = int(sCount)
#    except: 
#        nCount = default
    nCount = multiprocessing.cpu_count()
    return nCount


# f n n G e t U s e r C o r e s 
@ntracef("GETC")
def fnnGetUserCores(default=32):
    nCount = default
    try:
        nCount = int(os.getenv("NCORES", default))
    except (ValueError, TypeError):
        raise TypeError('Environment variable NCORES must be an integer.')
    return nCount


# f n n G e t R e s o l v e d C o r e s 
@ntracef("GETC")
def fnnGetResolvedCores():
    nHWCount = fnnGetHWCores()
    nUserCount = fnnGetUserCores()
    nCount = nUserCount if nUserCount < nHWCount else nHWCount
    return nCount


# m a i n 
@ntracef("GETC")
def main():
    nHW = fnnGetHWCores()
    nUser = fnnGetUserCores()
    nResolved = fnnGetResolvedCores()
    print("hw={} user={} resolved={}".format(nHW, nUser, nResolved))


# E n t r y   p o i n t 
if __name__ == "__main__":
    sys.exit(main())


# Edit history:
# 20170520  RBL Original version, extracted from broker.py.  
# 20200717  RBL Use multiprocssing.cpu_count() instead of running 
#                an external command to get nCores.
# 
    
#END
