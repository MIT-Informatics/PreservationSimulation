#!/usr/bin/env python3
# -*-coding: utf8-*-
# newbroker6workers.py
#                   RBLandau 20200710

''' Multiprocessing job stream executor.

    Have a number of computing jobs that can be executed
     in parallel on a multi-core machine?  Express those
     jobs as a sequence of CLI commands and feed the shell
     commands to this class.  Put the instructions for each
     job in a tuple, put the tuples into the queue of jobs
     to be done.  When you have queued the last instruction, 
     tell the here to close all the multi-processes.  
    Each job's results go into a log file that you specify, 
     and there is an option for getting a real-time copy
     of the results as the jobs finish, for use in a 
     thermometer display, for instance, or just a listing
     to give the human watchers confidence in progress.  
    The job instructions may be queued at whatever rate
     is convenient to the caller.  Instructions are 
     typically small, so memory requirements are minimal.  
    
    Processes sequences of instructions as shell commands
     one line at a time in sequence, collects the output.
    Lines are time stamped and presented with command
     followed by output.  Timestamps are in milliseconds.  
    The output is sent to a specified log file and to a 
     specified multiprocessing queue (for logging, thermometer
     assessment, whatever).  
'''

''' class CWorker creates and manages the multiprocessing jobs.
    The caller specifies how many parallel jobs to be run, 
     the name of the input queue on which job instructions are
     queued for execution, and the name of the output queue, 
     if any, to receive a copy of the output.
    Job instructions specify the 
'''

''' Function chain:
    DoManyJobs: take job items from queue, process them in turn.  
        if a job contains no commands, that is the signal to exit.
    DoOneJob: execute the command stream of the job, send
        the resulting output to the specified log file and to 
        the specified multiprocessing queue.  
    DoOneCmdList: execute the sequence of shell commands, 
        return the resulting commands and output.  
    DoOneCmdLine: execute a single shell command and collect the output.
        mark the output lines with a timestamp.  

    Additional function: 
    Default receiver for the output queue, to be run as a separate
     multiprocessing process.  This default version sends the output
     to stdout and uses lockPrint to attempt to make it thread-safe.
'''

import multiprocessing as mp
import subprocess as sp
import collections
import datetime
import sys
import re
from NewTraceFac import NTRC, ntrace, ntracef
import pathlib


# Named Tuples to communicate results of command lines.  
# Line returned from a single command
tLineOut = collections.namedtuple("tLineOut"
                , "callstatus cmdstatus ltext ")
# List of lines returned from list of commands
tLinesOut = collections.namedtuple("tLinesOut"
                , "procname, listoflists")
# Complete instruction info to pass to DoCase.
tInstruction = collections.namedtuple("tInstruction"
                , "cmdlist logdir logname")


