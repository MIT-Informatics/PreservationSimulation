#!/usr/bin/python
# makeinstructionfiles.py
'''
Create instruction files for runsequence.py.
Substitutes strings into a multi-line template.
Can be used to expand one dimension at a time.
Currently used to substitute number of copies, ber, and seeds.

The meta-instruction file for this program contains two regions, the 
template and the data to be substituted into the template.  Each 
region begins with an introducer line that starts with an = sign.  
Template comes first.  

The program creates an instruction file for each line of the parameters
region in the meta-instruction file.  Each parameter line contains 
values to be substituted into the entire template, which is then written
into an output file.  

A typical file has the following format:

=template
A bunch of lines that can contain named substitutions to be resolved
by the Python string.format() method.  

Comment lines starting with # and blank lines will be removed.  

HOWEVER, lines starting with ## will be placed in the output
as single-# comments.  (That's okay because runsequence.py is 
also happy to remove comments.  Its input is not pure CSV.)

AND lines beginning with ### will be transferred literally to 
the output with the ### removed; no substitutions will be attempted
on such lines.  

=parameters
A CSV region, header plus data lines, that contain the substitutions
to be made in the template.  This region is processed by the Python 
csv standard library module DictReader.  
Again, # comments and blank lines are removed.  

Substitution variables can be named anything you wish, but the name 
"filename" is reserved for the output file to be created containing the 
expanded output from the template and the substitutions.  
(We don't just send the output to stdout because the filenames are
pretty intimately tied to the substitutions to be made, and we don't
want the filenames to get confused.  When there are dozens of them 
floating around with very similar names, bad idea to permit mistakes.  
Six sigma, dude.  

The CLI now permits a number of arguments to override the parameters 
in the meta-instruction file:
- meta-instruction filename (required)
- output directory to put the new instruction files into, instead of just . (optional)
- --family directory for the instructions
- --specific directory for the instructions
- --extra1  --extra2  --extra3
  three "extra" strings to insert other options that we didn't think of
  in advance into the command lines; the syntax for the extra strings is
  peculiar, you have to do --extra1="--additionaloption=itsvalue" with 
  the equal sign and the quotes.

Typical command line:
python makeinstructionfiles-01.py --family=Q0 --specific=v1manysmalldocs make-instructions-b0010.txt ../q0/v1manysmalldocs/log0010


'''

import csv
import re
from NewTraceFac    import TRC,trace,tracef
import argparse


# C l i P a r s e 
@tracef("CLI")
def fndCliParse(mysArglist):
    ''' Parse the mandatory and optional positional arguments, and the 
        many options for this run from the command line.  
        Return a dictionary of all of them.  Strictly speaking that is 
        not necessary, since most of them have already been decanted
        into the P params object.  
    '''
    sVersion = "0.0.3"
    cParse = argparse.ArgumentParser(description="Digital Library Preservation Simulation, Parameter File Creator",epilog="Defaults for args as follows:\n\
        extra string example --extra1='--option=value'; \n\
        version=%s; \n" % sVersion
        )

    # P O S I T I O N A L  arguments
    #cParse.add_argument('--something', type=, dest='', metavar='', help='')

    cParse.add_argument('sInstructionsFile', type=str
                        , metavar='sINSTRUCTIONFILE'
                        , help='File with command template and CSV params'
                        )

