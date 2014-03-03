#!/usr/bin/python

import simpy
from NewTraceFac07 import TRC,trace,tracef
import itertools
from server import *
from globaldata import *


# D O C U M E N T 
#----------------

class CDocument(object):
    getID = itertools.count(100).next

    @tracef("DOC")
    def __init__(self,size):
        self.nSize = size
        self.ID = "D" + str(self.getID())
        G.nDocLastID = self.ID
        TRC.tracef(3,"DOC","proc init created doc|%s| size|%d|" % (self.ID,self.nSize))
        self.lActions = list()
        G.dID2Doc[self.ID] = self

    def mAudit(self):
        pass

# C O L L E C T I O N 
#--------------------

class CCollection(object):
    getID = itertools.count().next

    @tracef("COLL")
    def __init__(self,mysName,mynValue,mynSize):
        self.sName = mysName
        self.nValue = mynValue
        self.ID = "C" + str(self.getID())
        G.nCollLastID = self.ID
        self.lDocuments = list()
        self.lLibraries = list()
        self.mMakeBooks(mynSize)
        G.dID2Collection[self.ID] = self

    @tracef("COLL")
    def mMakeBooks(self,nbooks):
        # A collection has lots of books
        nrandbooks = int(makennnorm(int(nbooks)))
        for icoll in xrange(nrandbooks):
            ndocsize = makeunif(1,1000)
            cDoc = CDocument(ndocsize)
            self.lDocuments.append(cDoc)
        return self.ID

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
        self.sName = mysName
        self.ID = "T" + str(self.getID())
        G.dID2Client[self.ID] = self
        for lCollectionParams in mylCollections:
            (sCollName,nCollValue,nCollSize) = lCollectionParams
            cColl = CCollection(sCollName,nCollValue,nCollSize)
            self.lCollections.append(cColl)
            # select lib based on value

            # T E M P 
            # put collection into a cheap library
            lLibInfo = G.dQual2Libs[1]
            (sLibName,cLib) = lLibInfo[1]
            TRC.tracef(3,"CLI","proc init assign collection|%s| named|%s| to libinfo|%s| named|%s| quality|%d|" % (cColl,cColl.sName,cLib,cLib.sName,1))
            cLib.mAddCollection(cColl)
            # E N D   T E M P 

# Create all clients; give them their params for the simulation.
@tracef("MAIN")
def makeClients(mydClients):
    for sClientName in mydClients:
        cClient = CClient(sClientName,mydClients[sClientName])
        G.lAllClients.append(cClient)



# END
