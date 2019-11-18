#/usr/bin/python3
# newbroker4.py
#               RBL 20191106

'''
Thread/Queue based design for newbroker4        RBL 20191106
The orchestration layer for the MIT Preservation Simulation project.  

Stick to Raymond Hettinger's principles of queueing instead of locking. Except
oops on the ntrace routines which don't use queued print, so we still have to
lockprint around them.  Sorry about that.  Work in progress. 
And another oops on locking around set/del of the dictionary that tracks
all transient threads so they all get gone.  


------------------
------------------
job process

do all the usual stuff with do1case and do1line
send output in msg to q param


------------------
sendinstructions

while instructions available:
get iterator of instructions
wait for slot
create thread to manage job
add to list of jobs
start job thread, args=tInstr, thread obj
make thread dict entry of thread name and obj
endwhile
set last instr flag


------------------
function startonejob thread

create multiprocessing job
create mp queue for return data
start job
wait for return data on mp q
queue task to delete job from list
send your own thread object to killallmonstrers
if there is anything else to be done with the mp job's output, 
 do it here


------------------
function killallmonsters daemon thread

get thread name from qjobend
translate to thread object
if it is alive, join it
remove entry from thread dict
taskdone

------------------
startup

create jobslist

create qjobend
create jobend thread
set daemon
start jobend thread

create qJobmod
create jobsmod thread
create qJobadddone
create qJobdeldone
create qJobaskdone
start jobsmod thread

call sendinstructions

join qjobend
clean up any remaining threads

end


------------------
modjob daemon thread to modify jobslist

this is a separate thread but calls to it are often synchronous:
callers will wait for return info on the particular qJobxxxdone queue; 
they supply an event to be set when output is ready.  
this is done to isolate all access to the jobs list in a single thread 
that has exclusive access to that list.  no locking needed.  no races.  

needed operations are 
- put job in empty slot because i know that one is available; return slot nr?
- remove job from slot n
- interrogate if empty slot is available; how do i get the answer back?
use qJobadddone to return job slot number
use qJobdeldone to return empty slot number
use qJobaskdone to return yes/no

qjobmod.get()
taskdone
switch opreq:

case ask
scan for empty slot
return y/n on qJobaskdone.put()

case add arg=jobnum
find an empty slot
insert job info into that slot
return slot number in qJobadddone.put()

case del arg=jobnum
remove jobinfo from slot n
return n on qJobdeldone.put()


------------------

'''


import multiprocessing
import subprocess 
import threading
import time
import sys
import collections
import re
import itertools
import datetime
import os
import queue
from NewTraceFac import NTRC, ntrace, ntracef

import os
import json
import copy
import math

#===========================================================
# N a m e d   t u p l e s 

# Complete instruction info to pass to newbroker.
tInstruction = collections.namedtuple("tInstruction"
                , "runid cmdlist logdir logname casedict")
# Job process ID and output queue.
tJob = collections.namedtuple("tJob", "procid")
# Line returned from a single command
tLineOut = collections.namedtuple("tLineOut", 
            "callstatus cmdstatus casenr linenr ltext ")
# List of lines returned from list of commands
tLinesOut = collections.namedtuple("tLinesOut", "procname, listoflists")


#===========================================================
# class   C G   f o r   g l o b a l   d a t a 
class CG(object):
    ''' Global data.
    '''
    # Administrative options to guide broker's behavior.
    nCores = 8          # Default, overridden by NCORES env var.
    nPoliteTimer = 20   # Wait between sequential launches, in milliseconds.

    nJobCounter = itertools.count(1)
    
    # Command template components.
    #  filled in from templates.  
    sCommandListFilename = "broker2commandlist.txt"  # default, not overridden.
    # Special fake CPU-bound commands to test for proper parallel execution.  
    # These take about a minute (75s) and a third of a minute (22s) on an
    #  Intel 3Gi7 CPU in my Dell Optiplex 7010 i7-3770(2016-08).  Your mileage
    #  may differ.  
    # Make sure we have the right version of bash and Python.
    sStartTime = 'date +%Y%m%d_%H%M%S.%3N'
    sBashIdCmd = 'sh --version'
    sPythonIdCmd = ('python -c "import sys; print sys.version; '
                    'print sys.version_info"'
                    )
    sFibCmd1 = 'python fib.py 33'
    sFibCmd2 = 'python fib.py 32'
    sEndTime = 'date +%Y%m%d_%H%M%S.%3N'
    lFibTemplates = [sStartTime, sBashIdCmd, sPythonIdCmd, 
                    sFibCmd1, sFibCmd2, sEndTime]
    
    bLast = False   # Have we come to the end of all instructions.

    lCommands = [
                  "# test instructions for newnewbroker4"
                , "python3 -c 'import time,random; time.sleep(1.0*random.random())'"
                , ""
                ]


