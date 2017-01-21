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

    @ntracef("SRDB")
    def __init__(self,mysDatabaseName, mysProgressCollectionName, 
                mysDoneCollectionName):
        self.sDbName = mysDatabaseName
        self.sProgressName = mysProgressCollectionName
        self.sDoneName = mysDoneCollectionName
        self.oDb = searchlib.fnoOpenDb(self.sDbName)

    @ntracef("SRDB")
    def fnitGetInstructionIterator(self, mydQuery):
        raise NotImplementedError
        pass

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


############### leftovers from mongo ###################
"""
    @ntracef("DB")
    def __init__(self,mysDatabaseName, mysPendingCollectionName, mysDoneCollectionName):
        self.ID = mysDatabaseName
        self.oDb = mongolib.fnoOpenDb(mysDatabaseName)
        self.oPendingCollection = self.oDb[mysPendingCollectionName]
        self.oDoneCollection = self.oDb[mysDoneCollectionName]
        nPendingCount = self.oPendingCollection.count()
        NTRC.ntracef(0,"DB","proc main pending nRecs|{}|".format(nPendingCount))

    @catchex
    @ntracef("DB")
    def fnitGetInstructionIterator(self,mydQuery):
        '''
        Query pending instructions to get subset of work for today.
        '''
        itCurrentSet = self.oPendingCollection.find(mydQuery)
        '''
        MongoDB tends to time out cursors if they are kept too long.  
         Max number of runs we get is just over 100 before the timeout.  
        Don't want to disable the timeout completely, so collect the entire
         instruction stream into a list up front.  Icky.  Try to be a good
         citizen and what does it get you.  Try to keep the instruction set
         reasonable size, like under a million.  
        '''
        ldAllInstructions = list(itCurrentSet)
        NTRC.ntracef(0,"DB","proc main nInstructionsqueried|{}|".format(len(ldAllInstructions)))
        return ldAllInstructions

    @catchex
    @ntracef("DB")
    def fnbIsItDone(self,mysInstructionId):
        '''
        Does this sDoneId(=mongoid) value already appear in the done collection?
        '''
        dIsItDone = { "sDoneId" : mysInstructionId }
        lMaybeDone = list(self.oDoneCollection.find(dIsItDone))
        NTRC.ntracef(3,"DB","proc check donelist id|%s| list|%s|" % (mysInstructionId, lMaybeDone))
        return len(lMaybeDone) > 0

    @catchex
    @ntracef("DB")
    def fnbDeleteDoneRecord(self,mysInstructionId):
        dIsItDone = { "sDoneId" : mysInstructionId }
        result = self.oDoneCollection.remove(dIsItDone)
        NTRC.ntracef(3,"DB","proc DeleteDone result|%s|" % (result))
        return result["ok"] != 0



#=================================================
# c l a s s   C D a t a b a s e 
class CDatabase(object):
    '''
    Isolate all the Mongo-specific stuff here.  
    '''
    @ntracef("DB")
    def __init__(self,mysDatabaseName, mysPendingCollectionName, mysDoneCollectionName):
        self.ID = mysDatabaseName
        self.oDb = mongolib.fnoOpenDb(mysDatabaseName)
        self.oPendingCollection = self.oDb[mysPendingCollectionName]
        self.oDoneCollection = self.oDb[mysDoneCollectionName]
        nPendingCount = self.oPendingCollection.count()
        NTRC.ntracef(0,"DB","proc main pending nRecs|{}|".format(nPendingCount))

    @catchex
    @ntracef("DB")
    def fnitGetInstructionIterator(self,mydQuery):
        '''
        Query pending instructions to get subset of work for today.
        '''
        itCurrentSet = self.oPendingCollection.find(mydQuery)
        '''
        MongoDB tends to time out cursors if they are kept too long.  
         Max number of runs we get is just over 100 before the timeout.  
        Don't want to disable the timeout completely, so collect the entire
         instruction stream into a list up front.  Icky.  Try to be a good
         citizen and what does it get you.  Try to keep the instruction set
         reasonable size, like under a million.  
        '''
        ldAllInstructions = list(itCurrentSet)
        NTRC.ntracef(0,"DB","proc main nInstructionsqueried|{}|".format(len(ldAllInstructions)))
        return ldAllInstructions

    @catchex
    @ntracef("DB")
    def fnbIsItDone(self,mysInstructionId):
        '''
        Does this sDoneId(=mongoid) value already appear in the done collection?
        '''
        dIsItDone = { "sDoneId" : mysInstructionId }
        lMaybeDone = list(self.oDoneCollection.find(dIsItDone))
        NTRC.ntracef(3,"DB","proc check donelist id|%s| list|%s|" % (mysInstructionId, lMaybeDone))
        return len(lMaybeDone) > 0

    @catchex
    @ntracef("DB")
    def fnbDeleteDoneRecord(self,mysInstructionId):
        dIsItDone = { "sDoneId" : mysInstructionId }
        result = self.oDoneCollection.remove(dIsItDone)
        NTRC.ntracef(3,"DB","proc DeleteDone result|%s|" % (result))
        return result["ok"] != 0

"""

# Edit history:
# 20170120  RBL Original version.  
# 
# 
