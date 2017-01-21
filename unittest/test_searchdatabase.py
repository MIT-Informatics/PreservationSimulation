#!/usr/bin/python
# test1searchdatabase.py
# 
# Unit tests for the searchdatabase.py module, which has many nasty functions.

# Extend the path so that unittest can find modules in the shelf dir.
import sys
sys.path.append('..')


import unittest
from shelf.searchdatabase import *

class CSearchDatabaseTest(unittest.TestCase):
    
    def setUp(self):
        self.sDbName = "./tmp/testsearchlib.json"
        self.sProgressCollectionName = "progress"
        self.sDoneCollectionName = "done"
        self.sKey = "testcase"
        self.sVal = {"value" : 123}
        self.oDb = CSearchDatabase(self.sDbName, self.sProgressCollectionName, 
                    self.sDoneCollectionName)

    def tearDown(self):
        pass


    @ntracef("TSRD")
    def test_deletealldone(self):
        self.oDb.fnvDeleteDoneCollection()
        result = self.oDb.fniCountCollection(self.sDoneCollectionName)
        self.assertEqual(result, 0)

    @ntracef("TSRD")
    def test_insertdone(self):
        result = self.oDb.fndInsertDoneRecord(self.sKey, self.sVal)
        self.assertTrue(isinstance(result,dict))
        self.assertTrue(self.sKey in result.keys())
        self.assertTrue(self.sVal in result.values())

    @ntracef("TSRD")
    def test_isitdoneno1(self):
        self.oDb.fnvDeleteDoneCollection()
        result = self.oDb.fnbIsItDone(self.sKey)
        self.assertFalse(result)

    @ntracef("TSRD")
    def test_isitdoneno2(self):
        result = self.oDb.fndInsertDoneRecord(self.sKey, self.sVal)
        result = self.oDb.fnbIsItDone(self.sKey+"_NOT_HERE")
        self.assertFalse(result)
    
    @ntracef("TSRD")
    def test_isitdoneno3(self):
        result = self.oDb.fndInsertDoneRecord(self.sKey, self.sVal)
        result = self.oDb.fnbIsItDone(self.sKey)
        self.assertTrue(result)
    
    @ntracef("TSRD")
    def test_deletedone(self):
        result = self.oDb.fniCountCollection(self.sDoneCollectionName)
        nCountBefore = result
        result = self.oDb.fndInsertDoneRecord(self.sKey, self.sVal)
        result = self.oDb.fndDeleteDoneRecord(self.sKey)
        self.assertTrue(isinstance(result, dict))
        result = self.oDb.fniCountCollection(self.sDoneCollectionName)
        nCountAfter = result
        self.assertEqual(nCountAfter, 0)

    @ntracef("TSRD")
    def test_count(self):
        result = self.oDb.fndInsertDoneRecord(self.sKey, self.sVal)
        result = self.oDb.fniCountCollection(self.sDoneCollectionName)
        self.assertEqual(result, 1)
    
    @ntracef("TSRD")
    def test_deleteallprogress(self):
        self.oDb.fnvDeleteProgressCollection()
        result = self.oDb.fniCountCollection(self.sProgressCollectionName)
        self.assertEqual(result, 0)

    @ntracef("TSRD")
    def test_insertprogress(self):
        result = self.oDb.fndInsertProgressRecord(self.sKey, self.sVal)
        self.assertTrue(isinstance(result,dict))
        self.assertTrue(self.sKey in result.keys())
        self.assertTrue(self.sVal in result.values())

    def test_deleteprogress(self):
        result = self.oDb.fniCountCollection(self.sProgressCollectionName)
        nCountBefore = result
        result = self.oDb.fndInsertProgressRecord(self.sKey, self.sVal)
        result = self.oDb.fndDeleteProgressRecord(self.sKey)
        self.assertTrue(isinstance(result, dict))
        result = self.oDb.fniCountCollection(self.sProgressCollectionName)
        nCountAfter = result
        self.assertEqual(nCountAfter, 0)

# Edit history:
# 20170120  RBL Original version.
# 
# 



#END
