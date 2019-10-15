#!/usr/bin/python
# broker.py

import  os
import  re
import  time
import  json
from    NewTraceFac     import  NTRC,ntrace,ntracef
import  sys
from    catchex         import  catchex
import  searchspace
import  searchdatabase
import  searchdatabasemongo
import  util
import  brokercli
import  copy
import  brokerformat
import  brokergetcores
import  newbroker3 as nb
import  collections
import  queue


# namedtuples

# Complete instruction info to pass to newbroker.
tInstruction = collections.namedtuple("tInstruction"
                , "runid cmdlist logdir logname casedict")

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
    nCopies = None
    nLifem = None
    nAuditFreq = None
    sAuditType = None
    nAuditSegments = None
    nGlitchFreq = None
    nGlitchImpact = None
    nGlitchDecay = None
    nGlitchMaxlife = None
    nGlitchSpan = None

    nShockFreq = None
    nShockImpact = None
    nShockSpan = None
    nShockMaxlife = None
    nServerDefaultLife = 0

    nRandomSeeds = 21
    sRandomSeedFile = "randomseeds.txt"
    nSimLength = 0

    nShelfSize = None
    nDocuments = None
    nDocSize = None
    sShortLog = "N"     # Log only setup and results info, no error details.  

    # Administrative options to guide broker's behavior.
    sQuery = None
    nCores = 8          # Default, overridden by NCORES env var.
    nCoreTimer = 50     # Wait for a free core (msec).
    nPoliteTimer = 20   # Wait between sequential launches, in milliseconds.
    nStuckLimit = 20000 # Max nr of CoreTimer waits before giving up.
    nTestLimit = 0      # Max nr of runs executed for a test run, 0=infinite.
    sTestCommand = "N"  # Should just echo commands instead of executing them?
    sTestFib = "N"      # Should use Fibonacci calc instead of real programs?
    sListOnly = "N"     # Just list out all cases matching the stated criteria.  
                        #  but don't execute them.
    sRedo = "N"         # Force cases to be redone (recalculated)?

    # Options that are string-valued but special, have only Y/N/YES/NO 
    #  answers.  DO NOT JSON-ify them.  
    lYesNoOptions = ("sRedo sListOnly sTestCommand sTestFib").split()
    
    # Mandatory arguments that are strings shouldn't be manhandled, either.
    lMandatoryArgs = ("sSearchDbProgressCollectionName "
                        "sSearchDbDoneCollectionName "
                        "sFamilyDir sSpecificDir").split()
    
    sFamilyDir = '../hl'        # lifetimes expressed as half-lives, and
    sSpecificDir = 'a0'         #  no auditing.

    # SearchSpace db info (for instructions)
    sInsDir = './instructions'  # Where to find instruction (*.ins) files.
    sInsTyp = '.ins3'   # File type (extension) specifier for instruction files.

    # SearchDatabase db info (for progress and done records)
    #sSearchDbFile = "./searchspacedb/searchdb.json"     # Obsolete, I hope.
    sSearchDbMongoName = "brokeradmin"
    sSearchDbProgressCollectionName = "inprogress"
    sSearchDbDoneCollectionName = "done"
    #sdb = None          # Instance of searchspace db.   # Obsolete, I hope.
    mdb = None          # Instance of searchdatabasemongo db.
    
    # Command template components.
    sShelfLogFileTemplate = (
        'doc{nDocSize}cop{nCopies}shlf{nShelfSize}lif{nLifem}_'
        'af{nAuditFreq}s{nAuditSegments}t{sAuditType}_'
        'gf{nGlitchFreq}i{nGlitchImpact}d{nGlitchDecay}m{nGlitchMaxlife}_'
        'sh{nShockFreq}i{nShockImpact}s{nShockSpan}m{nShockMaxlife}_'
        'svrdeflif{nServerDefaultLife}simlen{nSimLength}_seed{nRandomseed}'
        )
    sShelfLogFileName = None

    # Templates to be obtained from instruction file, and commands to be 
    #  filled in from templates.  
    sCommandListFilename = "broker2commandlist.txt"  # default, not overridden.
    lTemplates = []
    lCommands = []

    sActorLogDirTemplate = '{sFamilyDir}/{sSpecificDir}/act/'
    sActorLogDir = None

    # Only field names that appear in items in the database should ever
    #  be in the query dictionary.  Otherwise, no item in the database 
    #  can possibly satisfy such a query; i.e., no instructions, no results.  
    lSearchables = ('nAuditFreq nAuditSegments sAuditType nDocSize '
                    'nGlitchDecay nGlitchFreq nGlitchIgnorelevel '
                    'nGlitchImpact nGlitchMaxlife nGlitchSpan '
                    'nShockFreq nShockImpact nShockSpan nShockMaxlife '
                    'nLifem nServerDefaultLife nDocuments '
                    'nCopies nRandomseed nShelfSize nSimLength sQuery' 
                    ).split()
    # Special fake CPU-bound commands to test for proper parallel execution.  
    # These take about a minute (75s) and a third of a minute (22s) on an
    #  Intel 3Gi7 CPU in my Dell Optiplex 7010 (2016-08).  Your mileage
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

    '''
    Directory structure under the familydir/specificdir:
    cmd - command files for the listactor program (obsolete)
    log - log file output from the main simulation runs
    act - little bitty log files from the listactor program
    ext - the single line (plus heading) extracts from the log files
    dat - the combined output from appending all the extract files (less 
          redundant headers)
    '''
    
    # If this file exists, broker will append its command to the file.
    sBrokerCommandLogFile = "tmp/BrokerCommands.log"

    # List of all instructions, to be given to RunEverything.
    lGiantInstr = []

    # queue to pass instructions to runeverything thread.
    qInstructions = queue.Queue()
    bLast = False   # Have we come to the end of all instructions.

