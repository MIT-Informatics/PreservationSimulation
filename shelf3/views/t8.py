#!/usr/bin/python

import jinja2
import sys
import searchspace
from NewTraceFac import NTRC,ntrace,ntracef


templateLoader = jinja2.FileSystemLoader( searchpath="." )
templateEnv = jinja2.Environment( loader=templateLoader, 
            trim_blocks='true', 
            #lstrip_blocks='true',  
            )

if 1:
    TEMPLATE_FILE = sys.argv[1]
    template = templateEnv.get_template( TEMPLATE_FILE )
    
    sTitle = "Test page j8"
    sSlugline = "<p>Trying to insert multiple vars with multiple values.</p>"
    dPage= dict()
    dPage["sTitle"] = sTitle
    dPage["sSlugline"] = sSlugline

    dIns = searchspace.fndReadAllInsFilesForGUI(
                './ins', '.ins3'
    )

    dVars = dIns
    for (sVarname, dVardef) in dVars.items():
        NTRC.ntrace(3,"proc onevar varname|%s| vardef|%s|" % (sVarname, dVardef))
    dFinal = {"dVars" : dVars}
    dFinal.update(dPage)
    NTRC.ntrace(3,"proc dFinal|%s|" % (dFinal))
    NTRC.ntrace(3,"proc dFinal.dVars|%s|" % (dFinal["dVars"]))
    NTRC.ntrace(3,"proc dFinal.dVars.nCopies|%s|" % (dFinal['dVars']['nCopies']))
    for varname,vardict in dFinal['dVars'].iteritems():
        NTRC.ntrace(3,"proc dFinal.dVars.varname|%s| : |%s|" % (varname, vardict))
        
    outputText = template.render( dFinal )
    print(outputText)

