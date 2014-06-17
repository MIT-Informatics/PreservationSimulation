#!/usr/bin/python
# server.py
# Recovered, we hope, after commit/delete screw-up.  

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
    getID = itertools.count(1).next

    @tracef("SHOW")
    @tracef("SERV")
    def __init__(self,mysName,mynQual,mynShelfSize):
        self.sName = mysName
        self.nQual = mynQual
        self.nShelfSize = mynShelfSize * 1000000    # Scale up from TB to MB.
        self.ID = "L" + str(self.getID())
        self.lShelfIDs = list()
        self.lDocIDs = list()
        self.lDocIDsComplete = list()
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
        self.lDocIDsComplete.append(mysDocID)
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
        logInfo("SERVER","server |%s| created storage shelf|%s| quality|%s| size|%s|MB" % (self.ID,cShelf.ID,cShelf.nQual,cShelf.nCapacity))
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

# S e r v e r . m T e s t D o c u m e n t 
    def mTestDocument(self,mysDocID):
        ''' Do we still have a copy of this document?  Y/N
        '''
        bResult = mysDocID in self.lDocIDs
        # Might want to do something other than just return T/F.
        if bResult:
            return True
        else:
            return False


#===========================================================
# C l a s s  S H E L F 
#---------------------

class CShelf(object):
    getID = itertools.count(1).next

    @tracef("SHOW")
    @tracef("SHLF")
    def __init__(self,mycServer,mynQual,mynCapacity):
        self.ID = "H" + ("%02d" % self.getID())
        G.nShelfLastID = self.ID
        G.dID2Shelf[self.ID] = self

        # Parallel lists.        
        self.lDocIDs = list()           # Docs currently alive, copied onto this shelf.
        self.lCopyIDs = list()          # Copies currently alive on this shelf.
        self.lDocIDsComplete = list()   # Docs, all ever put onto this shelf.
        self.lCopyIDsComplete = list()  # Copies, all ever put onto this shelf.  
        self.lCopyTops = [0]            # BlkEnd for each doc ever placed here, for searching.
        self.lClientIDs = list()        # From what client did we get this doc (all docs).

        self.nCapacity = mynCapacity
        self.nFreeSpace = mynCapacity
        self.sServerID = mycServer.ID   # Server instance we belong to.
        self.nQual = mynQual
        self.birthdate = G.env.now
        self.bAlive = True              # Shelf failed = False.
        self.nHiWater = 0               # Highest sector used, inclusive.

        self.nSectorHits = 0            # How many sector errors.
        self.nEmptySectorHits = 0       # How many sector errors.
        self.nHitsAboveHiWater = 0      # How many hits out of the occupied region.
        self.nMultipleHits = 0          # How many document slots hit more than once.
        self.bContig = True             # Is the document region still contiguous?

        # Get error rate params and start aging processes
        (self.nSectorLife,self.nShelfLife) = G.dShelfParams[self.nQual][0]
        G.env.process(self.mAge_shelf(self.nShelfLife*1000))
        G.env.process(self.mAge_sector())

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
        self.lDocIDsComplete.append(mysDocID)
        self.lClientIDs.append(mysClientID)
        cDoc = G.dID2Document[mysDocID]
        nSize = cDoc.nSize

        # Make a copy of the document and shelve that.  
        cCopy = CCopy(mysDocID,mysClientID)
        sCopyID = cCopy.ID
        TRC.tracef(3,"SHLF","proc mAddDocument made copy|%s| of doc|%s| from client|%s|" % (sCopyID,mysDocID,mysClientID))

        # Where does document go on this shelf.  Closed interval [Begin,End].
        nBlkBegin = self.nCapacity - self.nFreeSpace
        self.nFreeSpace -= nSize
        nBlkEnd = nBlkBegin + nSize - 1
        self.nHiWater = nBlkEnd         # Last block used.  
