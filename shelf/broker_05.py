#!/usr/bin/python
# broker.py

import  argparse
import  os
import  re
import  time
import  json
from    NewTraceFac     import NTRC,ntrace,ntracef
import  mongolib


@ntracef("CLI")
def fndCliParse(mysArglist):
    ''' Parse the mandatory and optional positional arguments, and the 
         many options for this run from the command line.  
        Return a dictionary of all of them.  
    '''
    sVersion = "0.0.3"
    cParse = argparse.ArgumentParser(description="Digital Library Preservation Simulation Instruction Broker CLI v"+sVersion+"  "+
        "Enter either a value or a MongoDB dictionary spec " + 
        "that is a valid JSON dictionary string.  \n" + 
        "Note that special characters such as $ { } must be escaped " +
        "or single-quoted to protect them from the shell.  " + 
        "" +
        ""
        ,epilog="Defaults for args as follows: (none)\n"
        , version=sVersion)
    
    # P O S I T I O N A L  arguments
    #cParse.add_argument('--something', type=, dest='', metavar='', help='')

    cParse.add_argument('sDatabaseName', type=str
                        , metavar='sDATABASENAME'
                        , help='Name of MongoDB database that pymongo will find.'
                        )

    cParse.add_argument('sPendingCollectionName', type=str
                        , metavar='sPENDINGCOLLECTIONNAME'
                        , help='Collection name within the database of the instructions to be executed.'
                        )

    cParse.add_argument('sDoneCollectionName', type=str
                        , metavar='sDONECOLLECTIONNAME'
                        , help='Collection name within the database of the instructions that have been completed.'
                        )

    # - - O P T I O N S

    cParse.add_argument("--ncopies", type=str
                        , dest='nCopies'
                        , metavar='nCOPIES'
                        , nargs='?'
                        , help='Number of copies in session.'
                        )

    cParse.add_argument("--lifem", "--lifetimemegahours", type=str
                        , dest='nLifem'
                        , metavar='nLIFE_Mhrs'
                        , nargs='?'
                        , help='Sector mean lifetime for storage shelf.'
                        )

    cParse.add_argument("--auditfreq", type=str
                        , dest='nAuditFreq'
                        , metavar='nAUDITCYCLEINTERVAL_hrs'
                        , nargs='?'
                        , help='Hours between auditing cycles; zero=no auditing.'
                        )

    cParse.add_argument("--audittype", type=str
                        , dest='sAuditType'
                        , choices=['TOTAL','OFF']
                        , nargs='?'
                        , help='Strategy for auditing, default=SYSTEMATIC.'
                        )

    cParse.add_argument("--auditsegments", type=str
                        , dest='nAuditSegments'
                        , metavar='nAUDITSEGMENTS'
                        , nargs='?'
                        , help='Number of subsamples per audit cycle, default=1.'
                        )

    cParse.add_argument("--glitchfreq", type=str
                        , dest='nGlitchFreq'
                        , metavar='nGLITCHFREQ_hrs'
                        , nargs='?'
                        , help='Half-life of intervals between glitches; 0=never happens.'
                        )

    cParse.add_argument("--glitchimpact", type=str
                        , dest='nGlitchImpact'
                        , metavar='nGLITCHIMPACT_pct'
                        , nargs='?'
                        , help='Percent reduction in sector lifetime due to glitch; 100%%=fatal to shelf.'
                        )

    cParse.add_argument("--glitchdecay", type=str
                        , dest='nGlitchDecay'
                        , metavar='nGLITCHDECAY_hrs'
                        , nargs='?'
                        , help='Half-life of glitch impact exponential decay; zero=infinity.'
                        )

    cParse.add_argument("--glitchmaxlife", type=str
                        , dest='nGlitchMaxlife'
                        , metavar='nGLITCHMAXLIFE_hrs'
                        , nargs='?'
                        , help='Maximum duration of glitch impact, which ceases after this interval; zero=infinity.'
                        )

    cParse.add_argument("--shelfsize", type=str
                        , dest='nShelfSize'
                        , metavar='nSHELFSIZE_TB'
                        , nargs='?'
                        , help='Size for storage shelf in TB.'
                        )
   
    cParse.add_argument("--docsize", type=str
                        , dest='nDocSize'
                        , metavar='nDOCSIZE_MB'
                        , nargs='?'
                        , help='Document size in MB.'
                        )
    
