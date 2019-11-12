#/usr/bin/python3
# newbroker4.py
#               RBL 20191106

'''
Thread/Queue based design for newbroker4        RBL 20191106
Stick to Raymond Hettinger's principles of queueing instead of locking. 
Except oops on the ntrace routines which don't use queued print, so 
we still have to lockprint around them.  Sorry about that.  Work in progress. 


------------------
------------------
job process

do all the usual stuff
send output in msg to q param


------------------
sendinstructions

while instructions available:
get iterator of instructions
wait for slot
create thread to handle job
create queue for return data
add to list of jobs
start job thread, args=tInstr, thread obj
endwhile
set last instr flag


------------------
function startonejob thread

create multiprocessing job
create mp queue for return data
start job
wait for return data on mp q
forward data, incl job number, thread id, etc.
delete job from list
send your own thread object to killallmonstrers


------------------
startup

create jobslist

create qinstructions
create jobstart thread
set daemon

create qjobend
create jobend thread
set daemon

start jobstart thread
start jobend thread

create qJobmod
create jobsmod thread
create qJobadddone
create qJobdeldone
create qJobaskdone
start jobsmod thread

call sendinstructions

join qinstructions
join qjobend

end


------------------
modify jobslist

this is a separate thread but calls to it are essentially synchronous:
callers will always wait for return info on the particular qJobxxxdone queue.
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

'''
maybe there's another way.  don't keep a list of jobs, but only a counter.
ops: ask if still room, add one, subtract one.
the jobs themselves have to keep context to return to the ender.
start:
while forever; ask if still room; wait for return q; break if room
send add 1 to counter
start job
end:
get job info from qjobend
send subtract 1 to counter
log job info

'''

'''
well, that worked, but the threads don't know when to exit.  start would 
be easy, but how would end know that the last job jsut passed by?  

new approach: make StartOne a function, not a daemon thread, so that it 
exits when the function exits.  one thread per job.  

meter the issuing of instructions so that waiting for an empty core is
done by the instruction generator stream.  then the job-start function
has to wait only for the job to finish.  metering still done only with
the counter, same as last time.  increment counter when sending the 
instruction to start, decrement the counter when the job is completely 
finished.  

i don't think we need to join all those thousands of threads; i hope that 
non-persistent threads exit when the function exits.  if not, then the 
instruction generator that creates the thread can join it when the function
returns.

StartOne: args=tInstruction, return queue
decode the instruction tuple
create the multiprocessing job
create the multiprocessing queue for answers
start the multiprocessing job with cmdlist and queue
wait for return info in the mp queue
send the data to the generator on return queue

InstructionGenerator:
for list of instructions:
wait for opening
assign job number and other such
assign logfilename
increment core counter
make instruction tuple
create thread to start job
set thread name and other stuff
start thread
receive data from queue
correlate returned data with pending jobs
remove job from list
join the thread to kill it
decrement core counter

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
# Sadistics on how many times we waited for something
tWaitStats = collections.namedtuple("tWaitStats", "ncases slot done inst")


