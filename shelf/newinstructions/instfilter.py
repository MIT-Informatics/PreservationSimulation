#!/usr/bin/python
# instfilter.py
# Functions to filter potential instructions.

import  re
import  json
import  csv
from    NewTraceFac     import  NTRC, ntrace, ntracef
import  abc
from    memoize         import memoize


'''
Problem: the complete cross-product of possible instruction values is too large.
 Many of the combinations are nonsensical.  Let's filter some of them out.  

Dict list external as json or text (see example).

Additional things in the dict beyond attributes:
- action : permit or deny
    no default.
- reverse : true or false
    like grep -v: do the action for whatever doesn't match.
    default = false if absent.
- need wildcard value, e.g., *, to permit any value?  no. 
    just don't mention the condition in dict for that rule.


List of rules, processed all the way to the end
- permit everything (lines all pass by default, rules state exceptions)
- deny some broad stuff
- permit some specifics
- deny
- permit


Syntax rules for rules (ABNF):
- instructionruleline = verb 1*(WSP condition) [CR] LF / commentline
- verb = permit / deny
- condition = fieldname *1(operator)value
            # if no conditional operator present, 
            #  then comparison will be "==" with 
            #  possible integer conversion.
- operator = "=" / "!=" / "<" / "<=" / ">" / ">="
- value = DIGIT *DIGIT / ALPHA *(ALPHA / DIGIT)
- fieldname = ALPHA *(ALPHA / DIGIT)
            # fieldname must appear in the line to be matched, 
            #  that is, it must appear in the header of the 
            #  file of instruction lines.  
- commentline = "#" *(WSP / VCHAR) [CR] LF
- WSP = SP / HTAB
- SP = %x20
- HTAB = %x09
- VCHAR = %x21-7E
            # visible (printing) characters
- CR = %x0D
- LF = %x0A


Examples (but with bad field names):

# Remember: everything permitted by default.
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
                    # Contains an abstract method for subclasses to implement.

    @ntracef("FILT")
    def __init__(self):
        '''Absorb rules json file now, if given.'''
        self.ldRules = []

# f n S a v e H e a d e r L i n e 
    @ntracef("FILT")
    def fnSaveHeaderLine(self, mysLine):
        '''Store header line for all instruction lines.
            Usually comes from the first line of the file.'''
        self.sHeaderLine = mysLine.strip()

# f n d M a k e L i n e D i c t 
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

# f n b D o e s L i n e P a s s A l l R u l e s 
    @ntracef("FILT")
    def fnbDoesLinePassAllRules(self,mydLine):
        bEval = True            # Lines pass by default.
        self.g.nRule = 0
        self.g.nRuleDenyTrue = 0
        self.g.sRuleDenyTrue = ""
        for dRule in self.ldRules:
            # Save rule data for debugging.  
            if self.ID == "text":
                self.g.sRule = self.g.lRules[self.g.nRule]
            else:
                self.g.sRule = str(dRule)   # Best we can do for json.
            self.g.nRule += 1
            # Check line and permit or deny if it matches.
            bMatch = self.fnbDoesLineMatchOneRule(mydLine, dRule)
            if bMatch:
                if dRule['action'] == 'permit':
                    bEval = True
                elif dRule['action'] == 'deny':
                    bEval = False
                    self.g.sRuleDenyTrue = self.g.sRule
                    self.g.nRuleDenyTrue = self.g.nRule
                else:
                    raise ValueError('Invalid rule action: "%s"'%(dRule['action']))
        return bEval

    @ntracef("FILT")
    def fnbDoesLineMatchAllRules(self, mydLine):
        return all([self.fnbDoesLineMatchOneRule(mydLine, dRule) 
            for dRule in self.ldRules])

# f n s G e t V a l u e 
    @ntracef("FILT")
    def fnsGetValue(self,opandval):
        oMatch = re.match(r'[<>!=]+(\S+)', opandval)
        if oMatch:
            return oMatch.groups()[0]
        else:
            return opandval

# f n b D o e s L i n e M a t c h O n e R u l e 
    @ntracef("FILT")
    def fnbDoesLineMatchOneRule(self, mydLine, mydRule):
        for key, val in mydRule.items():
            if key != "reverse" and key != "action":
                try:
                    linevalue = mydLine[key]
                except KeyError:
                    raise KeyError('Bad field name in rule, not found in instruction line: |%s|' % (key))
                # Try to match a single criterion in the rule.
                # Stop on first negative result (implicit and).
                # Action included for debug info.
                sAction = mydRule["action"]
                bResult = self.fnbDoesLineMatchOneCriterion(key, val, linevalue, sAction)
                if not bResult:
                    break

        return bResult if not mydRule.get('reverse', False) else not bResult

    @memoize
    @ntracef("FILT")
    def fnbDoesLineMatchOneCriterion(self, mysRuleKey, mysRuleRight, mysLineVal, mysAction):
        # Get value from rule expression, and its maybe-integer form.
        sRuleValue = self.fnsGetValue(mysRuleRight)
        sRuleValueInt = fnIntPlease(sRuleValue)
        sLineValueInt = fnIntPlease(mysLineVal)

        if str(mysRuleRight).startswith('='):
            bResult = sLineValueInt == sRuleValueInt
        elif str(mysRuleRight).startswith('>='):
            bResult = int(mysLineVal) >= int(sRuleValue)
        elif str(mysRuleRight).startswith('<='):
            bResult = int(mysLineVal) <= int(sRuleValue)
        elif str(mysRuleRight).startswith('>'):
            bResult = int(mysLineVal) > int(sRuleValue)
        elif str(mysRuleRight).startswith('<'):
            bResult = int(mysLineVal) < int(sRuleValue)
        elif str(mysRuleRight).startswith('!='):
            bResult = sLineValueInt != sRuleValueInt
        else:
            bResult = sLineValueInt == fnIntPlease(mysRuleRight)

        if not bResult:
            NTRC.tracef(2,"FILT","proc FailCriterion rule|%s%s| val|%s| action|%s|" 
                % (mysRuleKey, mysRuleRight, mysLineVal, mysAction))

        return bResult

# f n l d R e a d R u l e s  ( a b s t r a c t  m e t h o d )
    @abc.abstractmethod
    @ntracef("FILT")
    def fnldReadRules(self, mysRules):
        pass

# f n S e t R u l e s 
    @ntracef("FILT")
    def fnSetRules(self,mysRules):
        ''' Calls the (abstract) ReadRules routine to parse file.'''
        ldRulesx = self.fnldReadRules(mysRules)
        self.ldRules = ldRulesx
        return self.ldRules


# f n I n t P l e a s e 
def fnIntPlease(value):
    try:
        result = int(value)
    except ValueError:
        result = value
    return result


# c l a s s   C I n s t r u c t i o n F i l t e r _ J s o n 
class CInstructionFilter_Json(CInstructionFilter):
    '''\
    Read rule list from JSON input.
     Just read and store.
    '''
    ID = "json"

    @ntracef("FLTJ") 
    def __init__(self, mysRules, myGlob): 
        self.g = myGlob
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
    '''\
    Carefully read and compile rules in text form to make suitable
     dictionary for processing.
    '''
    ID = "text"

    @ntracef("FLTT") 
    def __init__(self, mysRules, myGlob):
        self.g = myGlob
        self.ldRules = self.fnSetRules(mysRules)

    @ntracef("FLTT") 
    def fnldReadRules(self, mysRules):
        
        @ntracef("FLTT") 
        def fndRuleLine2Dict(mysLine):
            sLine = mysLine.strip()
            self.g.lRules.append(sLine)
            oMatch = re.match("(permit|deny)\s+(.+)", sLine)
            if not oMatch:
                raise ValueError('Ill-formed line in rule input file: |%s|.' % (mysLine))
            sAction, sRest = oMatch.groups()
            dResult = {"action" : sAction}
            lRest = sRest.split()
            for sWord in lRest:
                oMatch = re.match("(\w+)(=|<|>|<=|>=|!=)(\w+)", sWord)
                if not oMatch:
                    raise ValueError('Ill-formed condition in rule input line: |%s|' % sWord)
                sName, sOper, sVal = oMatch.groups()
                dResult[sName] = "%s%s" % (sOper, sVal)
            return dResult
    
        lRules = mysRules.split("\n")
        lResult = [fndRuleLine2Dict(sLine) for sLine in lRules]
        return lResult


#END
