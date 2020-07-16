#!/usr/bin/env python3
# -*-coding: utf8-*-
# t15main.py

'''
argv[1] = total number of cases to run; default 20.
argv[2] = max number to run simultaneously; default=number of CPUs available.
argv[3] = overbooking percentage, default 0.  
argv[4] = time between sending job instructions, in msec, default 100.          
'''

import multiprocessing as mp
import subprocess as sp
import time
import sys
import collections
import re
from NewTraceFac import NTRC, ntrace, ntracef
#from newbroker5actor import tLinesOut, tInstruction, doManyJobs, defaultReceiveOutput
import newbroker5actor as nba

# Global data, read-only, or at most write-once.
class CG(object):
    qJobs = None
    qOutput = None
    lockPrint = None
    procOutput = None
    
    nParallel = None
    nOverbookPct = None
    nPoliteTimerMsec = None
    
    # =================== test instruction stream =====================
    # A few lines just to see if the process works.  
    lLines = ["date +%Y%m%d_%H%M%S.%3N"
            , "# comment 1"
            , "pwd"
            , "ls | head -3"
            , ""
            , "# comment 2"
            , "cat /proc/version"
            , "#ps | grep python | grep -v grep | head -3"
            , "date +%Y%m%d_%H%M%S.%3N"
            ]

    # Even fewer lines just to see if the process works.  
    lLines = ["date +%Y%m%d_%H%M%S.%3N"
            , "# comment 1"
            , "pwd"
            ]
    
    sIdentLine = "# ============= t15main Job # {}"
    
    # Poison messages to cause workers to exit.
    tEndJobMsg = nba.tInstruction(cmdlist="", qoutput=qOutput, logdir='', logname='')
    tEndOutMsg = nba.tLinesOut(listoflists='', procname='')


# =======================================
# f n S e n d I n s t r u c t i o n s 
@ntrace
def fnSendInstructions(mygInstructionSource, mynHowMany, mynPoliteTimerMsec):
    ''' Send all instructions, or a chunk of them, to the jobs queue.
        HowMany == 0 implies send all, exhaust the generator.
    '''
    nCountInst = 0

    def fnSendOneInstruction(mytInst, mynPoliteTime):
        ''' Send just one instruction, and wait a polite amount of time.'''
        g.qJobs.put(mytInst)
        NTRC.ntrace(5, "proc SendInstructions sent|%s|" % (repr(tInst)))
        time.sleep(mynPoliteTime/1000.0)
        
    if mynHowMany:
        for _ in range(mynHowMany):
            tInst = next(mygInstructionSource)
            fnSendOneInstruction(tInst, mynPoliteTimerMsec)
            nCountInst += 1
    else:
        for tInst in mygInstructionSource:
            fnSendOneInstruction(tInst, mynPoliteTimerMsec)
            nCountInst += 1
    return nCountInst


# ===================== main ========================
@ntrace
def main():

    # =======================================
    # Get CLI input args if any.
    nArgs = len(sys.argv)
    nCases = 20 
    if nArgs > 1: nCases = int(sys.argv[1]) if sys.argv[1] else nCases
    g.nParallel = mp.cpu_count()
    if nArgs > 2: g.nParallel = int(sys.argv[2]) if sys.argv[2] else g.nParallel
    g.nOverbookPct = 0
    if nArgs > 3: g.nOverbookPct = int(sys.argv[3]) if sys.argv[3] else g.nOverbookPct
    g.nPoliteTimerMsec = 100
    if nArgs > 4: g.nPoliteTimerMsec = int(sys.argv[4]) if sys.argv[4] else g.nPoliteTimerMsec
    NTRC.ntrace(0, "proc params ncases|%s| nparallel|%s| "
                    "overbookpct|%s| politetime|%s|" 
                % (nCases, g.nParallel, g.nOverbookPct, g.nPoliteTimerMsec))

    # =======================================
    # Need a Multiprocessing Manager to own the output queue.  (Do we?)
    mpmgr = mp.Manager()
    g.qJobs = mp.Queue()
    g.qOutput = mpmgr.Queue()
    # And a lock for safety of stdout printing.
    g.lockPrint = mp.Lock()
    
    # =======================================
    # Maybe increase worker pool by some overbooking amount.
    g.nParallel *= int(1.0 + (g.nOverbookPct / 100.0))
    lprocWorkers = nba.fnCreateWorkerProcesses(g.nParallel, g.qJobs)

    # =======================================
    # Dumb testing version, same instructions many times.
    # Put all the instructions into a list of tInstruction tuples.
    lIdents = [ [g.sIdentLine.format(linenr+1)] 
                for linenr in range(nCases)]
    for lIdent1 in lIdents:
        lIdent1.extend(g.lLines)
    llsInstructions = [x for x in lIdents]
    NTRC.ntracef(5, "MAKI", "proc llsinstructions|%s|" % (llsInstructions))
    # Generator for the instruction stream, merely reads the list.  
    gtInstructions = (nba.tInstruction(cmdlist=lsInstr
                        , qoutput=g.qOutput
                        , logdir="./tmp"
                        , logname=f't15foo{(nCaseNumber+1):03d}.log')
                        for (nCaseNumber, lsInstr) in enumerate(llsInstructions)
                        )

    # =======================================
    # Make one more async process to receive job outputs.
    g.procOutput = nba.fnCreateOutputReceiver(g.qOutput, g.lockPrint)

    # =======================================
    # Now, they're all waiting for work.  Give them some.
    NTRC.ntrace(3, "proc sending instructions from|%s|" % (gtInstructions))
    fnSendInstructions(gtInstructions, 0, g.nPoliteTimerMsec)    

    # Wait some decent interval before killing all the workers.
#    time.sleep(10)
#    time.sleep(2)
    
    # =======================================
    # Send out suicide messages.
    NTRC.ntrace(3, "proc sending end msgs")
    nba.fnCloseAllWorkers()

    # =======================================
    # Close up.  Make sure everything exits.  
    nba.fnCloseOutputReceiver(g.qOutput)


    return 0


g = CG()
    
if __name__ == "__main__":
    sys.exit(main())

#END
