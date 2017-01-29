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
                mysDoneCollectionName, 
                mysMongoSystem="localhost", mynMongoPort=27017):
        self.sDbName = mysDatabaseName
        self.sProgressName = mysProgressCollectionName
        self.sDoneName = mysDoneCollectionName
        self.sMongoSystem = mysMongoSystem
        self.nMongoPort = mynMongoPort
        # Open the db and get important collection pointers.
        self.oDb = self._fnoOpenDb(self.sDbName)
        self.oDoneCollection = self.oDb[mysDoneCollectionName]
        self.oProgressCollection = self.oDb[mysProgressCollectionName]

# f n o O p e n D b 
    @ntracef("SRDM")
    def _fnoOpenDb(self, mysDbName):
        client = MongoClient(self.sMongoSystem, self.nMongoPort)
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

# f n v D e l e t e C o l l e c t i o n 
    @ntracef("SRDM")
    def fnvDeleteCollection(self, mysCollectionName):
        self.oDb[mysCollectionName].remove()
        return

# f n v D e l e t e D o n e C o l l e c t i o n 
    @ntracef("SRDM")
    def fnvDeleteDoneCollection(self):
        self.fnvDeleteCollection(self.sDoneName)
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
        self.fnvDeleteCollection(self.sProgressName)
        return

# f n i C o u n t C o l l e c t i o n 
    @ntracef("SRDM")
    def fniCountCollection(self, mysCollectionName):
        nResult = self.oDb[mysCollectionName].count()
        return nResult

# f n l G e t C o l l e c t i o n 
    @ntracef("SRDM")
    def fnlGetCollection(self, mysCollectionName):
        oCollection = self.oDb[mysCollectionName]
        oCursor = oCollection.find()
        lOut = list()
        for record in oCursor:
            lOut.append(record)
        return lOut

# f n l G e t D o n e C o l l e c t i o n 
    @ntracef("SRDM")
    def fnlGetDoneCollection(self):
        return self.fnlGetCollection(self.sDoneName)

# f n l G e t P r o g r e s s C o l l e c t i o n 
    @ntracef("SRDM")
    def fnlGetProgressCollection(self):
        return self.fnlGetCollection(self.sProgressName)


# Edit history:
# 20170124  RBL Original version cribbed from the CSearchDatabase and mongolib.
# 20170126  RBL Finally works with its unittest.  Does NOT use searchlibmongo; 
#                goes directly to mongolib.
# 20170128  RBL Add GetCollection, GetDoneCollection, GetProgressCollection.
# 
# 

#END
