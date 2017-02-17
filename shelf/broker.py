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
import  command
import  copy


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
    sRandomSeedFile = "1000Randoms.txt"

    nShelfSize = None
    nDocSize = None
    sShortLog = "N"     # Log only setup and results info, no error details.  

    # Administrative options to guide broker's behavior.
    sQuery = None
    nCores = 8          # Default, overridden by NCORES env var
    nCoreTimer = 10     # Wait for a free core,
    nPoliteTimer = 2    # Shorter wait between sequential launches.
    nStuckLimit = 600   # Max nr of CoreTimer waits before giving up.
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
    sSearchDbFile = "./searchspacedb/searchdb.json"     # Obsolete, I hope.
    sSearchDbMongoName = "brokeradmin"
    sSearchDbProgressCollectionName = "inprogress"
    sSearchDbDoneCollectionName = "done"
    sdb = None          # Instance of searchspace db.   # Obsolete, I hope.
    mdb = None          # Instance of searchdatabasemongo db.
    
    # Command template components.
    sShelfLogFileTemplate = (
        'doc{nDocSize}cop{nCopies}shlf{nShelfSize}lif{nLifem}_'
        'af{nAuditFreq}s{nAuditSegments}t{sAuditType}_'
        'gf{nGlitchFreq}i{nGlitchImpact}d{nGlitchDecay}m{nGlitchMaxlife}_'
        'sh{nShockFreq}i{nShockImpact}s{nShockSpan}_m{nShockMaxlife}'
        'seed{nRandomseed}'
        )
    sShelfLogFileName = None

    # Templates to be obtained from instruction file, and commands to be 
    #  filled in from templates.  
    sCommandListFilename = "brokercommandlist.txt"  # default, not overridden.
    lTemplates = []
    lCommands = []

    # The listactor command must redirect all output to a file.
    #  Otherwise, it will not run asynchronously to take advantage
    #  of multiple cores.
    sActorCmdFileTemplate = ('{sFamilyDir}/{sSpecificDir}/cmd/'
                            '{sShelfLogFileName}.cmds'
                            )
    sActorCmdFileName = None
    sActorCmdTemplate = ('export TRACE_LEVEL=0; export TRACE_FACIL=; '
                        'python listactor.py {sActorCmdFileName} > '
                        '{sFamilyDir}/{sSpecificDir}/act/'
                        '{sShelfLogFileName}_actor.log 2>&1 &'
                        )
    sActorCmd = None

    # Only field names that appear in items in the database should ever
    #  be in the query dictionary.  Otherwise, no item in the database 
    #  can possibly satisfy such a query; i.e., no instructions, no results.  
    lSearchables = ('nAuditFreq nAuditSegments sAuditType nDocSize '
                    'nGlitchDecay nGlitchFreq nGlitchIgnorelevel '
                    'nGlitchImpact nGlitchMaxlife nGlitchSpan '
                    'nShockFreq nShockImpact nShockSpan nShockMaxlife '
                    'nLifem nServerDefaultLife '
                    'nCopies nRandomseed nShelfSize nSimlen sQuery' 
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
    sFibCmd1 = 'python fib.py 42'
    sFibCmd2 = 'python fib.py 40'
    sEndTime = 'date +%Y%m%d_%H%M%S.%3N'
    lFibTemplates = [sStartTime, sBashIdCmd, sPythonIdCmd, 
                    sFibCmd1, sFibCmd2, sEndTime]

    # Command used to count instances and wait for an open core.  
    # I added the temp files so that we can track certain errors
    #  that seem to occur on AWS Ubuntu, running out of disk space 
    #  or memory or some other resource.  Whatever the cause, the 
    #  command below returns an empty string, oops.  
    # NOTE: When we translate this entire application to python3, this 
    #  command will have to change.  Now it eliminates the python3 something
    #  that Ubuntu is running in the background.  
    sWaitForOpeningCmd = ("ps axu 2>&1 | tee ps.tmp | grep {Name} 2>&1 "
                        "| grep -v grep | grep -v python3 | "
                        "grep -v 'sh -c' | grep -v '/sh ' | "
                        "tee grep.tmp | wc -l | tee wc.tmp"
                        )
    nWcLimit = 100          # How many times to try for a number out of 
                            #  the above command.
    nLinuxScrewupTime = 3   # How long between attempts.

    '''
    Directory structure under the familydir/specificdir:
    cmd - command files for the listactor program
    log - log file output from the main simulation runs
    act - little bitty log files from the listactor program
    ext - the single line (plus heading) extracts from the log files
    dat - the combined output from appending all the extract files (less 
          redundant headers)
    '''

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
                        if fnbDoNotIgnoreLine(line)]
        return g.lTemplates

