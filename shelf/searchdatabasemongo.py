#!/usr/bin/python
# searchdatabasemongo.py
# 
# Database functions for shelf's use of MongoDB.

import mongolib
from NewTraceFac import NTRC, ntrace, ntracef
from pymongo import MongoClient


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
        self.oDb = self.fnoOpenDb(self.sDbName)
        self.oDoneCollection = self.oDb[mysDoneCollectionName]
        self.oProgressCollection = self.oDb[mysProgressCollectionName]

# f n o O p e n D b 
    @ntracef("SRDM")
    def fnoOpenDb(self, mysDbName):
        client = MongoClient('localhost', 27017)
        db = client.__getattr__(mysDbName)
        NTRC.ntracef(3, "SRDM", "Connected to db.")
        return db

# f n b I s I t D o n e 
    @ntracef("SRDM")
    def fnbIsItDone(self, mysInstructionId):
        dIsItDone = { "sDoneId" : mysInstructionId }
        dMaybeDone = self.oDoneCollection.find_one(dIsItDone)
        NTRC.ntracef(3,"DB","proc check donelist id|%s| list|%s|" 
            % (mysInstructionId, dMaybeDone))
        return isinstance(dMaybeDone, dict) # None if not found.

# f n d I n s e r t D o n e R e c o r d 
    @ntracef("SRDM")
    def fndInsertDoneRecord(self, mysInstructionId, mysOtherInfo):
        dValues = { "sDoneId" : mysInstructionId, "info" : mysOtherInfo }    
        self.oDoneCollection.insert_one(dValues)
        return self.oDoneCollection.count()

# f n d D e l e t e D o n e R e c o r d 
    @ntracef("SRDM")
    def fndDeleteDoneRecord(self, mysInstructionId):
        dIsItDone = { "sDoneId" : mysInstructionId }
        result = self.oDoneCollection.remove(dIsItDone)
        NTRC.ntracef(3,"DB","proc DeleteDone result|%s|" % (result))
        return result["ok"] != 0

# f n v D e l e t e D o n e C o l l e c t i o n 
    @ntracef("SRDM")
    def fnvDeleteDoneCollection(self):
        self.oDb[self.sDoneName].remove()
        return

# f n d I n s e r t P r o g r e s s R e c o r d 
    @ntracef("SRDM")
    def fndInsertProgressRecord(self, mysInstructionId, mysOtherInfo):
        dValues = { "sProgressId" : mysInstructionId, "info" : mysOtherInfo }    
        self.oProgressCollection.insert_one(dValues)
        return self.oProgressCollection.count()

# f n d D e l e t e P r o g r e s s R e c o r d 
    @ntracef("SRDM")
    def fndDeleteProgressRecord(self, mysInstructionId):
        dIsItThere = { "sProgressId" : mysInstructionId }
        result = self.oProgressCollection.remove(dIsItThere)
        NTRC.ntracef(3,"DB","proc DeleteProgress result|%s|" % (result))
        return result["ok"] != 0

# f n v D e l e t e P r o g r e s s C o l l e c t i o n 
    @ntracef("SRDM")
    def fnvDeleteProgressCollection(self):
        self.oDb[self.sProgressName].remove()
        return

# f n i C o u n t C o l l e c t i o n 
    @ntracef("SRDM")
    def fniCountCollection(self, mysCollectionName):
        nResult = self.oDb[mysCollectionName].count()
        return nResult


# Edit history:
# 20170124  RBL Original version cribbed from the CSearchDatabase and mongolib.
# 20170126  RBL Finally works with its unittest.  Does NOT use searchlibmongo; 
#                goes directly to mongolib.
# 
# 
