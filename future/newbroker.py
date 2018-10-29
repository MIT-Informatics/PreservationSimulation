#!/usr/bin/env python
# -*-coding: utf8-*-
# newbroker.py
'''
One root process (like broker) starts a multiprocessing job.  
This job has two threads.
- 1: start all jobs ("StartJobs") from a list of instructions until 
    none remain, then sleep a short time.
- 2: finish all jobs ("FinishJobs") running until none remain, 
    then sleep a short time.  
Each case is a separate multiprocessing task (like listactor) that receives 
    a list of commands to execute.  
  A single listactor-like case itself a multiprocessing job 
    (mp jobs 3 thru nParallel).
    The case runs a sequence of subprocess jobs, one per command, 
      collects output.
      Case writes logfile where specified, returns list of output lines.
- For each command in the list, the subprocess job executes 
    that command via the shell and receives its stdout as a string, 
    which is splits into a list of lines.
- The multiprocessing job (listactor) appends the outputs of the several 
    commands, each output a list of lines, into a list, and queues 
    that list back to the single parent (broker). 
'''


'''
argv[1] = total number of cases to run; default 20.
argv[2] = max number to run simultaneously; default 8.
argv[3] = sleep interval in loop waiting for open process slot; 
            default 50 (msec).
argv[4] = max number of times to sleep waiting for an open process slot; 
            default = 100.
argv[5] = if present, causes debug printing of all the job output.
'''

import multiprocessing
import subprocess 
import threading
import time
import sys
import collections
import re
import itertools
from NewTraceFac import NTRC, ntrace, ntracef


# tuples
# Job process ID and output queue.
tJob = collections.namedtuple("tJob", "procid")
# Line returned from a single command
tLineOut = collections.namedtuple("tLineOut", "callstatus cmdstatus ltext ")
# List of lines returned from list of commands
tLinesOut = collections.namedtuple("tLinesOut", "procname, listoflists")


# ==================== subprocess user: do one line ====================

# f n D o O n e L i n e 
@ntracef("DO1L")
def fntDoOneLine(mysLine):
    """Execute one command.  
    
    Input: single line of command.  
    Output: tuple of the (Popen PIPE return code, command return code, list
     of output lines as strings.
    """
    proc = (subprocess.Popen(mysLine
        , stdout=subprocess.PIPE
        , close_fds=True            # The default anyway, I think.  
        , stderr=subprocess.DEVNULL
        , universal_newlines=True
        , shell=True)
        )
#    sProcOut = proc.stdout.read()
    (sProcOut, sProcErr) = proc.communicate()
    proc.stdout.close()
    if not sProcErr: sProcErr = ""
    sOut = "$ " + mysLine + "\n" + sProcOut.rstrip() + sProcErr.rstrip()
    nCmdStat = "none available - RBL"
    nReturnCode = proc.returncode
    lOut = sOut.split("\n")
    return(tLineOut(callstatus=nReturnCode, cmdstatus=nCmdStat, ltext=lOut))


# ==================== multiprocessing: DoOneCase ====================

# f n t D o O n e C a s e 
@ntracef("DO1")
def fntDoOneCase(mylInstruction, qToUse, mysLogfileName):
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
    lResults = []                   # list of strings
    for sLine in mylInstruction:
        if fnbDoNotIgnoreLine(sLine):
            tAnswer = fntDoOneLine(sLine)
            (nRtn, nErr, lResult) = tAnswer
            lResults.extend(lResult)
        else:
            lResults.extend([sLine])
    NTRC.ntracef(3, "DO1", "proc onecase lResults|%s|" % (lResults))
    
    fnWriteLogFile((lResults), mysLogfileName)
    lPrefix = [("BEGIN results from " + sWhoami)]
    lSuffix = [("ENDOF results from " + sWhoami)]
    lResultsToSee = ['\n'] + lPrefix + lResults + lSuffix + ['\n']
    tAnswers = tLinesOut(procname=sWhoami, listoflists=lResultsToSee)
    qToUse.put(tAnswers)
    qToUse.close()
    return (tAnswers)


# f n W r i t e L o g F i l e 
@ntracef("DO1")
def fnWriteLogFile(mylContents, mysFileName):
    sContents = '\n'.join(mylContents)
    with (open(mysFileName, "w")) as fhOut:
        print(sContents, file=fhOut)


# ==================== Global Data ====================

