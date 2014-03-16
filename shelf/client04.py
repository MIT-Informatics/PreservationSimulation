#!/usr/bin/python
# client.py

import simpy
from NewTraceFac07 import TRC,trace,tracef
import itertools
from server import *
from globaldata import *
import math


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
        self.sServerID = None
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
        self.lServers = list()
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
    lCollectionIDs = list()
    sCollIDLastAudited = ""
    getID = itertools.count().next

    @tracef("CLI")
    def __init__(self,mysName,mylCollections):
        self.ID = "T" + str(self.getID())
        G.dID2Client[self.ID] = self
        self.sName = mysName

        for lCollectionParams in mylCollections:
            (sCollName,nCollValue,nCollSize) = lCollectionParams
            sCollID = CCollection(sCollName,nCollValue,nCollSize).ID
            self.lCollectionIDs.append(sCollID)

            # Put the collection in all the right places.  
            self.mPlaceCollection(sCollID)

            # For each collection, select a set of servers
            # based on value.
#            lServersForCollection = self.mSelectServersForCollection(nCollValue)
#
            # T E M P 
            # pick the first guy in the list of available servers.
#            (sServerName,sServerID) = lServersForCollection[0]
#
#            cColl = G.dID2Collection[sCollID]
#            cServer = G.dID2Server[sServerID]
#            TRC.tracef(3,"CLI","proc init assign collection|%s| named|%s| to serverid|%s| named|%s| quality|%d|" % (sCollID,cColl.sName,sServerID,cServer.sName,nCollValue))
#            (G.dID2Server[sServerID]).mAddCollection(sCollID)
            # E N D   T E M P 
            # EVENTUALLY
            # select set of servers for collection
            # place collection on each server
            ''' If there aren't enough at this level, it's an error.  
                We *could* go to a higher level, but this is only
                a simulation, not real life.  
            '''
            # END EVENTUALLY

    @tracef("CLI")
    def mPlaceCollection(self,mysCollID):
        ''' Client.mPlaceCollection()
            Get list of servers available at the right quality level.
            Select the policy-specified number of them.
            Send the collection to each server in turn.  
        '''
        cColl = G.dID2Collection[mysCollID]
        nCollValue = cColl.nValue
        lServersForCollection = self.mSelectServersForCollection(nCollValue)

        # T E M P
        # We don't have distribution policy params yet, 
        # so use the entire available list.
        lServersToUse = lServersForCollection
        # E N D   T E M P

        # Distribute collection to a set of servers.
        for (sServerName,sServerID) in lServersToUse:
            # Send copy of collection to server.
            (G.dID2Server[sServerID]).mAddCollection(mysCollID)
            # Record that this server has a copy of this collection.
            cColl.lServers.append(sServerID)


    @tracef("CLI")
    def mSelectServersForCollection(self,mynCollValue):
        ''' Get list of servers at this quality level.
            Return a random permutation of the list of servers.
        '''
        # Get list of all servers at this quality level.
        lServersAtLevel = G.dQual2Servers[mynCollValue]
        # Pick a random number of a permutation.
        nNumPerms = math.factorial(len(lServersAtLevel))
        nPermChoice = int(makeunif(0,nNumPerms))
        # Make a list of all the permutations.  
        lPerms = list()
        for lPerm in itertools.permutations(lServersAtLevel):
            lPerms.append(lPerm)
        # Pick one. 
        lPermChosen = lPerms[nPermChoice]
        TRC.tracef(3,"CLI","proc mSelectServers perm|%d| of|%d| list|%s|" % (nPermChoice,nNumPerms,lPermChosen))
        

#temp
        (sServerName,sServerID) = lPermChosen[0]
        
#        cColl = G.dID2Collection[mysCollID]
#        cServer = G.dID2Server[sServerID]
#        TRC.tracef(3,"CLI","proc init assign collection|%s| #named|%s| to serverid|%s| named|%s| quality|%d|" % #(mysCollID,cColl.sName,sServerID,cServer.sName,mynCollValue))
#        (G.dID2Server[sServerID]).mAddCollection(mysCollID)
        # E N D   T E M P 
        return lPermChosen

    @tracef("CLI")
    def mAuditCycle(self):
        # wait for a while, then auditnext
        pass

    @tracef("CLI")
    def mAuditNextCollection(self):
        self.sCollIDLastAudited = self.lCollectionIDs[(index(self.sCollIDLastAudited) + 1) % len(self.lCollections)]
        self.mAuditCollection(self.sCollIDLastAudited)
        return self.sCollIDLastAudited

    @tracef("CLI")
    def mAuditCollection(self,mysCollectionID):
        # find server with a copy of collection to audit
        
        for cDoc in G.dID2Collection[mysCollectionID].lDocumentIDs:
            # ask for validation of each doc
            # if not valid, initiate repair
            pass


# m a k e C l i e n t s 
# Create all clients; give them their params for the simulation.
@tracef("MAIN")
def makeClients(mydClients):
    for sClientName in mydClients:
        cClient = CClient(sClientName,mydClients[sClientName])
        G.lAllClients.append(cClient)
    return G.lAllClients


# END