#===========================================================

    """Additional data needed by the newbroker module.  
    """
    ltJobs = list()     # Job numbers or None
    lockJobList = None  # Thread lock for ltJobs job list.
    lockPrint = None    # Thread lock for trace printing.
    
    # Dictionaries that contain references to things we want cleaned up.
    # These must be emptied when the jobs they point to are complete.
    dId2Proc = dict()   # Map job number -> process object
    dId2Queue = dict()  # Map job number -> queue object
    
    nParallel = 4       # Limit on jobs running in parallel (on separate CPUs)
                        #  (overridden by nCores).
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
    thrEnd = None
    

#===========================================================


# f n G e t C o m m a n d T e m p l a t e s 
@ntrace
def fnGetCommandTemplates(mysCommandFilename):
    '''
    Read (interesting) lines from external file as command templates
     to be filled in and executed.
    '''
    with open(mysCommandFilename, 'r') as fhIn:
        g.lTemplates = [line.rstrip() for line in fhIn 
                        if util.fnbDoNotIgnoreLine(line)]
        return g.lTemplates


#===========================================================


# f n d M a y b e E n h a n c e I n s t r u c t i o n 
@catchex
@ntracef("MAIN", level=5)
def fndMaybeEnhanceInstruction(mydRawInstruction):
    '''
    There may be some qualifiers that are neither searchable nor
    merely adminstrative, but have to be passed thru to main.py.  
    If they are not searchable, they probably don't come back in 
    the instruction dict.  Add them to instruction dict.
    '''
    dInstruction = copy.deepcopy(mydRawInstruction)
    # Add additional attributed here.
    
    # shortlog is unusual in not taking an argument but being true by presence.
    dInstruction["sShortLogOption"] = ("--shortlog" 
                if g.sShortLog.startswith("Y") 
                else "")
    
    return dInstruction

#===========================================================
#===========================================================