#===========================================================

    """Additional data needed by the newbroker module.  
    """
    ltJobs = list()     # Job numbers or None
    lockPrint = None    # Thread lock for trace printing.
    
    # Dictionaries that contain references to things we want cleaned up.
    # These must be emptied when the jobs they point to are complete.
    dName2Thread = dict()   # Threads of fnStartOne, to be join()ed later.
    lockThreadDict = None

    nParallel = 4       # Limit on jobs running in parallel (on separate CPUs)
                        #  (overridden by nCores).
    nOverbook = 0       # Percentage by which we should overbook the cores. 
                        #  E.g., 0 is not overbooked, 100 is double-booked, 
                        #  and 50 for 1.50 times as many jobs as cores.

    nCases = 1          # DEBUG
    nWaitedForSlot = 0  # DEBUG
    bDebugPrint = False # Print output of all jobs? (obsolete) 
    qJobEnd = None    
    thrJobMod = None    
    qJobMod = None
    
    nJobsCurrent = 0
    
    nTickInterval = 0

#===========================================================





#===========================================================

# ==================== subprocess user: do one line ====================

# f n D o O n e L i n e 
@ntracef("DO1L")
def fntDoOneLine(mysLine, mynProc, mynLine):
    """Execute one single-line command.  
    
    Input: single line of command.  
    Output: tuple of the (Popen PIPE return code, command return code, list
     of output lines as strings.
    Contributes line(s) to be in log file.
     Input lines and the first line of output blocks have timestamps;
     other lines in output blocks are indented with spaces.  
    """
    sTimeBegin = fnsGetTimestamp()
    proc = (subprocess.Popen(mysLine
        , stdout=subprocess.PIPE
        , close_fds=True            # The default anyway, I think.  
        , stderr=subprocess.DEVNULL
        , universal_newlines=True
        , shell=True)
        )
    (sProcOut, sProcErr) = proc.communicate()
    proc.stdout.close()
    if not sProcErr: sProcErr = ""
    sTimeEnd = fnsGetTimestamp()
    NTRC.ntracef(4, "DO1L", "proc DoOneLine sProcOut case|%s| line|%s| "
                "sline|%s| sProcOut|%s| len|%s|" 
                % (mynProc, mynLine, mysLine, sProcOut, len(sProcOut)))
    
    # Format lines for output by timestamping or indenting each line.  
    sOut = ("-"*len(sTimeBegin) + "\n"
            + sTimeBegin + "  " + "$ " + mysLine + "\n")
    lTmpOut1 = sProcOut.rstrip().split("\n")
    lTmpOut2 = [fnsStampLine(sTimeEnd, sLine, (i==0))
                    for i,sLine in enumerate(lTmpOut1)]
    sOut += "\n".join(lTmpOut2)
    sOut += sProcErr.rstrip()
    
    # Collect and return everything to caller.  
    nCmdStat = "n/a - RBL"
    nReturnCode = proc.returncode
    lOut = sOut.split("\n")
    NTRC.ntracef(4, "DO1L", "proc DoOneLine case|%s| line|%s| "
                "sline|%s| lResult|%s|" 
                % (mynProc, mynLine, mysLine, lOut))
    
    return(tLineOut(callstatus=nReturnCode, cmdstatus=nCmdStat
            , linenr=mynLine, casenr=mynProc, ltext=lOut))


# ==================== multiprocessing: DoOneCase ====================

