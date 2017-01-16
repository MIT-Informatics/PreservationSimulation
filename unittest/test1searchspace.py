import sys
sys.path.append('..')

import unittest
from shelf.searchspace import *

class CSearchSpaceTest(unittest.TestCase):
    sInsTestDir = "./ins"
    
    def setUp(self):
        self.ddd = fndReadAllInsFiles(self.sInsTestDir, ".ins")

    def test_getonefile(self):
        (sName, lValues) = fntReadOneFile(self.sInsTestDir+'/'+"docsize.ins")
        self.assertEqual("nDocSize", sName)
        self.assertIn(50, lValues)
    
    def test_getfiles(self):
        self.assertEqual(len([k for k,v in self.ddd.items()]), 19)

    def test_matchone(self):
        foo = fndProcessOneUserRule(self.ddd, "nShelfSize", '1')
        self.assertEqual(foo["nShelfSize"], [1])

    def test_matchonebad(self):
        foo = fndProcessOneUserRule(self.ddd, "nShelfSize", '1000')
        self.assertEqual(foo["nShelfSize"], [])

    def test_dicteq(self):
        foo = fndProcessOneUserRule(self.ddd, "nShelfSize", '{"$eq":1}')
        self.assertEqual(foo["nShelfSize"], [1])

    def test_dictne(self):
        foo = fndProcessOneUserRule(self.ddd, "nShelfSize", '{"$ne":1111}')
        self.assertEqual(foo["nShelfSize"], [1])

    def test_dictset(self):
        foo = fndProcessOneUserRule(self.ddd, "nShockSpan", '[2,3,4]')
        self.assertEqual(foo["nShockSpan"], [2,3])

    def test_dictlt(self):
        foo = fndProcessOneUserRule(self.ddd, "nCopies", '{"$lt":9}')
        self.assertEqual(foo["nCopies"], [1,2,3,4,5,8])

    def test_dictgt(self):
        foo = fndProcessOneUserRule(self.ddd, "nAuditSegments", '{"$gt":1}')
        self.assertEqual(foo["nAuditSegments"], [2,4])

    def test_dictlte(self):
        foo = fndProcessOneUserRule(self.ddd, "nCopies", '{"$lte":9}')
        self.assertEqual(foo["nCopies"], [1,2,3,4,5,8])

    def test_dictgte(self):
        foo = fndProcessOneUserRule(self.ddd, "nAuditSegments", '{"$gte":2}')
        self.assertEqual(foo["nAuditSegments"], [2,4])

    def test_dictbetween(self):
        foo = fndProcessOneUserRule(self.ddd, "nCopies", '{"$gte":2,"$lte":9}')
        self.assertEqual(foo["nCopies"], [2,3,4,5,8])

    def test_userruledict(self):
        rules = {
                "nCopies" : '{"$gte":2,"$lte":9}'
                ,"nAuditSegments" : '{"$gte":2}'
                ,"nShockSpan" : '[2,3,4]'
                ,"nShelfSize" : '1'
                ,"nGlitchDecay" : '{"$ne":0}'
                }
        (foo, originaldict) = fntProcessAllUserRules(rules, self.ddd)
        diffs = [(name,val) for (name,val) in originaldict.items()
                if name not in self.ddd or self.ddd[name] != val ]
        self.assertEqual(diffs, [])
        self.assertEqual(foo["nCopies"], [2,3,4,5,8])
        self.assertEqual(foo["nAuditSegments"], [2,4])
        self.assertEqual(foo["nShockSpan"], [2,3])
        self.assertEqual(foo["nShelfSize"], [1])
        self.assertEqual(foo["nGlitchDecay"], [300])



