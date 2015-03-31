#!/usr/bin/python
# server.py

import simpy
from NewTraceFac import TRC,trace,tracef
import itertools
from globaldata import G
from math import exp, log
import util
import copy
import logoutput as lg


#===========================================================
# C l a s s  S E R V E R 
#-----------------------

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
        self.ID = "V" + str(self.getID())
        self.lShelfIDs = list()
        self.lDocIDs = list()           # Docs that still live in this server.
        self.dDocIDs = dict()           # Dictionary version of alive doc IDs, for fast checking.
        self.lDocIDsComplete = list()   # All docs that were ever in this server.
        G.dID2Server[self.ID] = self
        G.nServerLastID = self.ID

# S e r v e r . m A d d C o l l e c t i o n
    @tracef("SERV")
    def mAddCollection(self,mysCollID,mysClientID):
        lTempDocIDs = list()
        cCollection = G.dID2Collection[mysCollID]
        lTempDocIDs = cCollection.mListDocuments()
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
        self.dDocIDs[mysDocID] = mysClientID
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
        cShelf = CShelf(self.ID,self.nQual,self.nShelfSize)
        lg.logInfo("SERVER","server |%s| created storage shelf|%s| quality|%s| size|%s|MB" % (self.ID,cShelf.ID,cShelf.nQual,cShelf.nCapacity))
        return cShelf.ID

# S e r v e r . m R e p l a c e S h e l f 
# NYI

# S e r v e r . m D e s t r o y C o p y 
    @tracef("SERV")
    def mDestroyCopy(self,mysCopyID,mysDocID,mysShelfID):
        ''' Server.mDestroyCopy()
            Oops, a doc died, maybe just one or maybe the whole shelf.
        '''
        TRC.tracef(3,"SERV","proc mDestroyCopy remove copy|%s| doc|%s| from shelf|%s|" % (mysCopyID,mysDocID,mysShelfID))
        # Inform the client that the copy is gonzo.  
        cClient = G.dID2Client[self.dDocIDs[mysDocID]]
        cClient.mDestroyCopy(mysDocID,self.ID)
        # Clear out local traces of the doc and copy.
        self.lDocIDs.remove(mysDocID)
        del self.dDocIDs[mysDocID]
        # The Shelf will nuke the copy, because it created it.  
        return self.ID + "-" + mysDocID

# S e r v e r . m T e s t D o c u m e n t 
    def mTestDocument(self,mysDocID):
        ''' Do we still have a copy of this document?  Y/N
        '''
        #bResult = mysDocID in self.lDocIDs
        # Oops, item-in-list is incredibly slow, linear search.
        # It doesn't know that the list is sorted.
        # Try dictionary lookup, which is lots faster.  
        # (The dictionary is maintained by Add and Destroy.)
        bResult = mysDocID in self.dDocIDs
        # Might someday want to do something other than just return T/F.
        if bResult:
            return True
        else:
            return False


#===========================================================
# C l a s s  S H E L F 
#---------------------

class CShelf(object):
    getID = itertools.count(1).next

    @tracef("SHLF")
    def __init__(self,mysServerID,mynQual,mynCapacity):
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
        self.sServerID = mysServerID   # Server instance we belong to.
        self.nQual = mynQual
        self.birthdate = G.env.now
        self.bAlive = True              # Shelf failed = False.
        self.nHiWater = 0               # Highest sector used, inclusive.

        self.nSectorHits = 0            # How many sector errors.
        self.nEmptySectorHits = 0       # How many sector errors.
        self.nHitsAboveHiWater = 0      # How many hits out of the occupied region.
        self.nMultipleHits = 0          # How many document slots hit more than once.
        self.bContig = True             # Is the document region still contiguous?
        self.nConsecutiveMisses = 0     # How many misses in a row?

        # Get error rate params 
        (self.nSectorLife, self.nShelfLife) = G.dShelfParams[self.nQual][0]
        (self.nGlitchFreq, self.nGlitchImpact, self.nGlitchHalflife, self.nGlitchMaxlife) = fnlGetGlitchParams(self.ID)
        self.fLifeParam = util.fnfCalcBlockLifetime(self.nSectorLife*1000, self.nCapacity)
        cLifetime = CLifetime(self.ID,self.fLifeParam, self.nGlitchFreq, self.nGlitchImpact, self.nGlitchHalflife, self.nGlitchMaxlife)
        self.sSectorLifetimeID = cLifetime.ID
        G.dID2Lifetime[self.sSectorLifetimeID] = cLifetime

        # Start aging processes
        G.env.process(self.mAge_shelf(self.nShelfLife*1000))
        G.env.process(self.mAge_sector())
