#!/usr/bin/python
# server.py

import simpy
from NewTraceFac import TRC,trace,tracef
import itertools
from globaldata import *
from util import *
import copy
from logoutput import logInfo


#===========================================================
# C l a s s  S E R V E R 
#-------------------------

class CServer(object):
    # Function to get a unique, autoincrementing ID for instances
    # of this class.  
    getID = itertools.count().next

    @tracef("SHOW")
    @tracef("SERV")
    def __init__(self,mysName,mynQual,mynShelfSize):
        self.sName = mysName
        self.nQual = mynQual
        self.nShelfSize = mynShelfSize
        self.ID = "L" + str(self.getID())
        self.lShelfIDs = list()
        self.lDocIDs = list()
        G.dID2Server[self.ID] = self
        G.nServerLastID = self.ID

# S e r v e r . m A d d C o l l e c t i o n
    @tracef("SERV")
    def mAddCollection(self,mysCollID,mysClientID):
        lTempDocIDs = list()
        lTempDocIDs = G.dID2Collection[mysCollID].mListDocuments()
        for sDocID in lTempDocIDs:
            self.mAddDocument(sDocID,mysClientID)
        return mysCollID

# S e r v e r . m A d d D o c u m e n t 
    @tracef("SERV")
    def mAddDocument(self,mysDocID,mysClientID):
        ''' mAddDocument(docid)
            Find a shelf with room for the doc, or create one.
            Put the doc on the shelf, decrement the remaining space.
        '''
        cDoc = G.dID2Document[mysDocID]
        nSize = cDoc.nSize
        # Find a shelf with sufficient empty space and place the doc there. 
        cShelf = None
        for sShelfID in self.lShelfIDs:
            cShelf = G.dID2Shelf[sShelfID]
            
            bResult = cShelf.mAcceptDocument(mysDocID,nSize,mysClientID)
            if bResult:
                break       # True = doc has been stored
            else:
                continue    # False = no, try another shelf, if any
        else:               # If no more shelves, create another and use that one.
            sNewShelfID = self.mCreateShelf()
            self.lShelfIDs.append(sNewShelfID)
            cShelf = G.dID2Shelf[sNewShelfID]
            sShelfID = cShelf.ID
            result = cShelf.mAcceptDocument(mysDocID,nSize,mysClientID)
            
        # Record that the doc has been stored on this server. 
        self.lDocIDs.append(mysDocID)
        TRC.tracef(3,"SERV","proc mAddDocument serv|%s| id|%s| docid|%s| size|%s| assigned to shelfid|%s| remaining|%s|" % (self.sName,self.ID,mysDocID,cDoc.nSize,sShelfID,cShelf.nFreeSpace))

        return self.ID+"+"+sShelfID+"+"+mysDocID

# S e r v e r . m C r e a t e S h e l f 
    @tracef("SERV")
    def mCreateShelf(self):
        ''' mCreateShelf()
            Add a new shelf of the standard size for this Server.
            Called as needed when a doc arrives too large for available space.  
        '''
        cShelf = CShelf(self,self.nQual,self.nShelfSize)
        logInfo("SERVER","created storage shelf|%s|" % (cShelf.ID))
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
        self.lDocIDs.remove(mysDocID)
        return self.ID + "-" + mysDocID

#===========================================================
# C l a s s  S H E L F 
#---------------------

class CShelf(object):
    getID = itertools.count().next

    @tracef("SHOW")
    @tracef("SHLF")
    def __init__(self,mycServer,mynQual,mynCapacity):
        self.ID = "H" + str(self.getID())
        G.nShelfLastID = self.ID
        G.dID2Shelf[self.ID] = self
        
        self.lDocIDs = list()
        self.lCopyIDs = list()
        self.lClientIDs = list()
        self.nCapacity = mynCapacity
        self.nFreeSpace = mynCapacity
        self.sServerID = mycServer.ID          # Server instance we belong to
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

# S h e l f . m A c c e p t D o c u m e n t 
    @tracef("SHLF")
    def mAcceptDocument(self,mysDocID,mynDocSize,mysClientID):
        ''' Shelf.mAcceptDocument
            If the shelf is still alive and 
            there is room on the shelf, then add the document 
            and return True.  
            A shelf, once failed, cannot be reused.
            If not, return False.
        '''
        if self.bAlive and self.nFreeSpace >= mynDocSize:
            self.mAddDocument(mysDocID,mysClientID)
            return True
        else:
            return False

