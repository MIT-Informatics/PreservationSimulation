#!/usr/bin/python
# shelf.py

import  simpy
from    NewTraceFac     import  TRC, trace, tracef, NTRC, ntrace, ntracef
import  itertools
from    globaldata      import  G
from    math            import  exp, log
import  util
import  copy
import  logoutput       as lg
from    catchex         import  catchex
from    doccopy         import  CCopy
from    lifetime        import  CLifetime, fnlGetGlitchParams


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
        self.lDocIDs = list()       # Docs currently alive, copied onto this shelf.
        self.lCopyIDs = list()      # Copies currently alive on this shelf.
        self.lDocIDsComplete = list() # Docs, all ever put onto this shelf.
        self.lCopyIDsComplete = list() # Copies, all ever put onto this shelf.  
        self.lCopyTops = [0]        # BlkEnd for each doc ever placed, for searching.
        self.lClientIDs = list()    # From what client did we get this doc (all docs).

        self.nCapacity = mynCapacity
        self.nFreeSpace = mynCapacity
        self.sServerID = mysServerID # Server instance we belong to.
        self.nQual = mynQual
        self.birthdate = G.env.now
        self.bAlive = True          # Shelf failed = False.
        self.nHiWater = 0           # Highest sector used, inclusive.

        self.nSectorHits = 0        # How many sector errors.
        self.nEmptySectorHits = 0   # How many sector errors.
        self.nHitsAboveHiWater = 0  # How many hits out of the occupied region.
        self.nMultipleHits = 0      # How many document slots hit more than once.
        self.bContig = True         # Is the document region still contiguous?
        self.nConsecutiveMisses = 0 # How many misses in a row?

        # Get error rate params 
        self.fLn2 = log(2)
        (self.nSectorHalflife, self.nShelfLife) = G.dShelfParams[self.nQual][0]
        # Sector life now determined by scalar nLifek for all servers.
        self.nSectorHalflife = G.nLifek
        (self.nGlitchFreq, self.nGlitchImpact, self.nGlitchHalflife, 
            self.nGlitchMaxlife, self.nGlitchSpan) = fnlGetGlitchParams(self.ID)
        self.fSectorExponentiallife = util.fnfHalflife2Exponentiallife(
            self.nSectorHalflife)
        self.fLifeParam = util.fnfCalcBlockLifetime(
            self.fSectorExponentiallife*1000, self.nCapacity)

        # Add a CLifetime object, which will schedule glitches if necessary.
        cLifetime = CLifetime(self.ID,self.fLifeParam, self.nGlitchFreq, 
            self.nGlitchImpact, self.nGlitchHalflife, self.nGlitchMaxlife, 
            self.nGlitchSpan)
        self.sSectorLifetimeID = cLifetime.ID
        G.dID2Lifetime[self.sSectorLifetimeID] = cLifetime

        # Start aging processes
        G.env.process(self.mAge_shelf(self.nShelfLife*1000))
        G.env.process(self.mAge_sector())

    @property
    def cServer(self):
        return G.dID2Server[self.sServerID]

# S h e l f . m A c c e p t D o c u m e n t 
    @catchex
    @tracef("SHLF")
    def mAcceptDocument(self, mysDocID, mynDocSize, mysClientID):
        ''' If the shelf and the server are still alive and 
            there is room on the shelf, then add the document 
            and return True.  
            A shelf, once failed, cannot be reused.
            If not, return False.
        '''
        if (self.bAlive 
        and self.nFreeSpace >= mynDocSize 
        and (not self.cServer.bDead)
        ):
            self.mAddDocument(mysDocID, mysClientID)
            return True
        else:
            return False

# S h e l f . m A d d D o c u m e n t 
    @catchex
    @tracef("SHLF")
    def mAddDocument(self, mysDocID, mysClientID):
        ''' Add a document to this shelf and record some information
            in the document itself.
        '''
        self.lDocIDs.append(mysDocID)
        self.lDocIDsComplete.append(mysDocID)
        self.lClientIDs.append(mysClientID)
        cDoc = G.dID2Document[mysDocID]
        nSize = cDoc.nSize

        # Make a copy of the document and shelve that.  
        cCopy = CCopy(mysDocID, mysClientID, self.sServerID)
        sCopyID = cCopy.ID
        TRC.tracef(3,"SHLF","proc mAddDocument made copy|%s| of doc|%s| "
            "from client|%s|" 
            % (sCopyID, mysDocID, mysClientID))

        # Where does document go on this shelf.  Closed interval [Begin,End].