# M A I N 
@catchex
@ntracef("MAIN")
def main():
    '''
    Process:
    - Parse the CLI command into g.various data items.
    - Validate user-supplied directories; get environment variables.
    - Query the searchspace for the stream of instructions
    - For each instruction from database selection, get dict for line
    - Using dict args, construct plausible command lines, into file
    - Check to see that there aren't too many similar processes 
      already running; if too many, then wait.
    - Launch ListActor process to execute commands.
    - Wait a polite interval before launching another.
    '''
    NTRC.ntracef(0, "MAIN", "Begin.")
    NTRC.ntracef(0, "MAIN", "TRACE  traceproduction|%s|" % NTRC.isProduction())


    def fnbQEnd():
        return g.bLast


    sBrokerCommand = fnsReconstituteCommand(sys.argv)
    fnbMaybeLogCommand(sBrokerCommand)
    NTRC.ntracef(0, "MAIN", "command=|%s|" % (sBrokerCommand.rstrip()))

    # Get args from CLI and put them into the global data
    dCliDict = brokercli.fndCliParse("")
    # Carefully insert any new CLI values into the Global object.  
    dCliDictClean = {k:util.fnIntPlease(v) for k,v in dCliDict.items() 
                        if v is not None}
    g.__dict__.update(dCliDictClean)

    # Validate that the user-specified directories exist.
    if not fnbValidateDir(g.sFamilyDir):
        raise ValueError("FamilyDir \"%s\" not found" % (g.sFamilyDir))
    if not fnbValidateDir("%s/%s" % (g.sFamilyDir, g.sSpecificDir)):
        raise ValueError("SpecificDir \"%s\" not found" % (g.sSpecificDir))

    # Get command templates from external file.
    fnGetCommandTemplates(g.sCommandListFilename)

    # Construct database query for this invocation.
    g.cFmt = brokerformat.CFormat()
    dQuery = g.cFmt.fndFormatQuery(dCliDict, g)

    # Look for overriding environment variables
    fnvGetEnvironmentOverrides()

    # Open the database to keep "done" records,
    #  and delete moldy, old in-progress records.
    g.mdb = searchdatabasemongo.CSearchDatabase(g.sSearchDbMongoName, 
                g.sSearchDbProgressCollectionName, 
                g.sSearchDbDoneCollectionName)
    g.mdb.fnvDeleteProgressCollection()

    # Get the set of instructions for today from database.
    NTRC.tracef(0,"MAIN","proc querydict2|%s|" 
                % (list(util.fngSortDictItemsByKeys(dQuery))))
    itAllInstructions = searchspace.fndgGetSearchSpace(g.sInsDir, g.sInsTyp, 
                        dQuery)
    
    # Start the start-end threads.
    nb.fntRunEverything(g, g.qInstructions, fnbQEnd
                            , g.nCoreTimer, g.nStuckLimit)

    # If this wasn't just a listonly run, do all the cases.  
    if not g.sListOnly.startswith("Y"):
        NTRC.ntracef(3, "MAIN", "proc all instr|%s|" % (g.lGiantInstr))
    else:
        NTRC.ntracef(0, "MAIN", "Listonly.")
    nRuns = fnnProcessAllInstructions(itAllInstructions)
    NTRC.ntracef(0, "MAIN", "End queued all runs ncases|%s|" % (g.nCases,))


# f n n P r o c e s s A l l I n s t r u c t i o n s 
@catchex
@ntracef("MAIN")
def fnnProcessAllInstructions(myitInstructionIterator):
    ''' 
    Get the set of instructions that match the user's criteria for this batch,
     and run them one by one.
    Each instruction (run) is executed once for each random seed value.
    Count the number of runs, and don't exceed the user's limit, if any.
    If the execution reports a serious error, stop the loop.
    '''
    nRunNumber = 0
    maxcount = int(g.nTestLimit)
    # Is this a completely fake test run?  Replace templates.
    if g.sTestFib.startswith("Y"):
        g.lTemplates = g.lFibTemplates

    # Process each instruction in turn.
    for dRawInstruction in myitInstructionIterator: 
        NTRC.ntracef(3,"MAIN","proc main raw instruction\n|%s|" 
            % (dRawInstruction))
        dInstruction = fndMaybeEnhanceInstruction(dRawInstruction)
        NTRC.ntracef(3,"MAIN","proc main enhanced instruction\n|%s|" 
            % (dInstruction))

        # Execute each instruction once for each random seed value.
        nRunNumber += 1
        fnnProcessOneInstructionManyTimes(nRunNumber
                        , dInstruction)
        
        # If user asked for a short test run today, maybe stop now.
        maxcount -= 1
        if int(g.nTestLimit) > 0 and maxcount <= 0: break

    g.bLast = True
    return nRunNumber


