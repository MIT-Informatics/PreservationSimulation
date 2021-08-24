#!/usr/bin/python
# brokergroupform_setup.py
# Form to execute PreservationSimulation broker.py setup UI page.

import os
import bottle
from catchex import catchex
from NewTraceFac import NTRC, ntrace, ntracef
import re
import subprocess
import util
import command


#==============  S E T U P   P A G E  ===============


@bottle.get('/setup')
@bottle.get('/mainsim/setup')
@bottle.jinja2_view('brokergroup_setupform_insert.j2', template_lookup=['./views/'])
@ntrace
def mainsim_setup_get():
    """ Make the form anew and display it."""
    """ Used to do this here, but now do it dynamically with the
         bottle.jinja2_view decorator and dict return.  
         Don't store the result file at all.
    """
    """
    sMakeformCmd = ('python3 brokergroup_makeform.py '
                        'brokergroup_setupform_insert.j2 '
                        'views/brokergroup_setupform.tpl '
                        'instructions')
    result = subprocess.check_output(sMakeformCmd, shell=True)
    """
    return {}


@bottle.post('/setup')
@bottle.post('/mainsim/setup')
@bottle.jinja2_view('brokergroup_setupform_done.j2', template_lookup=['./views/'])
@ntrace
def mainsim_setup_post():
    #   C O L L E C T   D A T A 
    sFamilyDir = bottle.request.forms.get("sFamilyDir")
    sSpecificDir = bottle.request.forms.get("sSpecificDir")
    bClearDirs = bottle.request.forms.get("bClearDirs")
    bClearDone = bottle.request.forms.get("bClearDone")
    sAction = bottle.request.forms.get("submit")
    sOK = bottle.request.POST.ok
    sCancel = bottle.request.POST.cancel

    msg = "mainsim_setup_post: done"

    #   F O R M   D I C T I O N A R Y   O F   S U B S T I T U T I O N S 
    # Make a dictionary to use to substitute params into CLI command.
    dVals = dict(sFamilyDir=sFamilyDir
                ,sSpecificDir=sSpecificDir
                ,bClearDirs=("Yes" if bClearDirs else "No")
                ,bClearDone=("Yes" if bClearDone else "No")
                ,sOK=sOK
                ,sCancel=sCancel
                ,sAction=("DONE" if sOK else "CANCELLED")
                ,msg=msg
                )
    NTRC.ntrace(3,"proc first dict|%s|" % (dVals))

    if sOK:
        # If instructed to clear area, do that first.
        if bClearDirs:
            sClearDirsCmd = cCmd.mMakeCmd(sCmdClearDirs, dVals)
            lCmdOut = cCmd.mDoCmdLst(sClearDirsCmd)
            dVals["sResultClearDirs"] = fnsMakeReadable(sClearDirsCmd, lCmdOut)
        
        # Use standard script to setup output dirs.
        sSetupDirsCmd = cCmd.mMakeCmd(sCmdSetupDirs, dVals)
        lCmdOut = cCmd.mDoCmdLst(sSetupDirsCmd)
        dVals["sResultSetupDirs"] = fnsMakeReadable(sSetupDirsCmd, lCmdOut)

        # Use standard script to clear done records.
        if bClearDone:
            sClearDoneCmd = cCmd.mMakeCmd(sCmdClearDone, dVals)
            lCmdOut = cCmd.mDoCmdLst(sClearDoneCmd)
            dVals["sResultClearDone"] = fnsMakeReadable(sClearDoneCmd, lCmdOut)

    # Tell user what we did.
    lVals = ["k:|%s| v:|%s|" % (k, v) for (k, v) in sorted(dVals.items())]
    sVals = "\n<br/>".join(lVals)
    sOut = sVals
    return dVals


# f n s M a k e R e a d a b l e 
def fnsMakeReadable(sCmd, lOut):
    """ Put HTML line breaks into command and its output lines. """
    sOut = "<br/>".join(lOut)
    return sCmd + "<br/>" + sOut


#==============  D A T A  ===============


cCmd = command.CCommand()
sCmdSetupDirs = "sh setupfamilydir.sh {sFamilyDir} {sSpecificDir}"
sCmdClearDirs = "rm -rf {sFamilyDir}/{sSpecificDir}"
sCmdClearDone = "sh dbcleardone.sh"


# Edit history:
# 20171230  RBL Add processing for setup page to establish 
#                output directory structure, erase done records, etc.
#               Separate SETUP page code from entry point and main line.
#               Use Jinja2 template calls directly rather than 
#                manually creating the output template.  
# 

#END