# f n t D o O n e C a s e 
@ntracef("DO1C")
def fntDoOneCase(mytInstruction, qToUse):
    """Input: list of instructions generated by the broker for this case; 
     multiprocessing queue through which to report results.
    
    Remove blanks, comments, etc., from the instructions.  Each line that
     is not blank or comment is a command to be executed.  Blanks and 
     comments are written directly into the output.

    Output: list of commands and their output, sent to the supplied queue.
     The text will also be written to a log file for the case.  
    
    This function will be a multiprocessing external process.
    """
    sWhoami = multiprocessing.current_process().name
    NTRC.ntracef(3, "DO1C", "proc procname|%s|" % (sWhoami))
    nProc = fnsGetProcessNumber(sWhoami)
    lResults = []                   # list of strings

    # Unpack instruction command list and other items.
    lInstruction = mytInstruction.cmdlist
    (sLogfileDir, sLogfileName) = (mytInstruction.logdir
                                , mytInstruction.logname)

    # Process all command lines of the instruction list and collect results.  
    for nLine, sLine in enumerate(lInstruction):
        if fnbDoNotIgnoreLine(sLine):
            # Genuine line; execute and collect answer line(s).  
            tAnswer = fntDoOneLine(sLine, nProc, nLine)
            (nRtn, nErr, lResult) = (tAnswer.callstatus
                                    , tAnswer.cmdstatus
                                    , tAnswer.ltext)
            lResults.extend(lResult)
            NTRC.ntracef(4, "DO1C", "proc DoOneCase case|%s| line|%s| "
                        "lResult|%s|" 
                        % (nProc, nLine, lResult))
        else:
            # Comment or blank line; just append to results.
            lResults.extend([("-"*len(fnsGetTimestamp()))
                            , (fnsGetTimestamp() + "  " + sLine)])
            NTRC.ntracef(4, "DO1C", "proc DoOneCase case|%s| line|%s| "
                        "comment|%s|" 
                        % (nProc, nLine, sLine))
    fnWriteLogFile(nProc, (lResults), sLogfileDir, sLogfileName)

    lPrefix = [("BEGIN results from " + sWhoami)]
    lSuffix = [("ENDOF results from " + sWhoami)]
    lResultsToSee = ['\n'] + lPrefix + lResults + lSuffix + ['\n']
    tAnswers = tLinesOut(procname=sWhoami, listoflists=lResultsToSee)
    qToUse.put(tAnswers)
    NTRC.ntracef(4, "DO1C", "proc DoOneCase case|%s| tanswers|%s| "
                % (nProc, tAnswers))
#    qToUse.close()
    return (tAnswers)


# f n W r i t e L o g F i l e 
@ntracef("DO1C")
def fnWriteLogFile(mynProc, mylContents, mysFileDir, mysFileName):
    sFullName = mysFileDir + "/" + mysFileName
    sContents = '\n'.join(mylContents)
    with (open(sFullName, "w")) as fhOut:
        print(sContents, file=fhOut)

# Debug version of same: write only every tenth log file.
if not (os.getenv("DEBUG", "") == ""):
    @ntracef("DO1C")
    def fnWriteLogFile(mynProc, mylContents, mysFileName):
        sContents = '\n'.join(mylContents)
        if fnIntPlease(mynProc) % 10 == 0:
            with (open(mysFileName, "w")) as fhOut:
                print(sContents, file=fhOut)


# f n s G e t P r o c e s s N u m b e r 
@ntrace
def fnsGetProcessNumber(mysProcName):
    '''Extract the process number, which is the same as the case number
    in this case, so we can use its abbreviated form in logs and traces.
    '''
    sProcNum = re.match("Process-(\d+)", mysProcName).group(1)
    return sProcNum if sProcNum else ""


# f n s G e t T i m e s t a m p 
def fnsGetTimestamp():
    '''Return timestamp with milliseconds.
    '''
    return datetime.datetime.now().strftime('%Y%m%d_%H%M%S.%f')[:-3]
#    return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')   # without msec


# f n s S t a m p L i n e 
def fnsStampLine(mysStamp, mysLine, mybFirstLine):
    """To indent paras of lines where the timestamp appears only
    on the first line, blanks to indent all the others.  
    """
    if mybFirstLine:
        return fnsGetTimestamp() + "  " + mysLine
    else:
        return " "*len(fnsGetTimestamp()) + "  " + mysLine


# f n b D o N o t I g n o r e L i n e 
def fnbDoNotIgnoreLine(mysLine):
    '''
    True if not a comment or blank line.
    '''
    # Ignore comment and blank lines, but take all others.
    return (not re.match("^\s*#", mysLine)) and (not re.match("^\s*$", mysLine))


# f n I n t P l e a s e 
def fnIntPlease(mysIn):
    try:
        val = int(mysIn)
    except ValueError:
        val = mysIn
    return val


# f n b Q E n d 
def fnbQEnd():
    return g.bLast


