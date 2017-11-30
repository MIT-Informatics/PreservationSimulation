#!/usr/bin/python
# brokergroupform.py
# Form to collect params for PreservationSimulation broker.py.
# Creates the crazy way-too-large form of broker options.
# Runs the program and may collect the results to show on the page.

import os
from bottle import route, run, template, request, get, post, \
    static_file, view, response
from catchex import catchex
from NewTraceFac import NTRC, ntrace, ntracef
import re
import subprocess
import util


@get('/')
@get('/broker')
@get('/mainsim')
@ntrace
def mainsim_get():
    sMakeformCmd = ('python brokergroup_makeform.py '
                        'brokergroup_form_insert.j2 '
                        'views/brokergroup_form2.tpl '
                        'instructions')
    result = subprocess.check_output(sMakeformCmd, shell=True)
    return template('brokergroup_form2')

@post('/broker')
@post('/mainsim')
@ntrace
def mainsim_post():
#   C O L L E C T   D A T A 
    # Collect all the bloody data, one item at a time, grumble.
    sFamilyDir = request.forms.get("sFamilyDir")
    sSpecificDir = request.forms.get("sSpecificDir")

    lCopies= request.forms.getall("nCopies")

    lLifem = request.forms.getall("nLifem")
    nServerDefaultLife = request.forms.get("nServerDefaultLife")

    nAuditFreq = request.forms.get("nAuditFreq")
    nAuditSegments = request.forms.get("nAuditSegments")
    sAuditType = request.forms.get("sAuditType")

    lGlitchFreq = request.forms.getall("nGlitchFreq")
    lGlitchImpact = request.forms.getall("nGlitchImpact")
    lGlitchMaxlife = request.forms.getall("nGlitchMaxlife")
    nGlitchSpan = request.forms.get("nGlitchSpan")
    nGlitchDecay = request.forms.get("nGlitchDecay")

    lShockFreq = request.forms.getall("nShockFreq")
    lShockImpact = request.forms.getall("nShockImpact")
    lShockSpan = request.forms.getall("nShockSpan")
    lShockMaxlife = request.forms.getall("nShockMaxlife")

    nDocSize = request.forms.get("nDocSize")
    nShelfSize = request.forms.get("nShelfSize")

    bShortLog = request.forms.get("bShortLog")

    nRandomSeeds = request.forms.get("nRandomSeeds")
    nSimLength = request.forms.get("nSimLength")
    nBandwidthMbps = request.forms.get("nBandwidthMbps")

    bRedo = request.forms.get("bRedo")
    bTestOnly = request.forms.get("bTestOnly")
    sDatabaseName = request.forms.get("sDatabaseName")

    msg = "mainsim_post: NOT YET IMPLEMENTED"

#   F O R M   D I C T I O N A R Y   O F   S U B S T I T U T I O N S 
    # Make a dictionary to use to substitute params into CLI command.
    dVals = dict(sFamilyDir=sFamilyDir, sSpecificDir=sSpecificDir,

                sCopies=fnsQuoteMulti(lCopies),
                nServerDefaultLife=nServerDefaultLife, 

                sLifem=fnsQuoteMulti(lLifem), 

                nAuditFreq=nAuditFreq, nAuditSegments=nAuditSegments, 
                sAuditType=sAuditType,

                sGlitchFreq=fnsQuoteMulti(lGlitchFreq), 
                sGlitchImpact=fnsQuoteMulti(lGlitchImpact), 
                sGlitchMaxlife=fnsQuoteMulti(lGlitchMaxlife), 
                nGlitchSpan=nGlitchSpan, 
                nGlitchDecay=nGlitchDecay, 

                bShortLog=bShortLog, 

                nSimLength=nSimLength, nBandwidthMbps=nBandwidthMbps, 
                nRandomSeeds=nRandomSeeds, 

                sShockFreq=fnsQuoteMulti(lShockFreq), 
                sShockImpact=fnsQuoteMulti(lShockImpact), 
                sShockSpan=fnsQuoteMulti(lShockSpan), 
                sShockMaxlife=fnsQuoteMulti(lShockMaxlife), 

                nDocSize=nDocSize, nShelfSize=nShelfSize, 

                bRedo=bRedo,
                bTestOnly=bTestOnly, 
                sDatabaseName=sDatabaseName, 
                
                msg=msg
                )
    NTRC.ntrace(3,"proc first dict|%s|" % (dVals))
