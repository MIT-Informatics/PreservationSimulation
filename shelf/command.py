#!/usr/bin/python
# command.py
# Functions to execute CLI commands and collect output.


from catchex import catchex
from NewTraceFac import NTRC, ntrace, ntracef
import os


#===========================================================

# class   C C o m m a n d
class CCommand(object):
    '''
    Class to format and execute a CLI command, parse results
     using a regular expression supplied by the caller.  
    Nothing specific here, so should probably be a separate module.  
    '''

    @catchex
    @ntracef("CMD")
    def doCmdStr(self,mysCommand):
        ''' Return concatenated string of result lines with newlines stripped.  
        '''
        sResult = ""
        for sLine in os.popen(mysCommand):
            sResult += sLine.strip()
        return sResult
        
    @catchex
    @ntracef("CMD")
    def doCmdLst(self,mysCommand):
        ''' Return list of result lines with newlines stripped.  
        '''
        lResult = list()
        for sLine in os.popen(mysCommand):
            lResult.append(sLine.strip())
        return lResult
        
    @catchex
    @ntracef("CMD")
    def doParse(self,mysCommand,mysRegex):
        sOutput = self.doCmd(mysCommand)
        mCheck = search(mysRegex,sOutput)
        if mCheck:
            sResult = mCheck.groups()
        else:
            sResult = None
        return sResult

    @catchex
    @ntracef("CMD")
    def makeCmd(self,mysCmd,mydArgs):
        ''' Substitute arguments into command template string.  
        '''
        sCmd = mysCmd.format(**mydArgs)
        return sCmd

# Edit history
# 20170126  RBL Original version, extracted from broker.py.
# 
# 

#END