#        nBlkBegin = self.nCapacity - self.nFreeSpace
        # BZZZT: Never reuse space.  Any empty space in the area that 
        # *used* to be occupied by documents has already been damaged
        # and destroyed a document.  Do not reuse the space.  
        # Yeah, I know it's all just hypothetical, but why not.  
        nBlkBegin = self.nHiWater + 1
        self.nFreeSpace -= nSize
        nBlkEnd = nBlkBegin + nSize - 1
        if nBlkEnd > self.nHiWater:
            self.nHiWater = nBlkEnd         # Last block used.  
#        sShelfID = self.ID
#        sServerID = self.sServerID
        cCopy.mShelveCopy(self.sServerID, self.ID, nBlkBegin, nBlkEnd)
        self.lCopyIDs.append(sCopyID)
        self.lCopyIDsComplete.append(sCopyID)
        self.lCopyTops.append(nBlkEnd)

        cDoc.mCopyPlacedOnServer(sCopyID, self.sServerID)
        TRC.tracef(5,"SHLF","proc mAddDocument add doc|%s| to shelf|%s| "
            "size|%d| remaining|%d|" 
            % (mysDocID,self.ID,nSize,self.nFreeSpace))
        
        return self.sServerID+"+"+self.ID+"+"+mysDocID+"+"+sCopyID


# F A I L U R E S 

# S h e l f . m A g e _ s e c t o r 
    @catchex
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
            TRC.tracef(3, "SHLF", "proc mAge_sector time|%d| shelf|%s| "
                "next interval|%.3f|hr from life rate|%.3f|hr" 
                % (G.env.now, self.ID, fSectorLifeInterval, fLifetimeNow))
            yield G.env.timeout(fSectorLifeInterval)

            # S E C T O R  E R R O R
            self.nSectorHits += 1
            G.nTimeLastEvent = G.env.now
            TRC.tracef(3, "SHLF", "proc mAge_sector time|%d| shelf|%s| "
                "Sector_error hits|%d| emptyhits|%d|" 
                % (G.env.now, self.ID, self.nSectorHits, self.nEmptySectorHits))

            # Select a victim Document, probability proportional to size.
            # Small error, size=1.  What doc dies as a result?
            sCopyVictimID = self.mSelectVictimCopy(mynErrorSize=1)

            # New version: compress strings of consecutive misses into single line.
            # Normally we log one line per error regardless of whether it hits or 
            # misses a document.  That results in hideously long log files for 
            # sparse storage structures, like small docs on large shelf. 
            # Count consecutive misses, and issue one summary line before the 
            # next hit.
            # CANDIDATE FOR REFACTORING
            if sCopyVictimID:               # Hidden error in victim doc.
                # Destroy copy on this shelf.
                cCopy = G.dID2Copy[sCopyVictimID]
                sDocID = cCopy.mGetDocID()
                self.mDestroyCopy(sCopyVictimID)
                # Log the summary line if we just ended a string of misses
                if self.nConsecutiveMisses > 0:
                    lg.logInfo("SERVER", "small error t|%6.0f| svr|%s| "
                        "shelf|%s| consecutive misses|%d|" 
                        % (G.env.now, self.sServerID, self.ID, 
                        self.nConsecutiveMisses))
                self.nConsecutiveMisses = 0
                lg.logInfo("SERVER", "small error t|%6.0f| svr|%s| "
                    "shelf|%s| hidden failure in copy|%s| doc|%s|" 
                    % (G.env.now,self.sServerID,self.ID,sCopyVictimID,sDocID))
                TRC.tracef(3, "FAIL", "proc t|%d| sector failure server|%s| "
                    "qual|%d| shelf|%s| doc|%s| copy|%s|" 
                    % (G.env.now, self.sServerID, 
                    G.dID2Server[self.sServerID].nQual, self.ID, sDocID, 
                    sCopyVictimID))
            else:                           # No victim, hit empty space.
                self.nEmptySectorHits += 1
                TRC.tracef(3, "SHLF", "proc mAge_sector shelf|%s| "
                    "sector error fell in empty space" 
                    % (self.ID))
                if self.nConsecutiveMisses == 0:
                    lg.logInfo("SERVER", "small error t|%6.0f| svr|%s| "
                        "shelf|%s| hidden failure in copy|%s|" 
                        % (G.env.now, self.sServerID, self.ID, sCopyVictimID))
                self.nConsecutiveMisses += 1
                TRC.tracef(3, "FAIL", "proc t|%d| sector failure server|%s| "
                    "qual|%d| shelf|%s| copy|%s|" 
                    % (G.env.now, self.sServerID, 
                    G.dID2Server[self.sServerID].nQual, self.ID, sCopyVictimID))
            # Initiate a repair of the dead document.
            # BZZZT NYI: currently all such failures are silent, so they are 
            #  not detected by the client until audited (or end of run).  
        # Shelf is no longer alive, so we do not notice or schedule 
        #  future sector errors.  Log the event.  
        lg.logInfo("SHELF ", "t|%6.0f| dead shelf|%s| of svr|%s|, "
            "no future errors" 
            % (G.env.now, self.ID, self.sServerID))

