#!/usr/bin/python
# server.py

import simpy
from NewTraceFac07 import TRC,trace,tracef
import itertools
from shelf import *
from globaldata import *
from util import *
import copy


# C l a s s  S E R V E R 
#-------------------------

class CServer(object):
    # Function to get a unique, autoincrementing ID for instances
    # of this class.  
    getID = itertools.count().next

    @tracef("SERV")
    def __init__(self,mysName,mynQual,mynShelfSize):
        self.sName = mysName
        self.nQual = mynQual
        self.nShelfSize = mynShelfSize
        self.ID = "L" + str(self.getID())
        self.lShelves = list()
        self.lDocuments = list()
        G.dID2Server[self.ID] = self

# S e r v e r . m A d d C o l l e c t i o n
    @tracef("SERV")
    def mAddCollection(self,cCollID):
        for cDocID in G.dID2Collection[cCollID].lDocuments:
            self.mAddDocument(cDocID)
        return cCollID

# S e r v e r . m A d d D o c u m e n t 
    @tracef("SERV")
    def mAddDocument(self,myDocID):
        ''' mAddDocument(docid)
            Find a shelf with room for the doc, or create one.
            Put the doc on the shelf, decrement the remaining space.
        '''
        cDoc = G.dID2Document[myDocID]
        cShelf = None
        for shelfID in self.lShelves:
            cShelf = G.dID2Shelf[shelfID]
            if cShelf.nFreeSpace >= cDoc.nSize:
                break
            else:
                continue
        else:
            shelfID = self.mCreateShelf()
            self.lShelves.append(shelfID)
            cShelf = G.dID2Shelf[shelfID]
        # Add the doc to this shelf and decrement the space available.
        self.lDocuments.append(myDocID)
        cShelf.mAddDocument(myDocID)
        TRC.tracef(3,"SERV","proc mAddDocument serv|%s| id|%s| docid|%s| size|%s| assigned to shelfid|%s| remaining|%s|" % (self.sName,self.ID,myDocID,cDoc.nSize,shelfID,cShelf.nFreeSpace))
        return self.ID+"+"+shelfID+"+"+myDocID

# S e r v e r . m C r e a t e S h e l f 
    @tracef("SERV")
    def mCreateShelf(self):
        ''' mCreateShelf()
            Add a new shelf of the standard size for this Server.
            Called as needed when a doc arrives too large for available space.  
        '''
        cShelf = CShelf(self,self.nQual,self.nShelfSize)
        return cShelf.ID

# S e r v e r . m R e p l a c e S h e l f 
# NYI

# S e r v e r . m D e s t r o y D o c u m e n t 
    @tracef("SERV")
    def mDestroyDocument(self,mysDocID,mysShelfID):
        ''' Server.mDestroyDocument()
            Oops, a doc died, maybe just one or maybe the whole shelf.
        '''
        TRC.tracef(3,"SERV","proc mDestroyDocument remove doc|%s| from shelf|%s|" % (mysDocID,mysShelfID))
        self.lDocuments.remove(mysDocID)
        return self.ID + "-" + mysDocID

# m a k e S e r v e r s 
@tracef("SVRS")
def makeServers(mydServers):
    for sServerName in mydServers:
        (nServerQual,nShelfSize) = mydServers[sServerName][0]
        sServerID = CServer(sServerName,nServerQual,nShelfSize).ID
        # Invert the server list so that clients can look up 
        # all the servers that satisfy a quality criterion.  
        if nServerQual in G.dQual2Servers:
            G.dQual2Servers[nServerQual].append([sServerName,sServerID])
        else:
            G.dQual2Servers[nServerQual] = [[sServerName,sServerID]]
        TRC.tracef(5,"SVRS","proc makeServers dQual2Servers qual|%s| servers|%s|" % (nServerQual,G.dQual2Servers[nServerQual]))
    return G.dQual2Servers

