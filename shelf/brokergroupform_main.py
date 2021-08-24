#!/usr/bin/python
# brokergroupform_main.py
# Form to collect params for PreservationSimulation broker.py main UI page.
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
import command


#==============  M A I N   P A G E  ===============


@get('/')
@get('/mainsim')
@ntrace
def mainsim_get():
    sMakeformCmd = ('python3 brokergroup_makeform.py '
                        'brokergroup_form_insert.j2 '
                        'views/brokergroup_form2.tpl '
                        'instructions')
    result = subprocess.check_output(sMakeformCmd, shell=True)
    return template('brokergroup_form2')


@post('/')
@post('/mainsim')
@ntrace
def mainsim_post():
#   C O L L E C T   D A T A 
    # Collect all the bloody data, one item at a time, grumble.
    sFamilyDir = request.forms.get("sFamilyDir")
    sSpecificDir = request.forms.get("sSpecificDir")
    sDatabaseName = request.forms.get("sDatabaseName")
    nRandomSeeds = request.forms.get("nRandomSeeds")

    lCopies= request.forms.getall("nCopies")

    lLifem = request.forms.getall("nLifem")
    nServerDefaultLife = request.forms.getall("nServerDefaultLife")

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

    nDocuments = request.forms.getall("nDocuments")
    nDocSize = request.forms.get("nDocSize")
    nShelfSize = request.forms.get("nShelfSize")

    bShortLog = request.forms.get("bShortLog")

    nSimLength = request.forms.getall("nSimLength")
    nBandwidthMbps = request.forms.get("nBandwidthMbps")

    bRedo = request.forms.get("bRedo")
    bTestOnly = request.forms.get("bTestOnly")
    
    bRunDetached = request.forms.get("bRunDetached")
    sDetachedLogfile = request.forms.get("sDetachedLogfile")

    msg = "mainsim_post: NOT YET IMPLEMENTED"

#   F O R M   D I C T I O N A R Y   O F   S U B S T I T U T I O N S 
    # Make a dictionary to use to substitute params into CLI command.
    dVals = dict(sFamilyDir=sFamilyDir, sSpecificDir=sSpecificDir,

                sCopies=fnsQuoteMulti(lCopies),
                nServerDefaultLife=fnsQuoteMulti(nServerDefaultLife), 

                sLifem=fnsQuoteMulti(lLifem), 

                nAuditFreq=nAuditFreq, nAuditSegments=nAuditSegments, 
                sAuditType=sAuditType,

                sGlitchFreq=fnsQuoteMulti(lGlitchFreq), 
                sGlitchImpact=fnsQuoteMulti(lGlitchImpact), 
                sGlitchMaxlife=fnsQuoteMulti(lGlitchMaxlife), 
                nGlitchSpan=nGlitchSpan, 
                nGlitchDecay=nGlitchDecay, 

                bShortLog=bShortLog, 

                nSimLength=fnsQuoteMulti(nSimLength), 
                nBandwidthMbps=nBandwidthMbps, 
                nRandomSeeds=nRandomSeeds, 

                sShockFreq=fnsQuoteMulti(lShockFreq), 
                sShockImpact=fnsQuoteMulti(lShockImpact), 
                sShockSpan=fnsQuoteMulti(lShockSpan), 
                sShockMaxlife=fnsQuoteMulti(lShockMaxlife), 

                nDocSize=nDocSize, nShelfSize=nShelfSize, 
                nDocuments=fnsQuoteMulti(nDocuments),

                bRedo=bRedo,
                bTestOnly=bTestOnly, 
                sDatabaseName=sDatabaseName, 

                bRunDetached=bRunDetached,
                sDetachedLogfile=sDetachedLogfile,

                msg=msg
                )
    NTRC.ntrace(3,"proc first dict|%s|" % (dVals))

#  S P E C I A L   C A S E S   O F   I N T E R D E P E N D E N C E 
    # If the user specified a logfile for detached running, then 
    #  pretend that he remembered to check the box, too.
    if dVals["sDetachedLogfile"]:
        dVals["bRunDetached"] = True
    # If the user wants to run detached, we may have to supply 
    #  a default filename.
    # Be sure to add today's date to the default filename.
    if dVals["bRunDetached"] and not dVals["sDetachedLogfile"]:
        dVals["sDetachedLogfile"] = ("./BrokerDetachedLogfile"
                                + "_"
                                + util.fnsGetTimeStamp().split("_")[0]
                                + ".log")

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

    # If running detached with output to a log file, 
    #  specify append to file and detach process.
    if dVals["sDetachedLogfile"]:
        dVals["xLogfileExpr"] = (" >> " 
                                + dVals["sDetachedLogfile"]
                                + " &")
    else:
        dVals["xLogfileExpr"] = ""

#  S E L E C T   C O M M A N D  A N D   F O R M A T  I T
    # Do something with the form data
    sActualCli = cCmd.mGentlyFormat(sMainCommandStringToStdout, dVals)
#    sActualCli = cCmd.mGentlyFormat(sMainCommandStringTestOnly, dVals)
#    sActualCli = cCmd.mGentlyFormat(sMainCommandStringDumbTest, dVals)
    NTRC.ntrace(3,"proc actual cli|%s|" % (sActualCli))
    sPrefix = '''<html><body>
        <font face="Courier">\n
    '''
    sPrefix += '<br />'
    sPrefix += util.fnsGetTimeStamp()
    sPrefix += '  Working. . . \n'
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


# f n s Q u o t e M u l t i 
@ntrace
def fnsQuoteMulti(mylMultiList):
    '''
    Render list from multi-select input box into list syntax
     acceptable to json.
    '''
    return '\'' + str([util.fnIntPlease(s) for s in mylMultiList]) + '\''


#==============  D A T A  ===============


# Make instance of Command class to use.
cCmd = command.CCommand()


# CLI commands to run the main program.
sMainCommandStringToStdout = ('python3 broker2.py inprogress done '
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
            '--ndocuments={nDocuments} '
            '--nseeds={nRandomSeeds} --simlen={nSimLength} '
            '{xshortlog} {xtestonly} {xredo} '
            '2>&1 '
            '{xLogfileExpr} '
#            '--help'
            )
# Itsy bitsy test versions
sMainCommandStringTestOnly = '''python3 main.py -h
'''
sMainCommandStringDumbTest = '''ls -l
'''

# Template for Mongo range expression.  
# Note that only the quotes matching the outside quotes need to be escaped.  
sRangeTemplate = "'{\"$gte\":%s, \"$lte\":%s}'"


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
#               Separate page code from entry point and main line.
# 20171231  RBL Import command from common module.  
# 20180408  RBL Add --simlen option in command to broker.py.
# 20180925  RBL Change ServerDefaultLife to multi-select.
# 20181113  RBL Invoke broker2 with python3.
# 20181115  RBL Add nDocuments.
# 20190204  RBL Add standard timestamp to Working... message.
# 
# 

#END