#===========================================================
# Joblist maintenance routines
#===========================================================
# f n J o b M o d 
@ntracef("JMOD")
def fnJobMod():
    ''' fnJobMod is the owner of the jobs list.  Jobs are identified
         here only by job number (runid).  This is a daemon thread.  
        Operations:
        - ask if there is an opening in the list for another job.
        - add a job to the list.
        - delete a job from the list.
        Most callers will use these operations synchronously by waiting
         for the event arg to be declared true.  If they need the information
         returned in the return queue, they must wait for the event.
        Input: 
        - operation, a little string: ask, add, del.
        - an event obj to set() when the operation is completed.
        - optional additional arg: job number to be added or removed.  
    '''
    while(True):
        [sCommand, evDone, *xMore] = g.qJobMod.get()
        g.qJobMod.task_done()
        with g.lockPrint:
            NTRC.ntracef(3, "JMOD", "JobMod args|%s| |%s| |%s|" 
            % (sCommand, evDone, xMore))
        with g.lockPrint:
            NTRC.ntracef(5, "JMOD", "JobMod atentry joblist|%s| len|%s|" 
                % (g.ltJobs, len(g.ltJobs)))
        if sCommand is None: break

        # Caller wants to know if there is an empty slot for a new job.
        #  Reply true or false.
        if sCommand == "ask":
            if g.nJobsCurrent < len(g.ltJobs):
                result = True
            else:
                result = False
            with g.lockPrint:
                NTRC.ntracef(4, "JMOD", "JobMod ask result|%s|" % result)
            g.qJobModAskDone.put(result)

        # Caller wants to add a new job number to an empty slot in the list.
        elif sCommand == "add":
            lEmptySlots = [idx for (idx,x) in enumerate(g.ltJobs) 
                            if not x]
            assert len(lEmptySlots) > 0, ("Supposed to be an empty slot "
                        "for new case, but I can\'t find one.")
            idxEmpty = lEmptySlots[0]
            nTmpJobnum = xMore[0]
            g.ltJobs[idxEmpty] = nTmpJobnum
            g.nJobsCurrent += 1
            g.qJobModAddDone.put(g.nJobsCurrent)
            with g.lockPrint:
                NTRC.ntracef(5, "JMOD", "JobMod add end joblist|%s| |%s|" 
                    % (g.ltJobs, len(g.ltJobs)))

        # Caller wants to delete the job number from the list, making
        #  an empty slot for some other job to fill.  
        elif sCommand == "del":
            nTmpJobnum = xMore[0]
            lFoundSlot = [idx for (idx,x) in enumerate(g.ltJobs) 
                            if x == nTmpJobnum]
            assert len(lFoundSlot) == 1, ("Did not find slot to match"
                        "case number|%s|" % nTmpJobnum)
            idxFound = lFoundSlot[0]
            g.ltJobs[idxFound] = None
            g.nJobsCurrent -= 1
            with g.lockPrint:
                NTRC.ntracef(5, "JMOD", "JobMod del done joblist|%s| current|%s|" 
                    % (g.ltJobs, g.nJobsCurrent))
            g.qJobModDelDone.put(g.nJobsCurrent)

        else:
            assert False, ("Bad command to fnJobMod: %s" % sCommand)
        # Turn on the caller's event to indicate that the answer is
        #  in the queue.  
        evDone.set()

#===========================================================
# Thread dictionary maintenance routines
#===========================================================
# f n T h r D i c t A d d 
@ntracef("TDIC")
def fnThrDictAdd(mysThrName, myThrObj):
    ''' Add a thread name/obj pair to the dict.
    '''
    with g.lockThreadDict:
        g.dName2Thread[mysThrName] = myThrObj

# f n T h r D i c t D e l 
@ntracef("TDIC")
def fnThrDictDel(mysThrName):
    ''' Delete a thread name/obj pair from the dict.
    '''
    with g.lockThreadDict:
        del g.dName2Thread[mysThrName]

# f n T h r D i c t G e t 
@ntracef("TDIC")
def fnThrDictGet(mysThrName):
    ''' Retrieve the thread obj given the name
    '''
    with g.lockThreadDict:
        thrResult = g.dName2Thread[mysThrName]
    return(thrResult)

# f n T h r D i c t G e t A l l 
@ntracef("TDIC")
def fnThrDictGetAll():
    ''' Retrieve a list of tuples of the entire dict.
    '''
    with g.lockThreadDict:
        lResult = list(g.dName2Thread.items())
    return(lResult)