# S h e l f . m S e l e c t V i c t i m C o p y  
    @catchex
    @tracef("SHLF")
    def mSelectVictimCopy(self, mynErrorSize):
        ''' Which doc copy on this shelf, if any, was hit by this error?
            Throw a uniform dart at all the docs on the shelf, see 
            which one gets hit, or dart falls into empty space.  Doc size counts.  
        '''
        nRandomSpot = util.makeunif(1, self.nCapacity + mynErrorSize - 1)
        nLoc = 0
        TRC.tracef(5, "SHLF", "proc SelectVictimCopy0 wherehit spot|%s| "
            "hiwater|%s|  shelfid|%s| capacity|%s|" 
            % (nRandomSpot,self.nHiWater,self.ID,self.nCapacity))
        # First, check to see if the failure is maybe in an occupied region.  
        if nRandomSpot <= self.nHiWater:
            # Find the document hit by the error.  May have been hit before, too.  
            # New version, vanilla binary search with adjacent interval checking
            #  on list of all locations assigned on this shelf.
            # After you find the location, check to see that it 
            #  is still occupied by live copy.  
            nLen = len(self.lCopyIDsComplete)
            nDist = (nLen + 1) / 2
            nLoc = nDist
            TRC.tracef(5, "SHLF", "proc SelectVictimCopy0 searchsetup len|%s| "
                "loc|%s| dist|%s|" 
                % (nLen, nLoc, nDist))
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
                        TRC.tracef(5, "SHLF", "proc SelectVictimCopy5D "
                            "found victim id|%s| at spot|%s| in[%s,%s]| " 
                            "doc|%s|" 
                            % (sCopyID, nRandomSpot, nBottom, nTop, sDocID))
                        # Is this slot still occupied by a live copy?
                        if sCopyID in self.lCopyIDs:
                            sVictimID = sCopyID
                            TRC.tracef(3, "SHLF", "proc mSelectVictimCopy "
                                "NEWD end shelf|%s| spot|%d| hits doc|%s| "
                                "placed[%d,%d] size|%d| outof|%d|" 
                                % (self.ID, nRandomSpot, sVictimID, 
                                cCopy.nBlkBegin, cCopy.nBlkEnd, 
                                (cCopy.nBlkEnd-cCopy.nBlkBegin+1), 
                                self.nCapacity))
                        else:
                            sVictimID = None
                            TRC.tracef(5, "SHLF", "proc SelectVictimCopy2D "
                                "no longer valid copyid|%s| docid|%s|" 
                                % (sCopyID, sDocID))
                            self.nMultipleHits += 1
                        break
                    else:
                        nLoc -= nDist
                        TRC.tracef(5, "SHLF", "proc SelectVictimCopy3D "
                            "down spot|%s| intvl|[%s,%s| newloc|%s| newdist|%s|" 
                            % (nRandomSpot, nBottom, nTop, nLoc, nDist))
                else:
                    # Higher than top, look up.
                    if nRandomSpot <= self.lCopyTops[nLoc+1]:
                        # Found to right of nLoc.
                        # Reevaluate ids and locations to the next slot 
                        #  on the right.  
                        sCopyID = self.lCopyIDsComplete[nLoc+1-1]
                        sDocID = self.lDocIDsComplete[nLoc+1-1]
                        cCopy = G.dID2Copy[sCopyID]
                        nBottom = self.lCopyTops[nLoc+1-1]
                        sCopyID = self.lCopyIDsComplete[nLoc+1-1]
                        TRC.tracef(5, "SHLF", "proc SelectVictimCopy5U "
                            "found victim id|%s| at spot|%s| in[%s,%s]| doc|%s|" 
                            % (sCopyID, nRandomSpot, nBottom, nTop, sDocID))
                        # Is this slot still occupied by a live copy?
                        if sCopyID in self.lCopyIDs:
                            sVictimID = sCopyID
                            TRC.tracef(3, "SHLF", "proc mSelectVictimCopy NEWU "
                                "end shelf|%s| spot|%d| hits doc|%s| "
                                "placed[%d,%d] size|%d| outof|%d|" 
                                % (self.ID, nRandomSpot, sVictimID, 
                                cCopy.nBlkBegin, cCopy.nBlkEnd, 
                                (cCopy.nBlkEnd-cCopy.nBlkBegin+1), 
                                self.nCapacity))
                        else:
                            sVictimID = None
                            TRC.tracef(5, "SHLF", "proc SelectVictimCopy2U "
                                "no longer valid copyid|%s| docid|%s|" 
                                % (sCopyID, sDocID))
                            self.nMultipleHits += 1
                        break
                    else:
                        nLoc += nDist
                        TRC.tracef(5, "SHLF", "proc SelectVictimCopy3U up   "
                            "spot|%s| intvl|[%s,%s| newloc|%s| newdist|%s|" 
                            % (nRandomSpot, nBottom, nTop, nLoc, nDist))

        else:   # Outside hiwater area, just count as a miss.
            TRC.tracef(3, "SHLF", "proc mSelectVictimCopy shelf|%s| spot|%d| "
                "above hiwater|%s| empty" 
                % (self.ID, nRandomSpot, self.nHiWater))
            sVictimID = None
            self.nHitsAboveHiWater += 1
        return sVictimID

