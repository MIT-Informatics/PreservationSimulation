#!/usr/bin/python
# brokergroup_makeform.py
# Generate brokergroup form from instructions/*.ins3 thru Jinja2 templates.
# Likely use: 
# python brokergroup_makeform.py                        \
#                   brokergroup_form_insert.j2          \ (input)
#                   views/brokergroup_form2.tpl         \ (output)
#                   instructions                          (.ins3 dir)
# 

import jinja2
import sys
import datetime
import searchspace
from NewTraceFac import NTRC,ntrace,ntracef

# BEWARE hardwired search path here. Jinja loader needs it, 
#  but I prefer feeding relative filespecs in thru CLI.  
templateLoader = jinja2.FileSystemLoader( searchpath="./views" )
templateEnv = jinja2.Environment( loader=templateLoader, 
            trim_blocks='true', 
            #lstrip_blocks='true',  
            line_comment_prefix="##",
            )

if 1:
    if len(sys.argv) > 1:
        sInFile = sys.argv[1]
    else:
        print "Usage: %s <child.j2 file> [<outputfile>|-] [<ins3 directory>]"
        sys.exit(1)
    if len(sys.argv) > 2:
        sOutFile = (sys.argv[2] if sys.argv[2] != '-' else "")
    if len(sys.argv) > 3:
        sInsLoc = sys.argv[3]
    else: 
        sInsLoc = '.'

    TEMPLATE_FILE = sInFile
    template = templateEnv.get_template( TEMPLATE_FILE )
    
    sTitle = "Test page d5"
    sSlugline = "<p>Trying to insert multiple vars with multiple values.</p>"
    dPage= dict()
    dPage["sTitle"] = sTitle
    dPage["sSlugline"] = sSlugline
    dPage["sGeneratedTimestamp"] = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    # Process all instructions into dict.
    dVars = searchspace.fndReadAllInsFilesForGUI(
                sInsLoc, '.ins3'
    )
    for (sVarname, dVardef) in dVars.items():
        NTRC.ntrace(3,"proc onevar varname|%s| vardef|%s|" % (sVarname, dVardef))

    dFinal = {"dVars" : dVars}
    dFinal.update(dPage)
    NTRC.ntrace(3,"proc dFinal|%s|" % (dFinal))
        
    # Process dict and forms thru Jinja2.
    outputText = template.render( dFinal )
    if sOutFile:
        with open(sOutFile, 'w') as fhOut:
            print >> fhOut, outputText
    else:
        print(outputText)

# Edit history
# 20170218  RBL Original version.  
# 20190225  RBL Add timestamp for generated form.
# 
# 

#END
