#!/usr/bin/python
# brokergroupform.py
# Form to collect params for PreservationSimulation broker.py.
# Creates the crazy way-too-large form of broker options.
# Runs the program and may collect the results to show on the page.

from __future__ import print_function
from __future__ import absolute_import
import os
import sys
from .catchex import catchex
from .NewTraceFac import NTRC, ntrace, ntracef
import re


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


#==============  M A I N   P A G E  ===============


from .brokergroupform_main import *



#==============  S E T U P  P A G E  ===============


from .brokergroupform_setup import *


#==============  M A I N  ===============


@ntrace
def runme():
    port = int(os.environ.get('PORT', 8080))
    result = run(host='0.0.0.0', port=port, debug=True, reloader=True)
    return result


#==============  E N T R Y   P O I N T  ===============


if __name__ == '__main__':
    print("")
    sys.exit(runme())


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
# 20171231  RBL Fix namespace problems with CCommand.  Remove it from here
#                and let the page processors use the common module.  
# 
# 

#END