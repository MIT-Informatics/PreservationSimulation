#!/usr/bin/python
# command.py
# Functions to execute CLI commands and collect output.


from catchex import catchex
from NewTraceFac import NTRC, ntrace, ntracef
import os
import re


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
        return self.mDoCmdStr(mysCommand)

    # m D o C m d S t r ( )
    @catchex
    @ntracef("CMD")
    def mDoCmdStr(self,mysCommand):
        ''' Return concatenated string of result lines with newlines stripped.  
        '''
        sResult = ""
        for sLine in os.popen(mysCommand):
            sResult += sLine.rstrip()
        return sResult


    @catchex
    @ntracef("CMD")
    def doCmdLst(self,mysCommand):
        return self.mDoCmdLst(mysCommand)

    # m D o C m d L s t ( ) 
    @catchex
    @ntracef("CMD")
    def mDoCmdLst(self,mysCommand):
        ''' Return list of result lines with newlines stripped.  
        '''
        lResult = list()
        for sLine in os.popen(mysCommand):
            lResult.append(sLine.rstrip())
        return lResult


    @catchex
    @ntracef("CMD")
    def doCmdGen(self,mysCommand):
        return self.mDoCmdGen(mysCommand)

    # m D o C m d G e n ( ) 
    @catchex
    @ntracef("CMD")
    def mDoCmdGen(self, mysPrefix, mysSuffix, 
        mysLinePrefix, mysLineSuffix, mysCommand):
        ''' 
        Generator that returns lines with newlines intact.  
        Adds prefix before and suffix after the entire block of lines
         obtained by executing the command.
        Add lineprefix and linesuffix to each line in turn.  
        (All this so we can output HTML and not just plaintext.)
        '''
        yield mysPrefix
        for sLine in os.popen(mysCommand):
            yield mysLinePrefix + sLine + mysLineSuffix
        yield mysSuffix


    @catchex
    @ntracef("CMD")
    def doParse(self,mysCommand):
        return self.mDoParse(mysCommand)

    # m D o P a r s e ( )         
    @catchex
    @ntracef("CMD")
    def mDoParse(self,mysCommand,mysRegex):
        sOutput = self.doCmd(mysCommand)
        mCheck = search(mysRegex,sOutput)
        if mCheck:
            sResult = mCheck.groups()
        else:
            sResult = None
        return sResult


    @catchex
    @ntracef("CMD")
    def makeCmd(self,mysCommand):
        return self.mMakeCmd(mysCommand)

    # m M a k e C m d ( )
    @catchex
    @ntracef("CMD")
    def mMakeCmd(self,mysCmd,mydArgs):
        ''' Substitute arguments into command template string.  
        '''
        sCmd = mysCmd.format(**mydArgs)
        return sCmd


    # m G e n t l y F o r m a t ( )
    @ntrace
    def mGentlyFormat(self, mysCmd, mydVals):
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
        #NTRC.ntracef(3,"FMT","proc gently tuples|%s|" % (lNameTuples))
        lNames = [x[1] for x in lNameTuples]
        dNames = dict(zip(lNames, map(lambda s: "{"+s+"}", lNames)))
        # And then add values from the specific instructions.
        dNames.update(mydVals)
        #NTRC.ntrace(3,"proc gently dnames|%s|" % (dNames))
        sOut = mysCmd.format(**dNames)
        return sOut


# Edit history
# 20170126  RBL Original version, extracted from broker.py.
# 20171231  RBL Replace with slightly more advanced version that includes
#                mGentlyFormat.
#               And correctly only rstrips newlines from string and list.
#               Oh, and catch all the old names that I changed, oops.
# 20180104  RBL Remove old version, which had been commented out with if 0.
# 

#END
