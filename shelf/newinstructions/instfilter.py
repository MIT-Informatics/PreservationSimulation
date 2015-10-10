#!/usr/bin/python
# instfilter.py
# Functions to filter potential instructions.

import  re
import  json
import  csv
from    NewTraceFac     import  NTRC, ntrace, ntracef

'''
dict list external as json
    permit comments?  have to filter before jload

additional things in the dict beyond attributes:
- action : permit or deny
    no default
- reverse : true or false
    like grep -v, do action for whatever doesn't match
    default = false if absent
- need wildcard value, e.g., *, to permit any value
    or maybe just not mentioned in dict?


list of rules, processed all the way to the end
- permit everything
- deny some broad stuff
- permit some specifics
- deny
- permit

Examples:

permit  *
deny    glitchfreq=30000 impact=100 
permit  impact=100 decay=0 life=0
deny    glitchfreq=0
permit  glitchfreq=0 impact=100 decay=0 life=0
permit  audit=0
deny    audit=10000
permit  audit=10000 segments=1 type=TOTAL
deny    audit=20000
permit  audit=20000 segments=1 type=TOTAL
deny    audit=5000
permit  audit=5000 segments=1 type=TOTAL
deny    lifetime<10
deny    lifetime>1000
deny    copies>=10

'''

class CInstructionFilter(object):
    @ntrace
    def __init__(self, mysRuleFilename=None):
        '''Absorb rules json file now, if given.'''
        self.ldRules = []
        if mysRuleFilename:
            self.fnSetRules(mysRuleFilename)

    @ntrace
    def fnSaveHeaderLine(self, mysLine):
        '''Store header line for all instruction lines.
            Usually comes from the first line of the file.'''
        self.sHeaderLine = mysLine.strip()

    @ntrace
    def fndMakeLineDict(self, mysLine):
        '''Turn a single line into a dictionary of fields and values.
            Assume blank-delimited file.
            Add the header row on front so the csvreader can parse it.'''
        csv.register_dialect('blankdelim', delimiter=' ')
        lVarLines = [self.sHeaderLine]
        lVarLines.append(mysLine)
        lRowDicts = list(csv.DictReader(lVarLines, dialect='blankdelim'))
        return lRowDicts[0]

    @ntrace
    def fnbDoesLinePassAllRules(self,mydLine):
        bEval = True                # Lines pass by default.
        for dRule in self.ldRules:
            bMatch = self.fnbDoesLineMatchOneRule(mydLine, dRule)
            if bMatch:
                if dRule['action'] == 'permit':
                    bEval = True
                elif dRule['action'] == 'deny':
                    bEval = False
                else:
                    raise ValueError('Invalid rule action: "%s"'%(dRule['action']))
        return bEval

    @ntrace
    def fnbDoesLineMatchAllRules(self, mydLine):
        return all([self.fnbDoesLineMatchOneRule(mydLine, dRule) 
            for dRule in self.ldRules])

    @ntrace
    def fnsGetValue(self,opandval):
        oMatch = re.match(r'[<>!=]+\s*(\S+)', opandval)
        if oMatch:
            return oMatch.group(1)
        else:
            return opandval

    @ntrace
    def fnbDoesLineMatchOneRule(self, mydLine, mydRule):
        for key, val in mydRule.items():
            if key != "reverse" and key != "action":
                linevalue = mydLine[key]
                if str(val).startswith('>'):
                    bResult = int(linevalue) > int(self.fnsGetValue(val))
                elif str(val).startswith('<'):
                    bResult = int(linevalue) < int(self.fnsGetValue(val))
                elif str(val).startswith('!='):
                    bResult = linevalue != self.fnsGetValue(val)
                else:
                    bResult = linevalue == val
                if not bResult:
                    break
        return bResult if not mydRule.get('reverse', False) else not bResult
        
    @ntrace
    def fnldGetRules(self, mysRuleFilename):
        with open(mysRuleFilename,"rb") as fhInfile:
        # Remove comments and blank lines.  
            lLines = filter( lambda sLine:                          
                        not re.match("^\s*#",sLine)          
                        and not re.match("^\s*$",sLine.rstrip()) 
                        , fhInfile 
                        )
        sLines = ' '.join(lLines)
        try:
            ldRules = json.loads(sLines)
        except ValueError:
            raise ValueError('Invalid JSON in rule input file.')
        return ldRules

    @ntrace
    def fnSetRules(self,mysRuleFilename):
        self.ldRules = self.fnldGetRules(mysRuleFilename)