# if glitches
#   start glitch process cLifetime.mInjectError(reduction, decay, now?) at some freq


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
        cCopy = CCopy(mysDocID,mysClientID,self.sServerID)
        sCopyID = cCopy.ID
        TRC.tracef(3,"SHLF","proc mAddDocument made copy|%s| of doc|%s| from client|%s|" % (sCopyID,mysDocID,mysClientID))

        # Where does document go on this shelf.  Closed interval [Begin,End].
#        nBlkBegin = self.nCapacity - self.nFreeSpace
        # BZZZT: Never reuse space.  Any empty space in the area that 
        # *used* to be occupied by documents has already been damaged
        # and destroyed a document.  Do not reuse the space.  
        nBlkBegin = self.nHiWater + 1
        self.nFreeSpace -= nSize
        nBlkEnd = nBlkBegin + nSize - 1
        if nBlkEnd > self.nHiWater:
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
            # Sector lifetime depends on shelf lifetime and glitch age.
            fNow = G.env.now
            cLifetime = G.dID2Lifetime[self.sSectorLifetimeID]
            fLifetimeNow = cLifetime.mfCalcCurrentSectorLifetime(fNow)
            fSectorLifeInterval = util.makeexpo(fLifetimeNow)
            TRC.tracef(3,"SHLF","proc mAge_sector time|%d| shelf|%s| next lifetime|%.3f|hr from rate|%.3f|hr" % (G.env.now,self.ID,fSectorLifeInterval,fLifetimeNow))
            yield G.env.timeout(fSectorLifeInterval)

            # S E C T O R  F A I L S 
            self.nSectorHits += 1
            G.nTimeLastEvent = G.env.now
            TRC.tracef(3,"SHLF","proc mAge_sector time|%d| shelf|%s| Sector_error hits|%d| emptyhits|%d|" % (G.env.now,self.ID,self.nSectorHits,self.nEmptySectorHits))

            # Select a victim Document, probability proportional to size.
            # Small error, size=1.  What doc dies as a result?
            sCopyVictimID = self.mSelectVictimCopy(mynErrorSize=1)

            # New version: compress strings of consecutive misses into single line.
            # Normally we log one line per error regardless of whether it hits or 
            # misses a document.  That results in hideously long log files for 
            # sparse storage structures, like small docs on large shelf. 
            # Count consecutive misses, and issue one summary line before the 
            # next hit.
            if sCopyVictimID:               # Hidden error in victim doc.
                # Destroy copy on this shelf.
                cCopy = G.dID2Copy[sCopyVictimID]
                sDocID = cCopy.mGetDocID()
                self.mDestroyCopy(sCopyVictimID)
                # Log the summary line if we just ended a string of misses
                if self.nConsecutiveMisses > 0:
                    lg.logInfo("SERVER","small error t|%6.0f| svr|%s| shelf|%s| consecutive misses|%d|" % (G.env.now,self.sServerID,self.ID,self.nConsecutiveMisses))
                self.nConsecutiveMisses = 0
                lg.logInfo("SERVER","small error t|%6.0f| svr|%s| shelf|%s| hidden failure in copy|%s| doc|%s|" % (G.env.now,self.sServerID,self.ID,sCopyVictimID,sDocID))
                TRC.tracef(3,"FAIL","proc t|%d| sector failure server|%s| qual|%d| shelf|%s| doc|%s| copy|%s|" % (G.env.now,self.sServerID,G.dID2Server[self.sServerID].nQual,self.ID,sDocID,sCopyVictimID))
            else:                           # No victim, hit empty space.
                self.nEmptySectorHits += 1
                TRC.tracef(3,"SHLF","proc mAge_sector shelf|%s| sector error fell in empty space" % (self.ID))
                if self.nConsecutiveMisses == 0:
                    lg.logInfo("SERVER","small error t|%6.0f| svr|%s| shelf|%s| hidden failure in copy|%s|" % (G.env.now,self.sServerID,self.ID,sCopyVictimID))
                self.nConsecutiveMisses += 1
                TRC.tracef(3,"FAIL","proc t|%d| sector failure server|%s| qual|%d| shelf|%s| copy|%s|" % (G.env.now,self.sServerID,G.dID2Server[self.sServerID].nQual,self.ID,sCopyVictimID))

            # Initiate a repair of the dead document.
            # NYI: currently all such failures are silent, so they are 
            #  not detected by the client until audited (or end of run).  

