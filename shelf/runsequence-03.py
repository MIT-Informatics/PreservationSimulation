#!/usr/bin/python
'''
runsequence.py

Run a sequence of commands specified in an instruction file.
Format of instruction file:
- Blank lines ignored.
- Comment lines, beginning with # ignored.
- The first non-blank, non-comment line is the command template.  
The template is processed with the Python string.format() function, 
so you probably want to use keyword args in braces.

The program limits the number of simultaneous processes to the --ncores 
option.  It looks for the number of python instances in ps, waits if 
there are too many, looks again.  

@author: landau
'''
import csv
from util           import fnIntPlease
from sys            import argv
from os             import popen
from time           import localtime, sleep
import re
from NewTraceFac    import TRC,trace,tracef
import argparse

# C l i P a r s e 
@tracef("CLI")
def fndCliParse(mysArglist):
    ''' Parse the mandatory and optional positional arguments, and the 
        many options for this run from the command line.  
        Return a dictionary of all of them.  Strictly speaking that is 
        not necessary, since most of them have already been decanted
        into the P params object.  
    '''
    sVersion = "0.0.1"
    cParse = argparse.ArgumentParser(description="Digital Library Preservation Simulation Run Sequencer",epilog="Defaults for args as follows:\n\
        cores=2, \n\
        coretimer=20 sec, \
        stucklimit=99, \
        file=instructions.txt, version=%s" % sVersion
        )

    # P O S I T I O N A L  arguments
    #cParse.add_argument('--something', type=, dest='', metavar='', help='')

    cParse.add_argument('sInstructionsFile', type=str
                        , metavar='sINSTRUCTIONFILE'
                        , nargs="?"
                        , help='File with command template and CSV params'
                        )

    # - - O P T I O N S

    cParse.add_argument("--ncores", type=int
                        , dest='nCores'
                        , metavar='nCORES'
                        , help='Number of cores to feed at fast rate (coretimer)'
                        )

    cParse.add_argument("--coretimer", type=int
                        , dest='nCoreTimer'
                        , metavar='nCORETIMER'
                        , help='Time between starts up to the number of cores, in seconds'
                        )

#    cParse.add_argument("--grouptimer", type=int
#                        , dest='nGroupTimer'
#                        , metavar='nGROUPTIMER'
#                        , help='Time between groups of starts (up to nCores #max), in seconds'
#                        )

    cParse.add_argument("--stucklimit", type=int
                        , dest='nStuckLimit'
                        , metavar='nSTUCKLIMIT'
                        , help='Max nr of nCORETIMER intervals to wait before giving up waiting for a free core'
                        )

    if mysArglist:          # If there is a specific string, use it.
        (xx) = cParse.parse_args(mysArglist)
    else:                   # If no string, then parse from argv[].
        (xx) = cParse.parse_args()

    return vars(xx)


# class  C C o m m a n d
class CCommand(object):
    '''
    class CCommand: Execute a CLI command, parse results
    using a regular expression supplied by the caller.  
    '''

    @trace
    def doCmdStr(self,mysCommand):
        ''' Return concatenated string of result lines with newlines stripped.  
        '''
        sResult = ""
        for sLine in popen(mysCommand):
            sResult += sLine.strip()
        return sResult
        
    @trace
    def doCmdLst(self,mysCommand):
        ''' Return list of result lines with newlines stripped.  
        '''
        lResult = list()
        for sLine in popen(mysCommand):
            lResult.append(sLine.strip())
        return lResult
        
    @trace
    def doParse(self,mysCommand,mysRegex):
        sOutput = self.doCmd(mysCommand)
        mCheck = search(mysRegex,sOutput)
        if mCheck:
            sResult = mCheck.groups()
        else:
            sResult = None
        return sResult

    @trace
    def makeCmd(self,mysCmd,mydArgs):
        ''' Substitute arguments into command template string.  
        '''
        sCmd = mysCmd.format(**mydArgs)
        return sCmd

