#!/usr/bin/python
# test_instfilter.py

'''\
Vague sort of unit test for the instruction filter class.
'''

import  instfilter
from    NewTraceFac     import  NTRC,ntrace,ntracef
import  re
import  sys


def main(fhIn, cfilter):
    '''\
    First line of file is the header with field names.
    All others get dictionary-ified and tested.
    '''
    header = fhIn.next()
    cfilter.fnSaveHeaderLine(header)
    print header
    for sLine in fhIn:
        if not re.match('^\s*$', sLine):
            dLine = cfilter.fndMakeLineDict(sLine)
            bAnswer = cfilter.fnbDoesLinePassAllRules(dLine)
            sEval = '      ' if bAnswer else 'DENY  '
            print sEval, sLine.strip()

def fnsSanitizeFileString(mysContents):
    '''\
    Remove blank lines and comments from a string concatenated 
    from multiple lines of a file.
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


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print "Usage: %s datafile rulefile" % (sys.argv[0])
        sys.exit(1)
    sInfile = sys.argv[1] if len(sys.argv) > 1 else 'filterme1.txt'
    sRulesfile = sys.argv[2] if len(sys.argv) > 2 else 'rulesjsongood.txt'

    with open(sRulesfile,'r') as fhR:
        sRulesRaw = fhR.read()
    sRules = fnsSanitizeFileString(sRulesRaw)
    if sRulesfile.find("json") >= 0:
        cfilter = instfilter.CInstructionFilter_Json(sRules)
    else:
        cfilter = instfilter.CInstructionFilter_Text(sRules)

    with open(sInfile,'r') as fhIn:
        main(fhIn, cfilter)

#END