# ================================================
# c l a s s   C W o r k e r s 
class CWorkers(object):
    ''' Create and manage a collection of multiprocessing processes
         to execute a set of (CLI shell) jobs on multiple cores in 
         parallel.  Uses the standard Python3 multiprocessing package.  
        
        Inputs: 
        - nservers: number of multiprocessing processes to create as
            workers for the sequence of jobs.  This may be equal to, 
            or smaller, or slightly larger than the number of cores
            available, depending on local needs.  
            The number of cores can be read from 
            multiprocessing.cpu_count().
        - qinputjobs: a multiprocessing queue into which job
            instructions will be fed.  The instructions must be 
            in the form of a tInstruction named tuple, defined
            here. The shell commands are in a list of strings, 
            each string being one shell command.  
        - qoutputdata: a managed multiprocessing queue that, if not
            None, will be sent a copy of the output of each job
            as the job completes.  
        - outputreceiver: if not None, a multiprocessing process to 
            process the stream of job results in the qoutputdata 
            queue.  

        To start: Create an instance of this class.  The multiple
         processes will be created and started in the construction.  
        To stop: After all the job instructions have been *queued*
         (but not necessarily executed, of course), call 
         cworkerinstance.Close().
        
        Caution: a job instruction with an empty list of shell 
         commands will cause the worker process that takes that
         command to exit.  
    '''    
    qJobs = None
    qOutput = None  # BEWARE! This needs to be accessed statically for each job.
    nParallel = None
    lprocWorkers = None
    procOutput = None

    # Poison messages to cause workers to exit.
    tEndJobMsg = tInstruction(cmdlist="", logdir='', logname='')
    tEndOutMsg = tLinesOut(listoflists='', procname='')

    @ntrace
    def __init__(self, nservers, qinputjobs, qoutputdata=None, outputreceiver=None):
        self.nParallel = nservers if nservers>0 else 8
        self.qJobs = qinputjobs
        CWorkers.qOutput = qoutputdata
        
        self.m_CreateWorkers()
        self.m_CreateOutputReceiver()


    # ================================================
    # m _ C r e a t e W o r k e r s 
    @ntrace
    def m_CreateWorkers(self):
        ''' Create worker pool and start them all. 
            The number of workers was specified in the class construction.
        '''
        lProcs = []
        for iProcessNum in range(self.nParallel):
            proc = mp.Process(target=doManyJobs
                    , args=(self.qJobs,)
                    , name=f'CWorker-{iProcessNum+1}'
                    )
            lProcs.append(proc)
            proc.start()
        NTRC.ntrace(3, "proc worker|%s| started on q|%s|" % (proc, self.qJobs))
        self.lprocWorkers = lProcs   # Save a list of all workers.
        return lProcs


    # ================================================
    # m _ C r e a t e O u t p u t R e c e i v e r 
    @ntrace
    def m_CreateOutputReceiver(self, myfReceiver=None):
        ''' Make one more async process to receive job outputs. 
            If there is no output queue at all, then there will be no 
             receiver process.
            If the user does not specify a function for the receiver, 
             the default receiver will be used.
        '''
        if CWorkers.qOutput:
            if not myfReceiver:
                # Take default if none specified.
                procRcvrToday = defaultReceiveOutput
            else:
                procRcvrToday = myfReceiver
            procReceiver = mp.Process(target=procRcvrToday, 
                                args=(CWorkers.qOutput,))
            procReceiver.start()
            NTRC.ntrace(3, "proc rcvr|%s||%s| started on q|%s|" 
                    % (procRcvrToday, procReceiver, CWorkers.qOutput))
            self.procOutput = procReceiver
        else:
            self.procOutput = None
        return self.procOutput


    # ================================================
    # m _ C l o s e W o r k e r s 
    @ntrace
    def m_CloseWorkers(self):
        ''' Nuke all the worker processes.
            Send please-kill-yourself messages to all
             and wait for them all to exit.
            NB: The user must wait for the last job instruction to be sent
             (to the jobs queue) before invoking this, so that the 
             end messages come after all work has been completed.  
        '''
        for _ in range(self.nParallel):
            self.qJobs.put(self.tEndJobMsg)
        for proc in self.lprocWorkers:
            proc.join()


    # ================================================
    # m _ C l o s e O u t p u t R e c e i v e r 
    @ntrace
    def m_CloseOutputReceiver(self):
        ''' Nuke the output receive process, if any. '''
        qOut = CWorkers.getOutputQueue()
        if qOut:
            qOut.put(self.tEndOutMsg)
            # And wait for the last output.
            self.procOutput.join()


    # ================================================
    # C l o s e 
    @ntrace
    def Close(self):
        ''' Close all async processes that we started.
            This is the routine that the user should invoke.
        '''
        self.m_CloseWorkers()
        self.m_CloseOutputReceiver()


    # ================================================
    # g e t O u t p u t Q u e u e 
    @staticmethod
    @ntrace
    # g e t O u t p u t Q u e u e 
    def getOutputQueue():
        ''' Return the managed multiprocessing queue used
            for output to a receiver.  This is used by 
            each job to determine whether to send a copy
            of the job output, and if so where.
            '''
        return CWorkers.qOutput