# S h e l f . m D e s t r o y C o p y  
    @catchex
    @tracef("SHLF",level=3)
    def mDestroyCopy(self,mysCopyID):
        try:
            nCopyIndex = self.lCopyIDs.index(mysCopyID)
        except ValueError:
            TRC.tracef(0, "SHLF", "BUGCHECK copyID not found for removal|%s|" 
                % (mysCopyID))
            return False
        # Remove doc and copy from current lists.  
        del self.lCopyIDs[nCopyIndex]
        del self.lDocIDs[nCopyIndex]
        # Tell the server that the copy is gone.
        cCopy = G.dID2Copy[mysCopyID]
        sDocID = cCopy.sDocID
        self.cServer.mDestroyCopy(mysCopyID, sDocID, self.ID)
        # And give back the space it occupied.  
        self.bContig = False
        cDoc = G.dID2Document[sDocID]
        
        # BZZZT: DO NOT put this region back into use.  It has already 
        # suffered an error once and caused a document to fail.  
        #self.nFreeSpace += cDoc.nSize
        TRC.tracef(3, "SHLF", "proc mDestroyCopy remove doc|%s| copy|%s| "
            "idx|%d| size|%d| from shelf|%s| remainingdocs|%d| free|%d|" 
            % (cCopy.sDocID, mysCopyID, nCopyIndex, cDoc.nSize, self.ID, 
            len(self.lCopyIDs), self.nFreeSpace))
        # And, at long last, destroy the Copy oject itself.
        del cCopy
        return self.ID + "-" + sDocID + "-" + mysCopyID

# S h e l f . m A g e _ s h e l f 
# BZZZT: This isn't used anymore.  We now model server failures with glitches.
    @tracef("SHLF",level=3)
    def mAge_shelf(self, mynLifeParam):
        ''' An entire shelf fails.  Remove all the docs it contained.
            Eventually, this will trigger a repair event and make the 
            collection more vulnerable during the repair.  
        '''
        fShelfLife = util.makeexpo(mynLifeParam)
        TRC.tracef(3, "SHLF", "proc mAge_shelf  time|%d| shelf|%s| "
            "next lifetime|%.3f|khr" 
            % (G.env.now,self.ID,fShelfLife))
        yield G.env.timeout(fShelfLife)

        # S H E L F  F A I L S 
        G.nTimeLastEvent = G.env.now
        self.bAlive = False         # Shelf can no longer be used to store docs.
        TRC.tracef(3, "SHLF", "proc mAge_shelf  time|%d| shelf|%s| shelf_error" 
            % (G.env.now,self.ID))
        lg.logInfo("SERVER", "storage shelf failed time|%6q.0f| server|%s| "
            "shelf|%s| lost |%d| docs" 
            % (G.env.now,self.sServerID,self.ID,len(self.lCopyIDs)))
        # This whole shelf is a goner.  Kill it. 
        TRC.tracef(5, "SHLF", "proc mAge_shelf kill contents ldocs|%s| "
            "lcopies|%s|" 
            % (self.lDocIDs,self.lCopyIDs)) 
        # Note that we have to copy the list before modifying it and 
        # iterate over the copy of the list.  
        # Standard problem with updating an iterable inside the for loop.
        templCopyIDs = copy.deepcopy(self.lCopyIDs)
        for sCopyID in templCopyIDs:
            sDocID = G.dID2Copy[sCopyID].sDocID
            self.mDestroyCopy(sCopyID)
            G.dID2Server[self.sServerID].mDestroyDocument(sDocID,self.ID)
            self.mReportDocumentLost(sDocID)
        TRC.tracef(3, "FAIL", "proc t|%d| shelf failure server|%s| qual|%d| "
            "shelf|%s| docs|%d|" 
            % (G.env.now, self.sServerID, G.dID2Server[self.sServerID].nQual, 
            self.ID,len(templCopyIDs)))
        # Rescind any pending sector error aging for this shelf.
        # (Only a trivial performance improvement, I think, since the shelf
        # will be destroyed and never reused.)  
        # NYI
        # Tell the Server to replace the dead shelf.
        # NYI

