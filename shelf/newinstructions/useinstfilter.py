#!/usr/bin/python
# useinstfilter.py

'''\
Apply the instruction filter to an input file
'''

import  instfilter
from    NewTraceFac     import  NTRC,ntrace,ntracef
import  re
import  sys
import  argparse
import  os


# C l i P a r s e 
@ntracef("CLI")
def fndCliParse(mysArglist):
    ''' Parse the mandatory and optional positional arguments, and the 
        many options for this run from the command line.  
        Return a dictionary of all of them.  Strictly speaking that is 
        not necessary, since most of them have already been decanted
        into the P params object.  
    '''
    sVersion = "0.0.1"
    cParse = argparse.ArgumentParser(description="Digital Library Preservation Simulation, UseInstFilter: apply instruction rules filter to input file",epilog="Defaults for args as follows:\n\
        (none), version=%s" % sVersion
        )

    # P O S I T I O N A L  arguments
    #cParse.add_argument('--something', type=, dest='', metavar='', help='')
    cParse.add_argument('sRulesFile', type=str
                        , metavar='sRULESFILE'
                        , help='File of rules that instructions must pass.'
                        )

    cParse.add_argument('sInstructionsFile', type=str
                        , metavar='sINSTRUCTIONFILE'
                        , help='File with sequence of instructions.'
                        )

    # - - O P T I O N S
    # None today.  
    if mysArglist:          # If there is a specific string, use it.
        (xx) = cParse.parse_args(mysArglist)
    else:                   # If no string, then parse from argv[].
        (xx) = cParse.parse_args()
    return vars(xx)


# C G   c l a s s   f o r   g l o b a l   d a t a 
class CG(object):
    ''' Global data.
    '''
    sInstructionsFile = "instructions.txt"
    sRulesFile = "rules.txt"

    # Debug data.
    sHeader = "header line goes in here"
    nLine = 0
    sLine = "each instruction line goes in here"
    lRules = list()
    nRule = 0
    sRule = "each rule line goes in here in turn"
    sRuleDenyTrue = "last deny rule that evaluated to true goes here"
    nRuleDenyTrue = 0


# m a i n 
@ntrace
def main(fhIn, cfilter):
    '''First line of file is the header with field names.
        All others get dictionary-ified and tested.'''
    header = fhIn.next().strip()
    cfilter.fnSaveHeaderLine(header)
    g.sHeader = header
    print header
    # Check all lines against the set of rules.
    # Skip over any vagrant blank lines.
    for sLine in fhIn:
        g.nLine += 1
        if not re.match('^\s*$', sLine):
            g.sLine = sLine
            dLine = cfilter.fndMakeLineDict(sLine)
            bAnswer = cfilter.fnbDoesLinePassAllRules(dLine)
            if os.environ.get("DEBUG", "no") in ("Y","YES","y","yes"):
                sEval = ' ' if bAnswer else 'DENY'
                print "%-7s%s" % (sEval, sLine.strip())
                if not bAnswer:
                    print "rule%2d %s" % (g.nRuleDenyTrue, g.sRuleDenyTrue)
            else:
                if bAnswer:
                    print sLine.strip()

# f n s S a n i t i z e F i l e S t r i n g 
def fnsSanitizeFileString(mysContents):
    '''\
    Remove blank lines and comments from a string concatenated 
    from multiple lines of a file.  And regularize line endings.  
    '''
    lLinesRaw = mysContents.split("\n")
    lLinesReal = filter( lambda sLine:                          
            not re.match("^\s*#",sLine.lstrip())
            and not re.match("^\s*$",sLine.rstrip()) 
            , lLinesRaw
            )
    lLines = [line.strip() for line in lLinesReal]
    sLines = '\n'.join(lLines)
    return sLines


# M A I N   L I N E 
if __name__ == "__main__":
    g = CG()
    dArgs = fndCliParse("")
    g.__dict__.update(dArgs)
    
    with open(g.sRulesFile,'r') as fhR:
        sRulesRaw = fhR.read()
    sRules = fnsSanitizeFileString(sRulesRaw)
    if g.sRulesFile.find("json") >= 0:
        cfilter = instfilter.CInstructionFilter_Json(sRules, g)
    else:
        cfilter = instfilter.CInstructionFilter_Text(sRules, g)

    with open(g.sInstructionsFile,'r') as fhIn:
        main(fhIn, cfilter)

#END