# S h e l f . m A d d D o c u m e n t 
    @tracef("SHLF")
    def mAddDocument(self,mysDocID,mysClientID):
        ''' mAddDocument(docID)
            Add a document to this shelf and record some information
            in the document itself.
        '''
        self.lDocIDs.append(mysDocID)
        self.lClientIDs.append(mysClientID)
        cDoc = G.dID2Document[mysDocID]
        nSize = cDoc.nSize

        # Make a copy of the document and shelve that.  
        cCopy = CCopy(mysDocID,mysClientID)
        sCopyID = cCopy.ID
        TRC.tracef(3,"SHLF","proc made copy|%s| of doc|%s| from client|%s|" % (sCopyID,mysDocID,mysClientID))

        nBlkBegin = self.nCapacity - self.nFreeSpace
        self.nFreeSpace -= nSize
        nBlkEnd = nBlkBegin + nSize - 1
        sShelfID = self.ID
        sServerID = self.sServerID
        cCopy.mShelveCopy(self.sServerID,self.ID,nBlkBegin,nBlkEnd)
        self.lCopyIDs.append(sCopyID)

        cDoc.mCopyPlacedOnServer(sCopyID,self.sServerID)
        TRC.tracef(5,"SHLF","proc mAddDocument add doc|%s| to shelf|%s| size|%d| remaining|%d|" % (mysDocID,self.ID,nSize,self.nFreeSpace))
        
        return self.sServerID + "+" + self.ID+"+"+mysDocID+"+"+sCopyID

# F A I L U R E S 

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

            # S E C T O R  F A I L S 
            self.nSectorHits += 1
            G.nTimeLastEvent = G.env.now
            TRC.tracef(3,"SHLF","proc mAge_sector time|%d| shelf|%s| Sector_error hits|%d| emptyhits|%d|" % (G.env.now,self.ID,self.nSectorHits,self.nEmptySectorHits))
            # Select a victim Document, probability proportional to size.
            # Small error, size=1.  What doc dies as a result?
            sCopyVictimID = self.mSelectVictimCopy(mynErrorSize=1)
            if sCopyVictimID:
                self.mDestroyCopy(sCopyVictimID)
                cCopy = G.dID2Copy[sCopyVictimID]
                cDoc = G.dID2Document[cCopy.sDocID]
                G.dID2Server[self.sServerID].mDestroyDocument(cDoc.ID,self.ID)
            else:
                self.nEmptySectorHits += 1
                TRC.tracef(3,"SHLF","proc shelf|%s| sector error fell in empty space" % (self.ID))
            TRC.tracef(3,"FAIL","proc t|%d| sector failure server|%s| qual|%d| shelf|%s| doc|%s|" % (G.env.now,self.sServerID,G.dID2Server[self.sServerID].nQual,self.ID,sCopyVictimID))
            logInfo("SERVER","small error time|%s| server|%s| shelf|%s| hidden failure in doc|%s|" % (G.env.now,self.sServerID,self.ID,sCopyVictimID))

            # Initiate a repair of the dead document.
            # NYI

# S h e l f . m S e l e c t V i c t i m C o p y  
    @tracef("SHLF")
    def mSelectVictimCopy(self,mynErrorSize):
        ''' mSelectVictimCopy(errorsize)
            Which doc copy on this shelf, if any, was hit by this error?
            Throw a uniform dart at all the docs on the shelf, see 
            which one gets hit.  Doc size counts.  
        '''
        nRandomSpot = makeunif(1,self.nCapacity+mynErrorSize-1)
        nLoc = 0
        for idxCopy,sCopyID in enumerate(self.lCopyIDs):
            cCopy = G.dID2Copy[sCopyID]
            iVictim = cCopy
            sVictimID = cCopy.ID
            if nRandomSpot >= cCopy.nBlkBegin and nRandomSpot <= cCopy.nBlkEnd:
                TRC.tracef(5,"SHLF","proc mSelectVictimCopy shelf|%s| sector|%d| hits doc|%s| size|%d| outof|%d|" % (self.ID,nRandomSpot,sVictimID, (cCopy.nBlkEnd-cCopy.nBlkBegin+1),self.nCapacity))
                break
        else:
            iVictim = None
            sVictimID = None
            TRC.tracef(5,"SHLF","proc mSelectVictimCopy shelf|%s| sector|%d| hits empty space" % (self.ID,nRandomSpot))
        return sVictimID