# S h e l f . m S e l e c t V i c t i m C o p y  
    @tracef("SHLF")
    def mSelectVictimCopy(self,mynErrorSize):
        ''' mSelectVictimCopy(errorsize)
            Which doc copy on this shelf, if any, was hit by this error?
            Throw a uniform dart at all the docs on the shelf, see 
            which one gets hit.  Doc size counts.  
        '''
        nRandomSpot = util.makeunif(1,self.nCapacity + mynErrorSize - 1)
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
            TRC.tracef(5,"SHLF","proc SelectVictimCopy0 searchsetup len|%s| loc|%s| dist|%s|" % (nLen,nLoc,nDist))
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
                        TRC.tracef(5,"SHLF","proc SelectVictimCopy5D found victim id|%s| at spot|%s| in[%s,%s]| doc|%s|" % (sCopyID,nRandomSpot,nBottom,nTop,sDocID))
                        # Is this slot still occupied by a live copy?
                        if sCopyID in self.lCopyIDs:
                            sVictimID = sCopyID
                            TRC.tracef(3,"SHLF","proc mSelectVictimCopy NEWD end shelf|%s| spot|%d| hits doc|%s| placed[%d,%d] size|%d| outof|%d|" % (self.ID,nRandomSpot,sVictimID,cCopy.nBlkBegin,cCopy.nBlkEnd, (cCopy.nBlkEnd-cCopy.nBlkBegin+1),self.nCapacity))
                        else:
                            sVictimID = None
                            TRC.tracef(5,"SHLF","proc SelectVictimCopy2D no longer valid copyid|%s| docid|%s|" % (sCopyID,sDocID))
                            self.nMultipleHits += 1
                        break
                    else:
                        nLoc -= nDist
                        TRC.tracef(5,"SHLF","proc SelectVictimCopy3D down spot|%s| intvl|[%s,%s| newloc|%s| newdist|%s|" % (nRandomSpot,nBottom,nTop,nLoc,nDist))
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
                        TRC.tracef(5,"SHLF","proc SelectVictimCopy5U found victim id|%s| at spot|%s| in[%s,%s]| doc|%s|" % (sCopyID,nRandomSpot,nBottom,nTop,sDocID))
                        # Is this slot still occupied by a live copy?
                        if sCopyID in self.lCopyIDs:
                            sVictimID = sCopyID
                            TRC.tracef(3,"SHLF","proc mSelectVictimCopy NEWU end shelf|%s| spot|%d| hits doc|%s| placed[%d,%d] size|%d| outof|%d|" % (self.ID,nRandomSpot,sVictimID,cCopy.nBlkBegin,cCopy.nBlkEnd, (cCopy.nBlkEnd-cCopy.nBlkBegin+1),self.nCapacity))
                        else:
                            sVictimID = None
                            TRC.tracef(5,"SHLF","proc SelectVictimCopy2U no longer valid copyid|%s| docid|%s|" % (sCopyID,sDocID))
                            self.nMultipleHits += 1
                        break
                    else:
                        nLoc += nDist
                        TRC.tracef(5,"SHLF","proc SelectVictimCopy3U up   spot|%s| intvl|[%s,%s| newloc|%s| newdist|%s|" % (nRandomSpot,nBottom,nTop,nLoc,nDist))


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
        # Tell the server that the copy is gone.
        cCopy = G.dID2Copy[mysCopyID]
        sDocID = cCopy.sDocID
        cServer = G.dID2Server[self.sServerID]
        cServer.mDestroyCopy(mysCopyID,sDocID,self.ID)
        # And give back the space it occupied.  
        self.bContig = False
        cDoc = G.dID2Document[sDocID]
        
        # BZZZT: DO NOT put this region back into use.  It has already 
        # suffered an error once and caused a document to fail.  
        #self.nFreeSpace += cDoc.nSize
        TRC.tracef(3,"SHLF","proc mDestroyCopy remove doc|%s| copy|%s| idx|%d| size|%d| from shelf|%s| remainingdocs|%d| free|%d|" % (cCopy.sDocID,mysCopyID,nCopyIndex,cDoc.nSize,self.ID,len(self.lCopyIDs),self.nFreeSpace))
        # And, at long last, destroy the Copy oject itself.
        del cCopy
        return self.ID + "-" + sDocID + "-" + mysCopyID