#    cParse.add_argument('sOutputDir', type=str
#                        , metavar='sOUTPUTDIR'
#                        , nargs="?"
#                        , help='Directory into which to place the output instruction files.'
#                        )

    # - - O P T I O N S
    # Some of these so-called options will be considered mandatory; 
    #  sorry about that.  They are options rather than positional arguments
    #  so that they cam be given with nice names.  Basically, they are 
    #  keyword args rather than options.  
    #  family, familyroot, and specific are all mandatory.  
    
    cParse.add_argument("--family", type=str
                        , dest='family'
                        , metavar='sFAMILYDIR'
                        , help='Family directory for these tests.'
                        )
    cParse.add_argument("--familyroot", type=str
                        , dest='familyroot'
                        , metavar='sFAMILYROOTDIR'
                        , help='Family root directory for these tests, often "..".'
                        )

    cParse.add_argument("--specific", type=str
                        , dest='specific'
                        , metavar='sSPECIFICDIR'
                        , help='Specific directory for these tests.'
                        )

    cParse.add_argument("--extra1", type=str
                        , dest='extra1'
                        , metavar='sEXTRA1'
                        , help='Additional argument (probably --option=value) string for template command.'
                        )
    cParse.add_argument("--extra2", type=str
                        , dest='extra2'
                        , metavar='sEXTRA2'
                        , help='Additional argument (probably --option=value) string for template command.'
                        )
    cParse.add_argument("--extra3", type=str
                        , dest='extra3'
                        , metavar='sEXTRA3'
                        , help='Additional argument (probably --option=value) string for template command.'
                        )

    if mysArglist:          # If there is a specific string, use it.
        (xx) = cParse.parse_args(mysArglist)
    else:                   # If no string, then parse from argv[].
        (xx) = cParse.parse_args()

    return vars(xx)


# class  C C o m m a n d
class CCommand(object):
    '''
    class CCommand: Execute a CLI command, parse results
    using a regular expression supplied by the caller.  
    '''
    @trace
    def doCmdStr(self,mysCommand):
        ''' Return concatenated string of result lines with newlines stripped.  
        '''
        sResult = ""
        for sLine in popen(mysCommand):
            sResult += sLine.strip()
        return sResult
    @trace
    def doCmdLst(self,mysCommand):
        ''' Return list of result lines with newlines stripped.  
        '''
        lResult = list()
        for sLine in popen(mysCommand):
            lResult.append(sLine.strip())
        return lResult
    @trace
    def doParse(self,mysCommand,mysRegex):
        sOutput = self.doCmd(mysCommand)
        mCheck = search(mysRegex,sOutput)
        if mCheck:
            sResult = mCheck.groups()
        else:
            sResult = None
        return sResult
    @trace
    def makeCmd(self,mysCmd,mydArgs):
        ''' Substitute arguments into command template string,
            by name, from the supplied dictionary.  
        '''
        sCmd = mysCmd.format(**mydArgs)
        return sCmd