# S h e l f . m D e s t r o y C o p y  
    @tracef("SHLF",level=3)
    def mDestroyCopy(self,mysCopyID):
        try:
            nCopyIndex = self.lCopyIDs.index(mysCopyID)
        except ValueError:
            TRC.tracef(0,"SHLF","BUGCHECK copyID not found for removal|%s|" % (mysCopyID))
        del self.lCopyIDs[nCopyIndex]
        del self.lDocIDs[nCopyIndex]
        self.bContig = False
        cCopy = G.dID2Copy[mysCopyID]
        cDoc = G.dID2Document[cCopy.sDocID]
        self.nFreeSpace += cDoc.nSize
        TRC.tracef(3,"SHLF","proc mDestroyCopy remove doc|%s| copy|%s| size|%d| from shelf|%s| remainingdocs|%d| free|%d|" % (cCopy.sDocID,mysCopyID,cDoc.nSize,self.ID,len(self.lCopyIDs),self.nFreeSpace))
        return self.ID + "-" + cCopy.sDocID + "-" + mysCopyID

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

        # S H E L F  F A I L S 
        G.nTimeLastEvent = G.env.now
        self.bAlive = False
        TRC.tracef(3,"SHLF","proc mAge_shelf  time|%d| shelf|%s| shelf_error" % (G.env.now,self.ID))
        logInfo("SERVER","storage shelf failed time|%d| server|%s| shelf|%s| lost |%d| docs" % (G.env.now,self.sServerID,self.ID,len(self.lCopyIDs)))
        # This whole shelf is a goner.  Kill it. 
        TRC.tracef(5,"SHLF","proc kill shelf contents ldocs|%s| lcopies|%s|" % (self.lDocIDs,self.lCopyIDs)) 
        # Note that we have to copy the list before modifying it and 
        # iterate over the copy of the list.  
        # Standard problem with updating an iterable inside the for loop.
        templCopyIDs = copy.deepcopy(self.lCopyIDs)
        for sCopyID in templCopyIDs:
            sDocID = G.dID2Copy[sCopyID].sDocID
            self.mDestroyCopy(sCopyID)
            G.dID2Server[self.sServerID].mDestroyDocument(sDocID,self.ID)
            self.mReportDocumentLost(sDocID)
        TRC.tracef(3,"FAIL","proc t|%d| shelf failure server|%s| qual|%d| shelf|%s| docs|%d|" % (G.env.now,self.sServerID,G.dID2Server[self.sServerID].nQual,self.ID,len(templCopyIDs)))
        
        # Rescind any pending sector error aging for this shelf.
        # (Only a performance improvement, I think, since the shelf
        # will be destroyed and never reused.)  
        # NYI
        # Tell the Server to replace the dead shelf.
        # NYI

# Shelf.mReportDocumentLost
    @tracef("SHLF")
    def mReportDocumentLost(self,mysDocID):
        cDoc = G.dID2Document[mysDocID]
        sClientID = cDoc.sClientID
        cClient = G.dID2Client[sClientID]
        cClient.mDocFailedOnServer(mysDocID,self.sServerID)
        return self.sServerID +"+"+ self.ID +"+"+ mysDocID


#===========================================================
# C O P Y  ( of  D o c u m e n t )
#---------------------------------

class CCopy(object):
    getID = itertools.count().next

    @tracef("COPY")
    def __init__(self,mysDocID,mysClientID):
        self.ID = "X" + str(self.getID())
        G.dID2Copy[self.ID] = self
        G.nCopyLastID = self.ID

        # What document is this a copy of?
        self.sDocID = mysDocID
        self.sClientID = mysClientID
        # Where is this copy being stored?
        self.sServerID = None
        self.sShelfID = None
        self.nBlkBegin = None
        self.nBlkEnd = None

    @tracef("COPY")
    def mShelveCopy(self,mysServerID,mysShelfID,mynBlkBegin,mynBlkEnd):
        self.sServerID = mysServerID
        self.sShelfID = mysShelfID
        self.nBlkBegin = mynBlkBegin
        self.nBlkEnd = mynBlkEnd
        return self.ID+"+"+mysServerID+"+"+mysShelfID+"+" + "["+str(mynBlkBegin)+","+str(mynBlkEnd)+"]"


# END
