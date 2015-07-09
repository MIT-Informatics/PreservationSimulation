#!/usr/bin/python
# expandinstructions.py
#                               RBLandau 20150414

'''
Expand instruction files by substituting a list of values for
 the placeholder name in the template.  Each line of the template 
 produces one or more lines of output, depending on the number of
 values to be substituted for a placeholder in the template.  
 
The header line of the template is unchanged in processing.  
 All other lines may contain placeholders, strings in curly braces,
 that will have values substituted for them by the Python 
 string.format() method with a dictionary.  

Template file starts out like this:

name1 name2 name3 name4 etc
{name1} {name2} {name3} {name4} {etc}

A substitutions file looks like this:

name1
value1
value2
value3

After combining the template and substitutions, the output looks like this:

name1 name2 name3 name4 etc
value1 {name2} {name3} {name4} {etc}
value2 {name2} {name3} {name4} {etc}
value3 {name2} {name3} {name4} {etc}

The one line of template resulted in three lines of output because 
three values were substituted for the name1 placeholder.  

Then you can do similar substitutions for name2, name3, and so forth.  
The resulting output gets larger each time by a multiplier of the 
number of different values substituted into each line.  

Notes: 
- Blank and comment (#) lines are eliminated from all inputs.
- Values to be substituted are stripped of white space.  
- The order of substitutions for placeholders does not affect the 
  set of result lines.  It affects only the order of the result lines.  
- If no substitutions are made, the input is just copied to the output, 
  so don't sweat accidentally doing superfluous substitution passes.  
- Placeholder names should probably be vanilla Python names.  Please,
  no embedded white space in the placeholder names.  
- Line endings are replaced by standard newlines, so don't sweat
  editing the templates or substitutions in Windows.  
'''

from NewTraceFac import ntrace,ntracef,NTRC
NTRC.ntrace(3, "Importing...")
import re
import sys
import copy

# f n h O p e n f i l e 
@ntrace
def fnhOpenFile(mysFilename, mysMode):
    '''
    Generator for possibly long input files.
    Removes newline from end so that the last field is not corrupted.
    '''
    with open(mysFilename, mysMode) as fhFile:
        for sLine in fhFile:
            NTRC.ntrace(3,"proc file|{}| line|{}| ".format(mysFilename,sLine.rstrip()))
            yield sLine.rstrip()

# f n b N o t I g n o r e L i n e 
@ntrace
def fnbNotIgnoreLine(mysLine):
    '''
    True if not a comment or blank line.
    '''
    # Ignore comment and blank lines.
    return (not re.match("^\s*#",mysLine)) and (not re.match("^\s*$",mysLine))

# f n I n t P l e a s e 
@ntrace
def fnIntPlease(myString):
    '''
    If it looks like an integer, make it one.
    '''
    try:
        return int(myString)
    except ValueError:
        return myString

# f n t G e t S u b s t V a l s 
@ntrace
def fntGetSubstVals(myfhIns):
    '''
    Return tuple: 
    - name of column to be substituted
    - list of values to be substituted
    '''
    sName = None
    lNames= list()
    for sLine in filter(fnbNotIgnoreLine, myfhIns):
        # The first line is header containing field name.
        # All other lines are data.
        if not sName: 
            sName = sLine.strip()
            NTRC.ntrace(3, "proc field name|{}|".format(sName))
            continue
        lNames.append(sLine.strip())
    return (sName,lNames)

# f n n I n s e r t s I n t o T e m p l a t e 
@ntrace
def fnnInsertsIntoTemplate(myfhTmp, mysSeparator, mysSubsName, mylSubsVals, myfhOut):
    '''
    Create an output line for each input line TIMES all
     values to be substituted for some column.
    '''
    nNewRecs = 0
    lNames = None
    for sLine in filter(fnbNotIgnoreLine, myfhTmp):
        # The first line is header containing field names.
        # All other lines are data.
        if not lNames:
            lNames = sLine.split(mysSeparator)
            NTRC.ntrace(3, "proc field names|{}|".format(lNames))
            # For items that are not being substituted in this pass, 
            #  the names translate to themselves again.
            #  Looks tricky because .format() insists on having a 
            #  value in the dict for every name mentioned.  
            #  This is easier than rewriting .format(), trust me.  
            dNames = dict(zip(lNames, map(lambda s: "{"+s+"}", lNames)))
            counter = fnnPutOut(sLine, myfhOut)
            continue
        bLinesOut = False
        for sValue in mylSubsVals:
            # Make every placeholder translate back to itself.
            dValues = copy.deepcopy(dNames)
            # Except for the one placeholder that is getting a new, real value.
            dValues[mysSubsName] = sValue
            sLineNew = sLine.format(**dValues)
            NTRC.ntrace(3,"proc template line\n|{}|\nnew line\n|{}|".format(sLine,sLineNew))
            '''
            We want the operation to be idempotent when no substitutions
             are being made.  Were there any non-same output lines?  
             If there were none, then spit out the original line.
            '''
            if not sLineNew == sLine:
                counter = fnnPutOut(sLineNew, myfhOut)
                bLinesOut = True
        if not bLinesOut:
            counter = fnnPutOut(sLine, myfhOut)
    return counter

# f n n P u t O u t 
@ntrace
def fnnPutOut(mysLine, myfhOut):
    '''
    Output new line.  
    Isolate this because we might go directly to database
     sometime in the future.
    Note that the newline is added back here.
    '''
    print >> myfhOut, mysLine


# m a i n 
@ntrace
def main(mysTmpFile,mysInsFile,mysOutFile):
    fhTmp = fnhOpenFile(mysTmpFile, 'r')
    fhIns = fnhOpenFile(mysInsFile, 'r')
    sSeparator = " "
    # Output to stdout if 
    if mysOutFile == "-" or mysOutFile == "stdout":
        fhOut = sys.stdout
    else:
        fhOut = open(mysOutFile, 'w')

    # Get the name and list of values to be substituted.
    (sSubstName, lSubsVals) = fntGetSubstVals(fhIns)
    # Multiply the number of input lines by the number of 
    #  substitution values.  Combinatorial expansion gets out
    #  of hand quickly.  
    counter = fnnInsertsIntoTemplate(fhTmp, sSeparator, sSubstName, lSubsVals, fhOut)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage {} <template file> <insertions file> [<output file>] ".format(sys.argv[0])
        exit(1)
    # If no last arg, or "-", output to stdout
    if len(sys.argv) < 4:
        sys.argv.append("-")
    # Give nice names to the positional arguments.
    [sTemplateFile,sInsertionsFile,sOutputFile] = \
            [sys.argv[1],sys.argv[2],sys.argv[3]]
    main(sTemplateFile,sInsertionsFile,sOutputFile)

# Edit history:
#
# 20150417  RBL Original version that works.
# 

#END
