#!/usr/bin/python

import simpy
from NewTraceFac07 import TRC,trace,tracef
import itertools
from server import *
from globaldata import *


# D O C U M E N T 
#----------------

class CDocument(object):
    getID = itertools.count(0).next

    @tracef("DOC")
    def __init__(self,size):
        self.ID = "D" + str(self.getID())
        G.dID2Document[self.ID] = self
        G.nDocLastID = self.ID
        self.nSize = size
        TRC.tracef(3,"DOC","proc init created doc|%s| size|%d|" % (self.ID,self.nSize))
        self.sLibID = None
        self.sShelfID = None
        self.nBlkBegin = None
        self.nBlkEnd = None
        self.lCopies = list()

    def mAudit(self):
        pass

# C O L L E C T I O N 
#--------------------

class CCollection(object):
    getID = itertools.count().next

    @tracef("COLL")
    def __init__(self,mysName,mynValue,mynSize):
        self.ID = "C" + str(self.getID())
        G.dID2Collection[self.ID] = self
        G.nCollLastID = self.ID
        self.sName = mysName
        self.nValue = mynValue
        self.lDocuments = list()
        self.lLibraries = list()
        # Create all booksin the collection.
        self.mMakeBooks(mynSize)

# C o l l e c t i o n . m M a k e B o o k s 
    @tracef("COLL")
    def mMakeBooks(self,nbooks):
        # A collection has lots of books
        nrandbooks = int(makennnorm(int(nbooks)))
        for icoll in xrange(nrandbooks):
            # T E M P
            ndocsize = makeunif(1,1000)
            # E N D   T E M P 
            cDoc = CDocument(ndocsize)
            self.lDocuments.append(cDoc.ID)
        return self.ID

# C o l l e c t i o n . m L i s t B o o k s 
    @tracef("COLL")
    def mListBooks(self):
        pass

# C L I E N T 
#------------

class CClient(object):
    lCollections = list()
    getID = itertools.count().next

    @tracef("CLI")
    def __init__(self,mysName,mylCollections):
        self.ID = "T" + str(self.getID())
        G.dID2Client[self.ID] = self
        self.sName = mysName

        for lCollectionParams in mylCollections:
            (sCollName,nCollValue,nCollSize) = lCollectionParams
            cCollID = CCollection(sCollName,nCollValue,nCollSize).ID
            self.lCollections.append(cCollID)
            # select lib based on value

            # T E M P 
            # put collection into a library
            lLibInfo = G.dQual2Libs[nCollValue]
            # pick the first guy in the list of available libs.
            (sLibName,cLibID) = lLibInfo[0]
            
            cColl = G.dID2Collection[cCollID]
            cLib = G.dID2Library[cLibID]
            TRC.tracef(3,"CLI","proc init assign collection|%s| named|%s| to libid|%s| named|%s| quality|%d|" % (cCollID,cColl.sName,cLibID,cLib.sName,nCollValue))
            (G.dID2Library[cLibID]).mAddCollection(cCollID)
            # E N D   T E M P 

# m a k e C l i e n t s 
# Create all clients; give them their params for the simulation.
@tracef("MAIN")
def makeClients(mydClients):
    for sClientName in mydClients:
        cClient = CClient(sClientName,mydClients[sClientName])
        G.lAllClients.append(cClient)



# END