# f n s t P r o c e s s O n e I n s t r u c t i o n M a n y T i m e s 
@catchex
@ntracef("MAIN")
def fnnProcessOneInstructionManyTimes(mynRunNumber, mydInstruction):
    ''' 
    Process a single instruction (set of params) once for each of a
     predetermined number and sequence of random seeds.
    Assign an id to each run that consists of the instruction hash (_id)
     followed by _<seed number>.  
    '''
    lManyInstr = []
    lSeedsToUse = fnlGetRandomSeeds(util.fnIntPlease(g.nRandomSeeds), 
                    g.sRandomSeedFile)
    mydInstruction["sBaseId"] = str(mydInstruction["_id"])
    for (nIdx, nMaybeSeed) in enumerate(lSeedsToUse):
        # Adjust run number and mongo id because there are now
        #  multiple seeds and runs per instruction.  
        sRunId = str(mynRunNumber) + "." + str(nIdx+1)
        sId = str(mydInstruction["sBaseId"])
        mydInstruction["_id"] = sId + "_" + str(nIdx+1)
        mydInstruction["_runid"] = sRunId
        
        nStatus = 0
        try:
            nSeed = int(nMaybeSeed)
        except ValueError:
            raise ValueError("Random seed not integer |%s|" % (nMaybeSeed))
        mydInstruction["nRandomseed"] = nSeed

        tOneInstr = fntProcessOneInstruction(sRunId, mydInstruction, nSeed)
    return g.nRandomSeeds


# f n t P r o c e s s O n e I n s t r u c t i o n 
@catchex
@ntracef("MAIN")
def fntProcessOneInstruction(mysRunNumber, mydInstruction, mynSeed):
    ''' 
    Process one single instruction for one run.  
    If just testing today, print instruction contents but do not run it.
    If the instruction has already been processed, skip over it unless
     the user requires it to be redone.  
    '''
    sInstructionId = str(mydInstruction["_id"])
    
    # If this instruction has already been processed, maybe skip it.
    bIsItDone = g.mdb.fnbIsItDone(sInstructionId)
    if bIsItDone and not g.sRedo.startswith("Y"): 
        # If the user has not insisted on redo, skip it.
        NTRC.ntracef(0,"MAIN","proc skip item already done run|%s| "
            "id|%s| copies|%s| lifem|%s|" 
            % (mysRunNumber, sInstructionId, mydInstruction["nCopies"],
            mydInstruction["nLifem"]))
    else:
        # If the user specifies, redo this case even if was done before.
        if g.sRedo.startswith("Y"): 
            NTRC.ntracef(0,"MAIN","proc force redo of run|%s| id|%s| " 
                % (mysRunNumber, sInstructionId))

        # Well, maybe.  Could be listonly.
        if g.sListOnly.startswith("Y"):
            NTRC.ntracef(0,"MAIN","proc ListOnly, item run|%s| "
                "ncopies|%s| lifem|%s| id|%s| dict|%s|" 
                % (mysRunNumber, mydInstruction["nCopies"], mydInstruction["nLifem"],
                sInstructionId, list(util.fngSortDictItemsByKeys(mydInstruction))))
        else:
            # Okay, really do this instruction.  
            mydInstruction["nRandomSeed"] = mynSeed
            NTRC.ntracef(0,"MAIN","proc queue instr, item run|%s| "
                "ncopies|%s| lifem|%s| id|%s|" 
                % (mysRunNumber, mydInstruction["nCopies"], mydInstruction["nLifem"],
                sInstructionId))

            # Format commands to be executed by actor.
            g.sShelfLogFileName = g.cFmt.msGentlyFormat(
                                g.sShelfLogFileTemplate, mydInstruction, g, CG)
            g.lCommands = []
            for sTemplate in g.lTemplates:
                sCmd = g.cFmt.msGentlyFormat(sTemplate, mydInstruction, g, CG)
                g.lCommands.append(sCmd)

            # Where do files go, and what are they called.
            g.sActorLogDir = g.cFmt.msGentlyFormat(
                                g.sActorLogDirTemplate, mydInstruction, g, CG)

            # Record that this job will soon be running.
            mydInstruction["starttime"] = util.fnsGetTimeStamp()
            g.mdb.fndInsertProgressRecord(mydInstruction["_id"], mydInstruction)
            
            # Return the full instruction.
            tThisInst = tInstruction(casedict=mydInstruction
                                    , cmdlist=g.lCommands
                                    , logname=g.sShelfLogFileName + "_case.log"
                                    , logdir=g.sActorLogDir
                                    , runid=mysRunNumber
                                    )

            # Send the instruction out to be done.
            g.qInstructions.put(tThisInst)
            
            if not g.thrStart.is_alive(): g.thrStart.start()
            if not g.thrEnd.is_alive(): g.thrEnd.start()

            return tThisInst