class CGlobal():
    """Data that is global, to this function, at least, so that it can
    shared between threads.  
    """
    ltJobs = list()     # Job numbers or None
    lockJobList = None  # 
    dId2Proc = dict()   # Map job number -> process object
    dId2Queue = dict()  # Map job number -> queue object
    nParallel = 4       # Limit on jobs running in parallel (on separate CPUs)
    bThatsAllFolks = False  # All cases done, ran out of instructions.
    nCasesTotal = 0     # Nr of instructions total, all started.
    nCasesStarted = 0   # How many cases started so far.  #DEBUG
    nCasesDone = 0      # How many cases done (finished) so far. #DEBUG
    llsFullOutput = list()  # Output for all test cases.
    nCases = 1          # DEBUG
    nWaitedForSlot = 0  # DEBUG
    bDebugPrint = False # Print output of all jobs?


# ==================== multiprocessing: RunEverything ====================

def fnRunEverything(gl, llsInstructions, nWaitMsec, nWaitHowMany
                , myqFullOutput):

    # Fill the list of jobs with empties.
    for i in range(gl.nParallel + 1): gl.ltJobs.append(None)

    gl.lockJobList = threading.Lock()

    # Create new threads
    NTRC.ntracef(5, "RUN", "proc make thread instances")
    thrStart = CStartAllCases(gl, gl.nWaitMsec, gl.nWaitHowMany, llsInstructions, )            # NEED ARGS
    thrEnd = CEndAllCases(gl, myqFullOutput, gl.nWaitMsec, )   # NEED ARGS
    gl.llsFullOutput = [["",""]]

    # Start new Threads
    thrStart.start()
    thrEnd.start()

    # Wait until all jobs have started and finished.
    thrStart.join()
    thrEnd.join()


# ==================== thread: DoAllCases ====================

class CStartAllCases(threading.Thread):
    """pseudocode:
    arg gives list of instructions,
     each instruction is list of command lines
    foreach instruction in list
      wait for opening
      create queue for result
      create process to do instruction
      append (process,queue) to job list
    """


    #@ntracef("STRT")
    def __init__(self, gl 
                , mynWaitMsec, mynWaitHowMany
                , myllInstructions
                ):
        threading.Thread.__init__(self)
        self.gl = gl
        self.nWaitMsec = mynWaitMsec
        self.nWaitHowMany = mynWaitHowMany
        self.nCounter = itertools.count(1)
        self.nProcess = 0
        self.llInstructions = myllInstructions
        NTRC.ntracef(5, "STRT", "exit init gl|%s| instrs|%s|" 
                % (self.gl, self.llInstructions))


    @ntracef("STRT")
    def run(self):
        while (fnbWaitForOpening(self.gl, self.nWaitMsec, self.nWaitHowMany)
                ):
            NTRC.ntracef(3, "STRT", "proc doallcases slot is avail nprocess|%s| " 
                        % (self.nProcess))

            # How many active jobs?  If maxed out, wait for an empty slot
            #  and to it again.
            with self.gl.lockJobList:
                nActive = len([tJob for tJob in self.gl.ltJobs if tJob])
            if nActive >= self.gl.nParallel:
                NTRC.ntracef(3, "STRT", "proc startall slots full nActive|%s|" 
                            % (nActive))
                time.sleep(self.nWaitMsec / 1000.0)
                continue

            # L O C K 
            with gl.lockJobList:
                # Find an empty slot in the jobs list.
                lEmptySlots = [idx for (idx,x) in enumerate(gl.ltJobs) 
                                if not x]
                idxEmpty = lEmptySlots[0]

                # Instruction list for this job.
                #  If the list is empty, then we are done here.
                # BEWARE: instruction list might be a generator, 
                #  cannot test length.  ONLY IRL
                # StopIteration for generator; IndexError for list.
                try:
                    lLines = self.llInstructions.pop(0)
                except(StopIteration, IndexError):
                    self.gl.bThatsAllFolks = True
                    self.gl.nCasesTotal = self.gl.nCasesStarted
                    NTRC.ntracef(1, "STRT", "proc startall "
                                "exhausted instructions nprocess|%s|" 
                                % (self.nProcess))
                    break

                # Create resources for the job.        
                qOut = multiprocessing.Queue()
                nJob = next(self.nCounter)
                sLogFile = "foo" + str(nJob) + ".log"        # TEMP
                proc = multiprocessing.Process(target=fntDoOneCase
                                , args=(lLines, qOut, sLogFile, )
                                )
                tThisJob = tJob(procid=nJob, )

                # Save job in empty slot of list, and save dict
                #  entries to get proc and queue.
                self.gl.dId2Proc[nJob] = proc
                self.gl.dId2Queue[nJob] = qOut
                # Save job info in jobs list.
                self.gl.ltJobs[idxEmpty] = tThisJob
                NTRC.ntracef(3, "STRT", "proc startall go slot|%s| njob|%s|" 
                            % (idxEmpty, nJob))

                proc.start()
                self.nProcess += 1
                self.gl.nCasesStarted += 1
            # E N D L O C K 