#===========================================================
# f n E n d O n e 
@ntracef("END1")
def fnEndOne():
    ''' Join (to kill) every thread that sends its thread object here.
         This is a daemon thread.
        Reads the qJobEnd queue.
        Input: 
        - name of the thread for which the mp job has completed.
          Translates from thread name to thread object using the 
          global dName2Thread dictionary.
        Output: 
        - Joins the thread to end it, if the thread is still alive.  
        - Removes the thread name->obj mapping from the dict.
    '''
    while True:
        sThrToKill = g.qJobEnd.get()
        thrToKill = fnThrDictGet(sThrToKill)
#        with g.lockThreadDict:
#            thrToKill = g.dName2Thread[sThrToKill]
        if thrToKill.is_alive():
            thrToKill.join()
            bAlive = True
        else:
            bAlive = False
        with g.lockPrint:
            NTRC.ntracef(3, "END1", "proc fnEndOne1 thread|%s| "
                "name|%s| was alive|%s|" 
                % (thrToKill, sThrToKill, bAlive))
        fnThrDictDel(sThrToKill)
#        with g.lockThreadDict:
#            del g.dName2Thread[sThrToKill]
        with g.lockPrint:
            NTRC.ntracef(3, "END1", "proc fnEndOne2 threaddict|%s| "
                % (g.dName2Thread))
        g.qJobEnd.task_done()


#===========================================================
# f n S t a r t O n e 
@ntracef("FST1")
def fnStartOne(mytInstruction, myqReturn):
    ''' Transient thread to run one multiprocessing job on some other core.  
         This is NOT NOT NOT a daemon thread, but invoked once per job.
         Therefore, it must die for the program to exit cleanly.  
        Input: 
        - instruction tuple for the job.
        - queue on which to put() the name of this thread, so it gets
          join()ed and killed someday.
    '''
    nJobNum = mytInstruction.runid
    # Create mp job to run instruction.  
    qMpOut = multiprocessing.Queue()
    proc = multiprocessing.Process(target=fntDoOneCase
                    , args=(mytInstruction, qMpOut)
                    )
    with g.lockPrint:
        NTRC.ntracef(4, "FST1", "starting runid|%s| mpjob|%s| mpq|%s|" 
            % (nJobNum, proc, qMpOut))
    proc.start()
    
    # Get output from the mp job and transfer it back to my caller.
    tJobOutput = qMpOut.get()
    with g.lockPrint:
        NTRC.ntracef(3, "FST1", "finished runid|%s| mpjob|%s| output|%s|" 
            % (nJobNum, proc, tJobOutput))

    # Delete job from list.
    evDone = threading.Event()
    g.qJobMod.put(("del", evDone, nJobNum))
    
    # Ensure that my thread (this one) is killed someday.
    sGotName = threading.current_thread().name
    myqReturn.put(sGotName)
    with g.lockPrint:
        NTRC.ntracef(4, "FST1", "really end runid|%s| mpjob|%s| thr|%s|" 
            % (nJobNum, proc, sGotName))
    return(sGotName, nJobNum, g.ltJobs, g.nJobsCurrent)


#===========================================================
# f n D o O n e I n s t r u c t i o n 
@ntracef("DO1I")
def fnDoOneInstruction(mytInstruction, mynJob):
    '''
    '''
    evDone = threading.Event()
    # Wait for a job slot.
    while True:
        evDone.clear()
        g.qJobMod.put(("ask", evDone))
        evDone.wait()
        bIsOpening = g.qJobModAskDone.get()
        if bIsOpening: 
            break
        else:
            # I know this is icky.  I should set up an event in JobMod
            #  to wait for instead.  Maybe a new function: "askwait", 
            #  but not simple without stalling the JobMod thread.
            time.sleep(g.nPoliteTimer/1000.0)
            g.nWaitedForSlot += 1
            with g.lockPrint:
                NTRC.ntracef(4,"DO1I","proc slotwait times|%s|" 
                    % (g.nWaitedForSlot))

    g.qJobMod.put(("add", evDone, mynJob))
    # Launch the starter thread that then launches the multiprocessing job.
    sThrStartOneName = "T%03d" % mynJob
    thrStartOne = threading.Thread(target=fnStartOne, 
                args=(mytInstruction, g.qJobEnd))
    thrStartOne.name = sThrStartOneName
    # And save the thread name and object 
    #  so that it can be joined when done.
    fnThrDictAdd(sThrStartOneName, thrStartOne)
