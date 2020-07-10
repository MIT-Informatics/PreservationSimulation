#!/usr/bin/env python3
# -*-coding: utf8-*-
# t15main.py

'''
argv[1] = total number of cases to run; default 20.
argv[2] = max number to run simultaneously; default=number of CPUs available.
argv[3] = sleep interval in loop waiting for open process slot; 
            default 50 (msec).
argv[4] = max number of times to sleep waiting for an open process slot; 
            default = 100.
'''

import multiprocessing as mp
import subprocess as sp
import time
import sys
import collections
import re
from NewTraceFac import NTRC, ntrace, ntracef
from t15docase import fntDoOneCase, tLinesOut, tInstruction



def printnow(sWhen):
    print(sWhen, time.process_time_ns(), time.perf_counter(), time.time())
    pass
    
def before():
    return time.time()

def after():
    return time.time()

def printdiff(beforetime, aftertime):
    pass
    diff = aftertime - beforetime
    print("diff = %.6f" % diff)





# f n b D o N o t I g n o r e L i n e 
@ntracef("UTIL", level=5)
def fnbDoNotIgnoreLine(mysLine):
    '''
    True if not a comment or blank line.
    '''
    # Ignore comment and blank lines, but take all others.
    return (not re.match("^\s*#", mysLine)) and (not re.match("^\s*$", mysLine))


@ntrace
def main():

    nArgs = len(sys.argv)
    nCases = 20 
    if nArgs > 1: nCases = int(sys.argv[1]) if sys.argv[1] else nCases
    nParallel = mp.cpu_count()
    if nArgs > 2: nParallel = int(sys.argv[2]) if sys.argv[2] else nParallel
    nWaitMsec = 50
    if nArgs > 3: nWaitMsec = int(sys.argv[3]) if sys.argv[3] else nWaitMsec
    nWaitHowMany = 100
    if nArgs > 4: nWaitHowMany = int(sys.argv[4]) if sys.argv[4] else nWaitHowMany
    NTRC.ntrace(3, "proc params ncases|%s| nparallel|%s| "
                    "nwaitmsec|%s| nwaitmany|%s|" 
                % (nCases, nParallel, nWaitMsec, nWaitHowMany))

    lLines = [""
            , "date +%Y%m%d_%H%M%S.%3N"
            , "# comment 1"
            , "pwd"
            , "ls | head -3"
            , ""
            , "# comment 2"
            , "cat /proc/version"
            , "#ps | grep python | grep -v grep | head -3"
            , "date +%Y%m%d_%H%M%S.%3N"
            ]

    # Manager to own queue.
    multiMgr = mp.Manager()
    qOut = multiMgr.Queue()
    
    # Ah, this won't work because pool.map cannot pickle a generator, oops.  
    # Never mind.
    def gentInstruction(myllsInstructions):
        ''' cheap generator to paste argument list together for callee'''
        for (nCaseNumber, lsInstr) in enumerate(myllsInstructions):
            tPacket = tInstruction(cmdlist=lsInstr
                    , qoutput=qOut
                    , logdir="."
                    , logname=f't15foo{(nCaseNumber+1):03d}.log')
            yield tPacket

    # MAP to worker pool.
    pool = mp.Pool(processes=nParallel)
    bef = before()
    printnow('map before')
    
    # Put all the instructions into a list of tInstruction tuples.
    llsInstructions = [lLines for _ in range(nCases)]  # Dummy repetitive list.
    ltInstructions = [tInstruction(cmdlist=lsInstr
                        , qoutput=qOut
                        , logdir="."
                        , logname=f't15foo{(nCaseNumber+1):03d}.log')
                        for (nCaseNumber, lsInstr) in enumerate(llsInstructions)]

    results = pool.map(fntDoOneCase, (ltInstructions))
    
    printnow('map after ')
    pool.close()
    pool.join()
    aft = after()
    printdiff(bef, aft)
    NTRC.ntrace(5, "map giant results = |%s|" % (results))
    print("")

    # Get all output from the multiprocessing queue.
    lOutput = []
    while not qOut.empty():
        lOutput.append(qOut.get())

    print("---------begin cases----------")
    print(f'Number of cases returned={len(lOutput)}')
    for (nCaseNumber, lCase) in enumerate(lOutput):
        print(f'Case number {nCaseNumber+1}')
        for tCmd in lCase:
            print(tCmd)
        print("")
    print("--------------")


if __name__ == "__main__":
    sys.exit(main())

#END