# S h e l f . m I s S h e l f A l i v e 
    @catchex
    @tracef("SHLF")
    def mbIsShelfAlive(self):
        return self.bAlive

# S h e l f . m R e p o r t D o c u m e n t L o s t 
    @catchex
    @tracef("SHLF")
    def mReportDocumentLost(self,mysDocID):
        cDoc = G.dID2Document[mysDocID]
        sClientID = cDoc.sClientID
        cClient = G.dID2Client[sClientID]
        cClient.mDocFailedOnServer(mysDocID,self.sServerID)
        return self.sServerID +"+"+ self.ID +"+"+ mysDocID

# S h e l f . m R e p o r t U s e S t a t s 
    @catchex
    @tracef("SHLF")
    def mReportUseStats(self):
        ''' Return ID,server ID,quality,capacity,high water mark,currently used
        '''
        return (self.ID, self.sServerID, self.nQual, 
            self.fSectorExponentiallife, self.nCapacity,self.nHiWater+1, 
            self.nCapacity-self.nFreeSpace)

# S h e l f . m R e p o r t E r r o r S t a t s 
    @catchex
    @tracef("SHLF")
    def mReportErrorStats(self):
        ''' 
        Return ID,server ID,quality,sector hits,empty sector hits,alive flag
        '''
        return (self.ID, self.sServerID, self.nQual, self.nSectorHits, 
            self.nEmptySectorHits, self.bAlive, self.nHitsAboveHiWater, 
            self.nMultipleHits)

# S h e l f . m K i l l S h e l f 
    def mKillShelf(self):
        ''' Declare shelf el croako and empty it of documents. '''
        lg.logInfo("SHELF ", "t|%6.0f| kill storage shelf|%s| of server|%s|" 
            % (G.env.now, self.ID, self.sServerID))
        self.bAlive = False
        self.mDestroyShelf()

# S h e l f . m D e s t r o y S h e l f 
    @catchex
    @tracef("SHLF")
    def mDestroyShelf(self):
        ''' Nuke all the copies on the shelf.  
            Can't delete the CShelf object, however.
        '''
        NTRC.ntracef(3, "SHLF", "proc mDestroyShelf1 shelf|%s| "
            "has ncopies|%s|" 
            % (self.ID, len(self.lCopyIDs)))
        lg.logInfo("SHELF ", "t|%6.0f| destroy shelf|%s| "
            "of svr|%s| ncopies|%s|" 
            % (G.env.now, self.ID, self.sServerID, 
            len(self.lCopyIDs)))
        lAllCopyIDs = self.lCopyIDs[:]  # DANGER: list modified inside loop, 
                                        #  requires deepcopy.
        for sCopyID in lAllCopyIDs:
                self.mDestroyCopy(sCopyID)

# Shelf.mCorrFailHappensToMe
    @catchex
    @tracef("SHLF")
    def mCorrFailHappensToMe(self):
        cLifetime = G.dID2Lifetime[self.sSectorLifetimeID]
        cLifetime.mCorrFailHappensToMe()
        pass

# Edit history:
# 20150812  RBL Move CShelf from server.py to its own file.  
# 20160115  RBL Use util's calculation from halflife to exponentiallife.
#               Add exponentiallife to use stats report.
# 20160223  RBL Correct some old, possibly misleading, comments.
# 20160224  RBL Add routines to catch correlated failures.
# 20170102  RBL Add routine to kill shelf and empty it of doc copies. 
#               Add logging for several shelf-death events.   
#               PEP8-ify most of the trace/log and comment lines.  
# 

#END