#    with g.lockThreadDict:
#        g.dName2Thread[sThrStartOneName] = thrStartOne
    with g.lockPrint:
        NTRC.ntracef(4, "DO1I", "startingOne thread|%s| njob|%s| name|%s|" 
            % (thrStartOne, mynJob, sThrStartOneName))
    # Finally, start the job-start thread.  
    thrStartOne.start()
    evDone.wait()


#===========================================================
#
@ntracef("DOAL")
def fnDoAllInstructions(mynCases):
    ''' Ordinary function to create list of instructions and send them 
         to fnDoOneInstruction().
    '''
    evDone = threading.Event()
    for nCase in range(1, mynCases+1):
        # Create job instruction.
        nJob = next(g.nJobCounter)
        # Have it print its own number.
        sIdent = "python3 -c 'print(%d)'" % (nJob)
        lCmdList = copy.deepcopy(g.lCommands)
        lCmdList.append(sIdent)
        sLogFilename = "testbr4_log%03d.log" % nCase
        tThisInst = tInstruction(cmdlist=lCmdList
                                , runid=nCase
                                , logdir="../tmp"
                                , logname=sLogFilename
                                , casedict={"nCase":nCase}
                                )
        with g.lockPrint:
            NTRC.ntracef(3, "DOAL", "proc doal inst|%s|" % (tThisInst,))
        fnDoOneInstruction(tThisInst, nJob)

    # If this is the end of all instructions, set flag.
    g.bLast = True          # Yes, sent the last instruction
    
    
"""
#===========================================================
# f n S e n d I n s t r u c t i o n s 
@ntracef("SNDI")
def fnSendInstructions(mynCases):
    ''' Create stream of instructions and start threads to execute them.  
         This is just an ordinary function.
       In the real version, this will accept one instruction at a time
         rather than creating its own stream.  
    '''
    evDone = threading.Event()
    for nCase in range(1, mynCases+1):
        # Wait for a job slot.
        while True:
            evDone.clear()
            g.qJobMod.put(("ask", evDone))
            evDone.wait()
            bIsOpening = g.qJobModAskDone.get()
            if bIsOpening: 
                break
            else:
                # I know this is icky.  I should set up an event in JobMod
                #  to wait for instead.  Maybe a new function: "askwait", 
                #  but not simple without stalling the JobMod thread.
                time.sleep(g.nPoliteTimer/1000.0)
                g.nWaitedForSlot += 1
                with g.lockPrint:
                    NTRC.ntracef(4,"SNDI","proc slotwait times|%s|" 
                        % (g.nWaitedForSlot))

        # Create job instruction.
        nJob = next(g.nJobCounter)
        g.qJobMod.put(("add", evDone, nJob))
        # Have it print its own number.
        sIdent = "python3 -c 'print(%d)'" % (nJob)
        lCmdList = copy.deepcopy(g.lCommands)
        lCmdList.append(sIdent)
        sLogFilename = "testbr4_log%03d.log" % nCase
        tThisInst = tInstruction(cmdlist=lCmdList
                                , runid=nCase
                                , logdir="../tmp"
                                , logname=sLogFilename
                                , casedict={"nCase":nCase}
                                )

        # Launch the starter thread that then launches the multiprocessing job.
        sThrStartOneName = "ThrOne-%06d" % nJob
        thrStartOne = threading.Thread(target=fnStartOne, 
                    args=(tThisInst, g.qJobEnd))
        thrStartOne.name = sThrStartOneName
        # And save the thread name and object 
        #  so that it can be joined when done.
        with g.lockThreadDict:
            g.dName2Thread[sThrStartOneName] = thrStartOne
        with g.lockPrint:
            NTRC.ntracef(4, "SNDI", "startingOne thread|%s| njob|%s| name|%s|" 
                % (thrStartOne, nJob, sThrStartOneName))
        # Finally, start the job-start thread.  
        thrStartOne.start()
#        evDone.wait()

    # If this is the end of all instructions, set flag.
    g.bLast = True          # Yes, sent the last instruction
"""

#===========================================================
# f n T h r T i c k 
@ntracef("TICK")
def fnThrTick(mynInterval):
    ''' Daemon thread to print time lines at some interval.
    '''
    if mynInterval > 0:
        while True:
            time.sleep(mynInterval)
            with g.lockPrint:
                NTRC.ntracef(0, "TICK", "")