#===========================================================
# class   C G   f o r   g l o b a l   d a t a 
class CG(object):
    ''' Global data.
    '''
    # Options that should be passed thru to main.py.
    # All the interesting options should be None here, so that 
    #  they are removed from the selection dictionary before
    #  it is handed to MongoDB.  (No longer a consideration.)
    #  If the user doesn't specify it on the command line, 
    #  then it is not a selection criterion for searching.
    nRandomSeeds = 21
    sRandomSeedFile = "randomseeds.txt"

    # Administrative options to guide broker's behavior.
    nCores = 8          # Default, overridden by NCORES env var.
    nCoreTimer = 50     # Wait for a free core (msec).
    nPoliteTimer = 20   # Wait between sequential launches, in milliseconds.
    nTestLimit = 0      # Max nr of runs executed for a test run, 0=infinite.
    sTestCommand = "N"  # Should just echo commands instead of executing them?
    sTestFib = "N"      # Should use Fibonacci calc instead of real programs?
    sListOnly = "N"     # Just list out all cases matching the stated criteria.  
                        #  but don't execute them.
    sRedo = "N"         # Force cases to be redone (recalculated)?

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
    dId2Proc = dict()   # Map job number -> process object
    dId2Queue = dict()  # Map job number -> queue object
    
    nParallel = 4       # Limit on jobs running in parallel (on separate CPUs)
                        #  (overridden by nCores).
    nOverbook = 0       # Percentage by which we should overbook the cores. 
                        #  E.g., 0 is not overbooked, 100 is double-booked, 
                        #  and 50 for 1.50 times as many jobs as cores.
    bThatsAllFolks = False  # All cases done, ran out of instructions.
    nCasesTotal = 0     # Nr of instructions total, all started.
    nCasesStarted = 0   # How many cases started so far.  # DEBUG
    nCasesDone = 0      # How many cases done (finished) so far. # DEBUG
    llsFullOutput = list()  # Output for all test cases.
    nCases = 1          # DEBUG
    nWaitedForSlot = 0  # DEBUG
    nWaitedForDone = 0  # DEBUG
    nWaitedForInstr = 0 # DEBUG
    bDebugPrint = False # Print output of all jobs? (obsolete) 
    thrStart = None
    qInstructions = queue.Queue()
    thrEnd = None
    qJobEnd = None    
    thrJobMod = None    
    qJobMod = None
    dName2Thread = dict()
    
    nJobsCurrent = 0
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
         for the event to be declared true.  If they need the information
         returned in the return queue, they must wait for the event.
    '''
    while(True):
        [sCommand, evDone, *xMore] = g.qJobMod.get()
        g.qJobMod.task_done()
        with g.lockPrint:
            NTRC.ntracef(3, "JMOD", "JobMod args|%s| |%s| |%s|" 
            % (sCommand, evDone, xMore))
        with g.lockPrint:
            NTRC.ntracef(5, "JMOD", "JobMod entry joblist|%s| |%s|" 
                % (g.ltJobs, len(g.ltJobs)))
        if sCommand is None: break

        if sCommand == "ask":
            if g.nJobsCurrent < len(g.ltJobs):
                result = True
            else:
                result = False
            with g.lockPrint:
                NTRC.ntracef(4, "JMOD", "JobMod Ask result|%s|" % result)
            g.qJobModAskDone.put(result)

        elif sCommand == "add":
            lEmptySlots = [idx for (idx,x) in enumerate(g.ltJobs) 
                            if not x]
            assert len(lEmptySlots) > 0, ("Supposed to be an empty slot"
                        "for new case, but I can\'t find one.")
            idxEmpty = lEmptySlots[0]
            nTmpJobnum = xMore[0]
            g.ltJobs[idxEmpty] = nTmpJobnum
            g.nJobsCurrent += 1
            g.qJobModAddDone.put(g.nJobsCurrent)
            with g.lockPrint:
                NTRC.ntracef(5, "JMOD", "JobMod add end joblist|%s| |%s|" 
                    % (g.ltJobs, len(g.ltJobs)))

        elif sCommand == "del":
            nTmpJobnum = xMore[0]
            with g.lockPrint:
                NTRC.ntracef(5, "JMOD", "JobMod del entry joblist|%s| |%s|" 
                    % (g.ltJobs, len(g.ltJobs)))
            lFoundSlot = [idx for (idx,x) in enumerate(g.ltJobs) 
                            if x == nTmpJobnum]
            assert len(lFoundSlot) == 1, ("Did not find slot to match"
                        "case number|%s|" % nTmpJobnum)
            idxFound = lFoundSlot[0]
            g.ltJobs[idxFound] = None
            g.nJobsCurrent -= 1
            g.qJobModDelDone.put(g.nJobsCurrent)

        else:
            assert False, ("Bad command to fnJobMod: %s" % sCommand)
        evDone.set()

#===========================================================



#===========================================================
# f n S t a r t u p 
@ntrace
def fnStartup():
    g.lockPrint = threading.Lock()
    
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


#===========================================================
# f n E n d O n e 
@ntracef("END1")
def fnEndOne():
    ''' Join (to kill) every thread that sends its thread object here.
         This is a daemon thread.
    '''
    while True:
        sThrToKill = g.qJobEnd.get()
        thrToKill = g.dName2Thread[sThrToKill]
        if thrToKill.is_alive():
            thrToKill.join()
            bAlive = True
        else:
            bAlive = False
        with g.lockPrint:
            NTRC.ntracef(3, "END1", "proc fnEndOne thread|%s| "
                "name|%s| was alive}%s|" 
                % (thrToKill, sThrToKill, bAlive))
        g.qJobEnd.task_done()


#===========================================================
# f n S t a r t O n e 
@ntracef("FST1")
def fnStartOne(mytInstruction, myqReturn, myThreadObj):
    ''' Thread to run one multiprocessing job on some other core.  
         This is NOT a daemon thread, but invoked once per job.
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
    myqReturn.put(myThreadObj)
    with g.lockPrint:
        NTRC.ntracef(4, "FST1", "really the end runid|%s| mpjob|%s|" 
            % (nJobNum, proc))


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
                    args=(tThisInst, g.qJobEnd, sThrStartOneName))
        # And save the thread name and object 
        #  so that it can be joined when done.
        g.dName2Thread[sThrStartOneName] = thrStartOne
        with g.lockPrint:
            NTRC.ntracef(4, "SNDI", "startingOne thread|%s| njob|%s| name|%s|" 
                % (thrStartOne, nJob, sThrStartOneName))
        # Finally, start the job-start thread.  
        thrStartOne.start()
        evDone.wait()

    # If this is the end of all instructions, set flag.
    g.bLast = True          # Yes, sent the last instruction


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
    if nArgs > 1: g.nCases = int(sys.argv[1]) 
    if nArgs > 2: g.nParallel = int(sys.argv[2]) 
    if nArgs > 3: g.nOverbook = int(sys.argv[3]) 

    fnStartup()

    fnSendInstructions(g.nCases)
    while not fnbQEnd():
        time.sleep(g.nPoliteTimer/1000.0)
#    g.qInstructions.join()
    g.qJobEnd.join()

    NTRC.ntracef(0, "MAIN", "End queued all runs ncases|%s|" % (g.nCases,))






#===========================================================
#
# E n t r y   p o i n t . 
if __name__ == "__main__":
    g = CG()
    sys.exit(main())



#===========================================================





#===========================================================





#===========================================================

