#!/usr/bin/python
# extractvalues.py


import re
from os import environ
import csv
from NewTraceFac    import TRC,trace,tracef
import argparse
#from time import clock

# TODO:
# - Don't have a separate header line that can get out of sync with
#   the data.  Form the header by stripping all braces from the template.

# C l i P a r s e 
@tracef("CLI")
def fndCliParse(mysArglist):
    ''' Parse the mandatory and optional positional arguments, and the 
        many options for this run from the command line.  
        Return a dictionary of all of them.   
    '''
    sVersion = "0.0.1"
    cParse = argparse.ArgumentParser(description="Digital Library Preservation Simulation, Utility to extract values from log files"\
        ,epilog="version %s" % sVersion
        )

    # P O S I T I O N A L  arguments
    #cParse.add_argument('--something', type=, dest='', metavar='', help='')

    cParse.add_argument('sInstructionsFileName', type=str
                        , metavar='sINSTRUCTIONSFILE'
                        , help='File with output template and CSV params for extracting values from file.'
                        )

    cParse.add_argument('sLogFileName', type=str
                        , metavar='sLOGFILE'
                        , help='Log file with real data in it.'
                        )

    # - - O P T I O N S
    
    cParse.add_argument("--header"
                        , action="store_true"
                        , dest='bHeader'
#                        , metavar='bHEADER'
                        , help='Header line desired if present.'
                        )

    if mysArglist:          # If there is a specific string, use it.
        (xx) = cParse.parse_args(mysArglist)
    else:                   # If no string, then parse from argv[].
        (xx) = cParse.parse_args()

    g.sInstructionsFileName = xx.sInstructionsFileName
    g.sLogFileName = xx.sLogFileName
    g.bHeader = getattr(xx,"bHeader",False)

    return vars(xx)

@tracef("MCMD")
def makeCmd(mysCmd,mydArgs):
    ''' Substitute arguments into command template string,
        by name, from the supplied dictionary.  
    '''
    sCmd = mysCmd.format(**mydArgs)
    return sCmd

# f n d P a r s e I n p u t 
@tracef("INPT")
def fnldParseInput(mysFilename):
    ''' Return tuple containing
        - the output template string, 
        - the header line for the output, 
        - a list, one item per line, of dicts of column args from the 
          csv that contain instructions for getting variable values
          from lines.  
        Beware duck-type integers that become strings.

        Format of csv lines:        
        varname,regex to find line,split word number,regex to strip out value

        instruction file format:

        ##becomes comment in output
        ###send out this string as header for the output, no hashes
        =outputformat
        format string
        =header
        varlist,var,var,var#variables
        =variables
        varname,lineregex,wordnumber,valueregex (header)
        (lines of csv data)

    '''
    dParams = dict()
    with open(mysFilename,"rb") as fhInfile:
        lLines = fhInfile.readlines()
        # Remove comments.  
        for sLine in lLines[:]:
            if re.match("^ *#[^#]",sLine) or re.match("^ *$",sLine.rstrip()):
                lLines.remove(sLine)
                TRC.tracef(3,"INPT","proc ParseInput remove comment or blank line |%s|" % (sLine.strip()))

        sCmd = lLines.pop(0).strip()
        TRC.tracef(3,"INPT","proc ParseInput command line|%s|" % (sCmd))

        if re.match("^=template",sCmd):
            lTemplate = list()
            while 1:
                sCmd = lLines.pop(0).rstrip()
                if re.match("^=header",sCmd):
                    break
                sCmd = sCmd.replace("###","")
                sCmd = sCmd.replace("##","#")
                lTemplate.append(sCmd)
            TRC.tracef(3,"INPT","proc ParseInput template|%s|" % (lTemplate))

        if re.match("^=header",sCmd):
            lHeader = list()
            while 1:
                sCmd = lLines.pop(0).rstrip()
                if re.match("^=variables",sCmd):
                    break
                sCmd = sCmd.replace("###","")
                sCmd = sCmd.replace("##","#")
                lHeader.append(sCmd)
            TRC.tracef(3,"INPT","proc ParseInput header|%s|" % (lHeader))

        # Now get the CSV args into a dictionary of dictionaries.
        lRowDicts = csv.DictReader(lLines)
        for dd in lRowDicts:
            dParams[dd["varname"]] = dd
            TRC.tracef(3,"INPT","proc ParseInput Params len|%s|" % (len(dParams.keys())))
            TRC.tracef(5,"INPT","proc ParseInput Params len|%s| all|%s|" % (len(dParams.keys()),dParams))
    return (lTemplate,lHeader,dParams)

