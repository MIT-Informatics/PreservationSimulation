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
        self.sPendingCollectionName = "pending"
        self.sDoneCollectionName = "done"
        self.sKey = "testcase"
        self.sVal = {"value" : 123}
        self.oDb = CSearchDatabase(self.sDbName, self.sPendingCollectionName, 
                    self.sDoneCollectionName)

    def tearDown(self):
        pass


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
        result = self.oDb.fndInsertDoneRecord(self.sKey, self.sVal)
        pass
    
    @ntracef("TSRD")
    def test_count(self):
        result = self.oDb.fndInsertDoneRecord(self.sKey, self.sVal)
        result = self.oDb.fniCountCollection(self.sDoneCollectionName)
        self.assertEqual(result, 1)
    