# Other options that are not used for selection, but for overrides or testing.

    cParse.add_argument("--familydir", type=str
                        , dest='sFamilyDir'
                        , metavar='sFAMILYDIR'
                        , nargs='?'
                        , help='Family directory for param and log files.'
                        )
    
    cParse.add_argument("--specificdir", type=str
                        , dest='sSpecificDir'
                        , metavar='sSPECIFICDIR'
                        , nargs='?'
                        , help='Specific directory for param and log files.'
                        )
    
    cParse.add_argument("--testlimit", type=str
                        , dest='nTestLimit'
                        , metavar='nTESTLIMIT'
                        , nargs='?'
                        , help='TESTING ONLY: limit on number of runs to execute.'
                        )
    
    cParse.add_argument("--testcommand", type=str
                        , dest='sTestCommand'
                        , choices=['YES','Y','NO','N']
                        , nargs='?'
                        , help='TESTING ONLY: echo formatted commands only, not execute.'
                        )
    
    cParse.add_argument("--testfib", type=str
                        , dest='sTestFib'
                        , choices=['YES','Y','NO','N']
                        , nargs='?'
                        , help='TESTING ONLY: use fako Fibonacci CPU intensive process instead of real stuff.'
                        )
    

    if mysArglist:          # If there is a specific string, use it.
        (xx) = cParse.parse_args(mysArglist)
    else:                   # If no string, then parse from argv[].
        (xx) = cParse.parse_args()

    return vars(xx)

# f n M a y b e O v e r r i d e 
@ntracef("CLI")
def fnMaybeOverride(mysCliArg,mydDict,mycClass):
    ''' Strange function to override a property in a global dictionary
        if there is a version in the command line dictionary.  
    '''
    try:
        if mydDict[mysCliArg]:
            setattr( mycClass, mysCliArg, mydDict[mysCliArg] )
    except KeyError:
            if not getattr(mycClass, mysCliArg, None):
                setattr(mycClass, mysCliArg, None)
    return getattr(mycClass, mysCliArg, "XXXXX")

# f n I n t P l e a s e 
@ntracef("INT",level=5)
def fnIntPlease(myString):
    # If it looks like an integer, make it one.
    try:
        return int(myString)
    except ValueError:
        return myString