# f n b D o N o t I g n o r e L i n e 
@ntrace
def fnbDoNotIgnoreLine(mysLine):
    '''
    True if not a comment or blank line.
    '''
    # Ignore comment and blank lines, but take all others.
    return (not re.match("^\s*#", mysLine)) and (not re.match("^\s*$", mysLine))

# f n I n t P l e a s e 
@ntracef("INT", level=5)
def fnIntPlease(myString):
    # If it looks like an integer, make it one.
    try:
        return int(myString)
    except ValueError:
        return myString

#===========================================================

# f n W a i t F o r O p e n i n g 
@catchex
@ntracef("WAIT")
def fnbWaitForOpening(mynProcessMax, mysProcessName, mynWaitTime, mynWaitLimit):
    ''' Wait for a small, civilized number of processes to be running.  
        If the number is too large, wait a while and look again.  
        But don't wait forever in case something is stuck.  
        Args: 
        - max nr of processes, including maybe this one
        - process name to look for
        - wait time between retries
        - max nr of retries before giving up
        NEW NEWS: Since the new listactor program is python, and the 
         simulation main is python, there are two programs running 
         python for each simulation run.  Plus this broker program.
         So, if we are looking for python processes, the arithmetic ought to be 
         - how many pythons are running
         - subtract one for the broker
         - divide by two for the actor and the main
         - is that number greater than the stated limit?
    '''
    cCmd = command.CCommand()
    dParams = dict()
    dParams['Name'] = mysProcessName
    for idx in range(mynWaitLimit):

        # Harden the slot detection loop against errors seen.
        #  If it fails many times in a row, let it really die.  
        # Ignore (at our peril) the frequent null results from wc on Ubuntu.
        nWcLimit = g.nWcLimit
        while nWcLimit > 0:
            sCmd = g.sWaitForOpeningCmd
            sFullCmd = cCmd.makeCmd(sCmd, dParams)
            sResult = cCmd.doCmdStr(sFullCmd)
            try:
                nResult = int(sResult)
                nWcLimit = 0
            except ValueError:
                nWcLimit -= 1
                time.sleep(g.nLinuxScrewupTime)
        #end while waiting for int from wc

        NTRC.tracef(3,"WAIT","proc WaitForOpening1 idx|%d| cmd|%s| result|%s|" 
            % (idx, sFullCmd, nResult))
        if mysProcessName.find("python") >= 0:
            nOtherProcs = nResult - 1               # Processes that are not me.
            nRealProcs = int(nOtherProcs / 2)       # They come in pairs.
            if nRealProcs < mynProcessMax: break    # If there's still room, go to it.
        else:
            if nResult < mynProcessMax: break
        NTRC.tracef(3,"WAIT","proc WaitForOpening2 sleep and do again idx|%d| nResult|%d|" 
            % (idx, nResult))
        time.sleep(mynWaitTime)
    return (idx < mynWaitLimit-1)                   # Return false if we ran out of retries.


#===========================================================