#        sShelfID = self.ID
#        sServerID = self.sServerID
        cCopy.mShelveCopy(self.sServerID,self.ID,nBlkBegin,nBlkEnd)
        self.lCopyIDs.append(sCopyID)
        self.lCopyIDsComplete.append(sCopyID)
        self.lCopyTops.append(nBlkEnd)

        cDoc.mCopyPlacedOnServer(sCopyID,self.sServerID)
        TRC.tracef(5,"SHLF","proc mAddDocument add doc|%s| to shelf|%s| size|%d| remaining|%d|" % (mysDocID,self.ID,nSize,self.nFreeSpace))
        
        return self.sServerID + "+" + self.ID+"+"+mysDocID+"+"+sCopyID


# F A I L U R E S 

# S h e l f . m A g e _ s e c t o r 
    @tracef("SHLF")
    def mAge_sector(self):
        ''' A sector in the shelf fails.  This corrupts a document.
            For the moment, assume that it destroys the document.  
            Eventually, it will have a probability of destroying the 
            document depending on the portion of the document 
            corrupted and the sensitivity of the document to corruption
            (e.g., compressed or encrypted), or the failure hits an
            encryption or license key.  
        '''
        # If the shelf has been emptied by a shelf failure, stop 
        # caring about sector failures.
        while self.bAlive:
            fLifeParam = fnfCalcBlockLifetime(self.nSectorLife*1000, self.nCapacity)
            fSectorLifetime = makeexpo(fLifeParam)
            TRC.tracef(3,"SHLF","proc mAge_sector time|%d| shelf|%s| next lifetime|%d|hr from rate|%.3f|hr" % (G.env.now,self.ID,fSectorLifetime,fLifeParam))
            yield G.env.timeout(fSectorLifetime)

            # S E C T O R  F A I L S 
            self.nSectorHits += 1
            G.nTimeLastEvent = G.env.now
            TRC.tracef(3,"SHLF","proc mAge_sector time|%d| shelf|%s| Sector_error hits|%d| emptyhits|%d|" % (G.env.now,self.ID,self.nSectorHits,self.nEmptySectorHits))

            # Select a victim Document, probability proportional to size.
            # Small error, size=1.  What doc dies as a result?
            sCopyVictimID = self.mSelectVictimCopy(mynErrorSize=1)
            if sCopyVictimID:               # Hidden error in victim doc.
                self.mDestroyCopy(sCopyVictimID)
                cCopy = G.dID2Copy[sCopyVictimID]
                # Destroy document on Server, too.  
                cDoc = G.dID2Document[cCopy.sDocID]
                G.dID2Server[self.sServerID].mDestroyDocument(cDoc.ID,self.ID)
                logInfo("SERVER","small error t|%6.0f| svr|%s| shelf|%s| hidden failure in copy|%s| doc|%s|" % (G.env.now,self.sServerID,self.ID,sCopyVictimID,cDoc.ID))
                TRC.tracef(3,"FAIL","proc t|%d| sector failure server|%s| qual|%d| shelf|%s| doc|%s| copy|%s|" % (G.env.now,self.sServerID,G.dID2Server[self.sServerID].nQual,self.ID,cDoc.ID,sCopyVictimID))
            else:                           # No victim, hit empty space.
                self.nEmptySectorHits += 1
                TRC.tracef(3,"SHLF","proc mAge_sector shelf|%s| sector error fell in empty space" % (self.ID))
                logInfo("SERVER","small error t|%6.0f| svr|%s| shelf|%s| hidden failure in copy|%s|" % (G.env.now,self.sServerID,self.ID,sCopyVictimID))
                TRC.tracef(3,"FAIL","proc t|%d| sector failure server|%s| qual|%d| shelf|%s| copy|%s|" % (G.env.now,self.sServerID,G.dID2Server[self.sServerID].nQual,self.ID,sCopyVictimID))

            # Initiate a repair of the dead document.
            # NYI

# OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD
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
        # TODO: improve the search for the victim document.
        # Already added a check for the high water mark.
        # Probably do a binary search for the missing element in range
        # (like the old stemming search).
        if nRandomSpot < self.nHiWater:
            for idxCopy,sCopyID in enumerate(self.lCopyIDs):
                cCopy = G.dID2Copy[sCopyID]
                iVictim = cCopy
                sVictimID = cCopy.ID
                if nRandomSpot >= cCopy.nBlkBegin and nRandomSpot <= cCopy.nBlkEnd:
                    TRC.tracef(3,"SHLF","proc mSelectVictimCopy shelf|%s| sector|%d| hits doc|%s| placed[%d,%d] size|%d| outof|%d|" % (self.ID,nRandomSpot,sVictimID,cCopy.nBlkBegin,cCopy.nBlkEnd, (cCopy.nBlkEnd-cCopy.nBlkBegin+1),self.nCapacity))
                    break
            else:
                iVictim = None
                sVictimID = None
                TRC.tracef(5,"SHLF","proc mSelectVictimCopy shelf|%s| sector|%d| hits empty space" % (self.ID,nRandomSpot))
        else:
            sVictimID = None
        return sVictimID

# NEW NEW NEW NEW NEW NEW NEW NEW NEW NEW NEW NEW NEW NEW NEW NEW NEW NEW
# Replaces old version above.