#===========================================================
# Utility functions:
# - Get list of random seeds
# - Get environment vars that control timing
# - Keep text log of commands to broker
# - Check for valid dirs


# f n l G e t R a n d o m S e e d s 
@catchex
@ntracef("MAIN")
def fnlGetRandomSeeds(mynHowMany, mysFilename):
    '''
    Return a list of the first mynHowMany random seeds from the 
     file specified.  
    This is the primitive version that does not permit blank lines, 
     comments, or other detritus in the list of seed numbers.  
    '''
    with open(mysFilename, "r") as fhSeeds:
        lsSeeds = [(next(fhSeeds)) for _ in range(mynHowMany)]
        lnSeeds = [util.fnIntPlease(_) for _ in lsSeeds]
    return lnSeeds


# f n v G e t E n v i r o n m e n t O v e r r i d e s 
@catchex
@ntracef("MAIN")
def fnvGetEnvironmentOverrides():
    # Allow user to override number of cores to use today.
    # Utility routine looks at HW and possible user envir override.
    g.nCores = brokergetcores.fnnGetResolvedCores()
    NTRC.ntracef(0, "MAIN", "proc ncores|%s|" % (g.nCores))
    g.nParallel = g.nCores      # Sorry for the name change.
    # Allow user to override the polite interval to use today.
    try:
        g.nPoliteTimer = int(os.getenv("NPOLITE", CG.nPoliteTimer)) 
        g.nCoreTimer = g.nPoliteTimer   # Sorry for the name change.  
        NTRC.ntracef(0, "MAIN", "proc politetimer|%s|msec" % (g.nPoliteTimer))
    except (ValueError, TypeError):
        raise TypeError("Environment variable NPOLITE must be "
                        "an integer number of milliseconds.")


# f n s R e c o n s t i t u t e C o m m a n d 
@ntrace
def fnsReconstituteCommand(lArgs):
    sPyVer = sys.version_info.major
    sOut = "python" + str(sPyVer) + " " + " ".join(lArgs)
    return sOut


# f n b M a y b e L o g C o m m a n d 
@ntrace
def fnbMaybeLogCommand(sCommand):
    if os.path.isfile(g.sBrokerCommandLogFile):
        sTime = util.fnsGetTimeStamp() + " "
        with open(g.sBrokerCommandLogFile, "a") as fhBrokerCommandLog:
            fhBrokerCommandLog.write(sTime)
            fhBrokerCommandLog.write(sCommand + "\n")
        return True
    else:
        return False


# f n b V a l i d a t e D i r 
@ntrace
def fnbValidateDir(sPath):
    return os.path.isdir(sPath)


#===========================================================
#
# E n t r y   p o i n t . 
if __name__ == "__main__":
    g = CG()
    sys.exit(main())


'''
main events in the broker:
cli
form request to db
start stream from db
foreach item
  multiply case for each seed value required
  if _id is in done tbl continue
  format instructions into cmdlist
  write cmdlist into queue
  start the startall and endall threads

newbroker:
two threads
  startall: 
    read instruction from queue
    if no instruction and temporary shortfall, wait
    if no instruction and end of all cases, exit
    wait for slot
    fork an async process to handle the case
  endall:
    examine all jobs running in slots
    if a job has finished
      clean up refs to the job
      if debug, get output from job
    if no jobs running and started last job, exit

extractor: 
for all lines of log file
  does any lineregex match
for lines that matched any regex
  evaluate valueregex, store value
add synthetic data 
format output line

cleanup:
foreach single-line file in holding dir
  append line to combined results file
  add _id to done tbl of db
  delete one-liner

'''