# ==================== thread: EndAllCases ====================

class CEndAllCases(threading.Thread):
    """pseudocode:
    while forever
        get list of (job,queue) *shared data*
        while noempty, foreach in list of job.notalive
            join job to make sure it's dead
            empty queue
            append output to big string
            pop job from list *shared data*
        if empty
            if instruction list empty
                return big string
            else
                wait a few milliseconds
    """

    #@ntracef("END")
    def __init__(self, gl, myqForOutput
                , mynWaitMsec
                ):
        threading.Thread.__init__(self)
        self.gl = gl
        self.nWaitMsec = mynWaitMsec
        self.qForOutput = myqForOutput
        self.llsFullOutput = list()
        NTRC.ntracef(5, "END", "exit init gl|%s| qout|%s| wait|%s|" 
                    % (self.gl, self.qForOutput, self.nWaitMsec))


    @ntracef("END")
    def run(self):
        NTRC.ntracef(5, "END", "proc run ltJobs|%s|" % (gl.ltJobs))
        nCasesDone = 0
        while True:
            # L O C K 
            with self.gl.lockJobList:
                NTRC.ntracef(3, "END", "proc ltJobs|%s|" % (gl.ltJobs))
                ltActiveJobs = [(idx,tJob) for idx,tJob in 
                                enumerate(gl.ltJobs) if tJob]
                NTRC.ntracef(3, "END", "proc ltActiveJobs|%s|" % (ltActiveJobs))
                for idxtJob in ltActiveJobs:
                    idx,tJob = idxtJob
                    nJob = tJob.procid
                    proc = self.gl.dId2Proc[nJob]
                    if not proc.is_alive():
                        NTRC.ntracef(3, "END", "proc endall found done "
                                    "job|%s||%s| alive?|%s|" 
                                    % (idxtJob, proc, proc.is_alive()))
                        # Job listed as still baking but reports that it is done.
                        # Wait until it is fully baked.
                        proc.join()
                        # Get its output for the full debug list.
                        queue = self.gl.dId2Queue[nJob]
                        lQOutput = []
                        while not queue.empty():
                            lLinesOut = queue.get().listoflists
                            lQOutput.append(lLinesOut)
                        queue.close()
                        if gl.bDebugPrint:
                            NTRC.ntracef(5, "END", "proc lQOutput from q|%s|" 
                                            % (lQOutput))
                            self.llsFullOutput.extend(lQOutput)
                            NTRC.ntracef(5, "END", "proc lOutput from q|%s|" 
                                        % (self.llsFullOutput))
                        # Remove job from active list.
                        gl.ltJobs[idx] = None
                        nCasesDone += 1
                        self.gl.nCasesDone += 1
                        NTRC.ntracef(3, "STRT", "proc job completed |%s|" 
                                    % (self.gl.nCasesDone))

                NTRC.ntracef(3, "END", "proc end of for activejobs"
                            " thatsall?|%s| ndone|%s| nstarted|%s|" 
                            % (self.gl.bThatsAllFolks
                            , self.gl.nCasesDone, self.gl.nCasesStarted))
                if (self.gl.bThatsAllFolks 
                    and self.gl.nCasesDone == self.gl.nCasesTotal):
                    break
                else:
                    NTRC.ntracef(3, "END", "proc endall waiting1, ndone|%s|" 
                                % (nCasesDone))
                    time.sleep(self.nWaitMsec / 1000.0)
                    continue
            # E N D L O C K 

        # llsFullOutput is a list of list of strings, where
        #  the inner list is lines output from commands for
        #  one job, more or less, with prefix and suffix 
        #  and comments, too.
        # Paste the whole thing together into a yuge list of lines.
        if gl.bDebugPrint:
            sFullOutput = ""
            for lJobOut in self.llsFullOutput:
                sJobOut = "\n".join(lJobOut)
                sFullOutput += sJobOut
            NTRC.ntracef(5, "END", "proc sFullOutput|%s|" % (sFullOutput))
        self.qForOutput.put(self.llsFullOutput)
        self.qForOutput.close()


# ==================== utilities ====================

# f n b D o N o t I g n o r e L i n e 
@ntracef("UTIL", level=5)
def fnbDoNotIgnoreLine(mysLine):
    '''
    True if not a comment or blank line.
    '''
    # Ignore comment and blank lines, but take all others.
    return (not re.match("^\s*#", mysLine)) and (not re.match("^\s*$", mysLine))