# S h e l f . m A g e _ s h e l f 
    @tracef("SHLF",level=3)
    def mAge_shelf(self,mynLifeParam):
        ''' An entire shelf fails.  Remove all the docs it contained.
            Eventually, this will trigger a repair event and make the 
            collection more vulnerable during the repair.  
        '''
        nShelfLife = util.makeexpo(mynLifeParam)
        TRC.tracef(3,"SHLF","proc mAge_shelf  time|%d| shelf|%s| next lifetime|%d|khr" % (G.env.now,self.ID,nShelfLife))
        yield G.env.timeout(nShelfLife)

        # S H E L F  F A I L S 
        G.nTimeLastEvent = G.env.now
        self.bAlive = False         # Shelf can no longer be used to store docs.
        TRC.tracef(3,"SHLF","proc mAge_shelf  time|%d| shelf|%s| shelf_error" % (G.env.now,self.ID))
        lg.logInfo("SERVER","storage shelf failed time|%6q.0f| server|%s| shelf|%s| lost |%d| docs" % (G.env.now,self.sServerID,self.ID,len(self.lCopyIDs)))
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
        # (Only a trivial performance improvement, I think, since the shelf
        # will be destroyed and never reused.)  
        # NYI
        # Tell the Server to replace the dead shelf.
        # NYI

# S h e l f . m I s S h e l f A l i v e 
    @tracef("SHLF", level=5)
    def mbIsShelfAlive(self):
        return self.bAlive

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
# Class C O P Y  ( of  D o c u m e n t )
#---------------------------------------

class CCopy(object):
    getID = itertools.count(1).next

    @tracef("COPY")
    def __init__(self,mysDocID,mysClientID,mysServerID):
        self.ID = "X" + str(self.getID())
        G.dID2Copy[self.ID] = self
        G.nCopyLastID = self.ID

        # What document is this a copy of?
        self.sDocID = mysDocID
        self.sClientID = mysClientID
        # Where is this copy being stored?
        self.sServerID = mysServerID
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

    @tracef("COPY")
    def mGetDocID(self):
        return self.sDocID

    @tracef("COPY")
    def mDestroyCopy(self):
        pass


#===========================================================
# C l a s s  L I F E T I M E 
#---------------------------

