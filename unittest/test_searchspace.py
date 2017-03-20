#!/usr/bin/python
# test1searchspace.py
# 
# Unit tests for the searchspace.py module, which has many nasty functions.

# Extend the path so that unittest can find modules in the shelf dir.
import sys
sys.path.append('..')


import unittest
from shelf.searchspace import *
from NewTraceFac import NTRC, ntrace, ntracef

class CSearchSpaceTest(unittest.TestCase):
    sInsTestDir = "./ins"
    
    @ntracef("TSRS")
    def setUp(self):
        self.ddd = fndReadAllInsFiles(self.sInsTestDir, ".ins3")

    @ntracef("TSRS")
    def test_getonefile(self):
        ''' Read a single file and check value. '''
        with self.assertRaises(NotImplementedError):
            (sName, lValues) = fntReadOneFile(self.sInsTestDir+'/'+"docsize.ins3")
            self.assertEqual("nDocSize", sName)
            self.assertIn(50, lValues)
    
    @ntracef("TSRS")
    def test_getfiles(self):
        ''' Do we get the right number of files? '''
        # BEWARE the number in here if we add any new param dimensions.  
        # Maybe glob and count would be safer.
        self.assertEqual(len([k for k,v in self.ddd.items()]), 19)

    @ntracef("TSRS")
    def test_matchone(self):
        ''' Match leaves string as is. '''
        foo = fndProcessOneUserRule(self.ddd, "nShelfSize", '1')
        self.assertEqual(foo["nShelfSize"], [1])

    @ntracef("TSRS")
    def test_matchonebad(self):
        ''' Mismatch removes values from list. '''
        foo = fndProcessOneUserRule(self.ddd, "nShelfSize", '1000')
        self.assertEqual(foo["nShelfSize"], [])

    @ntracef("TSRS")
    def test_dictset(self):
        ''' Does set extract multiple values from list? '''
        foo = fndProcessOneUserRule(self.ddd, "nShockSpan", '[2,3,4]')
        self.assertEqual(foo["nShockSpan"], [2,3])

    @ntracef("TSRS")
    def test_dicteq(self):
        ''' Test all the dictionary rules, one by one. '''
        foo = fndProcessOneUserRule(self.ddd, "nShelfSize", '{"$eq":1}')
        self.assertEqual(foo["nShelfSize"], [1])

    @ntracef("TSRS")
    def test_dictne(self):
        foo = fndProcessOneUserRule(self.ddd, "nShelfSize", '{"$ne":1111}')
        self.assertEqual(foo["nShelfSize"], [1])

    @ntracef("TSRS")
    def test_dictlt(self):
        foo = fndProcessOneUserRule(self.ddd, "nCopies", '{"$lt":9}')
        self.assertEqual(foo["nCopies"], [1,2,3,4,5,8])

    @ntracef("TSRS")
    def test_dictgt(self):
        foo = fndProcessOneUserRule(self.ddd, "nAuditSegments", '{"$gt":1}')
        self.assertEqual(foo["nAuditSegments"], [2,4])

    @ntracef("TSRS")
    def test_dictlte(self):
        foo = fndProcessOneUserRule(self.ddd, "nCopies", '{"$lte":9}')
        self.assertEqual(foo["nCopies"], [1,2,3,4,5,8])

    @ntracef("TSRS")
    def test_dictgte(self):
        foo = fndProcessOneUserRule(self.ddd, "nAuditSegments", '{"$gte":2}')
        self.assertEqual(foo["nAuditSegments"], [2,4])

    @ntracef("TSRS")
    def test_dictbetween(self):
        ''' Test two rules in one dict, as often done for range selection. '''
        foo = fndProcessOneUserRule(self.ddd, "nCopies", '{"$gte":2,"$lte":9}')
        self.assertEqual(foo["nCopies"], [2,3,4,5,8])

    @ntracef("TSRS")
    def test_userruledict(self):
        ''' Test entire rule dict. '''
        rules = {
                "nCopies" : '{"$gte":2,"$lte":9}'
                ,"nAuditSegments" : '{"$gte":2}'
                ,"nShockSpan" : '[2,3,4]'
                ,"nShelfSize" : '1'
                ,"nGlitchDecay" : '{"$ne":0}'
                }
        (foo, originaldict) = fntProcessAllUserRules(rules, self.ddd)
        # Is the original dict returned the same as before?
        diffs = [(name,val) for (name,val) in originaldict.items()
                if name not in self.ddd or self.ddd[name] != val ]
        self.assertEqual(diffs, [])
        # Check that this weird method of comparing dictionaries actually works.
        with self.assertRaises(AssertionError):
            originaldict["sAuditType"] = ["deliberately changed for testing"]
            diffs = [(name,val) for (name,val) in originaldict.items()
                    if name not in self.ddd or self.ddd[name] != val ]
            self.assertEqual(diffs, [])
        # Check that the rules worked.
        self.assertEqual(foo["nCopies"], [2,3,4,5,8])
        self.assertEqual(foo["nAuditSegments"], [2,4])
        self.assertEqual(foo["nShockSpan"], [2,3])
        self.assertEqual(foo["nShelfSize"], [1])
        self.assertEqual(foo["nGlitchDecay"], [200,1000])

    @ntracef("TSRS")
    def test_filterglitch(self):
        ''' Test the filters,one by one. '''
        self.ddd["nGlitchFreq"] = [0]
        foo = fndFilterResults(self.ddd)
        self.assertEqual(len(foo["nGlitchSpan"]), 1)
        self.assertEqual(len(foo["nGlitchImpact"]), 1)
        self.assertEqual(len(foo["nGlitchDecay"]), 1)
        self.assertEqual(len(foo["nGlitchMaxlife"]), 1)
        self.assertEqual(len(foo["nGlitchIgnorelevel"]), 1)

    @ntracef("TSRS")
    def test_filterserverdefaultlife(self):
        self.ddd["nServerDefaultLife"] = [0]
        foo = fndFilterResults(self.ddd)
        self.assertEqual(foo["nShockFreq"], [0])

    @ntracef("TSRS")
    def test_filtershock(self):
        self.ddd["nShockFreq"] = [0]
        foo = fndFilterResults(self.ddd)
        self.assertEqual(len(foo["nShockSpan"]), 1)
        self.assertEqual(len(foo["nShockImpact"]), 1)
        self.assertEqual(len(foo["nShockMaxlife"]), 1)

    @ntracef("TSRS")
    def test_filteraudit(self):
        self.ddd["nAuditFreq"] = [0]
        foo = fndFilterResults(self.ddd)
        self.assertEqual(len(foo["nAuditSegments"]), 1)
        self.assertEqual(foo["sAuditType"], ["TOTAL"])

    @ntracef("TSRS")
    def test_emptylistreport(self):
        ''' Test if empty lists get reported properly.  '''
        dNew = copy.deepcopy(self.ddd)
        dNew["nCopies"] = []
        with self.assertRaises(ValueError):
            fnvTestResults(dNew, self.ddd)

    @ntracef("TSRS")
    def test_getnames(self):
        ''' Get list of field names. Right length? '''
        rules = {
                "nCopies" : '1'
                ,"nLifem" : '1000'
                ,"nServerDefaultLife" : '0'
                ,"nAuditFreq" : '0'
                ,"nShockFreq" : '0'
                ,"nGlitchFreq" : '0'
                }
        (foo, originaldict) = fntProcessAllUserRules(rules, self.ddd)
        foo = fndFilterResults(foo)
        fnvTestResults(foo, self.ddd)
        lNames = fnlGetSearchSpaceNames(foo)
        self.assertEqual(len(lNames), 23)

    @ntracef("TSRS")
    def test_combine(self):
        ''' Test the minimal instruction. Do we get just one? '''
        rules = {
                "nCopies" : '1'
                ,"nLifem" : '1000'
                ,"nServerDefaultLife" : '0'
                ,"nAuditFreq" : '0'
                ,"nShockFreq" : '0'
                ,"nGlitchFreq" : '0'
                }
        (foo, originaldict) = fntProcessAllUserRules(rules, self.ddd)
        foo = fndFilterResults(foo)
        fnvTestResults(foo, self.ddd)
        lInstructions = [lInstruction for lInstruction 
                        in fndgCombineResults(foo)]
        self.assertEqual(len(lInstructions), 1)

    @ntracef("TSRS")
    def test_getallone(self):
        ''' Test the overall entry point with minimal instruction. '''
        rules = {
                "nCopies" : '1'
                ,"nLifem" : '1000'
                ,"nServerDefaultLife" : '0'
                ,"nAuditFreq" : '0'
                ,"nShockFreq" : '0'
                ,"nGlitchFreq" : '0'
                }
        lInstructions = [lInstruction for lInstruction in 
                        fndgGetSearchSpace("./ins", ".ins3", rules)]
        self.assertEqual(len(lInstructions), 1)

    @ntracef("TSRS")
    def test_getallseveral(self):
        ''' Test the overall entry point with a simple set of instructions. '''
        rules = {
                "nCopies" : '{"$gte":1, "$lte":5}'
                ,"nLifem" : '1000'
                ,"nServerDefaultLife" : '0'
                ,"nAuditFreq" : '0'
                ,"nShockFreq" : '0'
                ,"nGlitchFreq" : '0'
                }
        lInstructions = [lInstruction for lInstruction in 
                        fndgGetSearchSpace("./ins", ".ins3", rules)]
        self.assertEqual(len(lInstructions), 5)
        self.assertEqual(len(lInstructions[0]), 24)