# c l a s s   C F o r m a t 
class CFormat(object):

    @ntracef("FMT")
    def msGentlyFormat(self, mysCmd, mydVals):
        '''
        Like string.format() but does not raise exception if the string
         contains a name request for which the dictionary does not have 
         a value.  Leaves unfulfilled name requests in place.  
        Method: construct a dictionary that contains something for every
         name requested in the string.  The value is either a supplied 
         value from the caller or a placeholder for the name request.  
         Then use the now-defanged string.format() method.
        This is way harder than it ought to be, grumble.  
        '''
        # Make a dictionary from the names requested in the string
        #  that just replaces the request '{foo}' with itself.  
        sReNames = '(:?\{([^\}]+)\})+'
        oReNames = re.compile(sReNames)
        lNameTuples = oReNames.findall(mysCmd)
        NTRC.ntracef(3,"FMT","proc gently tuples|%s|" % (lNameTuples))
        lNames = [x[1] for x in lNameTuples]
        dNames = dict(zip(lNames, map(lambda s: "{"+s+"}", lNames)))
        # Pick up any specified values in the global object 
        #  and from CLI args.
        dNames.update(dict(vars(CG)))
        dNames.update(dict(vars(g)))
        # And then add values from the specific instructions.
        dNames.update(mydVals)
        NTRC.ntrace(3,"proc gently dnames|%s|" % (dNames))
        sOut = mysCmd.format(**dNames)
        return sOut

    @ntracef("FMT")
    def fndFormatQuery(self, mydCli):
        '''
        Take all the CLI options that might specify a searchable attribute, and 
         construct a MongoDB or searchspace query dictionary.  
         This is lots nastier than it first appears to be
         because json is so bloody picky.
        '''
        dOut = dict()
        for sAttrib,sValue in mydCli.items():
            result = None
            if sValue is not None:
                # Is it something valid in json?                
                try:
                    result = json.loads(sValue)
                except ValueError:
                    # Is it a string that should be an integer, ok in json?
                    try:
                        result = int(sValue)
                    except:
                        # Is it a naked string for some string-valued var
                        #  that isn't just Y/N or a mandatory string?  
                        #  Rule out dict values that are already formatted.
                        if (isinstance(sValue, str)
                            and sAttrib not in g.lYesNoOptions
                            and sAttrib not in g.lMandatoryArgs
                            and '{' not in sValue
                            and '}' not in sValue
                            and ':' not in sValue
                            and ',' not in sValue
                            ):
                            result = '{"$eq":' + '"'+sValue+'"' + '}'
                        else:
                            result = sValue
                    NTRC.tracef(3, "FMT", "proc FormatQuery notjson item "
                        "key|%s| val|%s| result|%s|" 
                        % (sAttrib, sValue, result))
            NTRC.tracef(3, "FMT", "proc FormatQuery item key|%s| val|%s| result|%s|" 
                % (sAttrib, sValue, result))
            # Can't process dicts thru json twice.
            if isinstance(result, dict):
                dOut[sAttrib] = sValue
            else:
                dOut[sAttrib] = result

        # Allow only attribs that appear in the database, else will get 
        #  no results due to implied AND of all items in query dict.  
        dOutSafe = {k:v for k,v in dOut.items() if k in g.lSearchables}
        dOutNotNone = {k:v for k,v in dOutSafe.items() if v is not None}
        NTRC.ntracef(3,"FMT","proc dict b4|%s| \nsafe|%s|\nclean|%s|" 
            % (dOut,dOutSafe,dOutNotNone))
        if "sQuery" in dOutNotNone.keys():
            # If the brave user has supplied a full, standalone query string,
            #  add its contents to the query dict so far.
            dTmp = dOutNotNone["sQuery"]
            del dOutNotNone["sQuery"]
            dOutNotNone.update(dTmp)
        return dOutNotNone

    @ntracef("FMT")
    def fnsMaybeTest(self, mysCommand):
        '''
        If TestCommand option is present, then change the command line to a line
         that just echos the command line instead of actually doing it.
        '''
        if g.sTestCommand.startswith("Y"):
            sCommand = 'echo "{}"'.format(mysCommand)
        else:
            sCommand = mysCommand
        return sCommand

#===========================================================

# f n d M a y b e E n h a n c e I n s t r u c t i o n 
@catchex
@ntracef("MAIN")
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