# END of class CWorkers


# ================ Functions that run in external processes =============
# ======================== and actually do work =========================

# ==================== subprocess user: DoOneCmdLine ====================
# f n t D o O n e C m d L i n e 
@ntracef("DO1L")
def fntDoOneCmdLine(mysLine):
    """Execute one single-line command.  
    
    Input: single line of command.  
    Output: tuple of the (Popen PIPE return code, command return code, list
     of output lines as strings.
    Contributes line(s) to be in log file.
     Input lines and the first line of output blocks have timestamps;
     other lines in output blocks are indented with spaces.  
    """
    sTimeBegin = fnsGetTimestamp()
    proc = (sp.Popen(mysLine
        , stdout=sp.PIPE
        , close_fds=True            # The default anyway, I think.  
        , stderr=sp.DEVNULL
        , universal_newlines=True
        , shell=True)
        )
    (sProcOut, sProcErr) = proc.communicate()
    proc.stdout.close()
    if not sProcErr: sProcErr = ""
    sTimeEnd = fnsGetTimestamp()
    
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
    
    return(tLineOut(callstatus=nReturnCode, cmdstatus=nCmdStat
        , ltext=lOut))


# ==================== multiprocessing: DoOneCmdList ====================
# f n t D o O n e C m d L i s t 
@ntracef("DOCL")
def fnlsDoOneCmdList(mylLines):
    """Input: list of instructions generated for this case; 
     multiprocessing queue through which to report results.
    
    Remove blanks, comments, etc., from the instructions.  Each line that
     is not blank or comment is a command to be executed.  Blanks and 
     comments are written directly into the output.

    Output: list of commands and their output, to be logged and 
     sent to the supplied queue.
    """

    # Process all command lines of the instruction list and collect results.  
    lResults = []               # list of strings
    for nLine, sLine in enumerate(mylLines):
        if fnbDoNotIgnoreLine(sLine):
            # Genuine line; execute and collect answer line(s).  
            tAnswer = fntDoOneCmdLine(sLine)
            (nRtn, nErr, lResult) = (tAnswer.callstatus
                                    , tAnswer.cmdstatus
                                    , tAnswer.ltext)
            lResults.extend(lResult)
            NTRC.ntracef(4, "DOCL", "proc DoOneList line|%s| "
                        "lResult|%s|" 
                        % (nLine, lResult))
        else:
            # Comment or blank line; just append to results.
            lResults.extend([("-"*len(fnsGetTimestamp()))
                            , (fnsGetTimestamp() + "  " + sLine)])
            NTRC.ntracef(4, "DOCL", "proc DoOneCase line|%s| "
                        "comment|%s|" 
                        % (nLine, sLine))
    return lResults


# ==================== multiprocessing: DoOneJob ====================
# f n D o O n e J o b 
@ntracef("DO1J")
def fnDoOneJob(mytInstruction):
    ''' Execute a single job: 
        Do all lines.  
        Log results and convey to output queue.
    '''
    # Get my name and number for ident.
    sWhoami = mp.current_process().name
    NTRC.ntracef(3, "DO1J", "proc procname|%s|" % (sWhoami))
    nProc = fnsGetProcessNumber(sWhoami)

    # Unpack instruction command list and other items.
    lInstructions = mytInstruction.cmdlist
    (sLogfileDir, sLogfileName) = (mytInstruction.logdir
                                , mytInstruction.logname)
    qToUse = CWorkers.getOutputQueue()

    lResults = fnlsDoOneCmdList(lInstructions)
    # Send official results to the log file.
    fnWriteLogFile((lResults), sLogfileDir, sLogfileName)

    # If an output queue specified, pack up the answer and send it.
    if qToUse:
        # And send a copy of results to the specified output queue.
        lPrefix = [("BEGIN results from " + sWhoami)]
        lSuffix = [("ENDOF results from " + sWhoami)]
        lResultsToSee = ['\n'] + lPrefix + lResults + lSuffix + ['\n']
        tAnswers = tLinesOut(procname=sWhoami, listoflists=lResultsToSee)
        qToUse.put(tAnswers)
    