# f n d P a r s e I n p u t 
@trace
def fndParseInput(mysFilename):
    ''' Return tuple containing
        - the command template string, 
        - a list, one item per line, of dicts of column args.  
        Make sure that (duck-type) integers remain integers.  
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
        if re.match("=template",sCmd):
            lTemplate = list()
            while 1:
                sCmd = lLines.pop(0).rstrip()
                if re.match("^=parameters",sCmd):
                    break
                sCmd = sCmd.replace("###","")
                sCmd = sCmd.replace("##","#")
                lTemplate.append(sCmd)
            TRC.trace(3,"proc ParseInput template|%s|" % (lTemplate))

        # Now get the CSV args into a list of dictionaries.
        lRowDicts = csv.DictReader(lLines)

        '''
        for dRow in lRowDicts:
            dNewRow = dict()
            # Sanitize (i.e., re-integerize) the entire row dict, 
            # keys and values, and use the new version instead.
            for xKey in dRow:
                dNewRow[fnIntPlease(xKey)] = fnIntPlease(dRow[xKey])
            # Put it back into a list, in order.
            lParams.append(dNewRow)
            TRC.trace(5,"proc fndParseInput dRow|%s| dNewRow|%s| lParams|%s|" % (dRow,dNewRow,lParams))
        '''
        # Today, we want strings instead of integers, so skip all that.  
        # Just put all the rest of the lines into the params list.  
        lParams = list()
        for dd in lRowDicts:
            lParams.append(dd)
    return (lTemplate,lParams)

# C G   c l a s s   f o r   g l o b a l   d a t a 
class CG(object):
    ''' Global data.
    '''
    sInstructionsFile = "instructions.txt"
    sOutputDir = "."
    sFamilyDir = ""
    sSpecificDir = ""
    family = ""
    familyroot = ""
    specific = ""

# f n M a y b e O v e r r i d e 
@trace
def fnMaybeOverride(mysCliArg,mydDict,mycClass):
    ''' Strange function to override a property in a global dictionary
        if there is a version in the command line dictionary.  
    '''
    try:
        if mydDict[mysCliArg]:
            setattr( mycClass, mysCliArg, mydDict[mysCliArg] )
    except KeyError:
            if not getattr(mycClass,mysCliArg,None):
                setattr( mycClass, mysCliArg, None )
    return getattr(mycClass,mysCliArg,"XXXXX")


# M A I N 
@trace
def main():
    g = CG()                # One instance of the global data.
    
    dCliDict = fndCliParse("")
    # Check for mandatory options.
    if not dCliDict['family'] \
    or not dCliDict['familyroot'] \
    or not dCliDict['specific']:
        print "ERROR: must specify --family and --familyroot and --specific mandatory options."
        exit(1)
    # Clean out "None" strings left over from CLI parsing, grumble.
    for kk in dCliDict: 
        if dCliDict[kk] == None:
            dCliDict[kk] = ""

    # Carefully insert any new CLI values into the Global object.
    fnMaybeOverride("sInstructionsFile",dCliDict,g)
    fnMaybeOverride("sOutputDir",dCliDict,g)
    fnMaybeOverride("family",dCliDict,g)
    fnMaybeOverride("familyroot",dCliDict,g)
    fnMaybeOverride("specific",dCliDict,g)

    # Read the file of meta-instructions.  
    sFilename = g.sInstructionsFile
    (lTemplate,lParams) = fndParseInput(sFilename)
    cCommand = CCommand()

    # Each line of CSV params creates a dictionary, column-name --> value.
    # We have a list of such dictionaries.  
    # Process the instructions one line at a time.
    for idx in range(len(lParams)):
        g.family = g.sFamilyDir
        g.specific = g.sSpecificDir
        dParamsFromFile = lParams[idx]
        # Now do backwards substitutions to let CLI override the instructions file.
#        fnMaybeOverride("family",dCliDict,dParamsFromFile) # can't setattr into a dict, oops
        if "family" in dCliDict: dParamsFromFile["family"] = dCliDict["family"]
        if "familyroot" in dCliDict: dParamsFromFile["familyroot"] = dCliDict["familyroot"]
        if "specific" in dCliDict: dParamsFromFile["specific"] = dCliDict["specific"]
        if "extra1" in dCliDict: dParamsFromFile["extra1"] = dCliDict["extra1"]
        if "extra2" in dCliDict: dParamsFromFile["extra2"] = dCliDict["extra2"]
        if "extra3" in dCliDict: dParamsFromFile["extra3"] = dCliDict["extra3"]
        dParams = dParamsFromFile
 
        # Construct output dir name from family, specific, and ber from params.
        sRoot = (dParams['familyroot']+"/" if dParams['familyroot'] else "")
        g.sOutputDir = dParams['family'] +'/'+ dParams['specific'] +'/'+'logb'+ dParams['ber']
        # Substitute params into each line of template, and write an output file.
        sOutFile = sRoot + g.sOutputDir + "/" + dParams["filename"]
        TRC.tracef(3,"MAIN","proc construct output name root|%s| family|%s| specific|%s| outdir|%s| outfile|%s|" % (sRoot,dParams['family'],dParams['specific'],g.sOutputDir,sOutFile))
        with open(sOutFile,"w") as fhOut:
            print "Writing %s" % (sOutFile)
            for sCommand in lTemplate:
                sFullCmd = cCommand.makeCmd(sCommand,dParams)
                TRC.tracef(3,"OUT","proc output line|%s|" % (sFullCmd))
                print >> fhOut, sFullCmd


# E n t r y   p o i n t . 
if __name__ == "__main__":
    main()

#END