# S h e l f . m S e l e c t V i c t i m C o p y  
    @tracef("SHLF")
    def mSelectVictimCopy(self,mynErrorSize):
        ''' mSelectVictimCopy(errorsize)
            Which doc copy on this shelf, if any, was hit by this error?
            Throw a uniform dart at all the docs on the shelf, see 
            which one gets hit.  Doc size counts.  
        '''
        nRandomSpot = makeunif(1,self.nCapacity + mynErrorSize - 1)
        nLoc = 0
        TRC.tracef(5,"SHLF","proc SelectVictimCopy0 wherehit spot|%s| hiwater|%s|  shelfid|%s| capacity|%s|" % (nRandomSpot,self.nHiWater,self.ID,self.nCapacity))
        # First, check to see if the failure is maybe in an occupied region.  
        if nRandomSpot <= self.nHiWater:
            # Find the document hit by the error.  May have been hit before, too.  
            # New version, binary search with adjacent checking
            # on list of all locations assigned on this shelf.
            # After you find the location, check to see that it 
            # is still occupied by live copy.  
            nLen = len(self.lCopyIDsComplete)
            nDist = (nLen + 1) / 2
            nLoc = nDist
            TRC.trace(5,"proc SelectVictimCopy0 searchsetup len|%s| loc|%s| dist|%s|" % (nLen,nLoc,nDist))
            while 1:
                if nLoc <= 0: nLoc = 1
                if nLoc >= nLen: nLoc = nLen - 1
                nDist = (nDist + 1) / 2
                if nDist == 0: nDist = 1

                nTop = self.lCopyTops[nLoc]
                nBottom = self.lCopyTops[nLoc-1]
                sCopyID = self.lCopyIDsComplete[nLoc-1]
                sDocID = self.lDocIDsComplete[nLoc-1]
                cCopy = G.dID2Copy[sCopyID]

                if nRandomSpot <= nTop:
                    # Lower than top, look down.
                    if nRandomSpot >= nBottom:
                        # Found to left of nLoc.  
                        TRC.trace(5,"proc SelectVictimCopy5D found victim id|%s| at spot|%s| in[%s,%s]| doc|%s|" % (sCopyID,nRandomSpot,nBottom,nTop,sDocID))
                        # Is this slot still occupied by a live copy?
                        if sCopyID in self.lCopyIDs:
                            sVictimID = sCopyID
                            TRC.tracef(3,"SHLF","proc mSelectVictimCopy NEWD end shelf|%s| spot|%d| hits doc|%s| placed[%d,%d] size|%d| outof|%d|" % (self.ID,nRandomSpot,sVictimID,cCopy.nBlkBegin,cCopy.nBlkEnd, (cCopy.nBlkEnd-cCopy.nBlkBegin+1),self.nCapacity))
                        else:
                            sVictimID = None
                            TRC.trace(5,"proc SelectVictimCopy2D no longer valid copyid|%s| docid|%s|" % (sCopyID,sDocID))
                            self.nMultipleHits += 1
                        break
                    else:
                        nLoc -= nDist
                        TRC.trace(5,"proc SelectVictimCopy3D down spot|%s| intvl|[%s,%s| newloc|%s| newdist|%s|" % (nRandomSpot,nBottom,nTop,nLoc,nDist))
                else:
                    # Higher than top, look up.
                    if nRandomSpot <= self.lCopyTops[nLoc+1]:
                        # Found to right of nLoc.
                        # Reevaluate ids and locations to the next slot on the right.  
                        sCopyID = self.lCopyIDsComplete[nLoc+1-1]
                        sDocID = self.lDocIDsComplete[nLoc+1-1]
                        cCopy = G.dID2Copy[sCopyID]
                        nBottom = self.lCopyTops[nLoc+1-1]
                        sCopyID = self.lCopyIDsComplete[nLoc+1-1]
                        TRC.trace(5,"proc SelectVictimCopy5U found victim id|%s| at spot|%s| in[%s,%s]| doc|%s|" % (sCopyID,nRandomSpot,nBottom,nTop,sDocID))
                        # Is this slot still occupied by a live copy?
                        if sCopyID in self.lCopyIDs:
                            sVictimID = sCopyID
                            TRC.tracef(3,"SHLF","proc mSelectVictimCopy NEWU end shelf|%s| spot|%d| hits doc|%s| placed[%d,%d] size|%d| outof|%d|" % (self.ID,nRandomSpot,sVictimID,cCopy.nBlkBegin,cCopy.nBlkEnd, (cCopy.nBlkEnd-cCopy.nBlkBegin+1),self.nCapacity))
                        else:
                            sVictimID = None
                            TRC.trace(5,"proc SelectVictimCopy2U no longer valid copyid|%s| docid|%s|" % (sCopyID,sDocID))
                            self.nMultipleHits += 1
                        break
                    else:
                        nLoc += nDist
                        TRC.trace(5,"proc SelectVictimCopy3U up   spot|%s| intvl|[%s,%s| newloc|%s| newdist|%s|" % (nRandomSpot,nBottom,nTop,nLoc,nDist))

            ''' the original old way
            for idxCopy,sCopyID in enumerate(self.lCopyIDs):
                cCopy = G.dID2Copy[sCopyID]
                iVictimx = cCopy
                sVictimIDx = cCopy.ID
                if nRandomSpot >= cCopy.nBlkBegin and nRandomSpot <= cCopy.nBlkEnd:
                    TRC.tracef(3,"SHLF","proc mSelectVictimCopy OLD shelf|%s| sector|%d| hits doc|%s| placed[%d,%d] size|%d| outof|%d|" % (self.ID,nRandomSpot,sVictimIDx,cCopy.nBlkBegin,cCopy.nBlkEnd, (cCopy.nBlkEnd-cCopy.nBlkBegin+1),self.nCapacity))
                    break
            else:
                iVictimx = None
                sVictimIDx = None
                TRC.tracef(5,"SHLF","proc mSelectVictimCopy shelf|%s| sector|%d| hits empty space" % (self.ID,nRandomSpot))
            '''

        else:
            TRC.tracef(3,"SHLF","proc mSelectVictimCopy shelf|%s| spot|%d| above hiwater|%s| empty" % (self.ID,nRandomSpot,self.nHiWater))
            sVictimID = None
            self.nHitsAboveHiWater += 1

        return sVictimID

