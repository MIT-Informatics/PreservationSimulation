# narrowfile.py
# Reduce the size of a data file by selecting only the really important columns.
#               RBL 20190118

import argparse
import csv
import time
from NewTraceFac import NTRC, ntrace, ntracef


#===========================================================
# C l i P a r s e 
@ntracef("CLI")
def fndCliParse(mysArglist):
    ''' Parse the mandatory and optional positional arguments, and the 
        many options for this run from the command line.  
        Return a dictionary of all of them.   
    '''
    sVersion = "0.0.1"
    cParse = argparse.ArgumentParser(
            description="Digital Library Preservation Simulation, "
                "Utility to reduce the size of a file "
                "by reducing columns to the essential ones "
                "needed for data analysis.  " 
                + "CLI version %s  "%(sVersion) + 
                "One filename in.  "
                "Produces to stdout. " 
            , epilog="Defaults for args as follows: none."
            , version=sVersion
        )

    # P O S I T I O N A L  arguments
    #cParse.add_argument('--something', type=, dest='', metavar='', help='')

    cParse.add_argument('sInputFilename', type=str
                        , metavar='sINPUTFILE'
                        , help='File with too many columns.'
                        )

    # - - O P T I O N S

    # None for this program.  
    """
    cParse.add_argument("--header"
                        , action="store_true"
                        , dest='bHeader'
                        , metavar='bHEADER'
                        , help='Header line desired if present.'
                        )
    """
    
    if mysArglist:          # If there is a specific string, use it.
        (xx) = cParse.parse_args(mysArglist)
    else:                   # If no string, then parse from argv[].
        (xx) = cParse.parse_args()

    g.sInputFilename = xx.sInputFilename

    return vars(xx)

# G l o b a l   d a t a 
class CG(object):
    sInputFilename = "instructions.txt"
    sSeparator = " "
    dVars = dict()
    sCoreColumns = ("timestamp docsize shelfsize copies lifem "
                    "simlength seed lost docstotal docslost "
                    "auditcycles auditfrequency auditsegments audittype "
                    "glitchfreq glitchimpact glitchdecay glitchmaxlife nglitches "
                    "serverdefaultlife "
                    "shockfreq shockimpact shockmaxlife shockspan shocktype "
                    "nshocks nshockdeaths "
                    "deadserversactive deadserversall "
                    "walltime cputime todaysdatetime "
                    ""
                    ).strip()
    lCoreColumns = sCoreColumns.split()


# M A I N 
def main(mysInputFilename):
    pass
    # Create output template.
    lTemplate = map(lambda field: ("{" + field + "}"), g.lCoreColumns)
    sTemplate = " ".join(lTemplate)

    # Process file.
    with open(mysInputFilename, "r") as fhIn:
        oReader = csv.reader(fhIn, delimiter=g.sSeparator)
    
        # First line better be the header.
        lHeader = next(oReader)
        NTRC.tracef(3, "NARO", "proc lHeader|%s|" % (lHeader))
    
        # For each data line, create dict of values and map them into 
        #  the reduced-width output template.  
        print(g.sCoreColumns)
        for sLine in fhIn:
            lValues = next(oReader)
            NTRC.tracef(3, "NARO", "proc lValues|%s|" % (lValues))
            dValues = dict(zip(lHeader, lValues))
            NTRC.tracef(3, "NARO", "proc dValues|%s|" % (dValues))
            sOut = sTemplate.format(**dValues)
            print(sOut)



# E N T R Y   P O I N T 
if "__main__" == __name__:
    g = CG()                # Global dict for options.
    
    # Read filename and options from cli
    dCliDict = fndCliParse("")
    dCliDictClean = {k:v for k,v in dCliDict.items() if v is not None}
    g.__dict__.update(dCliDictClean)
    
    # Do something with the file.  
    timestart = time.clock()
    main(g.sInputFilename)
    timestop = time.clock()
#    NTRC.tracef(0,"MAIN","proc cputime|%s|" % (timestop-timestart))

# Edit history:
# 20190118  RBL Original version.
# 
# 

#END