# f n n H o w M a n y A l i v e 
@ntracef("MANY", level=5)
def fnnHowManyAlive(gl):
    nAlive = len([1 for tJob in gl.ltJobs if tJob 
                and gl.dId2Proc[tJob.procid].is_alive()])
    return nAlive


# f n b W a i t F o r O p e n i n g 
@ntracef("WAIT")
def fnbWaitForOpening(gl, mynWaitTimeMsec, mynWaitMax):
    nWait = mynWaitMax
    while nWait:
        nAlive = fnnHowManyAlive(gl)
        if nAlive < gl.nParallel:
            break
        else:
            nWait -= 1
            gl.nWaitedForSlot += 1
            if gl.bDebugPrint:
                print(".", end='')          # DEBUG
            time.sleep(mynWaitTimeMsec / 1000.0)
            NTRC.ntracef(5, "WAIT", "proc waitforopening timesleft|%s|" 
                        % (nWait))
    if nWait <= 0:
        raise ValueError("Waited too long for empty job slot.")
    else:
        return (nWait > 0)


# ==================== in main process ====================

# ==================== m a i n N e w B r o k e r ====================
@ntrace
def mainNewBroker(gl,):

    NTRC.ntrace(3, "proc params ncases|%s| nparallel|%s| "
                    "nwaitmsec|%s| nwaitmany|%s|" 
                % (gl.nCases, gl.nParallel, gl.nWaitMsec, gl.nWaitHowMany))
    
    # Main loop
    
    # Create list of instructions.  Each instruction is a list of 
    #  command strings.
    lLinesTemp = [sLine.lstrip() 
                for sLine in sTempListOfCommands.split('\n')
                ]
    llsInstructionsTemp =  [lLinesTemp] * gl.nCases

    # Subprocess to start all case jobs.
    qOut = multiprocessing.Queue()
    jRunJobs = multiprocessing.Process(target=fnRunEverything, name="RunJobs"
                , args=(gl, llsInstructionsTemp
                        , gl.nWaitMsec, gl.nWaitHowMany
                        , qOut))
    jRunJobs.start()    # Start subproc that does the work
    jRunJobs.join()     #  and wait for it to finish.
    llOut = qOut.get()  # Get massive output list.
    qOut.close()
    return llOut


# m a i n 
def main(gl):
    """ Temp hack to make instructions for debugging.
    """
    NTRC.ntrace(0, "Starting...")
    llFullOutput = mainNewBroker(gl,)

    if gl.bDebugPrint:
        # Print all the crap that comes back.  
        print("---------begin cases----------")
        for lCase in llFullOutput:
            sCaseOut = ""
            NTRC.ntrace(3, "proc fromq lCase|%s|" % (lCase))
            '''
            for lCmd in lCase:
                sCmdOut = "\n".join(lCmd)    # out from a single command
                sCaseOut += sCmdOut
            '''
            sCaseOut = '\n'.join(lCase)
            print(sCaseOut)
            print("--------------")
        print("---------end cases----------")
        #NTRC.ntrace(5, "proc main sfulloutput|%s|" % (sFullOutput))
    NTRC.ntrace(0, "Finished nWaitedForSlot|%s|" % (gl.nWaitedForSlot))


# E n t r y   p o i n t 
if __name__ == "__main__":

    gl = CGlobal()      # Instantiate global data region.  

    # Get CLI args. 
    # Default values.
    gl.nCases = 20 
    gl.nParallel = 8
    gl.nWaitMsec = 50
    gl.nWaitHowMany = 100
    nArgs = len(sys.argv)
    if nArgs > 1: gl.nCases = int(sys.argv[1]) 
    if nArgs > 2: gl.nParallel = int(sys.argv[2]) 
    if nArgs > 3: gl.nWaitMsec = int(sys.argv[3]) 
    if nArgs > 4: gl.nWaitHowMany = int(sys.argv[4]) 
    if nArgs > 5: gl.bDebugPrint = True

    sTempListOfCommands = '''
        date +%Y%m%d_%H%M%S.%3N
        # this is comment 1
        ls | head -3
        pwd
        # this is comment 2
        
        # and a blank line before and after this one
        
        python3 -V
        cat /proc/version
        cat /proc/cpuinfo | grep processor |wc -l   
        ps | grep python | grep -v grep
        date +%Y%m%d_%H%M%S.%3N
    '''
    sTempListOfCommands = '''
        date +%Y%m%d_%H%M%S.%3N
    '''

    sys.exit(main(gl))

#END