# C l a s s  S H E L F 
#---------------------

class CShelf(object):
    getID = itertools.count().next

    @tracef("SHLF")
    def __init__(self,myiServer,mynQual,mynCapacity):
        self.ID = "H" + str(self.getID())
        G.nShelfLastID = self.ID
        G.dID2Shelf[self.ID] = self
        self.lDocuments = list()
        self.nCapacity = mynCapacity
        self.nFreeSpace = mynCapacity
        self.sServerID = myiServer.ID          # Server instance we belong to
        self.nQual = mynQual
        self.birthdate = G.env.now
        self.bAlive = True
        self.nSectorHits = 0
        self.nEmptySectorHits = 0
        self.bContig = True
        # Get error rate params and start aging processes
        (self.nSectorLife,self.nShelfLife) = P.dShelfParams[self.nQual][0]
        G.env.process(self.mAge_shelf(self.nShelfLife))
        G.env.process(self.mAge_sector(self.nSectorLife))

# S h e l f . m A d d D o c u m e n t 
    @tracef("SHLF")
    def mAddDocument(self,mysDocID):
        ''' mAddDocument(docID)
            Add a document to this shelf and record some information in 
            the document itself.
        '''
        self.lDocuments.append(mysDocID)
        cDoc = G.dID2Document[mysDocID]
        cDoc.nBlkBegin = self.nCapacity - self.nFreeSpace
        self.nFreeSpace -= cDoc.nSize
        cDoc.nBlkEnd = cDoc.nBlkBegin + cDoc.nSize - 1
        cDoc.sShelfID = self.ID
        cDoc.sServerID = self.sServerID
        TRC.tracef(5,"SHLF","proc mAddDocument add doc|%s| to shelf|%s| size|%d| remaining|%d|" % (mysDocID,self.ID,cDoc.nSize,self.nFreeSpace))
        
        return self.ID+"+"+mysDocID

# S h e l f . m A g e _ s e c t o r 
    @tracef("SHLF")
    def mAge_sector(self,mynLifeParam):
        ''' A sector in the shelf fails.  This corrupts a document.
            For the moment, assume that it destroys the document.  
            Eventually, it will have a probability of destroying the 
            documeht depending on the portion of the document 
            corrupted and the sensitivity of the document to corruption
            (e.g., compressed or encrypted).  
        '''
        # If the shelf has been emptied by a shelf failure, stop 
        # caring about sector failures.
        while self.bAlive:
            nSectorLife = makeexpo(mynLifeParam)
            TRC.tracef(3,"SHLF","proc mAge_sector time|%d| shelf|%s| next lifetime|%d|" % (G.env.now,self.ID,nSectorLife))
            yield G.env.timeout(nSectorLife)
            # F A I L 
            self.nSectorHits += 1
            G.nTimeLastEvent = G.env.now
            TRC.tracef(3,"SHLF","proc mAge_sector time|%d| shelf|%s| Sector_error hits|%d| emptyhits|%d|" % (G.env.now,self.ID,self.nSectorHits,self.nEmptySectorHits))
            # Select a victim Document, probability proportional to size.
            # Small error, size=1.  What doc dies as a result?
            sDocVictimID = self.mSelectVictimDoc(mynErrorSize=1)
            if sDocVictimID:
                self.mDestroyDocument(sDocVictimID)
                G.dID2Server[self.sServerID].mDestroyDocument(sDocVictimID,self.ID)
            else:
                self.nEmptySectorHits += 1
                TRC.tracef(3,"SHLF","shelf|%s| sector error fell in empty space" % (self.ID))
            TRC.tracef(3,"FAIL","proc t|%d| sector failure server|%s| qual|%d| shelf|%s| doc|%s|" % (G.env.now,self.sServerID,G.dID2Server[self.sServerID].nQual,self.ID,sDocVictimID))
            # Initiate a repair of the dead document.
            # NYI