# M A I N 
@catchex
@ntracef("MAIN")
def main():
    '''
    Process:
    - Query the searchspace for the stream of instructions
    - For each instruction from database selection, get dict for line
    - Using dict args, construct plausible command lines, into file
    - Check to see that there aren't too many similar processes 
      running already; wait if so.
    - Launch ListActor process to execute commands.
    - Wait a polite interval before launching another.
    '''
    NTRC.ntracef(0, "MAIN", "Begin.")
    NTRC.ntracef(0, "MAIN", "TRACE  traceproduction|%s|" % NTRC.isProduction())

    # Get args from CLI and put them into the global data
    dCliDict = brokercli.fndCliParse("")
    # Carefully insert any new CLI values into the Global object.
    dCliDictClean = {k:v for k,v in dCliDict.items() if v is not None}
    g.__dict__.update(dCliDictClean)

    # Get command templates from external file.
    fnGetCommandTemplates(g.sCommandListFilename)

    # Construct database query for this invocation.
    g.cFmt = CFormat()
    dQuery = g.cFmt.fndFormatQuery(dCliDict)

    # Look for overriding environment variables
    fnvGetEnvironmentOverrides()

    # Open the database to keep "done" records,
    #  and delete moldy, old in-progress records.
    g.mdb = searchdatabasemongo.CSearchDatabase(g.sSearchDbMongoName, 
                g.sSearchDbProgressCollectionName, 
                g.sSearchDbDoneCollectionName)
    g.mdb.fnvDeleteProgressCollection()
    
    # Get the set of instructions for today from database.
    NTRC.tracef(0,"MAIN","proc querydict2|%s|" % ((dQuery)))
    itAllInstructions = searchspace.fndgGetSearchSpace(g.sInsDir, g.sInsTyp, 
                        dQuery)
    fnnProcessAllInstructions(itAllInstructions)
    
    NTRC.ntracef(0,"MAIN","End.")

