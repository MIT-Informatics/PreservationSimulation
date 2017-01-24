#!/usr/bin/python
# searchdatabase.py
# 
# 

import searchlib
from NewTraceFac import NTRC, ntrace, ntracef


#=================================================
# c l a s s   C S e a r c h D a t a b a s e 
class CSearchDatabase(object):
    pass

    @ntracef("SRDM")
    def __init__(self,mysDatabaseName, mysProgressCollectionName, 
                mysDoneCollectionName):
        self.sDbName = mysDatabaseName
        self.sProgressName = mysProgressCollectionName
        self.sDoneName = mysDoneCollectionName
        self.oDb = searchlib.fnoOpenDb(self.sDbName)

    @ntracef("SRDM")
    def fnbIsItDone(self, mysInstructionId):
        result = searchlib.fnoGetOne(self.sDoneName, mysInstructionId)
        return (result is not None)

    @ntracef("SRDM")
    def fndInsertDoneRecord(self, mysInstructionId, mysOtherInfo):
        dCollection = searchlib.fndInsertOne(self.sDoneName, 
                        mysInstructionId, mysOtherInfo)
        return dCollection

    @ntracef("SRDM")
    def fndDeleteDoneRecord(self, mysInstructionId):
        dCollection = searchlib.fndDeleteOne(self.sDoneName, mysInstructionId)
        return dCollection

    @ntracef("SRDM")
    def fnvDeleteDoneCollection(self):
        dCollection = searchlib.fnvDeleteCollection(self.sDoneName)
        return

    @ntracef("SRDM")
    def fndInsertProgressRecord(self, mysInstructionId, mysOtherInfo):
        dCollection = searchlib.fndInsertOne(self.sProgressName, 
                        mysInstructionId, mysOtherInfo)
        return dCollection

    @ntracef("SRDM")
    def fndDeleteProgressRecord(self, mysInstructionId):
        dCollection = searchlib.fndDeleteOne(self.sProgressName, 
                        mysInstructionId)
        return dCollection

    @ntracef("SRDM")
    def fnvDeleteProgressCollection(self):
        dCollection = searchlib.fnvDeleteCollection(self.sProgressName)
        return

    @ntracef("SRDM")
    def fniCountCollection(self, mysCollectionName):
        nResult = searchlib.fniCollectionCount(mysCollectionName)
        return nResult


# Edit history:
# 20170120  RBL Original version.  
# 
# 