# S h e l f . m S e l e c t V i c t i m D o c 
    @tracef("SHLF")
    def mSelectVictimDoc(self,mynErrorSize):
        ''' mSelectVictimDoc(errorsize)
            Which doc on this shelf, if any, was hit by this error?
            Throw a uniform dart at all the docs on the shelf, see 
            which one gets hit.  Doc size counts.  
        '''
        nRandomSpot = makeunif(1,self.nCapacity+mynErrorSize-1)
        nLoc = 0
        for idxDoc,sDocID in enumerate(self.lDocuments):
            cDoc = G.dID2Document[sDocID]
            iVictim = cDoc
            sVictimID = cDoc.ID
            if nRandomSpot >= cDoc.nBlkBegin and nRandomSpot <= cDoc.nBlkEnd:
                TRC.tracef(5,"SHLF","proc mSelectVictimDoc shelf|%s| sector|%d| hits doc|%s| size|%d|outof|%d|" % (self.ID,nRandomSpot,sVictimID,cDoc.nSize,self.nCapacity))
                break
        else:
            iVictim = None
            sVictimID = None
            TRC.tracef(5,"SHLF","proc mSelectVictimDoc shelf|%s| sector|%d| hits empty space" % (self.ID,nRandomSpot))
        return sVictimID

# S h e l f . m D e s t r o y D o c u m e n t 
    @tracef("SHLF",level=3)
    def mDestroyDocument(self,mysDocID):
        self.lDocuments.remove(mysDocID)
        self.bContig = False
        self.nFreeSpace += G.dID2Document[mysDocID].nSize
        TRC.tracef(3,"SHLF","proc mDestroyDocument remove doc|%s| size|%d| from shelf|%s| remainingdocs|%d| free|%d|" % (mysDocID,G.dID2Document[mysDocID].nSize,self.ID,len(self.lDocuments),self.nFreeSpace))
        return self.ID + "-" + mysDocID

# S h e l f . m A g e _ s h e l f 
    @tracef("SHLF",level=3)
    def mAge_shelf(self,mynLifeParam):
        ''' An entire shelf fails.  Remove all the docs it contained.
            Eventually, this will trigger a repair event and make the 
            collection more vulnerable during the repair.  
        '''
        nShelfLife = makeexpo(mynLifeParam)
        TRC.tracef(3,"SHLF","proc mAge_shelf  time|%d| shelf|%s| next lifetime|%d|" % (G.env.now,self.ID,nShelfLife))
        yield G.env.timeout(nShelfLife)
        # F A I L 
        G.nTimeLastEvent = G.env.now
        TRC.tracef(3,"SHLF","proc mAge_shelf  time|%d| shelf|%s| shelf_error" % (G.env.now,self.ID))
        # This whole shelf is a goner.  Kill it. 
        TRC.tracef(5,"SHLF","proc kill shelf contents ldocs|%s|" % (self.lDocuments)) 
        # Note that we have to copy the list before modifying it and 
        # iterate over the copy.  
        # Standard problem with updating an iterable inside the for loop.
        templDocuments = copy.deepcopy(self.lDocuments)
        for sDocID in templDocuments:
            self.mDestroyDocument(sDocID)
            G.dID2Server[self.sServerID].mDestroyDocument(sDocID,self.ID)
        self.bAlive = False
        TRC.tracef(3,"FAIL","proc t|%d| shelf failure server|%s| qual|%d| shelf|%s| docs|%d|" % (G.env.now,self.sServerID,G.dID2Server[self.sServerID].nQual,self.ID,len(templDocuments)))
        # Rescind any pending sector error aging for this shelf.
        # (Only a performance improvement, I think, since the shelf
        # will be destroyed and never reused.)  
        # NYI
        # Tell the Server to replace the dead shelf.
        # NYI

# S h e l f . m L i s t B o o k s 
    @tracef("COLL")
    def mListBooks(self):
        pass


# END