#===========================================================
# NEW NEW NEW 
# functional if possible

# m a i n ( ) 
@tracef("MAIN")
def main(mysInstructionsFileName,mysLogFileName):
    (lTemplate,lHeader,dVars) = fnldParseInput(mysInstructionsFileName)
    lLines = list()
    with open(mysLogFileName,"r") as fhLogFile:

        # Double list comprehension to find lines that match.
        lMatchTuples = [ fnMatchLine(sLine,nLineNr,dVar) \
            for (sLine,lLines,nLineNr) in fnGetLineAndNumber(fhLogFile,lLines) \
            for dVar in dVars.values() ]
        TRC.tracef(5,"MN2","proc MatchTuples len|%s| first|%s|" % (len(lMatchTuples),lMatchTuples[0]))

        # Filter returns only the lines that matched.
        lLinesSelected = filter( lambda (var,matchobj,line): matchobj, \
                                lMatchTuples )
        TRC.tracef(5,"MN2","proc LinesSelected len|%s| all|%s|" % (len(lLinesSelected),lLinesSelected))

        # Extract variable value from each matching line.
        dValues = dict()
        for (sVarname,oMatch,sLine) in lLinesSelected:
            TRC.tracef(3,"MN2","proc selectedfromfilter var|%s| line|%s|" % (sVarname,sLine))
            dVar = dVars[sVarname]
            sValue = fnMatchValue(sLine,dVar)
            dValues[sVarname] = sValue

    # Fill in the template with values and print.  
    sTemplate = lTemplate[0]
    sLineout = makeCmd(sTemplate,dValues)
    if g.bHeader or environ.get("header",None):
        sHeader = lHeader[0]
        print sHeader
    print sLineout

# f n G e t L i n e A n d N u m b e r 
@tracef("GETL")
def fnGetLineAndNumber(myfh,mylLines):
    for sLine in myfh:
        TRC.tracef(3,"GETL","proc GetLine nr|%s| line|%s|" % (len(mylLines)+1,sLine))
        yield (sLine,mylLines.append(sLine),len(mylLines))

# f n M a t c h L i n e 
@tracef("MCHL")
def fnMatchLine(mysLine,mynLineNr,mydVar):
    sVarname = mydVar["varname"]
    sLineregex = mydVar["lineregex"]
    # Check line against regex from dict.  
    oMatch = re.search(sLineregex,mysLine)
    TRC.tracef(5,"MTLN","proc MatchLine try regex|%s| nr|%s| line|%s| match|%s|" % (sLineregex,mynLineNr,mysLine,oMatch))
    if oMatch:
        TRC.tracef(3,"LINE","proc MatchLine found line|%s|=|%s| var|%s| regex|%s|" % (mynLineNr,mysLine,sVarname,sLineregex))
    return (sVarname,oMatch,mysLine)

# f n M a t c h V a l u e 
@tracef("MCHV")
def fnMatchValue(mysLine,mydVar):
    # Get the right word from the line.
    #  If asked for word zero, use the whole line.  
    #  Makes the extraction harder, but sometimes necessary.
    sWordnumber = mydVar["wordnumber"]
    nWordnumber = int(sWordnumber)
    lWords = mysLine.split()
    if nWordnumber == 0:
        sWord = mysLine
    elif nWordnumber <= len(lWords):
        sWord = lWords[nWordnumber-1]
    else: 
        sWord = "nowordhereindexoutofrange"
    sValueregex = mydVar["valueregex"]
    sVarname = mydVar["varname"]
    oMatch = re.search(sValueregex,sWord)
    TRC.tracef(5,"MCHV","proc MatchValue matching word var|%s| word|%s| valueregex|%s| matchobj|%s|" % (sVarname,sWord,sValueregex,oMatch))
    if oMatch:
        # Word matches the valueregex.  Save the value.
        sValue = oMatch.group(1)
        TRC.tracef(3,"MCHV","proc addvalue name|%s| val|%s|" % (sVarname,sValue))
    else:
        # If not found, at least supply something conspicuous for printing.
        sValue = "novaluefound"
    return sValue


# Global data
class CG(object):
    bHeader = False
    sInstructionsFileName = "instructions.txt"
    sLogFileName = "logfile.txt"

# M a i n   l i n e 
if "__main__" == __name__:
    g = CG()
    #read filename and options from cli
    fndCliParse("")
#    timestart = clock()
    main(g.sInstructionsFileName,g.sLogFileName)
#    timestop = clock()
#    TRC.tracef(0,"MAIN","proc cputime|%s|" % (timestop-timestart))

#END
