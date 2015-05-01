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
    sVersion = "0.0.1"
    cParse = argparse.ArgumentParser(description="Digital Library Preservation Simulation Instruction Broker CLI v"+sVersion+"  "+
        "Enter either a value or a MongoDB dictionary spec " + 
        "in curly braces for $gt, $lt, etc., for each option.  " + 
        "Note that special characters such as $ { } must be escaped " +
        "or single-quoted to protect them from the shell.  " + 
        "OOPS: A string that looks like a dictionary is not a dictionary!" +
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
            if not getattr(mycClass,mysCliArg,None):
                setattr( mycClass, mysCliArg, None )
    return getattr(mycClass,mysCliArg,"XXXXX")

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
    
    sFamilyDir = '../../q3'
    sSpecificDir = '.'
    
    sShelfRunCmdTemplate = 'echo "    python main.py {sFamilyDir} {sSpecificDir} {nSimlen} {nRandomseed} --ncopies={nCopies} --lifem={nLifem} --audit={nAuditFreq} --auditsegments={nAuditSegments} --audittype={sAuditType} --glitchfreq={nGlitchFreq} --glitchimpact={nGlitchImpact} --glitchdecay={nGlitchDecay} --glitchmaxlife={nGlitchMaxlife} --shelfsize={nShelfSize} --docsize={nDocSize} --mongoid=\'{_id}\'> {sFamilyDir}/{sSpecificDir}/log/{sShelfLogFileName}.log  2>&1"'
    sExtractCmdTemplate = 'echo "    python extractsomethingorother {sFamilyDir}/{sSpecificDir}/log/{sShelfLogFileName}.log > {sFamilyDir}/{sSpecificDir}/dat/{sShelfLogFileName}.ext"'


    # TEMP TEMP TEMP
    sShelfRunCmdTemplate = ""
    sExtractCmdTemplate = 'python test/fib.py 42'
    # END


    sActorCmdFileTemplate = '{sFamilyDir}/{sSpecificDir}/cmd/{sShelfLogFileName}.cmds'
    sActorCmdFileName = None
    sActorCmdTemplate = 'python listactor.py {sActorCmdFileName} &'
    sActorCmd = None
    
    sShelfLogFileTemplate = 'doc{nDocSize}cop{nCopies}lif{nLifem}_af{nAuditFreq}s{nAuditSegments}t{sAuditType}_gf{nGlitchFreq}i{nGlitchImpact}d{nGlitchDecay}m{nGlitchMaxlife}_seed{nRandomseed}'
    sShelfLogFileName = None


# f n W a i t F o r O p e n i n g 
@ntracef("WAIT")
def fnWaitForOpening(mynProcessMax,mysProcessName,mynWaitTime,mynWaitLimit):
    ''' Wait for a small, civilized number of processes to be running.  
        If the number is too large, wait a while and look again.  
        But don't wait forever in case something is stuck.  
        Args: 
        - max nr of processes, including maybe this one
        - process name to look for
        - wait time between retries
        - max nr of retries before giving up
    '''
    cCmd = CCommand()
    dParams = dict()
    dParams['Name'] = mysProcessName
    for idx in range(mynWaitLimit):
        sCmd = "ps | grep {Name} | wc -l"
        sFullCmd = cCmd.makeCmd(sCmd,dParams)
        sResult = cCmd.doCmdStr(sFullCmd)
        nResult = int(sResult)
        NTRC.trace(3,"proc WaitForOpening1 idx|%d| cmd|%s| result|%s|" % (idx,sFullCmd,sResult))
        if nResult < mynProcessMax + 1 if (mysProcessName.find("python") >= 0) else 0:
            break
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
        NTRC.ntrace(3,"proc gently tuples|%s|" % (lNameTuples))
        lNames = [x[1] for x in lNameTuples]
        dNames = dict(zip(lNames, map(lambda s: "{"+s+"}", lNames)))
        # Pick up any specified values in the global object.
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
            if sValue is not None:
                try:
                    dOut[sAttrib] = json.loads(sValue)
                except ValueError:
                    dOut[sAttrib] = fnIntPlease(sValue)
        del dOut["sDatabaseName"]
        del dOut["sPendingCollectionName"]
        del dOut["sDoneCollectionName"]
        return dOut
    
    @ntracef("FMT")
    def fnlFormatCommandsForInstructions(self, mydInstructions):
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

    cFmt = CFormat()
    dQuery = cFmt.fndFormatQuery(dCliDict)
    NTRC.tracef(0,"MAIN","proc querydict|%s|" % ((dQuery)))

    oDb = mongolib.fnoOpenDb(g.sDatabaseName)
    oPendingCollection = oDb[g.sPendingCollectionName]
    nRecordCount = oPendingCollection.count()
    NTRC.ntracef(0,"MAIN","proc main nRecs|{}|".format(nRecordCount))

    itCurrentSet = oPendingCollection.find(dQuery)
    
    maxcount = 1
    
    for dInstruction in itCurrentSet: 
        NTRC.ntracef(3,"MAIN","proc main instruction\n|%s|" % (dInstruction))
        bContinue = fnWaitForOpening(g.nCores,"python",g.nCoreTimer,g.nStuckLimit)
        if bContinue:
            g.sShelfLogFileName = cFmt.msGentlyFormat(g.sShelfLogFileTemplate, dInstruction)
            sRunCommand = cFmt.msGentlyFormat(g.sShelfRunCmdTemplate, dInstruction)
            sExtractCommand = cFmt.msGentlyFormat(g.sExtractCmdTemplate, dInstruction)
    
            # Make instruction file for the actor and launch it.
            g.sActorCmdFileName = cFmt.msGentlyFormat(g.sActorCmdFileTemplate, dInstruction)
            g.sActorCommand = cFmt.msGentlyFormat(g.sActorCmdTemplate, dInstruction)
            NTRC.ntracef(0,"MAIN","proc main cmds\n1|%s|\n2|%s|\n3|%s|" % (sRunCommand, sExtractCommand, g.sActorCommand))
            
            with open(g.sActorCmdFileName, 'w') as fhActorCmdFile:
                print >> fhActorCmdFile, sRunCommand
                print >> fhActorCmdFile, sExtractCommand
            cCmd = CCommand()
            sResult = cCmd.doCmdStr(g.sActorCommand)
            time.sleep(g.nPoliteTimer)    
    
            
            maxcount -= 1
            if maxcount < 0: break



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
poll every, oh, minute
foreach log file in some holding dir
  move log file to its permanent home
foreach single-line file in holding dir
  append line to combined results file
  add _id to done tbl of db
  delete one-liner


'''