#===========================================================

#===========================================================
# f n S t a r t u p 
@ntrace
def fnStartup():
    ''' Establish all the queues and daemon threads at startup time.
    '''
    g.lockPrint = threading.Lock()
    g.lockThreadDict = threading.Lock()
    
    g.nJobsCurrent = 0
    nRunInParallel = int(math.ceil(g.nParallel * ((100.0 + g.nOverbook)/100.0)))
    g.ltJobs = [None for _ in range(nRunInParallel)]
    with g.lockPrint:
        NTRC.ntracef(5, "STRT", "joblist|%s| |%s|" 
            % (g.ltJobs, len(g.ltJobs)))
    
    g.qJobEnd = queue.Queue()
    g.thrJobEnd = threading.Thread(target=fnEndOne)
    g.thrJobEnd.daemon = True
    g.thrJobEnd.start()
    
    g.qJobMod = queue.Queue()
    g.qJobModAskDone = queue.Queue()
    g.qJobModAddDone = queue.Queue()
    g.qJobModDelDone = queue.Queue()
    g.thrJobMod = threading.Thread(target=fnJobMod)
    g.thrJobMod.daemon = True
    g.thrJobMod.start()

    g.thrTick = threading.Thread(target=fnThrTick, args=(g.nTickInterval,))
    g.thrTick.daemon = True
    g.thrTick.start()
    
    
#===========================================================
#===========================================================

# M A I N 
@ntracef("MAIN")
def main():
    '''
    '''
    NTRC.ntracef(0, "MAIN", "Begin.")
    NTRC.ntracef(0, "MAIN", "TRACE  traceproduction|%s|" % NTRC.isProduction())

    # Get args from CLI and put them into the global data
    nArgs = len(sys.argv)
    if nArgs <= 1:
        print("Usage: %s nCases [nParallel [nOverbookPct [nTickInterval]]]"
                % (sys.argv[0]))
        return(1)       # Error.
    if nArgs > 1: g.nCases = int(sys.argv[1]) 
    if nArgs > 2: g.nParallel = int(sys.argv[2]) 
    if nArgs > 3: g.nOverbook = int(sys.argv[3]) 
    if nArgs > 4: g.nTickInterval = int(sys.argv[4]) 
    NTRC.ntracef(0, "MAIN", "cli argv|%s| len|%s|" 
            % (sys.argv, len(sys.argv)))
    

    # Create all the queues and such.
    fnStartup()

    # Send instructions for all the jobs.
    fnDoAllInstructions(g.nCases)

    # Wait for the last instruction to be at least queued.
    with g.lockPrint:
        NTRC.ntracef(5, "MAIN", "proc last instr|%s|" 
            % (g.bLast))
    while not fnbQEnd():
        time.sleep(g.nPoliteTimer/1000.0)
    g.qJobEnd.join()

    # If there are any threads left in the dict that should have been 
    #  finished by fnEndOne, nuke 'em now so we can exit cleanly.  
    lTmpDict = fnThrDictGetAll()
    dTmpDict = dict(lTmpDict)
    with g.lockPrint:
        NTRC.ntracef(3, "MAIN", "proc endof threaddict|%s|" 
            % (dTmpDict))
    with g.lockThreadDict:
        for sThrX, thrX in g.dName2Thread.items():
            with g.lockPrint:
                NTRC.ntracef(5, "MAIN", "proc join()ing|%s| |%s|" 
                    % (sThrX, thrX))
            thrX.join()
            with g.lockPrint:
                NTRC.ntracef(5, "MAIN", "proc join()ed |%s| |%s|" 
                    % (sThrX, thrX))

    with g.lockPrint:
        NTRC.ntracef(0, "MAIN", "End queued all runs ncases|%s|" % (g.nCases,))
        NTRC.ntracef(0, "MAIN", "End nslotwait|%s|" % (g.nWaitedForSlot))
    return(0)


#===========================================================
#
# E n t r y   p o i n t . 
if __name__ == "__main__":
    g = CG()                # Create class for global data.
    nResult = main()
    with g.lockPrint:
        NTRC.ntracef(0, "MAIN", "endstatus|%s|" % (nResult))
        NTRC.ntracef(0, "MAIN", "allthreads|%s|" % (threading.enumerate()))
    
    sys.exit(nResult)



#===========================================================