# f n n P r o c e s s A l l I n s t r u c t i o n s 
@catchex
@ntracef("MAIN")
def fnnProcessAllInstructions(myitInstructionIterator):
    ''' 
    Get the set of instructions that match the user's criteria for this batch,
     and run them one by one.
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

        nRunNumber += 1
        nStatus = fnstProcessOneInstructionManyTimes(nRunNumber, dInstruction)
        if nStatus > 0:     # Some major error, stop loop right now.  
            break

        # If user asked for a short test run today, maybe stop now.
        maxcount -= 1
        if int(g.nTestLimit) > 0 and maxcount <= 0: break

    return nRunNumber

# f n s t P r o c e s s O n e I n s t r u c t i o n M a n y T i m e s 
@catchex
@ntracef("MAIN")
def fnstProcessOneInstructionManyTimes(mynRunNumber, mydInstruction):
    ''' 
    Process a single instruction (set of params) once for each of a
     predetermined number and sequence of random seeds.
    '''
    lSeedsToUse = fnlGetRandomSeeds(fnIntPlease(g.nRandomSeeds), 
                    g.sRandomSeedFile)
    mydInstruction["sBaseId"] = str(mydInstruction["_id"])
    for (nIdx, nMaybeSeed) in enumerate(lSeedsToUse):
        # Adjust run number and mongo id because there are now
        #  multiple seeds and runs per instruction.  
        sRunId = str(mynRunNumber) + "." + str(nIdx+1)
        sId = str(mydInstruction["sBaseId"])
        mydInstruction["_id"] = sId + "_" + str(nIdx+1)
        
        nStatus = 0
        try:
            nSeed = int(nMaybeSeed)
        except ValueError:
            raise ValueError, "Random seed not integer |%s|" % (nMaybeSeed)
        mydInstruction["nRandomseed"] = nSeed
        nStatus = fnstProcessOneInstruction(sRunId, mydInstruction, nSeed)
        if nStatus > 0:
            break
    return nStatus

# f n v P r o c e s s O n e I n s t r u c t i o n 
@catchex
@ntracef("MAIN")
def fnstProcessOneInstruction(mysRunNumber, mydInstruction, mynSeed):
    ''' 
    Process one single instruction for one run.  
    If just testing today, print instruction contents but do not run it.
    If the instruction has already been processed, skip over it unless
     the user requires it to be redone.  
    '''
    sInstructionId = str(mydInstruction["_id"])
    # If the user specifies, redo this case even if done before.
    if g.sRedo.startswith("Y"):
        NTRC.ntracef(0,"MAIN","proc force redo for item id|%s|" 
            % (sInstructionId))
        g.mdb.fndDeleteDoneRecord(sInstructionId)

    # If this instruction has already been processed skip it.
    bIsItDone = g.mdb.fnbIsItDone(sInstructionId)
    if bIsItDone: 
        NTRC.ntracef(0,"MAIN","proc skip item already done run|%s| "
            "id|%s| copies|%s| lifem|%s|" 
            % (mysRunNumber, sInstructionId, mydInstruction["nCopies"],
            mydInstruction["nLifem"]))
        #continue    # Skip this iteration of the loop.

    elif g.sListOnly.startswith("Y"):
        # Testing: Just dump out the instruction dictionary for this item.
        NTRC.ntracef(0,"MAIN","proc ListOnly, item run|%s| "
            "ncopies|%s| lifem|%s| id|%s| dict|%s|" 
            % (mysRunNumber, mydInstruction["nCopies"], mydInstruction["nLifem"],
            sInstructionId, mydInstruction))
    
    else:   # Real life: execute the instruction.
        bContinue = fnbWaitForOpening(g.nCores, "python", 
                    g.nCoreTimer, g.nStuckLimit)
        if bContinue:
            mydInstruction["nRandomSeed"] = mynSeed
            # Format commands to be executed by actor.
            g.sShelfLogFileName = g.cFmt.msGentlyFormat(
                                g.sShelfLogFileTemplate, mydInstruction)
            g.lCommands = []
            for sTemplate in g.lTemplates:
                sCmd = g.cFmt.msGentlyFormat(sTemplate, mydInstruction)
                g.lCommands.append(sCmd)

            # Make instruction file for the actor.
            g.sActorCmdFileName = g.cFmt.msGentlyFormat(
                                g.sActorCmdFileTemplate, mydInstruction)
            g.sActorCommand = g.cFmt.msGentlyFormat(
                                g.sActorCmdTemplate, mydInstruction)
            NTRC.ntracef(0, "MAIN", "proc main commands run|%s| "
                "ncopies|%s| lifem|%s| audit|%s| "
                "segs|%s|\n1-|%s|\n2-|%s|\n" 
                % (mysRunNumber, mydInstruction["nCopies"], 
                mydInstruction["nLifem"], mydInstruction["nAuditFreq"], 
                mydInstruction["nAuditSegments"], 
                g.lCommands, g.sActorCommand))
            with open(g.sActorCmdFileName, 'w') as fhActorCmdFile:
                fhActorCmdFile.write(
                                "# ListActor command file, "
                                "automatically generated by broker.  "
                                "Do not edit.\n")
                for sCommand in g.lCommands:
                    print >> fhActorCmdFile, g.cFmt.fnsMaybeTest(sCommand)

            # Record that this job is running.
            mydInstruction["starttime"] = util.fnsGetTimeStamp()
            g.mdb.fndInsertProgressRecord(mydInstruction["_id"], mydInstruction)
            # Launch the actor to perform main runs.  
            cCmd = command.CCommand()
            sResult = cCmd.doCmdStr(g.sActorCommand)
            time.sleep(g.nPoliteTimer)    

        else:
            NTRC.tracef(0, "MAIN", "OOPS, Stuck!  Too many python "
                "processes running forever.")
            #break
            return 1
    return 0

# f n v G e t E n v i r o n m e n t O v e r r i d e s 
@catchex
@ntracef("MAIN")
def fnvGetEnvironmentOverrides():
    # Allow user to override number of cores to use today.
    # First, find out how many cores there are that we could possibly use.
    nMaxCores = int(os.getenv("NUMBER_OF_PROCESSORS", None)) + 1
    # By default, use one fewer than max available, according to the o/s.  
    g.nCores = nMaxCores if nMaxCores else g.nCores
    # If the user specifies a number, larger or smaller, take it.
    try:
        g.nCores = int(os.getenv("NCORES", CG.nCores))
        g.nCores = min(g.nCores, nMaxCores)
        NTRC.ntracef(0, "MAIN", "proc ncores|%s|" % (g.nCores))
    except (ValueError, TypeError):
        raise TypeError('Environment variable NCORES must be an integer.')
    # Allow user to override the polite interval to use today.
    try:
        g.nPoliteTimer = int(os.getenv("NPOLITE", CG.nPoliteTimer))
        NTRC.ntracef(0, "MAIN", "proc politetimer|%s|" % (g.nPoliteTimer))
    except (ValueError, TypeError):
        raise TypeError('Environment variable NPOLITE must be an integer.')

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
        lsSeeds = [(fhSeeds.next()) for _ in range(mynHowMany)]
        lnSeeds = [fnIntPlease(_) for _ in lsSeeds]
    return lnSeeds


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
  wait for slot
  if _id is in done tbl continue
  format instructions into cmds
  write cmds into file
  format cmd for listactor
  start a listactor

cleaner:
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
# 20170128  RBL Adapt to searchdatabasemongo instead of json version.  
# 20170201  RBL Dump traceproduction y/n in trace-0.
# 
# 

#END