# class   C G   f o r   g l o b a l   d a t a 
class CG(object):
    ''' Global data.
    '''
    nCopies = None
    nLifem = None
    nAuditFreq = None
    sAuditType = None
    nAuditSegments = None
    nGlitchFreq = None
    nGlitchImpact = None
    nGlitchDecay = None
    nGlitchMaxlife = None
    nShelfSize = None
    nDocSize = None
    nCores = 8              # default, overridden by NCORES env var
    nCoreTimer = 10         # wait for a free core,
    nPoliteTimer = 10       # wait between launches.
    nStuckLimit = 100       # max nr of CoreTimer waits before giving up.
    nTestLimit = 0          # max nr of runs for a test run, 0=infinite
    sTestCommand = "NO"     # should just echo commands instead of executing them?
    sTestFib = "NO"         # should use Fibonacci calc instead of real programs?

    sFamilyDir = '../q3'
    sSpecificDir = '.'

    sDatabaseName = None
    sPendingCollectionName = None
    sDoneCollectionName = None

    # Command templates
    sShelfLogFileTemplate = 'doc{nDocSize}cop{nCopies}lif{nLifem}_af{nAuditFreq}s{nAuditSegments}t{sAuditType}_gf{nGlitchFreq}i{nGlitchImpact}d{nGlitchDecay}m{nGlitchMaxlife}_seed{nRandomseed}'
    sShelfLogFileName = None

    sShelfRunCmdTemplate = 'python main.py {sFamilyDir} {sSpecificDir} {nSimlen} {nRandomseed} --ncopies={nCopies} --lifek={nLifem}000 --audit={nAuditFreq} --auditsegments={nAuditSegments} --audittype={sAuditType} --glitchfreq={nGlitchFreq} --glitchimpact={nGlitchImpact} --glitchdecay={nGlitchDecay} --glitchmaxlife={nGlitchMaxlife} --shelfsize={nShelfSize} --mongoid=\'{_id}\'> {sFamilyDir}/{sSpecificDir}/log/{sShelfLogFileName}.log  2>&1'
    sExtractCmdTemplate = 'python extractvalues.py --header q3-extractinstructions-01.txt {sFamilyDir}/{sSpecificDir}/log/{sShelfLogFileName}.log > {sFamilyDir}/{sSpecificDir}/ext/{sShelfLogFileName}.ext'
    sCleanupCmdTemplate = 'python datacleanup.py {sFamilyDir}/{sSpecificDir}/ext/{sShelfLogFileName}.ext {sFamilyDir}/{sSpecificDir}/dat'

    # Make sure we have the right version of bash and Python.
    sBashIdCmd = 'sh --version'
    sPythonIdCmd = 'python -c "import sys; print sys.version; print sys.version_info"'

    lTemplates = [sBashIdCmd, sPythonIdCmd, sShelfRunCmdTemplate, sExtractCmdTemplate, sCleanupCmdTemplate]
    lCommands = []

    # The listactor command must redirect all output to a file.
    #  Otherwise, it will not run asynchronously to take advantage
    #  of multiple cores.
    sActorCmdFileTemplate = '{sFamilyDir}/{sSpecificDir}/cmd/{sShelfLogFileName}.cmds'
    sActorCmdFileName = None
    sActorCmdTemplate = 'python listactor.py {sActorCmdFileName} > {sFamilyDir}/{sSpecificDir}/act/{sShelfLogFileName}_actor.log 2>&1 &'
    sActorCmd = None

    # Only field names that appear in items in the database should ever
    #  be in the query dictionary.  Otherwise, no item in the database 
    #  can ever satisfy such a query, i.e., no results.  
    lSearchables = "nAuditFreq nAuditSegments sAuditType nDocSize nGlitchDecay nGlitchFreq nGlitchIgnorelevel nGlitchImpact nGlitchMaxlife nLifem nCopies nRandomseed nShelfSize nSimlen".split()

    # Special fake CPU-bound commands to test for proper parallel execution.  
    sFibCmd1 = 'python fib.py 42'
    sFibCmd2 = 'python fib.py 40'
    lFibTemplates = [sBashIdCmd, sPythonIdCmd, sFibCmd1, sFibCmd2]

    '''
    Directory structure under the family/specific dir:
    cmd - command files for the listactor program
    log - log file output from the main simulation runs
    act - little bitty log files from the listactor program
    ext - the single line (plus heading) extracts from the log files
    dat - the combined output from appending all the extract files (less 
          redundant headers)
    '''

