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
    cParse.add_argument('sInstructionsFile', type=str
                        , metavar='sINSTRUCTIONFILE'
                        , help='File with sequence of instructions.'
                        )

    cParse.add_argument('sRulesFile', type=str
                        , metavar='sRULESFILE'
                        , help='File of rules that instructions must pass.'
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


@ntrace
def main(fhIn, cfilter):
    '''First line of file is the header with field names.
        All others get dictionary-ified and tested.'''
    header = fhIn.next().strip()
    cfilter.fnSaveHeaderLine(header)
    print header
    for sLine in fhIn:
        if not re.match('^\s*$', sLine):
            dLine = cfilter.fndMakeLineDict(sLine)
            bAnswer = cfilter.fnbDoesLinePassAllRules(dLine)
            #sEval = '      ' if bAnswer else 'DENY  '
            #print sEval, sLine.strip()
            if bAnswer:
                print sLine.strip()

if __name__ == "__main__":
    g = CG()
    dArgs = fndCliParse("")
    g.__dict__.update(dArgs)
    with open(mysRuleFilename,"rb") as fhInfile:
    # Remove comments and blank lines.  
        lLines = filter( lambda sLine:                          
                    not re.match("^\s*#",sLine)          
                    and not re.match("^\s*$",sLine.rstrip()) 
                    , fhInfile 
                    )
    sLines = ' '.join(lLines)

    cfilter = instfilter.CInstructionFilter(sLines)
    with open(g.sInstructionsFile,'r') as fhIn:
        main(fhIn, cfilter)

#END