#  A D D   E X T R A   S P E C I F I C   S T R I N G S 
    # If the user asks for a shortlog, add the option to the command.
    dVals["xshortlog"] = "--shortlog" if bShortLog else ""

    # If the user asks for a test list only, add that option to the command.
    dVals["xtestonly"] = "--listonly" if bTestOnly else ""

    # If the user asks for a rematch, add that option to the command.
    dVals["xredo"] = "--redo" if bRedo else ""

    # Format the Mongo range expression for nCopies
    dVals["xcopies"] = dVals["sCopies"]

    # Format the Mongo range expression for nLifem
    dVals["xlifem"] = dVals["sLifem"]
    NTRC.ntrace(3,"proc expanded dict|%s|" % (dVals))

#  S E L E C T   C O M M A N D  A N D   F O R M A T  I T
    # Do something with the form data
    sActualCli = cCmd.mGentlyFormat(sMainCommandStringToStdout, dVals)
#    sActualCli = cCmd.mGentlyFormat(sMainCommandStringTestOnly, dVals)
#    sActualCli = cCmd.mGentlyFormat(sMainCommandStringDumbTest, dVals)
    NTRC.ntrace(3,"proc actual cli|%s|" % (sActualCli))
    sPrefix = '''<html><body>
        <font face="Courier">\n
    '''
    sPrefix += '<br />Working. . . \n'
    sPrefix += "<br />" + sActualCli + "<br />\n"
    sSuffix = '''
        </font>
        </body></html>
    '''
    sLinePrefix = '<br />'
    sLineSuffix = ''

#    return dVals         # DEBUG: return dict for visual inspection.

    sResult = fnValidateDirectories(dVals)
    if sResult:
        response.status = 300
        return sPrefix + sResult + sSuffix

    # Other validations go in here.

    if sResult == "":
    #  E X E C U T E   C L I   C M D ,   R E T U R N   R E S U L T S     
        return cCmd.mDoCmdGen(sPrefix, sSuffix, sLinePrefix, sLineSuffix, 
                sActualCli)


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

# f n s Q u o t e M u l t i 
@ntrace
def fnsQuoteMulti(mylMultiList):
    '''
    Render list from multi-select input box into list syntax
     acceptable to json.
    '''
    return '\'' + str([util.fnIntPlease(s) for s in mylMultiList]) + '\''


# CLI commands to run the main program.
sMainCommandStringToStdout = ('python broker.py inprogress done '
            '--familydir={sFamilyDir} '
            '--specificdir={sSpecificDir} '
            '--ncopies={xcopies} --lifem={xlifem} '
            '--serverdefaultlife={nServerDefaultLife} '
            '--auditfreq={nAuditFreq} --auditsegments={nAuditSegments} '
            '--audittype={sAuditType} '
            '--glitchfreq={sGlitchFreq} --glitchimpact={sGlitchImpact} '
            '--glitchdecay={nGlitchDecay} --glitchmaxlife={sGlitchMaxlife} '
            '--glitchspan={nGlitchSpan} '
            '--shockfreq={sShockFreq} --shockimpact={sShockImpact} '
            '--shockspan={sShockSpan} --shockmaxlife={sShockMaxlife} '
            '--docsize={nDocSize} --shelfsize={nShelfSize} '
            '--nseeds={nRandomSeeds} '
            '{xshortlog} {xtestonly} {xredo} '
            '2>&1 '
#            '--help'
            )
# Itsy bitsy test versions
sMainCommandStringTestOnly = '''python main.py -h
'''
sMainCommandStringDumbTest = '''ls -l
'''

# Template for Mongo range expression.  
# Note that only the quotes matching the outside quotes need to be escaped.  
sRangeTemplate = "'{\"$gte\":%s, \"$lte\":%s}'"

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


@ntrace
def runme():
    port = int(os.environ.get('PORT', 8080))
    run(host='0.0.0.0', port=port, debug=True, reloader=True)

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
# 

#END
