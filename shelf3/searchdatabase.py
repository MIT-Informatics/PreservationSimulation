#!/usr/bin/python
# searchdatabase.py
# 
# 

from __future__ import absolute_import
#!/usr/bin/python
# searchdatabase.py
# 
# 

from . import searchlib
from .NewTraceFac import NTRC, ntrace, ntracef


#=================================================
# c l a s s   C S e a r c h D a t a b a s e 
class CSearchDatabase(object):
    pass

    @ntracef("SRDB")
    def __init__(self,mysDatabaseName, mysProgressCollectionName, 
                mysDoneCollectionName):
        self.sDbName = mysDatabaseName
        self.sProgressName = mysProgressCollectionName
        self.sDoneName = mysDoneCollectionName
        self.oDb = searchlib.fnoOpenDb(self.sDbName)

    @ntracef("SRDB")
    def fnbIsItDone(self, mysInstructionId):
        result = searchlib.fnoGetOne(self.sDoneName, mysInstructionId)
        return (result is not None)

    @ntracef("SRDB")
    def fndInsertDoneRecord(self, mysInstructionId, mysOtherInfo):
        dCollection = searchlib.fndInsertOne(self.sDoneName, 
                        mysInstructionId, mysOtherInfo)
        return dCollection

    @ntracef("SRDB")
    def fndDeleteDoneRecord(self, mysInstructionId):
        dCollection = searchlib.fndDeleteOne(self.sDoneName, mysInstructionId)
        return dCollection

    @ntracef("SRDB")
    def fnvDeleteDoneCollection(self):
        dCollection = searchlib.fnvDeleteCollection(self.sDoneName)
        return

    @ntracef("SRDB")
    def fndInsertProgressRecord(self, mysInstructionId, mysOtherInfo):
        dCollection = searchlib.fndInsertOne(self.sProgressName, 
                        mysInstructionId, mysOtherInfo)
        return dCollection

    @ntracef("SRDB")
    def fndDeleteProgressRecord(self, mysInstructionId):
        dCollection = searchlib.fndDeleteOne(self.sProgressName, 
                        mysInstructionId)
        return dCollection

    @ntracef("SRDB")
    def fnvDeleteProgressCollection(self):
        dCollection = searchlib.fnvDeleteCollection(self.sProgressName)
        return

    @ntracef("SRDB")
    def fniCountCollection(self, mysCollectionName):
        nResult = searchlib.fniCollectionCount(mysCollectionName)
        return nResult


# Edit history:
# 20170120  RBL Original version.  
# 
# 