# S h e l f . m D e s t r o y C o p y  
    @tracef("SHLF",level=3)
    def mDestroyCopy(self,mysCopyID):
        try:
            nCopyIndex = self.lCopyIDs.index(mysCopyID)
        except ValueError:
            TRC.tracef(0,"SHLF","BUGCHECK copyID not found for removal|%s|" % (mysCopyID))
            return False
        # Remove doc and copy from current lists.  
        del self.lCopyIDs[nCopyIndex]
        del self.lDocIDs[nCopyIndex]
        # And give back the space it occupied.  
        self.bContig = False
        cCopy = G.dID2Copy[mysCopyID]
        cDoc = G.dID2Document[cCopy.sDocID]
        self.nFreeSpace += cDoc.nSize
        TRC.tracef(3,"SHLF","proc mDestroyCopy remove doc|%s| copy|%s| idx|%d| size|%d| from shelf|%s| remainingdocs|%d| free|%d|" % (cCopy.sDocID,mysCopyID,nCopyIndex,cDoc.nSize,self.ID,len(self.lCopyIDs),self.nFreeSpace))
        return self.ID + "-" + cCopy.sDocID + "-" + mysCopyID

# S h e l f . m A g e _ s h e l f 
    @tracef("SHLF",level=3)
    def mAge_shelf(self,mynLifeParam):
        ''' An entire shelf fails.  Remove all the docs it contained.
            Eventually, this will trigger a repair event and make the 
            collection more vulnerable during the repair.  
        '''
        nShelfLife = makeexpo(mynLifeParam)
        TRC.tracef(3,"SHLF","proc mAge_shelf  time|%d| shelf|%s| next lifetime|%d|khr" % (G.env.now,self.ID,nShelfLife))
        yield G.env.timeout(nShelfLife)

        # S H E L F  F A I L S 
        G.nTimeLastEvent = G.env.now
        self.bAlive = False         # Shelf can no longer be used to store docs.
        TRC.tracef(3,"SHLF","proc mAge_shelf  time|%d| shelf|%s| shelf_error" % (G.env.now,self.ID))
        logInfo("SERVER","storage shelf failed time|%6q.0f| server|%s| shelf|%s| lost |%d| docs" % (G.env.now,self.sServerID,self.ID,len(self.lCopyIDs)))
        # This whole shelf is a goner.  Kill it. 
        TRC.tracef(5,"SHLF","proc mAge_shelf kill contents ldocs|%s| lcopies|%s|" % (self.lDocIDs,self.lCopyIDs)) 
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

# S h e l f . m R e p o r t D o c u m e n t L o s t 
    @tracef("SHLF")
    def mReportDocumentLost(self,mysDocID):
        cDoc = G.dID2Document[mysDocID]
        sClientID = cDoc.sClientID
        cClient = G.dID2Client[sClientID]
        cClient.mDocFailedOnServer(mysDocID,self.sServerID)
        return self.sServerID +"+"+ self.ID +"+"+ mysDocID

# S h e l f . m R e p o r t U s e S t a t s 
    @tracef("SHLF")
    def mReportUseStats(self):
        ''' Return ID,server ID,quality,capacity,high water mark,currently used
        '''
        return (self.ID,self.sServerID,self.nQual,self.nCapacity,self.nHiWater+1,self.nCapacity-self.nFreeSpace)

# S h e l f . m R e p o r t E r r o r S t a t s 
    @tracef("SHLF")
    def mReportErrorStats(self):
        ''' Return ID,server ID,quality,sector hits,empty sector hits,alive flag
        '''
        return (self.ID,self.sServerID,self.nQual,self.nSectorHits,self.nEmptySectorHits,self.bAlive,self.nHitsAboveHiWater,self.nMultipleHits)

#===========================================================
# C O P Y  ( of  D o c u m e n t )
#---------------------------------

class CCopy(object):
    getID = itertools.count(1).next

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