class CLifetime(object):

    @tracef("LIFE")
    def __init__(self,mysShelfID, myfLifetime, mynGlitchFreq, mynGlitchImpact, mynGlitchHalflife, mynGlitchMaxlife):
        self.fOriginalLifetime = float(myfLifetime)
        self.fCurrentLifetime = self.fOriginalLifetime
        self.sShelfID = mysShelfID
        # Store glitch params. 
        self.nGlitchFreq = mynGlitchFreq
        self.nImpactReductionPct = mynGlitchImpact
        self.nGlitchDecayHalflife = mynGlitchHalflife
        self.nGlitchMaxlife = mynGlitchMaxlife
        # Glitch currently running?
        self.bGlitchActive = False
        self.fGlitchBegin = 0           # Not yet.
        self.nGlitches = 0              # Count glitches on this shelf.
        self.fGlitchTime = 0            # Total time glitches active at some level.

        self.fLn2 = log(2.0)
        self.ID = "LIFE-" + self.sShelfID
        G.dID2Lifetime[self.ID] = self

        # If there are to be any glitches, start the timer. 
        if self.nGlitchFreq > 0:
            G.env.process(self.mScheduleGlitch())

# L i f e t i m e . m S c h e d u l e G l i t c h 
    @tracef("LIFE")
    def mScheduleGlitch(self):
        cShelf = G.dID2Shelf[self.sShelfID]
        bAlive = cShelf.mbIsShelfAlive()
        fNow = G.env.now
        TRC.tracef(3,"LIFE","proc schedule glitch t|%d| shelf|%s| alive|%s|" % (fNow,self.sShelfID,bAlive))
        while bAlive:
            fShelfLife = self.mfCalcCurrentGlitchLifetime(fNow)
            if fShelfLife > 0:
                fShelfInterval = util.makeexpo(fShelfLife)
                TRC.tracef(3,"LIFE","proc schedule glitch life|%.3f| interval|%.3f|" % (fShelfLife,fShelfInterval))
                lg.logInfo("LIFETIME","schedule  t|%6.0f| for shelf|%s| freq|%d| life|%.3f| interval|%.3f|" \
                % \
                (fNow,self.sShelfID,self.nGlitchFreq,fShelfLife,fShelfInterval))
                yield G.env.timeout(fShelfInterval)
                
                # Glitch has now occurred.
                fNow = G.env.now
                self.mGlitchHappens(fNow)
                
            else:
                yield G.env.timeout(G.fInfinity)

# L i f e t i m e . m G l i t c h H a p p e n s 
    @tracef("LIFE")
    def mGlitchHappens(self,myfNow):
        self.bGlitchActive = True
        self.nGlitches += 1
        G.nGlitchesTotal += 1
        lg.logInfo("LIFETIME","glitch    t|%6.0f|  on shelf|%s| num|%s| impactpct|%d| decayhalflife|%d| maxlife|%d|" % (myfNow, self.sShelfID,  self.nGlitches, self.nImpactReductionPct, self.nGlitchDecayHalflife, self.nGlitchMaxlife))
        self.fGlitchBegin = float(G.env.now)
        TRC.tracef(3,"LIFE","proc happens t|%.3f| shelf|%s| num|%s| impact|%d| decayhalflife|%d| maxlife|%d|" % (myfNow, self.sShelfID, self.nGlitches, self.nImpactReductionPct, self.nGlitchDecayHalflife, self.nGlitchMaxlife))
        self.mInjectError(self.nImpactReductionPct, self.nGlitchDecayHalflife, self.nGlitchMaxlife)
        return (self.nGlitches, self.sShelfID)