# f n d P a r s e I n p u t 
@trace
def fndParseInput(mysFilename):
    ''' Return tuple containing
        - the command template string, 
        - a list, one item per line, of dicts of column args.  
        Make sure that (duck-type) integers remain integers.  
    '''
    lParams = list()
    with open(mysFilename,"rb") as fhInfile:
        lLines = fhInfile.readlines()
        # Remove comments.  
        for sLine in lLines[:]:
            if re.match("^ *#",sLine) or re.match("^ *$",sLine.rstrip()):
                lLines.remove(sLine)
                TRC.trace(3,"proc ParseInput remove comment or blank line |%s|" % (sLine.strip()))
        # The first non-blank, non-comment line is the command template.
        sCmd = lLines.pop(0).strip()
        TRC.trace(3,"proc ParseInput command line|%s|" % (sCmd))
        # Now get the CSV args into a list of dictionaries.
        lRowDicts = csv.DictReader(lLines)
        for dRow in lRowDicts:
            dNewRow = dict()
            # Sanitize (i.e., re-integerize) the entire row dict, 
            #  keys and values, and use the new version instead.
            # Exception: strings that look like integers but have 
            #  leading zeros will be kept as strings.  This is to 
            #  avoid corrupting the BER strings that are used in 
            #  directory and file names.  (The BER string is always
            #  a value, not a key.)  
            for xKey in dRow:
                sValue = dRow[xKey]
                if type(sValue) == type('str') and sValue.startswith('0'):
                    dNewRow[fnIntPlease(xKey)] = sValue
                else:
                    dNewRow[fnIntPlease(xKey)] = fnIntPlease(sValue)
            # Put it back into a list, in order.
            lParams.append(dNewRow)
            TRC.trace(5,"proc fndParseInput dRow|%s| dNewRow|%s| lParams|%s|" % (dRow,dNewRow,lParams))
    return (sCmd,lParams)

# C G   c l a s s   f o r   g l o b a l   d a t a 
class CG(object):
    ''' Global data.
    '''
    sInstructionsFile = "instructions.txt"
    nCores = 2
    nCoreTimer = 10
    nGroupTimer = 60
    nStuckLimit = 299
    nPoliteTimer = 5

# f n M a y b e O v e r r i d e 
@trace
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

# f n W a i t F o r O p e n i n g 
@trace
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
        TRC.trace(3,"proc WaitForOpening1 idx|%d| cmd|%s| result|%s|" % (idx,sFullCmd,sResult))
        if nResult < mynProcessMax + 1 if (mysProcessName.find("python") >= 0) else 0:
            break
        TRC.trace(3,"proc WaitForOpening2 sleep and do again idx|%d| nResult|%d|" % (idx,nResult))
        sleep(mynWaitTime)
    return (idx < mynWaitLimit-1)


'''
process:
- read command
- read csv file into list
- for each line, get dict for line
- using dict args, construct plausible command line
- check to see that there aren't too many running already
- if too many pythons already running, wait a while and look again.
- launch command with redirection and maybe no-wait &
- wait a while before launching another
'''

# M A I N 
@trace
def main():
    g = CG()                # One instance of the global data.
    
    dCliDict = fndCliParse("")
    # Carefully insert any new CLI values into the Global object.
    fnMaybeOverride("sInstructionsFile",dCliDict,g)
    fnMaybeOverride("nCores",dCliDict,g)
    fnMaybeOverride("nCoreTimer",dCliDict,g)
#    fnMaybeOverride("nGroupTimer",dCliDict,g)
    fnMaybeOverride("nStuckLimit",dCliDict,g)

    # Read the file of instructions.  
    sFilename = g.sInstructionsFile
    (sCommand,lParams) = fndParseInput(sFilename)
    cCommand = CCommand()

    # Process the instructions one line at a time.
    for idx in range(len(lParams)):
        # Wait until at least one core is free.  
        bContinue = fnWaitForOpening(g.nCores,"python",g.nCoreTimer,g.nStuckLimit)
        if bContinue:
            # Substitute params and execute command.
            dParams = lParams[idx]
            sFullCmd = cCommand.makeCmd(sCommand,dParams)
            # Print something to let the user know there is progress.
            print '-----------------'
            TRC.trace(0,sFullCmd)
            print '-----------------'
            lResult = cCommand.doCmdLst(sFullCmd)
            for sResult in lResult:
                TRC.trace(0,sResult)
            print '-----------------'
            sleep(g.nPoliteTimer)
        else:
            TRC.trace(0,"OOPS, Stuck!  Too many python processes running forever.")
            break

# E n t r y   p o i n t . 
if __name__ == "__main__":
    main()
