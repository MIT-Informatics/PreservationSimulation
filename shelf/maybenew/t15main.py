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
from t15docase import tLinesOut, tInstruction, doManyJobs, defaultReceiveOutput


# Global data, read-only, or at most write-once.
class CG(object):
    qJobs = None
    qOutput = None
    lockPrint = None
    procOutput = None
    
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

    # Poison message to cause workers to exit.
    tEndMsg = tInstruction(cmdlist="", qoutput=qOutput, logdir='', logname='')
    tEndOutMsg = tLinesOut(listoflists='', procname='')

# =======================================
# f n C r e a t e W o r k e r P r o c e s s e s 
@ntrace
def fnCreateWorkerProcesses(mynHowMany):
    ''' Create worker pool and start them all. '''
    lProcs = []
    for _ in range(g.nParallel):
        proc = mp.Process(target=doManyJobs, args=(g.qJobs,))
        lProcs.append(proc)
        proc.start()
    return lProcs

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


# =======================================
# f n S e n d A l l E n d M e s s a g e s 
# Send out suicide messages.
def fnSendAllEndMessages():
    for _ in range(g.nParallel):
        g.qJobs.put(g.tEndMsg)
    

# =======================================
# f n C r e a t e O u t p u t R e c e i v e r 
@ntrace
def fnCreateOutputReceiver(myqOutput, myLockPrint, myfReceiver=None):
    ''' Make one more async process to receive job outputs. '''
    if not myfReceiver:
        # Take default if none specified.
        procRcvrToday = defaultReceiveOutput
    else:
        procRcvrToday = myfReceiver

    procReceiver = mp.Process(target=procRcvrToday, 
                        args=(myqOutput, myLockPrint))
    procReceiver.start()
    NTRC.ntrace(3, "proc rcvr|%s| started on q|%s|" % (procRcvrToday, g.qOutput))
    return procReceiver

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
    nOverbookPct = 0
    if nArgs > 3: nOverbookPct = int(sys.argv[3]) if sys.argv[3] else nOverbookPct
    nPoliteTimerMsec = 100
    if nArgs > 4: nPoliteTimerMsec = int(sys.argv[4]) if sys.argv[4] else nPoliteTimerMsec
    NTRC.ntrace(0, "proc params ncases|%s| nparallel|%s| "
                    "overbookpct|%s| politetime|%s|" 
                % (nCases, g.nParallel, nOverbookPct, nPoliteTimerMsec))

    # =======================================
    # Need a Multiprocessing Manager to own the output queue.  (Do we?)
    mpmgr = mp.Manager()
    g.qJobs = mp.Queue()
    g.qOutput = mpmgr.Queue()
    # And a lock for safety of stdout printing.
    g.lockPrint = mp.Lock()
    
    # =======================================
    # Maybe increase worker pool by some overbooking amount.
    g.nParallel *= int(1.0 + (nOverbookPct / 100.0))
    lprocWorkers = fnCreateWorkerProcesses(g.nParallel)

    # =======================================
    # Dumb testing version, same instructions many times.
    # Put all the instructions into a list of tInstruction tuples.
    llsInstructions = [g.lLines for _ in range(nCases)]  # Dummy repetitive list.
    # Generator for the instruction stream, merely reads the list.  
    gtInstructions = (tInstruction(cmdlist=lsInstr
                        , qoutput=g.qOutput
                        , logdir="./tmp"
                        , logname=f't15foo{(nCaseNumber+1):03d}.log')
                        for (nCaseNumber, lsInstr) in enumerate(llsInstructions)
                        )

    # =======================================
    # Make one more async process to receive job outputs.
    g.procOutput = fnCreateOutputReceiver(g.qOutput, g.lockPrint)

    # =======================================
    # Now, they're all waiting for work.  Give them some.
    NTRC.ntrace(3, "proc sending instructions from|%s|" % (gtInstructions))
    fnSendInstructions(gtInstructions, 0, nPoliteTimerMsec)    

    # Wait some decent interval before killing all the workers.
#    time.sleep(10)
    time.sleep(5)
    
    # =======================================
    # Send out suicide messages.
    NTRC.ntrace(3, "proc sending end msgs")
    fnSendAllEndMessages()
    #!!!!!!!!!!!!! I should wait here for all workers to exit.

    # =======================================
    # Close up.  Make sure everything exits.  

    g.qOutput.put(g.tEndOutMsg)
    # And wait for the last output.
    g.procOutput.join()
    

    return 0


g = CG()
    
if __name__ == "__main__":
    sys.exit(main())

#END