# L i f e t i m e . m I n j e c t E r r o r 
    @tracef("LIFE")
    def mInjectError(self, mynReduction, mynDecayHalflife, myfNow):
        '''\
        When a glitch occurs, decrease lifetime by some amount, percentage.
        The decrease decays exponentially at some rate until negligible.  
        '''
        self.nReductionPercentage = mynReduction
        self.fDecayHalflife = float(mynDecayHalflife)
        self.fDecayRate = log(2.0) / self.fDecayHalflife
        TRC.tracef(3,"LIFE","proc inject reduct|%s| decayhalflife|%s| decayrate|%s|" % (mynReduction,mynDecayHalflife,self.fDecayRate))
        return self.fDecayRate

# L i f e t i m e . m f C a l c C u r r e n t S e c t o r L i f e t i m e 
    @tracef("LIFE")
    def mfCalcCurrentSectorLifetime(self,myfNow):
        '''
        if glitch in progress
          if glitch is too old
            turn it off
            log expired
            normal lifetime
          else 
            calc reduced lifetime
            if decay below ignore limit
              turn it off
              log below limit
        '''
        if self.bGlitchActive:
            fTimeDiff = myfNow - self.fGlitchBegin
            fDuration = (float(self.nGlitchMaxlife) if self.nGlitchMaxlife > 0 else float(G.fInfinity))
            # If the glitch lifetime has expired, turn it off.
            if fTimeDiff > fDuration:
                TRC.tracef(3,"LIFE","proc glitch lifetime expired id|%s| num|%s| start|%.3f| now|%.3f| maxlife|%s|" % (self.ID, self.nGlitches, self.fGlitchBegin, myfNow, self.nGlitchMaxlife))
                lg.logInfo("LIFETIME","expired   t|%6.0f| shelf|%s| id|%s| num|%s| start|%.3f| now|%.3f| maxlife|%s|" % (myfNow, self.sShelfID, self.ID, self.nGlitches, self.fGlitchBegin, myfNow, self.nGlitchMaxlife))
                self.bGlitchActive = False
                self.fGlitchTime += fTimeDiff
                self.fCurrentLifetime = self.fOriginalLifetime
            else:            
                # The glitch is still current.
                # Carefully calculate the new sector lifetime based on 
                #  some reduction due to glitch and the age of the glitch.
#                fTimeDiff = myfNow - self.fGlitchBegin
                fAgeInHalflives = fTimeDiff / self.nGlitchDecayHalflife
                fExponentialDecay = exp(- self.fLn2 * fAgeInHalflives )
                fReductionFraction= 1.0 * self.nReductionPercentage / 100.0
                self.fCurrentLifetime = 1.0 * self.fOriginalLifetime * (1.0 - fReductionFraction * fExponentialDecay) 
                TRC.tracef(3,"LIFE","proc calcsectorlife num|%s| started|%.3f| age|%.3f| decay|%.3f| reduct|%.3f| currlife|%.3f|" % (self.nGlitches, self.fGlitchBegin, fAgeInHalflives, fExponentialDecay, fReductionFraction, self.fCurrentLifetime))
                # If the glitch has diminished to a low level, 
                #  turn it off.  
                if fExponentialDecay < G.fGlitchIgnoreLimit:
                    self.bGlitchActive = False
                    self.fGlitchTime += fTimeDiff
                    TRC.tracef(3,"LIFE","proc glitch turned off lifeid|%s| num|%s| started|%.3f| age|%.3f| decay|%.3f|" % (self.ID, self.nGlitches, self.fGlitchBegin, fAgeInHalflives, fExponentialDecay))
        else:
            # No current glitch active.  Lifetime is as usual.  
            self.fCurrentLifetime = self.fOriginalLifetime
        return self.fCurrentLifetime

