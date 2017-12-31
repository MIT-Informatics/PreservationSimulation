#!/usr/bin/python
# brokergroupform.py
# Form to collect params for PreservationSimulation broker.py.
# Creates the crazy way-too-large form of broker options.
# Runs the program and may collect the results to show on the page.

import os
#from bottle import route, run, template, request, get, post, \
#    static_file, view, response
from catchex import catchex
from NewTraceFac import NTRC, ntrace, ntracef
import re
#import subprocess
import util


#==============  U T I L I T I E S  ===============


# f n V a l i d a t e D i r e c t o r i e s 
@ntrace
def fnValidateDirectories(dVals):
    sFamily = dVals["sFamilyDir"]
    sSpecific = dVals["sSpecificDir"]
    sPath = sFamily + "/" + sSpecific
    sValidationErrorMsg = ("<h2>"
                        "ERROR: directory not found: "
                        "\"%s\""
                        "</h2>"
                        % (sPath))
    if (sFamily and sSpecific
    and os.path.exists(sPath) and os.path.isdir(sPath)):
        return ""
    else:
        return sValidationErrorMsg


# class   C C o m m a n d
class CCommand(object):
    '''
    Class to format and execute a CLI command, parse results
     using a regular expression supplied by the caller.  
    Nothing specific here, so should probably be a separate module.  
    '''


# m D o C m d S t r ( )
    @catchex
    @ntracef("CMD")
    def mDoCmdStr(self,mysCommand):
        ''' Return concatenated string of result lines with newlines stripped.  
        '''
        sResult = ""
        for sLine in os.popen(mysCommand):
            sResult += sLine.strip()
        return sResult


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


#==============  M A I N   P A G E  ===============


from brokergroupform_main import *



#==============  S E T U P  P A G E  ===============


from brokergroupform_setup import *


#==============  M A I N  ===============


@ntrace
def runme():
    port = int(os.environ.get('PORT', 8080))
    run(host='0.0.0.0', port=port, debug=True, reloader=True)


#==============  E N T R Y   P O I N T  ===============


if __name__ == '__main__':
    cCmd = CCommand()
    print("")
    runme()


# Edit history:
# 20161230  RBL Original version, adapted from mainsimform.py.
# 20170101  RBL Flesh out most of it.
# 20170104  RBL Add Mongo-style range specifiers for ncopies and lifem.
# 20170214  RBL Change name pending to inprogress, no big deal.  
#               Remove dbname from generated command line.
# 20170221  RBL Change to use form generated by brokergroup_makeform.py
#                from .ins3 instruction files using Jinja2 template processor.
#               Call the makeform program to, guess what, make the form.  
# 20170318  RBL Validate directories before issuing broker command.
# 20170420  RBL Add tracing.
# 20170520  RBL Add Redo checkbox.
# 20171130  RBL Accept multi-select inputs, format as json lists. 
#                Affects nCopies, nLifem, 
#                nGlitchFreq, nGlitchImpact, nGlitchMaxlife, 
#                nShockFreq, nShockImpact, nShockMaxlife, nShockSpan.
# 20171230  RBL Add processing for setup page to establish 
#                output directory structure, erase done records, etc.
#               Segregate main and setup page processing into separate modules.
# 
# 

#END
