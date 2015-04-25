#!/usr/bin/python
# extractvalues.py
'''
Extract data from lines of log files, using regular expression commands
 supplied by the user.  
Reads thru all lines of file, trying to match one of the regexes supplied, 
 extracts data from particular fields on matching lines using additional
 regexes supplied by user. Each found field has a user-supplied name.  
Input file generates one (!) line of output containing data found, 
 in a format defined by the user.  Space- or tab-delimited most likely.  
 Even CSV is possible if there are no commas that require delimiting
 in the data.  :-)  
Header containing field names emitted optionally based on environment variable.  
Resulting output should be suitable for consumption by R, numpy, pandas, et al.
argparse for arguments, usage, help.  

Sounds simple.  Be *extremely* careful constructing the regexes.  
The voice of experience, from the instruction file:
# Be very careful constructing the regular expressions for this file.
# The lineregexes must match only the single line you want.  
#  re.search is used, so the regex does not have to begin at the beginning.
#  They may be enclosed in double quotes BUT NOT in single quotes.
#  If they contain any vertical bars, these must be escaped with backslash
#  so that they do not look like alternative choices.
# The valueregexes are there for grouping only, to extract the string
#  (usually a number) that you want.  Use the least specific expression
#  that works.
#  If a valueregex contains a vertical bar, it MUST be enclosed in 
#  single quotes (apostrophes).  If not, it MAY be.  
#  It MUST NOT be enclosed in double quotes, don't ask me why.  
#  To avoid the problems with vertical bars, mainly I just use dots
#  to skip over them.  
# If the word number for the valueregex is zero (0), then the 
#  entire line is used.  Sometimes it is easier to find a field
#  with regex context than to count reliably past five.  

'''

import re
from os                 import environ
import csv
from NewTraceFac        import TRC,trace,tracef
import argparse
from time               import clock,localtime
from os                 import stat


#===========================================================
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

#===========================================================
# f n d P a r s e I n p u t 
@tracef("INPT")
def fnldParseInput(mysFilename):
    ''' Return tuple containing
        - the output template string, 
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
        =variables
        varname,lineregex,wordnumber,valueregex (header)
        (lines of csv data)

    '''
    dParams = dict()
    with open(mysFilename,"rb") as fhInfile:
        # Remove comments.  
        lLines = filter( lambda sLine:                          \
                        not re.match("^ *#[^#]",sLine)          \
                        and not re.match("^ *$",sLine.rstrip()) \
                        , fhInfile )

        # Get the output template.  It may be longer than one line.  
        lTemplate = fnlLinesInRange(lLines,"^=template","^=variables")
        lTemplate = map( lambda sLine: sLine.rstrip().replace("###","").replace("##","#"), lTemplate )
        TRC.tracef(3,"INPT","proc ParseInput template|%s|" % (lTemplate))

        # Now get the CSV args into a dictionary of dictionaries.
        lVarLines = fnlLinesInRange(lLines,"^=variables","^=thiswillnotbefound")
        lRowDicts = csv.DictReader(lVarLines)
        TRC.tracef(5,"INPT","proc ParseInput lRowDicts all|%s|" % (lRowDicts))
        
        dParams = dict( map( lambda dRowDict:   \
            (dRowDict["varname"],dRowDict)      \
            , lRowDicts ))
        
    return (lTemplate,dParams)

@tracef("INPT")
def fnlLinesInRange(mylLines,mysStart,mysStop):
    ''' Return open interval of lines from start string to stop string
        excluding both ends.
    '''
    lResults = list()
    bCollect = False
    for sLine in mylLines:
        if re.match(mysStop,sLine):  bCollect = False
        if bCollect: lResults.append(sLine)
        if re.match(mysStart,sLine): bCollect = True
    return lResults

