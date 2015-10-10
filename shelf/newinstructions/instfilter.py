#!/usr/bin/python
# instfilter.py
# Functions to filter potential instructions.

import  re
import  json
import  csv
from    NewTraceFac     import  NTRC, ntrace, ntracef
import  abc


'''
Problem: the complete cross-product of possible instruction values is too large.
Many of the combinations are nonsensical.  Let's filter some of them out.  

Dict list external as json or text (see example).

Additional things in the dict beyond attributes:
- action : permit or deny
    no default
- reverse : true or false
    like grep -v, do action for whatever doesn't match
    default = false if absent
- need wildcard value, e.g., *, to permit any value?
    or maybe just not mentioned in dict?


List of rules, processed all the way to the end
- permit everything (lines all pass by default)
- deny some broad stuff
- permit some specifics
- deny
- permit

Examples:

permit  copies>0                        # permits everything
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

'''\
Base class.  Does everything but parse external rule files, 
which is done by the subclasses.
'''
# c l a s s   C I n s t r u c t i o n F i l t e r 
class CInstructionFilter(object):
    __metaclass__ = abc.ABCMeta

    @ntracef("FILT")
    def __init__(self):
        '''Absorb rules json file now, if given.'''
        self.ldRules = []

    @ntracef("FILT")
    def fnSaveHeaderLine(self, mysLine):
        '''Store header line for all instruction lines.
            Usually comes from the first line of the file.'''
        self.sHeaderLine = mysLine.strip()

    @ntracef("FILT")
    def fndMakeLineDict(self, mysLine):
        '''Turn a single line into a dictionary of fields and values.
            Assume blank-delimited file.
            Add the header row on front so the csvreader can parse it.'''
        csv.register_dialect('blankdelim', delimiter=' ')
        lVarLines = [self.sHeaderLine]
        lVarLines.append(mysLine)
        lRowDicts = list(csv.DictReader(lVarLines, dialect='blankdelim'))
        return lRowDicts[0]

    @ntracef("FILT")
    def fnbDoesLinePassAllRules(self,mydLine):
        bEval = True                    # Lines pass by default.
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

    @ntracef("FILT")
    def fnbDoesLineMatchAllRules(self, mydLine):
        return all([self.fnbDoesLineMatchOneRule(mydLine, dRule) 
            for dRule in self.ldRules])

    @ntracef("FILT")
    def fnsGetValue(self,opandval):
        oMatch = re.match(r'[<>!=]+\s*(\S+)', opandval)
        if oMatch:
            return oMatch.group(1)
        else:
            return opandval

    @ntracef("FILT")
    def fnbDoesLineMatchOneRule(self, mydLine, mydRule):
        for key, val in mydRule.items():
            if key != "reverse" and key != "action":
                try:
                    linevalue = mydLine[key]
                except KeyError:
                    raise KeyError('Bad key in rule, not found in instruction line: |%s|' % (key))
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
        
    @abc.abstractmethod
    @ntracef("FILT")
    def fnldReadRules(self, mysRules):
        pass

    @ntracef("FILT")
    def fnSetRules(self,mysRules):
        ldRulesx = self.fnldReadRules(mysRules)
        self.ldRules = ldRulesx
        return self.ldRules


# c l a s s   C I n s t r u c t i o n F i l t e r _ J s o n 
class CInstructionFilter_Json(CInstructionFilter):

    @ntracef("FLTJ") 
    def __init__(self,mysRules): 
        self.ldRules = self.fnSetRules(mysRules)

    @ntracef("FLTJ") 
    def fnldReadRules(self, mysRules):
        try:
            ldRules = json.loads(mysRules)
        except ValueError:
            raise ValueError('Invalid JSON in rule input file.')
        return ldRules


# c l a s s   C I n s t r u c t i o n F i l t e r _ T e x t 
class CInstructionFilter_Text(CInstructionFilter):

    @ntracef("FLTT") 
    def __init__(self,mysRules):
        self.ldRules = self.fnSetRules(mysRules)

    @ntracef("FLTT") 
    def fnldReadRules(self, mysRules):
        
        @ntracef("FLTT") 
        def fndRuleLine2Dict(mysLine):
            oMatch = re.match("(permit|deny)\s+(.+)", mysLine)
            if not oMatch:
                raise ValueError('Ill-formed line in rule input file: |%s|.' % (mysLine))
            sAction = oMatch.group(1)
            dResult = {"action" : sAction}
            sRest = oMatch.group(2)
            lRest = re.split("\s+", sRest)
            for s in lRest:
                oMatch = re.match("(\w+)(=|<|>|<=|>=)(\w+)", s)
                sName, sOper, sVal = oMatch.groups()
                dResult[sName] = "%s%s" % (sOper, sVal)
            return dResult
    
        lRules = mysRules.split("\n")
        lResult = [fndRuleLine2Dict(sLine) for sLine in lRules]
        return lResult


