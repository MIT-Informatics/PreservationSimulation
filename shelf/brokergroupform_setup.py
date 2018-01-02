#!/usr/bin/python
# brokergroupform_setup.py
# Form to execute PreservationSimulation broker.py setup UI page.

import os
from bottle import route, run, template, request, get, post, \
    static_file, view, response
from catchex import catchex
from NewTraceFac import NTRC, ntrace, ntracef
import re
import subprocess
import util
import command


#==============  S E T U P   P A G E  ===============


@get('/setup')
@get('/mainsim/setup')
@ntrace
def mainsim_setup_get():
    """ Make the form anew and display it."""
    sMakeformCmd = ('python brokergroup_makeform.py '
                        'brokergroup_setupform_insert.j2 '
                        'views/brokergroup_setupform.tpl '
                        'instructions')
    result = subprocess.check_output(sMakeformCmd, shell=True)
    return template('brokergroup_setupform')


@post('/setup')
@post('/mainsim/setup')
@ntrace
def mainsim_setup_post():
    #   C O L L E C T   D A T A 
    sFamilyDir = request.forms.get("sFamilyDir")
    sSpecificDir = request.forms.get("sSpecificDir")
    bClearDirs = request.forms.get("bClearDirs")
    sAction = request.forms.get("submit")
    foo=request.forms.get("forms")
    headers=request.forms.get("headers")
    msg = "mainsim_setup_post: NOT YET IMPLEMENTED"

    #   F O R M   D I C T I O N A R Y   O F   S U B S T I T U T I O N S 
    # Make a dictionary to use to substitute params into CLI command.
    dVals = dict(sFamilyDir=sFamilyDir, sSpecificDir=sSpecificDir,
                bClearDirs=bClearDirs, msg=msg
                )
    NTRC.ntrace(3,"proc first dict|%s|" % (dVals))

    # If instructed to clear area, do that first.
    
    
    # Use standard script to setup output dirs.


    # Tell user it's done.
    

    # Return to previous form.
    sOut = ("famdir|%s| specdir|%s| clr|%s| submitval|%s| foo|%s| hdrs|%s|" 
            % (sFamilyDir, sSpecificDir, bClearDirs, sAction, foo, headers))
    return sOut + "<br/>" + dVals["msg"]


#==============  D A T A  ===============


cCmd = command.CCommand()
# TBS


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
#               Separate SETUP page code from entry point and main line.
# 
# 

#END