# ==================== multiprocessing: DoManyJobs ====================
# f n D o M a n y J o b s 
@ntracef("DOMJ")
def doManyJobs(myqJobs):
    ''' This is the guy who gets called as a job worker
        Read a job from input queue.
        If it is a real instruction, do it.
        If it is an end code, exit.
        '''
    while True:
        tInstructionJob = myqJobs.get()
        sWhoami = mp.current_process().name
        NTRC.ntracef(3, "DOMJ", "proc DoManyJobs|%s| qget|%s|" % (sWhoami, tInstructionJob,))
        if tInstructionJob.cmdlist:
            result = fnDoOneJob(tInstructionJob)
        else:
            sys.exit(0)


# ==================== multiprocessing: DefaultReceiveOutput ====================
# This is an instance of mp.Process(), not part of a mp.Pool().
#
# d e f a u l t R e c e i v e O u t p u t 
@ntracef("RCVO")
def defaultReceiveOutput(myqOutput):
    while True:
        tAnswers = myqOutput.get()
        sWhoami = mp.current_process().name
        NTRC.ntracef(3, "RCVO", "proc DefRcvOut|%s| got output |%s|" 
                % (sWhoami, repr(tAnswers)))
        lOutput = tAnswers.listoflists
        if lOutput:
            # Print it all on stdout.  
            for sLine in lOutput:
                print(sLine)
            print("--------------")
        else:
            sys.exit(0)


# ===================================================================
# ======== Management routines for multiprocessing processes ========

# ===================================================================
# U T I L I T Y   F U N C T I O N S 

# f n W r i t e L o g F i l e 
@ntrace
def fnWriteLogFile(mylContents, mysFileDir, mysFileName):
    sFullName = mysFileDir + "/" + mysFileName
    # Remove file if present.
    pathToFile = pathlib.Path(sFullName)
    if pathToFile.is_file():
        pathToFile.unlink()
    # Contents should be a list of lines.
    sContents = '\n'.join(mylContents)
    with (open(sFullName, "w")) as fhOut:
        print(sContents, file=fhOut)


# f n s G e t T i m e s t a m p 
@ntracef("UTIL", level=5)
def fnsGetTimestamp():
    '''Return timestamp with milliseconds.
    '''
    return datetime.datetime.now().strftime('%Y%m%d_%H%M%S.%f')[:-3]    # with msec
#    return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')           # without msec


# f n s S t a m p L i n e 
@ntracef("UTIL", level=5)
def fnsStampLine(mysStamp, mysLine, mybFirstLine):
    """To indent paras of lines where the timestamp appears only
    on the first line, blanks to indent all the others.  
    """
    if mybFirstLine:
        return fnsGetTimestamp() + "  " + mysLine
    else:
        return " "*len(fnsGetTimestamp()) + "  " + mysLine


# f n s G e t P r o c e s s N u m b e r 
@ntracef("UTIL", level=5)
def fnsGetProcessNumber(mysProcName):
    '''Extract the process number, which is the same as the case number
    in this case, so we can use its abbreviated form in logs and traces.
    '''
    sProcNum = re.match(".*-(\d+)", mysProcName).group(1)
    return sProcNum if sProcNum else ""


# f n b D o N o t I g n o r e L i n e 
@ntracef("UTIL", level=5)
def fnbDoNotIgnoreLine(mysLine):
    '''
    True if not a comment or blank line.
    '''
    # Ignore comment and blank lines, but take all others.
    return (not re.match("^\s*#", mysLine)) and (not re.match("^\s*$", mysLine))


#END