# L i f e t i m e . m f C a l c C u r r e n t G l i t c h L i f e t i m e 
    @tracef("LIFE")
    def mfCalcCurrentGlitchLifetime(self,myfNow):
        """
        fDuration = (float(self.nGlitchMaxlife) if self.nGlitchMaxlife > 0 else float(G.fInfinity))
        TRC.tracef(3,"LIFE","proc glitchlife num|%d| now|%.3f| begin|%.3f| duration|%.3f|" % (self.nGlitches, myfNow, self.fGlitchBegin, fDuration))
        if (myfNow - self.fGlitchBegin) < fDuration:
            fLifetime = self.nGlitchFreq / self.fLn2
        else:
            fLifetime = 0
            if self.bGlitchActive:
                TRC.tracef(3,"LIFE","proc glitch lifetime expired id|%s| num|%s| start|%.3f| now|%.3f| maxlife|%s|" % (self.ID, self.nGlitches, self.fGlitchBegin, myfNow, self.nGlitchMaxlife))
                lg.logInfo("LIFETIME","expired   t|%6.0f| shelf|%s| id|%s| num|%s| start|%.3f| now|%.3f| maxlife|%s|" % (myfNow, self.sShelfID, self.ID, self.nGlitches, self.fGlitchBegin, myfNow, self.nGlitchMaxlife))
            self.bGlitchActive = False
        """
        fLifetime = self.nGlitchFreq / self.fLn2
        return fLifetime

    '''
    How to calculate current sector lifetime?
    decay rates
    0.10 = 0.5 ^ 3.3 => decay to 5% in 3.3 half-life intervals
    0.05 = 0.5 ^ 4.3
    0.01 = 0.5 ^ 6.6
    0.5 = exp(-0.7) (Note: 0.7=0.693=ln(2), not sqrt(2)=0.707)
    halflife = ln(2) / rate    and v-v    rate = ln(2) / halflife
    halflife = ln(2) * exponentiallifetime
    exponentiallifetime = halflife / ln(2)
    lifetime = 1 / rate    and v-v    rate = 1 / lifetime
    
    decaylevel = exp(-ln(2) * (timediff / glitchhalflife))
    losspct = impactpct * decaylevel
    remainpart = (1 - losspct/100)
    currlife = origlife * remainpart
    i.e., 
    currlife = origlife * (1 - ((impactpct/100) * (exp(-ln(2) * time))))
    currlife = origlife * (1 - (impactfraction * decaylevel))
    
    old invocation:
        fLifeParam = util.fnfCalcBlockLifetime(self.nSectorLife*1000, self.nCapacity)
        fSectorLife = util.makeexpo(fLifeParam)
    '''

# L i f e t i m e . m R e p o r t G l i t c h S t a t s 
    @tracef("LIFE")
    def mReportGlitchStats(self):
        dd = dict()
        dd["sShelfID"] = self.sShelfID
        dd["sLifetimeID"] = self.ID
        dd["nGlitchFreq"] = self.nGlitchFreq
        dd["nImpactReductionPct"] = self.nImpactReductionPct
        dd["nGlitchDecayHalflife"] = self.nGlitchDecayHalflife
        dd["nGlitchMaxlife"] = self.nGlitchMaxlife
        dd["nGlitches"] = self.nGlitches
        dd["fGlitchTime"] = self.fGlitchTime
        return dd
    
@tracef("LIFE")
def fnlGetGlitchParams(mysShelfID):
    # Do this through a function in case some calculation is 
    #  necessary someday, e.g., if shelves differ.  
    freq = G.nGlitchFreq
    impact = G.nGlitchImpact
    halflife = G.nGlitchDecay
    maxlife = G.nGlitchMaxlife
    return [freq,impact,halflife,maxlife]


''' TODO
- correlated failures: much trickier calculation of error rate
   depending on number of failures, time of last failure, 
   exponential decay of increased rate since failure, etc.
   I think something this complex belongs here, not in util.py.  
'''

# Edit History:
# 20150222  RBL Make imports explicit.
#               Add CLifetime class for correlated failures.
# 20150316  RBL Add glitches for associated failure.
#               Lifetime calculations are a bloody mess.
# 20150329  RBL Flesh out glitch code and counters.  
#               Clarify sector lifetime calculations and 
#                glitch deactivations for time limit and 
#                for fading.
#               Add logging glitch events.  
#               Add stats reporting.  
# 


# END
