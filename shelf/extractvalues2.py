#!/usr/bin/python
# extractvalues.py
from __future__ import absolute_import, division, print_function, unicode_literals

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
'''
Basically, this is a teensy subset of awk, which I would have used
except that no one left on earth except a few dinosaurs like me still
speak the language.  
The lineregex is the line selector expression for awk, except that it
is limited to a single regex, not a range, so I have to be careful 
to use unique codes on the lines to be selected.
Problem: to assess the impact of glitches, I have to add some programming
ability within the line selected to capture server id as well as the 
relevant data item.  Well, oops.  
'''

import  re
import  os
import  csv
from    NewTraceFac     import NTRC,ntrace,ntracef
import  argparse
import  time
import  extractcpuinfo


#===========================================================
# C l i P a r s e 
@ntracef("CLI")
def fndCliParse(mysArglist):
    ''' Parse the mandatory and optional positional arguments, and the 
        many options for this run from the command line.  
        Return a dictionary of all of them.   
    '''
    sVersion = "2.1.1"
    cParse = argparse.ArgumentParser(description="Digital Library Preservation Simulation, Utility to extract values from log files, CLI version %s.   "%(sVersion) + \
        "Takes one simulation log file and instruction file.  Produces (to stdout)" + \
        "one line of data, plus optional header line of field names."
        , epilog="Defaults for args as follows: separator=blank.\n"
#        , version=sVersion
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

    cParse.add_argument("--separator", type=str
                        , dest='sSeparator'
                        , metavar='sSEPARATORCHAR'
                        , nargs='?'
                        , help='Single-character separator for the sort-of-CSV output file.'
                        )
    
    if mysArglist:          # If there is a specific string, use it.
        (xx) = cParse.parse_args(mysArglist)
    else:                   # If no string, then parse from argv[].
        (xx) = cParse.parse_args()

    g.sInstructionsFileName = xx.sInstructionsFileName
    g.sLogFileName = xx.sLogFileName
    g.bHeader = getattr(xx,"bHeader",False)

    return vars(xx)

@ntracef("MCMD")
def makeCmd(mysCmd,mydArgs):
    ''' Substitute arguments into command template string,
        by name, from the supplied dictionary.  
    '''
    sCmd = mysCmd.format(**mydArgs)
    return sCmd

#===========================================================
# f n d P a r s e I n p u t 
@ntracef("INPT")
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
    with open(mysFilename,"r", encoding="'utf-8") as fhInfile:
        # Remove comments.  
        lLines = list(filter( lambda sLine:
                        not re.match("^ *#[^#]",sLine)
                        and not re.match("^ *$",sLine.rstrip())
                        , fhInfile ))

        # Get the output template.  It may be longer than one line.  
        lTemplate = fnlLinesInRange(lLines,"^=template","^=variables")
        lTemplate = list(map( lambda sLine: sLine.rstrip().replace("###","").replace("##","#"), lTemplate ))
        NTRC.tracef(3,"INPT","proc ParseInput1 template|%s|" % (lTemplate))

        # Fix the separator in the template according to the user spec.
        lAllTemplateNames = [lTemplateLine.split() for lTemplateLine in lTemplate]
        lNewTemplate = [g.sSeparator.join(lTemplateNamesOneLine) 
            for lTemplateNamesOneLine in lAllTemplateNames]
        NTRC.tracef(3,"INPT","proc ParseInput2 template|%s|" % (lNewTemplate))

        # Now get the CSV args into a dictionary of dictionaries.
        lVarLines = fnlLinesInRange(lLines,"^=variables","^=thiswillnotbefound")
        lRowDicts = csv.DictReader(lVarLines)
        NTRC.tracef(5,"INPT","proc ParseInput3 lRowDicts all|%s|" % (lRowDicts))
        
        dParams = dict( map( lambda dRowDict:   \
            (dRowDict["varname"],dRowDict)      \
            , lRowDicts ))

    return (lNewTemplate,dParams)

@ntracef("INPT")
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
@ntracef("MAIN")
def main(mysInstructionsFileName,mysLogFileName):
    (lTemplate, g.dVars) = fnldParseInput(mysInstructionsFileName)
    lLines = list()
    with open(mysLogFileName,"r", encoding="'utf-8") as fhLogFile:

        '''\
        get list of tuples: lines that match some lineregex, for which var

        foreach line, 
            if matches any lineregex
                extract value, 
                put varname and value in dictionary

        be careful never to form a list of lines of the input log file, 
         or of anything that is big-O of that.  filter first.
        '''

        # Form list of all lines that match some var.
        nLineNr = 0
        lLinesSelectedRaw = list()
        for sLine in fhLogFile:
            nLineNr += 1                # Need line nr only for debugging.
            for sVarname in g.dVars.keys():
                tResult = fntDoesLineMatchThisVar(sLine, nLineNr, sVarname)
                # If line matches any var, save the line and the varname.
                if tResult[0]: 
                    lLinesSelectedRaw.append(tResult)
        NTRC.tracef(3,"MN2","proc lLinesSelectedRaw len|%s| all|%s|" 
                    % (len(lLinesSelectedRaw),lLinesSelectedRaw))

    # Eliminate duplicates.  Should not be any if the lineregexes are 
    #  specific enough.  
    lLinesSelected = list(set(lLinesSelectedRaw))
    NTRC.tracef(5,"MN3","proc lLinesSelected len|%s| all|%s|" % (len(lLinesSelected),lLinesSelected))

    # Extract variable value from each matching line.
    # List of lines selected is actually a list of triples.
#    lResults = map( lambda ((omatch, sLine, sVarname)): 
#                fntMatchValue(sLine, g.dVars[sVarname])
#                , lLinesSelected )
# AAARGH: PythonV3 removed tuples as args for lambdas!!!
    lResults = map( lambda tLine: 
                fntMatchValue(tLine[1], g.dVars[tLine[2]])
                , lLinesSelected )
    # Returned list of (name,val) tuples for vars in lines selected.
    #  Make a dictionary.  
    dValues = dict(lResults)

    # In case we did not find the line for a variable, dummy up a value.
    for sKey in g.dVars: 
        dValues.setdefault(sKey,"nolinefound")

    # And in case we didn't even find a rule for some variable that
    #  will be used in the template, dummy up a value for it, too.  
    sTemplateHeader = "\n".join(lTemplate).replace("{","").replace("}","").replace("\n"," ")
    lTemplateVars = sTemplateHeader.split()
    for sTemplateVar in lTemplateVars: 
        dValues.setdefault(sTemplateVar,"norulefound")

    # Add the synthetic variables to the value dictionary.
    dSyntho = fndGetSyntheticVars()
    dValues.update(dSyntho)

    # Make the seed value, at least, print constant width for legibility.  
    sSeed = dValues["seed"]
    sSeednew = "%09d" % (int(sSeed))
    dValues["seed"] = sSeednew

    # Fill in the template with values and print.  
    # Template is allowed to be multiple lines.
    sTemplate = "\n".join(lTemplate)
    sLineout = makeCmd(sTemplate,dValues)
    if g.bHeader or os.environ.get("header",None):
        # Header is a single line concatenation of all the substitutions
        #  in the template.
        #  If the template is longer than one line, well, you can't read 
        #  the data with a simple header anyway.  Oops.  
        sHeader = sTemplateHeader
        print(sHeader)
    # Newline already pasted on the end of template; don't add another.
    print(sLineout,)
    # Done.  

# f n t D o e s L i n e M a t c h T h i s V a r 
@ntracef("MCHT",level=5)
def fntDoesLineMatchThisVar(mysLine, mynLineNr, mysVarname):
    '''\
    Check line against lineregex of var.
    Return tuple (matchobject, line, varname).
    '''
    dVar = g.dVars[mysVarname]
    sLineregex = dVar["lineregex"]
    oMatch = re.search(sLineregex,mysLine)
    NTRC.tracef(5,"MTLN","proc MatchLine try regex|%s| var|%s| nr|%s| line|%s| match|%s|" % (sLineregex,mysVarname,mynLineNr,mysLine,oMatch))
    if oMatch:
        NTRC.tracef(3,"LINE","proc MatchLine found line|%s|=|%s| var|%s| regex|%s|" % (mynLineNr,mysLine,mysVarname,sLineregex))
    return (oMatch, mysLine, mysVarname)

# f n M a t c h V a l u e 
@ntracef("MCHV")
def fntMatchValue(mysLine,mydVar):
    '''\
    Extract value from line according to valueregex for var.
     If no value found, supply suitably disappointing string.  
    Get the right word from the line.
     If asked for word zero, use the whole line.  
     Makes the extraction harder, but sometimes necessary.
    '''
    sWordnumber = mydVar["wordnumber"]
    nWordnumber = int(sWordnumber)
    lWords = mysLine.split()
    if nWordnumber == 0:
        sWord = mysLine
    elif nWordnumber <= len(lWords):
        sWord = lWords[nWordnumber-1]
    else: 
        sWord = "nowordhere_indexoutofrange"
    sValueregex = mydVar["valueregex"]
    sVarname = mydVar["varname"]
    oMatch = re.search(sValueregex,sWord)
    NTRC.tracef(5,"MCHV","proc MatchValue matching word var|%s| word|%s| valueregex|%s| matchobj|%s|" % (sVarname,sWord,sValueregex,oMatch))
    if oMatch:
        # Word matches the valueregex.  Save the value.
        sValue = oMatch.group(1)
        NTRC.tracef(3,"MCHV","proc addvalue name|%s| val|%s|" % (sVarname,sValue))
    else:
        # If not found, at least supply something conspicuous for printing.
        sValue = "novaluefound"
    return (sVarname,sValue)

# f n d G e t S y n t h e t i c V a r s 
@ntracef("SNTH")
def fndGetSyntheticVars():
    dTemp = dict()

    dTemp["logfilename"] = g.sLogFileName
    dTemp["logfilesize"] =  os.stat(g.sLogFileName).st_size
    dTemp["instructionfilename"] = g.sInstructionsFileName

    (yr,mo,da,hr,mins,sec,x,y,z) = time.localtime()
    sAsciiT = "%4d%02d%02d_%02d%02d%02d" \
        % (yr,mo,da,hr,mins,sec)
    dTemp["todaysdatetime"] = sAsciiT

    dTemp["extractorversion"] = "0.6_20170522"

    dTemp["cpuinfo"] = extractcpuinfo.fnsGetCpuIdString("short")

    return dTemp


# G l o b a l   d a t a 
class CG(object):
    bHeader = False
    sInstructionsFileName = "instructions.txt"
    sLogFileName = "logfile.txt"
    sSeparator = " "
    dVars = dict()
    

# M a i n   l i n e 
if "__main__" == __name__:
    g = CG()                # Global dict for options.
    # Read filename and options from cli
    dCliDict = fndCliParse("")
    dCliDictClean = {k:v for k,v in dCliDict.items() if v is not None}
    g.__dict__.update(dCliDictClean)
    timestart = time.clock()
    main(g.sInstructionsFileName,g.sLogFileName)
    timestop = time.clock()
#    NTRC.tracef(0,"MAIN","proc cputime|%s|" % (timestop-timestart))

# Edit history:
# 2014sometime  RBL Original version.
# 20150729  RBL Recode main loop entirely to avoid forming list of all lines.
#                (This required 800MB of RAM to process an 80MB log file, oops.)
#                Filter first to isolate the few lines that match any
#                lineregex, then you can take your time.  
#                Couldn't find a reasonable way to do this with all functional
#                forms without that giant list again.  
# 20150809  RBL Minor cleanup revisions.
#               Added a few comments, docstrings.  
#               After testing, this is about 2x faster than the original 
#                version, and uses an almost fixed <10MB of memory.  
# 20161018  RBL Add comments about future extension needed.  
# 20170522  RBL Add synthetic var for cpuinfo so one can 
#                maybe examine compute speed.  Just more crud
#                in the output line.  
#               And bump version number.  
# 20181218  RBL Make seed value print constant width to improve legibility of 
#                lost value.
# 20200726  RBL Sneak up on PythonV3.
#               Fix prints.
#               Fix lambda syntax to accept a tuple in V3.
#               Fix several map and filter calls that return iterators 
#                instead of lists.
#               Fix version arg given to ArgumentParser; arg removed in PyV3.
# 
# 

#END
