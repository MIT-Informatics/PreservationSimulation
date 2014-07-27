#!/usr/bin/python
# extractvalues.py


import re
from os import environ
import csv
from NewTraceFac    import TRC,trace,tracef
import argparse


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

@trace
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
    lParams = list()
    with open(mysFilename,"rb") as fhInfile:
        lLines = fhInfile.readlines()
        # Remove comments.  
        for sLine in lLines[:]:
            if re.match("^ *#[^#]",sLine) or re.match("^ *$",sLine.rstrip()):
                lLines.remove(sLine)
                TRC.trace(3,"proc ParseInput remove comment or blank line |%s|" % (sLine.strip()))

        sCmd = lLines.pop(0).strip()
        TRC.trace(3,"proc ParseInput command line|%s|" % (sCmd))

        if re.match("^=template",sCmd):
            lTemplate = list()
            while 1:
                sCmd = lLines.pop(0).rstrip()
                if re.match("^=header",sCmd):
                    break
                sCmd = sCmd.replace("###","")
                sCmd = sCmd.replace("##","#")
                lTemplate.append(sCmd)
            TRC.trace(3,"proc ParseInput template|%s|" % (lTemplate))

        if re.match("^=header",sCmd):
            lHeader = list()
            while 1:
                sCmd = lLines.pop(0).rstrip()
                if re.match("^=variables",sCmd):
                    break
                sCmd = sCmd.replace("###","")
                sCmd = sCmd.replace("##","#")
                lHeader.append(sCmd)
            TRC.trace(3,"proc ParseInput header|%s|" % (lHeader))

        # Now get the CSV args into a list of dictionaries.
        lRowDicts = csv.DictReader(lLines)
        for dd in lRowDicts:
            lParams.append(dd)
    return (lTemplate,lHeader,lParams)

# m a i n ( ) 
@tracef("MAIN")
def main(mysInstructionsFileName,mysLogFileName):
    ''' extractvalues.py
        Sort of a report generator
        
        read the csv instruction file
        foreach file
          read file
            foreach line
              for each variable
                does regex select this line
                split into words
                choose specific word
                strip out value
                store value in var
        at eof
        if some environ var is nonzero, print header line containing var names
        spit out one line
        
        first version of this reads one file, writes one line (and maybe header).
    '''

    (lTemplate,lHeader,lVars) = fnldParseInput(mysInstructionsFileName)
    with open(mysLogFileName,"r") as fhLogFile:
        lLines = fhLogFile.readlines()
        dValues = dict()
        for (nLineNr,sLine) in enumerate(lLines):
            nLineNr += 1
            TRC.tracef(3,"LINE","proc logline nr|%s|=|%s|" % (nLineNr,sLine))
            for dVar in lVars:
                sVarname = dVar["varname"]
                sLineregex = dVar["lineregex"]
                sWordnumber = dVar["wordnumber"]
                sValueregex = dVar["valueregex"]
                TRC.tracef(5,"LINE","proc matching line var|%s| lineregex|%s|" % (sVarname,sLineregex))
                if re.search(sLineregex,sLine): 
                    # Line matches the lineregex.
                    TRC.tracef(3,"LINE","proc found line|%s|=|%s| var|%s| regex|%s|" % (nLineNr,sLine,sVarname,sLineregex))
                    lWords = sLine.split()
                    nWordnumber = int(sWordnumber)
                    # Get the right word from the line.
                    #  If asked for word zero, give the whole line.  
                    #  Makes the extraction harder, but sometimes necessary.
                    if nWordnumber == 0:
                        sWord = sLine
                    elif nWordnumber <= len(lWords):
                        sWord = lWords[nWordnumber-1]
                    else: 
                        sWord = "XXXXXXXXXX"
                    oMatch = re.search(sValueregex,sWord)
                    TRC.tracef(5,"LINE","proc matching word var|%s| word|%s| valueregex|%s| matchobj|%s|" % (sVarname,sWord,sValueregex,oMatch))
                    if oMatch:
                        # Word matches the valueregex.  Store the value.
                        sValue = oMatch.group(1)
                        dValues[sVarname] = sValue
                        TRC.tracef(3,"VALU","proc addvalue name|%s| val|%s|" % (sVarname,sValue))
    sTemplate = lTemplate[0]
    sLineout = makeCmd(sTemplate,dValues)
    if g.bHeader or environ.get("header",None):
        sHeader = lHeader[0]
        print sHeader
    print sLineout

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
    main(g.sInstructionsFileName,g.sLogFileName)


#END