# Edit history:
# 20150501  RBL Original version, very crude but workable.  
# 20150512  RBL Version that could actually test parallelism.  
# 20150519  RBL Add testing, redo.
# 20150619  RBL Up to broker-10.py.
# 20150719  RBL Improve and correct brokercommandlist.
# 20150801  RBL Fix the wait-for grep command string to work on Linux
#                for AWS Ubuntu.
# 20150809  RBL Re-fix wait-for grep command string to work on CygWin.
#               Increase stuck timer because AWS single stream is 
#                reeeaaalllyyy ssslllooowww.  
# 20150813  RBL Cosmetic changes in anticipation of adding flat-file db.
# 20151211  RBL Get rid of required values for essentially boolean 
#                test options.
# 20151212  RBL Correct the previous edit because JSON requires strings, 
#                not True-False values.  Put back 90% of the code I changed.
# 20160216  RBL Add --glitchspan option.
#               Incr run counter before checking for already done.
# 20161006  RBL Make familydir and specificdir mandatory options.
#                BEWARE: if you say nargs=1 instead of nargs='?', 
#                the value returned is a list containing the string, 
#                not just the scalar string.  Yikes.  
#               Add audit info to run line.
#               Add run number to already-done line.
#               Reduce default number of cores so it doesn't kill laptop.
#               Reduce polite interval timer slightly to 3 sec.
# 20161009  RBL Reduce polite interval timer to 2 sec.
# 20170104  RBL Add shock params and server default life param.
#               Restore glitchspan, which had been removed.  
#               Begin to break out the set of random seeds from the 
#                stored instructions.  Loop here on seeds instead of 
#                having a single item in the db for each param set and seed.
# 20170117  RBL Begin to remove Mongo class so it can eventually be replaced
#                by the equivalent for searchspace.  
#               Put in special handling for dictionaries going into json.  
# 20170121  RBL Complete conversion to searchspace and searchdatabase.
# 20170122  RBL Fix calc of nCores, limit = cores on this ship.  
# 20170124  RBL Remove restrictions on --audittype because the string "TOTAL"
#                is not valid JSON.  Rather than put in an exception to 
#                translate string values to proper JSON (which I might do
#                later), let's permit --audittype='{"$eq":"TOTAL"}' to work.
# 20170124  RBL Smarten FormatQuery to permit string value for --audittype
#                and turn TOTAL into {"$eq":"TOTAL"} which is acceptable
#                to json.
# 20170126  RBL Move CLI to a separate file, brokercli.py.
#               Move CCommand to a separate file, command.py.
# 20170127  RBL Add hack to enhance the main.py instruction dictionary
#                with some options that are not searchable and don't 
#                appear in the instuctions but are still necessary, 
#                e.g., --shortlog.  
# 20170128  RBL Adapt to searchdatabasemongo instead of json version, 
#                which DFW due to file locking shortcomings in Windows 
#                and Linux.  At least, I couldn't get it to work reliably.  
# 20170201  RBL Dump traceproduction y/n in trace-0.
# 20170317  RBL Repair logfilename template, which had the shock maxlife
#                on the wrong side of the underscore, duh.  
# 20170520  RBL Add serverdefaultlife to logfilename, duh.  Different values
#                resulted in the same logfilename, which then was overwritten.  
#               Reorder code slightly for clarity (I hope).  
#               Reduce default polite timer to one second.
#               Move CFormat class to separate file.  
# 20170521  RBL Get real number of hardware cores from OS /proc/cpuinfo
#                and then maybe user limitation in NCORES env var.  
# 20170612  RBL Note that broker will append each command to a 
#                log file, if that file already exists.  
# 20171217  RBL Move a couple small functions to util.py.
# 20180408  RBL Add nSimLength var to take value from --simlen CLI option, 
#                to be passed to main.py in cmd.  
# 20180828  RBL Log commands on single line, timestamp then CLI command.  
# 20181002  RBL Change POLITE timer to be in milliseconds so that 
#                very short runs for shocks are not spaced out unduly.
# 20181112  RBL Begin major remodeling to adapt to newbroker job runner.  
#                Pile up all instructions into a list that then gets
#                fed to newbroker.RunEverything.
#               Remove old code that is not used, e.g., command import, 
#                Wait function.  These are now in newbroker.
#               Add new CLI options for core wait time and stuck limit.
# 20181113  RBL Fix name changes between broker2 and newbroker3 by overlaying
#                the old data with new.  Someday, clean this up.  
# 20181115  RBL Add nDocuments option.
# 20181116  RBL Sort dQuery when printing it.  
# 20181117  RBL Comment out obsolete data relating to listactor.  
# 20181118  RBL Change the way instructions are generated and transmitted; 
#                use a plain queue rather than piling up a giant list.
#                Puzzle: had to move the start instructions for the 
#                startall and endall threads here after the first 
#                instruction is enqueued.  Why?
# 
# 

#END

