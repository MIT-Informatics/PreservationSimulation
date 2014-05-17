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

@author: landau
'''
import csv
from util           import fnIntPlease
from sys            import argv
from os             import popen
from time           import localtime, sleep
import re
from NewTraceFac    import TRC,trace,tracef

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
            # keys and values, and use the new version instead.
            for xKey in dRow:
                dNewRow[fnIntPlease(xKey)] = fnIntPlease(dRow[xKey])
            # Put it back into a list, in order.
            lParams.append(dNewRow)
            TRC.trace(5,"proc fndParseInput dRow|%s| dNewRow|%s| lParams|%s|" % (dRow,dNewRow,lParams))
    return (sCmd,lParams)

'''
process:
- read command
- read csv file into list
- for each line, get dict for line
- using dict args, construct plausible command line
- launch command with redirection
- wait a while before launching another
'''

# M A I N 
@trace
def main():
    sFilename = argv[1] if len(argv)>1 else "instructions.txt"
    (sCommand,lParams) = fndParseInput(sFilename)
    cCommand = CCommand()
    for dParams in lParams:
        sFullCmd = cCommand.makeCmd(sCommand,dParams)
        lResult = cCommand.doCmdLst(sFullCmd)
        print '-----------------'
        print sFullCmd
        print '-----------------'
        for sResult in lResult:
            print sResult
        print '-----------------'
        sleep(20)

if __name__ == "__main__":
    main()