# f n W a i t F o r O p e n i n g 
@ntracef("WAIT")
def fnbWaitForOpening(mynProcessMax,mysProcessName,mynWaitTime,mynWaitLimit):
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
         python27 for each simulation run.  Plus this broker program.
         So, if we are looking for python processes, the arithmetic ought to be 
         - how many pythons are running
         - subtract one for the broker
         - divide by two for the actor and the main
         - is that number greater than the stated limit?
    '''
    cCmd = CCommand()
    dParams = dict()
    dParams['Name'] = mysProcessName
    for idx in range(mynWaitLimit):
        sCmd = "ps | grep {Name} | wc -l"
        sFullCmd = cCmd.makeCmd(sCmd,dParams)
        sResult = cCmd.doCmdStr(sFullCmd)
        nResult = int(sResult)
        NTRC.trace(3,"proc WaitForOpening1 idx|%d| cmd|%s| result|%s|" % (idx,sFullCmd,nResult))
        if mysProcessName.find("python") >= 0:
            nOtherProcs = nResult - 1               # Processes that are not me.
            nRealProcs = int(nOtherProcs / 2)       # They come in pairs.
            if nRealProcs < mynProcessMax: break    # If there's still room, go to it.
        else:
            if nResult < mynProcessMax: break
        NTRC.trace(3,"proc WaitForOpening2 sleep and do again idx|%d| nResult|%d|" % (idx,nResult))
        time.sleep(mynWaitTime)
    return (idx < mynWaitLimit-1)


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
        sReNames = '(:?\{(\w+)\})+'
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
        dOut = dict()
        for sAttrib,sValue in mydCli.items():
            result = None
            if sValue is not None:
                try:
                    result = json.loads(sValue)
                except ValueError:
                    result = fnIntPlease(sValue)
                    NTRC.tracef(3, "FMT", "proc FormatQuery notjson item key|%s| val|%s| result|%s|" % (sAttrib, sValue, result))
            NTRC.tracef(3, "FMT", "proc FormatQuery item key|%s| val|%s| result|%s|" % (sAttrib, sValue, result))
            dOut[sAttrib] = result
        # Allow only attribs that appear in the database, else will get 
        #  no results due to implied AND of all items in query dict.  
        dOutSafe = {k:v for k,v in dOut.items() if k in g.lSearchables}
        dOutNotNone = {k:v for k,v in dOutSafe.items() if v is not None}
        return dOutNotNone

    @ntracef("FMT")
    def fnlFormatCommandsForInstructions(self, mydInstructions):
        '''
        Currently assumes that there are only two command, 
         one for run and one for extract.  Should generalize
         this someday.  
        '''
        oCmd = CCommand()
        dFilenames = dict(vars(CG))
        g.sShelfLogFileName = oCmd.makeCmd(g.sShelfLogFileTemplate, dFilenames)
        dFilenames = dict(vars(CG))
        sCmd1a = oCmd.makeCmd(g.sShelfCmdTemplate, mydInstructions)
        sCmd1b = oCmd.makeCmd(sCmd1a, dFilenames)
        sCmd2a = oCmd.makeCmd(g.sExtractCmdTemplate, mydInstructions)
        sCmd2b = oCmd.makeCmd(sCmd2a, dFilenames)
        return [sCmd1b, sCmd2b]

    @ntracef("FMT")
    def fnsFormatCommandForActor(self, myd):
        pass

    @ntracef("FMT")
    def fnsMaybeTest(self, mysCommand):
        '''
        If TestCommand says YES, then change the command line to a line
         that just echos the command line instead of actually doing it.
        '''
        if g.sTestCommand.startswith('Y'):
            sCommand = 'echo "{}"'.format(mysCommand)
        else:
            sCommand = mysCommand
        return sCommand


# class   C C o m m a n d
class CCommand(object):
    '''
    class to format and execute a CLI command, parse results
     using a regular expression supplied by the caller.  
    '''

    @ntracef("CMD")
    def doCmdStr(self,mysCommand):
        ''' Return concatenated string of result lines with newlines stripped.  
        '''
        sResult = ""
        for sLine in os.popen(mysCommand):
            sResult += sLine.strip()
        return sResult + "\n"
        
    @ntracef("CMD")
    def doCmdLst(self,mysCommand):
        ''' Return list of result lines with newlines stripped.  
        '''
        lResult = list()
        for sLine in os.popen(mysCommand):
            lResult.append(sLine.strip())
        return lResult
        
    @ntracef("CMD")
    def doParse(self,mysCommand,mysRegex):
        sOutput = self.doCmd(mysCommand)
        mCheck = search(mysRegex,sOutput)
        if mCheck:
            sResult = mCheck.groups()
        else:
            sResult = None
        return sResult

    @ntracef("CMD")
    def makeCmd(self,mysCmd,mydArgs):
        ''' Substitute arguments into command template string.  
        '''
        sCmd = mysCmd.format(**mydArgs)
        return sCmd



# M A I N 
@ntracef("MAIN")
def main():
    '''
    Process:
    - Query the db for pending instructions
    - For each instruction from database selection, get dict for line
    - Using dict args, construct plausible command lines, into file
    - Check to see that there aren't too many similar processes 
      running already; wait if so.
    - Launch ListActor process to execute commands.
    - Wait a polite interval before launching another.
    '''
    NTRC.ntracef(0,"MAIN","Begin.")
    # Get args from CLI and put them into the global data
    dCliDict = fndCliParse("")
    # Carefully insert any new CLI values into the Global object.
    fnMaybeOverride("sDatabaseName", dCliDict, g)
    fnMaybeOverride("sPendingCollectionName", dCliDict, g)
    fnMaybeOverride("sDoneCollectionName", dCliDict, g)
    fnMaybeOverride("nTestLimit", dCliDict, g)
    fnMaybeOverride("sTestCommand", dCliDict, g)
    fnMaybeOverride("sTestFib", dCliDict, g)
    fnMaybeOverride("sFamilyDir", dCliDict, g)
    fnMaybeOverride("sSpecificDir", dCliDict, g)

    # Construct database query for this invocation.
    cFmt = CFormat()
    dQuery = cFmt.fndFormatQuery(dCliDict)
    NTRC.tracef(0,"MAIN","proc querydict|%s|" % ((dQuery)))
    # Query pending instructions to get subset of work for today.
    oDb = mongolib.fnoOpenDb(g.sDatabaseName)
    oPendingCollection = oDb[g.sPendingCollectionName]
    oDoneCollection = oDb[g.sDoneCollectionName]
    nPendingCount = oPendingCollection.count()
    NTRC.ntracef(0,"MAIN","proc main nRecs|{}|".format(nPendingCount))
    itCurrentSet = oPendingCollection.find(dQuery)
    NTRC.ntracef(0,"MAIN","proc main itCurrentSet|{}|".format(itCurrentSet))

    # Allow user to override number of cores to use today.
    try:
        g.nCores = int(os.getenv("NCORES", CG.nCores))
    except (ValueError, TypeError):
        raise TypeError('Environment variable NCORES must be an integer.')
    nRunNumber = 0
    # And check for short test run.
    maxcount = int(g.nTestLimit)
    # Or a completely fake test run.
    if g.sTestFib.startswith("Y"):
        g.lTemplates = g.lFibTemplates

    for dInstruction in itCurrentSet: 
        NTRC.ntracef(3,"MAIN","proc main instruction\n|%s|" % (dInstruction))

        # If this instruction has already been processed skip it.
        sInstructionId = str(dInstruction["_id"])
        dIsItDone = { "sDoneId" : sInstructionId }
        lMaybeDone = list(oDoneCollection.find(dIsItDone))
        NTRC.ntracef(3,"MAIN","proc main donelist id|%s| list|%s|" % (sInstructionId, lMaybeDone))
        if len(lMaybeDone) > 0: continue

        bContinue = fnbWaitForOpening(g.nCores,"python",g.nCoreTimer,g.nStuckLimit)
        if bContinue:
            nRunNumber += 1
            # Format commands to be executed by actor.
            g.sShelfLogFileName = cFmt.msGentlyFormat(g.sShelfLogFileTemplate, dInstruction)
            g.lCommands = []
            for sTemplate in g.lTemplates:
                sCmd = cFmt.msGentlyFormat(sTemplate, dInstruction)
                g.lCommands.append(sCmd)

            # Make instruction file for the actor.
            g.sActorCmdFileName = cFmt.msGentlyFormat(g.sActorCmdFileTemplate, dInstruction)
            g.sActorCommand = cFmt.msGentlyFormat(g.sActorCmdTemplate, dInstruction)
            NTRC.ntracef(0,"MAIN","proc main commands run|%s|\n1|%s|\n2|%s|\n" % (nRunNumber,g.lCommands, g.sActorCommand))
            with open(g.sActorCmdFileName, 'w') as fhActorCmdFile:
                fhActorCmdFile.write("# ListActor automatically generated command file; do not edit.\n")
                for sCommand in g.lCommands:
                    print >> fhActorCmdFile, cFmt.fnsMaybeTest(sCommand)

            # Launch the actor to perform main runs.  
            cCmd = CCommand()
            sResult = cCmd.doCmdStr(g.sActorCommand)
            time.sleep(g.nPoliteTimer)    

            # If just doing a short test run today, maybe stop now.
            maxcount -= 1
            if int(g.nTestLimit) > 0 and maxcount <= 0: break

        else:
            NTRC.tracef(0,"MAIN","OOPS, Stuck!  Too many python processes running forever.")
            break

    NTRC.ntracef(0,"MAIN","End.")


#
# E n t r y   p o i n t . 
if __name__ == "__main__":
    g = CG()
    main()

#END

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
poll every, oh, minute or so
foreach log file in some holding dir
  move log file to its permanent home
foreach single-line file in holding dir
  append line to combined results file
  add _id to done tbl of db
  delete one-liner

'''
