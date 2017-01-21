#!/usr/bin/python
# test1searchlib.py
# 
# Unit tests for the searchspace.py module, which has many nasty functions.

# Extend the path so that unittest can find modules in the shelf dir.
import sys
sys.path.append('..')


import unittest
from shelf.searchlib import *

class CSearchLibTest(unittest.TestCase):
    
    def setUp(self):
        self.sDbName = "./tmp/testsearchlib.json"
        self.sCollectionName = "done"
        self.sKey = "testcase"
        self.sVal = {"value" : 123}
        result = fnoOpenDb(self.sDbName)

    def tearDown(self):
        import os
        if os.path.isfile(self.sDbName):
            os.remove(self.sDbName)


    def test_open(self):
        result = fnoOpenDb(self.sDbName)
        self.assertTrue(isinstance(result, dict))

    def test_getname(self):
        result = fnsGetFilename()
        self.assertEqual(result, self.sDbName)

    def test_count1(self):  # Does count return an int?
        result = fniCollectionCount(self.sCollectionName)
        self.assertTrue(isinstance(result, int))

    def test_count2(self):  # Does count return zero for empty collection?
        fnvDeleteCollection(self.sCollectionName)
        result = fniCollectionCount(self.sCollectionName)
        self.assertEqual(result, 0)

    def test_insertone(self):   # Insert one item in one collection.
        result = fndInsertOne(self.sCollectionName, self.sKey, self.sVal)
        self.assertTrue(isinstance(result, dict))
        self.assertTrue(self.sKey in result)

    def test_getoneyes(self):  # Insert and retrieve one item in one collection.
        result = fndInsertOne(self.sCollectionName, self.sKey, self.sVal)
        result = fnoGetOne(self.sCollectionName, self.sKey)
        self.assertEqual(result, self.sVal)

    def test_getoneno(self):  # Insert and retrieve one item in one collection.
        result = fndInsertOne(self.sCollectionName, self.sKey, self.sVal)
        result = fnoGetOne(self.sCollectionName, self.sKey+"_NOT_HERE")
        self.assertEqual(result, None)

    def test_count3(self):  # Does count see one item in a collection?
        fnvDeleteCollection(self.sCollectionName)
        result = fndInsertOne(self.sCollectionName, self.sKey, self.sVal)
        result = fniCollectionCount(self.sCollectionName)
        self.assertEqual(result, 1)

    def test_deleteone(self):   # Does deleteone remove item from collection?
        fnvDeleteCollection(self.sCollectionName)
        result = fndInsertOne(self.sCollectionName, self.sKey, self.sVal)
        result = fniCollectionCount(self.sCollectionName)
        self.assertEqual(result, 1)
        result = fndDeleteOne(self.sCollectionName, self.sKey)
        result = fniCollectionCount(self.sCollectionName)
        self.assertEqual(result, 0)

    def test_clear(self):   # Does deletecollection clear all?
        result = fndInsertOne(self.sCollectionName, self.sKey, self.sVal)
        result = fniCollectionCount(self.sCollectionName)
        self.assertGreaterEqual(result, 1)
        fnvDeleteCollection(self.sCollectionName)
        result = fniCollectionCount(self.sCollectionName)
        self.assertEqual(result, 0)



