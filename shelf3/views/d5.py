#!/usr/bin/python

import jinja2
import sys
#from NewTraceFac import NTRC,ntrace,ntracef

templateLoader = jinja2.FileSystemLoader( searchpath="." )
templateEnv = jinja2.Environment( loader=templateLoader, 
            trim_blocks='true', 
            #lstrip_blocks='true',  
            line_comment_prefix="##",
            )
if 1:
    TEMPLATE_FILE = sys.argv[1]
    template = templateEnv.get_template( TEMPLATE_FILE )
    
    sTitle = "Figure out how scoping works d4"
    var1dat = {
                "varname"   :   "Var1",
                "varhead"   :   "Var1 heading",
    }
    var2dat = {
                "varname"   :   "Var2",
                "varhead"   :   "Var2 heading",
    }

    dFinal = {
                "title" : sTitle,
                "allvars"   : {
                            "Var1"  : var1dat, 
                            "Var2"  : var2dat, 
                              },
    }

    outputText = template.render( dFinal )
    print(outputText)

