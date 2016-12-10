#!/usr/bin/python
# mainsimform.py
# Form to collect params for PreservationSimulation main.py.
# Runs the program and may collect the results to show on the page.

import os
from bottle import route, run, template, request, get, post, static_file, view
from catchex import catchex
from NewTraceFac import NTRC, ntrace, ntracef
import re


@get('/')
@get('/mainsim')
def mainsim_get():
    return template('mainsim_form')

@post('/mainsim')
def mainsim_post():
    # Collect all the bloody data, one item at a time, grumble.
    sFamilyDir = request.forms.get("sFamilyDir")
    sSpecificDir = request.forms.get("sSpecificDir")

    nCopies= request.forms.get("nCopies")
    nRandomSeed = request.forms.get("nRandomSeed")

    nLifem = request.forms.get("nLifem")
    nLifek = request.forms.get("nLifek")

    nAuditFreq = request.forms.get("nAuditFreq")
    nAuditSegments = request.forms.get("nAuditSegments")
    sAuditType = request.forms.get("sAuditType")

    nGlitchFreq = request.forms.get("nGlitchFreq")
    nGlitchImpact = request.forms.get("nGlitchImpact")
    nGlitchMaxlife = request.forms.get("nGlitchMaxlife")
    nGlitchSpan = request.forms.get("nGlitchSpan")
    nGlitchDecay = request.forms.get("nGlitchDecay")

    bShortLog = request.forms.get("bShortLog")
    sLogLevel = request.forms.get("sLogLevel")
    sLogFile = request.forms.get("sLogFile")

    nShelfSize = request.forms.get("nShelfSize")
    nSmallDoc = request.forms.get("nSmallDoc")
    nLargeDoc = request.forms.get("nLargeDoc")
    nSmallDocPct = request.forms.get("nSmallDocPct")
    nPctDocVar = request.forms.get("nPctDocVar")

    nSimLength = request.forms.get("nSimLength")
    nBandwidthMbps = request.forms.get("nBandwidthMbps")

    msg = "mainsim_post: NOT YET IMPLEMENTED"

    # Make a dictionary to use to substitute params into CLI command.
    dVals = dict(sFamilyDir=sFamilyDir, sSpecificDir=sSpecificDir,
                nCopies=nCopies, nRandomSeed=nRandomSeed, 
                nLifem=nLifem, nLifek=nLifek,
                nAuditFreq=nAuditFreq, nAuditSegments=nAuditSegments, 
                sAuditType=sAuditType,
                nGlitchFreq=nGlitchFreq, nGlitchImpact=nGlitchImpact, 
                nGlitchMaxlife=nGlitchMaxlife, nGlitchSpan=nGlitchSpan, 
                nGlitchDecay=nGlitchDecay, 
                bShortLog=bShortLog, sLogLevel=sLogLevel, sLogFile=sLogFile, 
                nShelfSize=nShelfSize, nSmallDoc=nSmallDoc, nLargeDoc=nLargeDoc, 
                nSmallDocPct=nSmallDocPct, nPctDocVar=nPctDocVar, 
                nSimLength=nSimLength, nBandwidthMbps=nBandwidthMbps, 

                msg=msg
                )

    # Adjust lifem and lifek.
    if dVals["nLifem"] == "none" or dVals["nLifek"] != "":
       dVals["nLifek"] = str(dVals["nLifek"])
    else:
        dVals["nLifek"] = str(dVals["nLifem"])+"000"

    # Do something with the form data
#    print("<br/>Working...")   # How do we put this out into the HTML stream async?
#    print("")                  # ?
    sActualCli = cCmd.mGentlyFormat(sMainCommandStringToStdout, dVals)
#    sActualCli = cCmd.mGentlyFormat(sMainCommandStringWithLog, dVals)
#    sActualCli = cCmd.mGentlyFormat(sMainCommandStringTestOnly, dVals)
#    sActualCli = cCmd.mGentlyFormat(sMainCommandStringDumbTest, dVals)
    lResult = cCmd.mDoCmdLst(sActualCli)
    sOutput = '<font face="Courier">\n'
    sOutput += sActualCli+"<br />\n"
    for line in lResult:
        sOutput += "<br />"+line.expandtabs(4)+"\n"
    sOutput += "</font>\n"
#    return dVals         # TEMP: return dict for visual inspection.
    return sOutput      # TEMP: See if the test command even works.

# CLI commands to run the main program.
sMainCommandStringWithLog = '''python main.py {sFamilyDir} {sSpecificDir} {nSimLength} {nRandomSeed} --ncopies={nCopies} --lifek={nLifek} --audit={nAuditFreq} --auditsegments={nAuditSegments} --audittype={sAuditType} --glitchfreq={nGlitchFreq} --glitchimpact={nGlitchImpact} --glitchdecay={nGlitchDecay} --glitchmaxlife={nGlitchMaxlife} --glitchspan={nGlitchSpan} --shelfsize={nShelfSize} --smalldoc={nSmallDoc} --largedoc={nLargeDoc} --pctsmall={nSmallDocPct} --mongoid={mongoid}  >  {sFamilyDir}/{sSpecificDir}/log/{sLogFile}.log  2>&1
'''
sMainCommandStringToStdout = '''python main.py {sFamilyDir} {sSpecificDir} {nSimLength} {nRandomSeed} --ncopies={nCopies} --lifek={nLifek} --audit={nAuditFreq} --auditsegments={nAuditSegments} --audittype={sAuditType} --glitchfreq={nGlitchFreq} --glitchimpact={nGlitchImpact} --glitchdecay={nGlitchDecay} --glitchmaxlife={nGlitchMaxlife} --glitchspan={nGlitchSpan} --shelfsize={nShelfSize} --smalldoc={nSmallDoc} --largedoc={nLargeDoc} --pctsmall={nSmallDocPct} --mongoid={mongoid}   2>&1
'''
sMainCommandStringTestOnly = '''python main.py -h
'''
sMainCommandStringDumbTest = '''ls -l
'''

#=================================================
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



def runme():
    port = int(os.environ.get('PORT', 8080))
    run(host='localhost', port=port, debug=True, reloader=True)

if __name__ == '__main__':
    cCmd = CCommand()
    print("")
    runme()