#===========================================================
# m a i n ( ) 
@tracef("MAIN")
def main(mysInstructionsFileName,mysLogFileName):
    (lTemplate,dVars) = fnldParseInput(mysInstructionsFileName)
    lLines = list()
    with open(mysLogFileName,"r") as fhLogFile:

        # Double list comprehension to find lines that match.
        lMatchTuples = [ fntMatchLine(sLine,nLineNr,dVar) \
            for (sLine,lLines,nLineNr) in fnGetLineAndNumber(fhLogFile,lLines) \
            for dVar in dVars.values() ]
        TRC.tracef(5,"MN2","proc MatchTuples len|%s| first|%s|" % (len(lMatchTuples),lMatchTuples[0]))

        # Filter returns only the lines that matched.
        lLinesSelected = filter( lambda (var,matchobj,line): matchobj, \
                                lMatchTuples )
        TRC.tracef(5,"MN2","proc LinesSelected len|%s| all|%s|" % (len(lLinesSelected),lLinesSelected))

        # Extract variable value from each matching line.
        lResults = map( lambda (sVarname,omatch,sLine): \
            fntMatchValue(sLine,dVars[sVarname])         \
            , lLinesSelected )
        dValues = dict(lResults)
        # In case we did not find the line for a variable, dummy up a value.
        for sKey in dVars: dValues.setdefault(sKey,"nolinefound")
        # And in case we didn't even find a rule for some variable that
        #  will be used in the template, dummy up a value for it, too.  
        sTemplateHeader = "\n".join(lTemplate).replace("{","",-1).replace("}","",-1).replace("\n"," ",-1)
        lTemplateVars = sTemplateHeader.split()
        for sTemplateVar in lTemplateVars: dValues.setdefault(sTemplateVar,"norulefound")

    # Add the synthetic variables to the value dictionary.
    dSyntho = fndGetSyntheticVars()
    dValues.update(dSyntho)

    # Fill in the template with values and print.  
    # Template is allowed to be multiple lines.
    sTemplate = "\n".join(lTemplate)
    sLineout = makeCmd(sTemplate,dValues)
    if g.bHeader or environ.get("header",None):
        # Header is a single line concatenation of all the substitutions
        #  in the template.
        #  If the template is longer than one line, well, you can't read 
        #  the data with a simple header anyway.  Oops.  
        sHeader = sTemplateHeader
        print sHeader
    # Newline already pasted on the end of template; don't add another.
    print sLineout,

# f n G e t L i n e A n d N u m b e r 
@tracef("GETL")
def fnGetLineAndNumber(myfh,mylLines):
    for sLine in myfh:
        TRC.tracef(3,"GETL","proc GetLine nr|%s| line|%s|" % (len(mylLines)+1,sLine))
        yield (sLine,mylLines.append(sLine),len(mylLines))

# f n M a t c h L i n e 
@tracef("MCHL")
def fntMatchLine(mysLine,mynLineNr,mydVar):
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
def fntMatchValue(mysLine,mydVar):
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
    return (sVarname,sValue)

# f n d G e t S y n t h e t i c V a r s 
@tracef("SNTH")
def fndGetSyntheticVars():
    dTemp = dict()

    dTemp["logfilename"] = g.sLogFileName
    dTemp["logfilesize"] =  stat(g.sLogFileName).st_size
    dTemp["instructionfilename"] = g.sInstructionsFileName

    (yr,mo,da,hr,mins,sec,x,y,z) = localtime()
    sAsciiT = "%4d%02d%02d_%02d%02d%02d" \
        % (yr,mo,da,hr,mins,sec)
    dTemp["todaysdatetime"] = sAsciiT

    dTemp["extractorversion"] = "0.4"

    return dTemp


# G l o b a l   d a t a 
class CG(object):
    bHeader = False
    sInstructionsFileName = "instructions.txt"
    sLogFileName = "logfile.txt"

# M a i n   l i n e 
if "__main__" == __name__:
    g = CG()
    #read filename and options from cli
    fndCliParse("")
    timestart = clock()
    main(g.sInstructionsFileName,g.sLogFileName)
    timestop = clock()
#    TRC.tracef(0,"MAIN","proc cputime|%s|" % (timestop-timestart))

#END
