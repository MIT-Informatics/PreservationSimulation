#!/usr/bin/python
'''
listactor.py

Run a sequence of commands specified in an instruction file.
Format of instruction file:
- Blank lines ignored.
- Comment lines, beginning with # ignored.
- A sequence of commands, fully fledged, with no subsitutions to be made.  

The commands are run in sequence, in separate processes 
spawned with os.popen().

@author: rblandau
'''
import csv
from sys            import argv
from os             import popen
from time           import localtime, sleep
import re
from NewTraceFac    import NTRC,ntrace,ntracef
import argparse

# C l i P a r s e 
@ntracef("CLI")
def fndCliParse(mysArglist):
    ''' Parse the mandatory and optional positional arguments, and the 
        many options for this run from the command line.  
        Return a dictionary of all of them.  Strictly speaking that is 
        not necessary, since most of them have already been decanted
        into the P params object.  
    '''
    sVersion = "0.0.1"
    cParse = argparse.ArgumentParser(description="Digital Library Preservation Simulation ListActor run sequencer",epilog="Defaults for args as follows:\n\
        (none), version=%s" % sVersion
        )

    # P O S I T I O N A L  arguments
    #cParse.add_argument('--something', type=, dest='', metavar='', help='')

    cParse.add_argument('sInstructionsFile', type=str
                        , metavar='sINSTRUCTIONFILE'
#                        , nargs="?"
                        , help='File with sequence of commands'
                        )

    # - - O P T I O N S
    # None today in this simplified version.  

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

# C C o m m a n d . d o C m d S t r 
    @ntrace
    def doCmdStr(self,mysCommand):
        ''' Return concatenated string of result lines with newlines stripped.  
        '''
        sResult = ""
        for sLine in popen(mysCommand):
            sResult += sLine.strip()
        return sResult
        
# C C o m m a n d . d o C m d L s t 
    @ntrace
    def doCmdLst(self,mysCommand):
        ''' Return list of result lines with newlines stripped.  
        '''
        lResult = list()
        for sLine in popen(mysCommand):
            lResult.append(sLine.strip())
        return lResult
        
# C C o m m a n d . d o C m d P a r s e  
    @ntrace
    def doCmdParse(self,mysCommand,mysRegex):
        ''' Execute command, collect results as a string, 
            parse out some results with the caller's regex,
            and return whatever pops out.  
        '''
        sOutput = self.doCmdStr(mysCommand)
        mCheck = search(mysRegex,sOutput)
        if mCheck:
            sResult = mCheck.groups()
        else:
            sResult = None
        return sResult

# C C o m m a n d . m a k e C m d 
    @ntrace
    def makeCmd(self,mysCmd,mydArgs):
        ''' Substitute arguments into command template string.  
        '''
        sCmd = mysCmd.format(**mydArgs)
        return sCmd

# f n b D o N o t I g n o r e L i n e 
@ntrace
def fnbDoNotIgnoreLine(mysLine):
    '''
    True if not a comment or blank line.
    '''
    # Ignore comment and blank lines.
    return (not re.match("^\s*#",mysLine)) and (not re.match("^\s*$",mysLine))

# f n l P a r s e I n p u t 
@ntrace
def fnlParseInput(mysFilename):
    ''' Return list of the non-blank, non-comment lines in the file.
    '''
    lCommands = list()
    with open(mysFilename,"rb") as fhInfile:
        for sLine in filter(fnbDoNotIgnoreLine, fhInfile):
            lCommands.append(sLine)
    return lCommands

# C G   c l a s s   f o r   g l o b a l   d a t a 
class CG(object):
    ''' Global data.
    '''
    sInstructionsFile = "instructions.txt"

# f n M a y b e O v e r r i d e 
@ntrace
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

'''
process:
- read command
- launch command with redirection and maybe no-wait &
- wait a while before launching another
'''

# M A I N 
@ntrace
def main():
    g = CG()                # One instance of the global data.
    
    dCliDict = fndCliParse("")
    # Carefully insert any new CLI values into the Global object.
    fnMaybeOverride("sInstructionsFile",dCliDict,g)

    # Read the file of instructions.  
    sFilename = g.sInstructionsFile
    lCommands = fnlParseInput(sFilename)
    cCommand = CCommand()

    # Process the instructions one line at a time.
    for sFullCmd in lCommands:
        # Print something to let the user know there is progress.
        print('-----------------')
        NTRC.trace(0,sFullCmd)
        print('-----------------')
        lResult = cCommand.doCmdLst(sFullCmd)
        for sResult in lResult:
            NTRC.trace(0,"stdout=|%s|" % (sResult))
        print '-----------------'

# E n t r y   p o i n t . 
if __name__ == "__main__":
    main()

#END
