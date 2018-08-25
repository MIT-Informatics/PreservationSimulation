#!/usr/bin/python
# audit2.py
# This is the meanest, nastiest, ugliest, most convoluted code 
#  in the entire project.  See below for excuses and apologies.  

'''\
See commentary at end about actual algorithms. 
'''
from    globaldata      import  G
import  itertools
import  util
import  logoutput       as lg
from    NewTraceFac     import  NTRC, ntrace, ntracef
import  math
import  collections     as cc
from    catchex         import  catchex
from    shock           import  CShock


#===========================================================
# C l a s s   C A u d i t 2
#--------------------------
class CAudit2(object):
    '''\
    Procedures for auditing collections kept on 
    remote servers.  Clients will create one instance
    of this class for each collection (across all servers).
    Collection audits run asynchronously.  
    '''
    getID = itertools.count(1).next

    @ntracef("AUD2")
    def __init__(self, mysClientID, mysCollectionID, 
            mynInterval=G.nAuditCycleInterval):
        self.ID = "A" + str(self.getID())
        G.dID2Audit[self.ID] = self
        self.TYPE = "CAudit2"
        self.sClientID = mysClientID
        self.sCollectionID = mysCollectionID
        self.nCycleInterval = mynInterval
        self.nSegments = G.nAuditSegments

        # Per-audit data
        self.nNumberOfCycles = 0
        self.nRepairsThisCycle = 0

        self.nRepairsTotal = 0
        self.nPermanentLosses = 0
        self.nRepairsMajority = 0
        self.nRepairsMinority = 0

        # Per-segment data
        self.lDocsThisSegment = list()
        self.dlDocsDamagedOnServers = cc.defaultdict(list)
        self.lDocsRepairedMajority = list()
        self.lDocsRepairedMinority = list()
        self.lDocsPermanentlyLost = list()
        self.dDocsAlreadyLost = dict()
        
        # List of 2-tuples of serverID and collectionID for dead servers.
        self.stDeadServerIDs = set()

        # Start the free-running process of audit cycles for 
        # this collection.
        G.env.process(self.mAuditCycle(self.nCycleInterval,self.nSegments))


# C A u d i t 2 . m A u d i t C y c l e 
    @ntracef("AUD2")
    def mAuditCycle(self,mynCycleInterval,mynSegments):
        '''\
        SimPy generator to schedule audit cycles for this collection.
        Starts an async process that ticks every 
        audit cycle forever.
        '''
        # Initially, wait for some small random interval
        # so that client audit cycles are not synchronized,
        # like Ethernet collision retry waits. 
        nRandTime = util.makeunif(0,mynCycleInterval/20)
# Nope, not any more.  No need for the random offset since there is
#  only one auditor.
#        yield G.env.timeout(nRandTime)
        # And now wait for one segment interval before starting the first seg.
        #  Seems odd, but consider an annual audit in quarterly segments:
        #  you don't want to wait a whole year before starting quarterly audits; 
        #  start after the first quarter.  
        nSegmentInterval = self.mCalcSegmentInterval(mynCycleInterval, 
            mynSegments)
        yield G.env.timeout(nSegmentInterval)
        
        while True:
            lg.logInfo("AUDIT2", "begin cycle t|%10.3f| auditid|%s| type|%s| "
                "cycle|%s| cli|%s| coll|%s| interval|%s| nsegments|%s|" 
                % (G.env.now, self.ID, self.TYPE, self.nNumberOfCycles, 
                self.sClientID, self.sCollectionID, mynCycleInterval, 
                mynSegments))
            
            # Start the collection audit and wait for it to finish.
            tCycleStartTime = G.env.now
            self.nRepairsThisCycle = 0
            eSyncEvent = G.env.event()
            G.env.process(
                self.mAuditCollection(mynCycleInterval, G.nAuditSegments, 
                self.sCollectionID, eSyncEvent))
            yield eSyncEvent

            lg.logInfo("AUDIT2", "end cycle   t|%10.3f| auditid|%s| cycle|%s| "
                "cli|%s| coll|%s| repairs|%d| total|%d| perms|%d| "
                "majority|%s| minority|%d|" 
                % (G.env.now, self.ID, self.nNumberOfCycles, self.sClientID, 
                self.sCollectionID, self.nRepairsThisCycle, 
                self.nRepairsTotal, self.nPermanentLosses, 
                self.nRepairsMajority, self.nRepairsMinority))

            self.nNumberOfCycles += 1
            tNextCycleStartTime = tCycleStartTime + mynCycleInterval
            yield G.env.timeout(tNextCycleStartTime - G.env.now)

# C A u d i t 2 . m A u d i t C o l l e c t i o n 
    @ntracef("AUD2")
    def mAuditCollection(self, mynCycleInterval, mynSegments, mysCollectionID, 
            myeCallerSyncEvent):
        '''\
        SimPy generator to audit an entire collection.
        Divide the collection into segments and schedule audits
        for each segment in turn.
        '''
        fTimeCycleBegin = G.env.now
        lg.logInfo("AUDIT2","begin colln t|%10.3f| auditid|%s| cycle|%s| cli|%s| coll|%s|" % (G.env.now,self.ID,self.nNumberOfCycles,self.sClientID,self.sCollectionID))

        for iThisSegment in range(mynSegments):
            tSegmentStartTime = G.env.now
            nSegmentInterval = self.mCalcSegmentInterval(mynCycleInterval, 
                mynSegments)
            bLastSegment = (iThisSegment == mynSegments-1)

            self.lDocsThisSegment = self.mIdentifySegment(mysCollectionID, 
                mynSegments, iThisSegment)
            eSyncEvent = G.env.event()
            G.env.process(
                self.mAuditSegment(iThisSegment, self.lDocsThisSegment, 
                mysCollectionID, eSyncEvent))
            # Wait for completion of segment and its allotted time.
            yield eSyncEvent
            tNextSegmentStartTime = tSegmentStartTime + nSegmentInterval
            NTRC.tracef(3, "AUD2", "proc AuditCollection1 now|%s| tstart|%s| "
                "tnext|%s| tinterval|%s| blastseg|%s|" 
                % (G.env.now, tSegmentStartTime, tNextSegmentStartTime, 
                nSegmentInterval, bLastSegment))
            yield G.env.timeout(tNextSegmentStartTime - G.env.now)
        
        fTimeCycleEnd = G.env.now
        self.fTimeCycleLength = fTimeCycleEnd - fTimeCycleBegin
        lg.logInfo("AUDIT2", "end colln   t|%10.3f| auditid|%s| cycle|%s| "
            "cli|%s| coll|%s| repairs|%d| total|%d| perms|%d| "
            "majority|%s| minority|%d| duration|%9.3f|" 
            % (G.env.now, self.ID, self.nNumberOfCycles, self.sClientID, 
            self.sCollectionID, self.nRepairsThisCycle, self.nRepairsTotal, 
            self.nPermanentLosses, self.nRepairsMajority, 
            self.nRepairsMinority, self.fTimeCycleLength))
        # Tell the caller that we finished.
        myeCallerSyncEvent.succeed(value=self.nNumberOfCycles)

# C A u d i t 2 . m A u d i t S e g m e n t 
    @catchex
    @ntracef("AUD2")
    def mAuditSegment(self, mynThisSegment, mylDocs, mysCollectionID, 
            myeCallerSyncEvent):
        '''\
        SimPy generator to audit one segment of a collection.
        This does all the work.  
        This is the single worst, most confusing, most fragile, and 
         most awful code in the entire program.  Unfortunately, in 
         Python 2, one cannot yield from a vanilla function, only
         from a generator, so all that crap, and its convoluted 
         conditional logic, is in here.  
         *This* is the meanest, nastiest, ugliest father-raper of them all.
        '''

        lg.logInfo("AUDIT2", "begin segmt t|%10.3f| auditid|%s| cycle|%s| "
            "seg|%s| cli|%s| coll|%s| ndocs|%s|range %s-%s|" 
            % (G.env.now, self.ID, self.nNumberOfCycles, mynThisSegment, 
            self.sClientID, self.sCollectionID, len(mylDocs), 
            mylDocs[0], mylDocs[-1]))
    
        ###seize network resource
        # Seize the network resource so this audit cycle 
        # can use it exclusively.
        # The "with" should take care of releasing it
        cClient = G.dID2Client[self.sClientID]
        with cClient.NetworkBandwidthResource.request() as reqnetwork:
            fNetworkWaitBegin = G.env.now

            ###wait if necessary
            result = yield reqnetwork       # Wait for network to be free.
            fNetworkWaitEnd = G.env.now
            fNetworkWaitTime = fNetworkWaitEnd - fNetworkWaitBegin

            ###log result
            # Log event if we had to wait, or not, for the network to be free.  
            lg.logInfo("AUDIT2", "grabnetwork t|%10.3f| auditid|%s| cli|%s| "
                "coll|%s| seg|%s| delay|%9.3f|" 
                % (G.env.now, self.ID, self.sClientID, self.sCollectionID, 
                mynThisSegment, fNetworkWaitTime))
            # And restart the duration clock after the unproductive wait.
            fTimeCycleBegin = G.env.now
            # So much for timekeeping.  Now do some actual work.

            # P h a s e  0: Check to see if any servers have died of old age, 
            #  possibly from being weakened by shock.  If so, they get killed
            #  now so that this audit segment will discover the loss.  
            nResult = CShock.cmBeforeAudit()

            # P h a s e  1: Check servers for copies of docs, record losses.
            # Docs already permanently lost will not be put on the damaged list.
            self.dlDocsDamagedOnServers = cc.defaultdict(list)
            cCollection = G.dID2Collection[mysCollectionID]
            # foreach server used for this collection
            for sServerID in cCollection.lServerIDs:
                cServer = G.dID2Server[sServerID]
                ###foreach doc
                # foreach doc in this segment
                for sDocID in self.lDocsThisSegment:
                    cDoc = G.dID2Document[sDocID]
                    # If the doc is still on the server, retrieve it
                    #  and spend time doing that.
                    # If not, then record that doc damaged on this server. 
                    fTransferTime = self.mRetrieveDoc(sDocID,sServerID)
    
                    ###if okay
                    if fTransferTime:
                        NTRC.tracef(3, "AUD2", "proc AuditSegment3 retrieve "
                            "t|%10.3f| doc|%s| svr|%s| xfrtim|%f|" 
                            % (G.env.now, sDocID, sServerID, fTransferTime))
                        ###yield timeout
                        yield G.env.timeout(fTransferTime)
                    else:
                        if self.mIsDocumentLost(sDocID):
                            pass    # Do not complain if doc already known to be lost.
                        else:
                            # If copy is missing here, save server in 
                            #  lost-list for doc.
                            self.dlDocsDamagedOnServers[sDocID].append(sServerID)
                            NTRC.tracef(5, "AUD2", "proc AuditSegment2 doc|%s| "
                                "svr|%s| lost on|%s|" 
                                % (sDocID, sServerID, 
                                self.dlDocsDamagedOnServers[sDocID]))
                            ###log copy missing on some server
                            lg.logInfo("AUDIT2", "copymissing t|%10.3f| "
                                "doc|%s| svr|%s| aud|%s-c%s-s%s| cli|%s| "
                                "coll|%s|" 
                                % (G.env.now, sDocID, sServerID, self.ID, 
                                self.nNumberOfCycles, mynThisSegment, 
                                self.sClientID, self.sCollectionID))
                # end foreach doc
            # end foreach server used for collection

            '''NOTE: Phase 2 here can be factored out of this function entirely
                because it does not yield or otherwise molest the clock.
                But refactoring must be done carefully because it consumes
                and supplies data from phases 1 and 3.  
            '''

            # P h a s e  2: Record severity (majority/minority/permanent) of copy losses.
            # NOTE: This arithmetic seems to be reasonable for all numbers
            #  greater than two, but one copy remaining out of two is judged 
            #  to be a majority, so a repair from that single remaining copy
            #  is labeled a majority repair.  Seems kinda wrong.  
            # Would love to split the logic of this routine into separate
            #  functions; when you're indented seven levels, your logic is,
            #  um, hard to explain.  But we cannot yield from sub-functions, 
            #  at least not in Python2.  
            nServers = len(cCollection.lServerIDs)
            nMajority = (len(cCollection.lServerIDs)+1) / 2 # recall that
                                                            #  int div truncates

            ###foreach doc on damaged list
            for sDocID in sorted(self.dlDocsDamagedOnServers.keys(), 
                key=util.fniNumberFromID):

                ###count docs on all servers
                lDocLostOnServers = self.dlDocsDamagedOnServers[sDocID]
                nCopiesLost = len(lDocLostOnServers)
                nCopiesLeft = nServers - nCopiesLost
                # How many copies left: none, a lot, a few?
                NTRC.tracef(3, "AUD2", "proc AuditSegment1 doc|%s| nsvr|%s| "
                    "loston|%s| nleft|%s|" 
                    % (sDocID, nServers, lDocLostOnServers, nCopiesLeft))

                ###if doc not lost
                ###    assess majority/minority/lost
                if nCopiesLeft == 0:                    # N O N E  remain
                    # Report permanent loss, one ping only.
                    # Do not double-count docs already lost.  Doc will not
                    #  be put onto damaged list if already lost.
                    sRepair = "permloss"
                    lg.logInfo("AUDIT2", "perm loss   t|%10.3f| doc|%s| "
                        "aud|%s-c%s-s%s| cli|%s| coll|%s|" 
                        % (G.env.now, sDocID, self.ID, self.nNumberOfCycles, 
                        mynThisSegment, self.sClientID, self.sCollectionID))
                    self.mRecordDocumentLost(sDocID)
                else:
                    ###doc is repairable; determine majority/minority
                    if nCopiesLeft >= nMajority:      # M A J O R I T Y  remain
                        sRepair = "majority"
                    else:                             # M I N O R I T Y  remain
                        sRepair = "minority"
                    ###log repair type for doc
                    lg.logInfo("AUDIT2", "%s rp t|%10.3f| doc|%s| "
                        "aud|%s-c%s-s%s| cli|%s| coll|%s|" 
                        % (sRepair, G.env.now, sDocID, self.ID, 
                        self.nNumberOfCycles, mynThisSegment, self.sClientID, 
                        self.sCollectionID))

                # P h a s e  3: repair damaged docs, if possible.
                ###foreach server on which doc was damaged
                # Put a copy back on each server where it is missing.  
                for sServerID in lDocLostOnServers:
                    if nCopiesLeft > 0:
                        ###repair
                        fTransferTime = self.mRepairDoc(sDocID,sServerID)
                        '''\
                        If the repair returns False instead of a time, 
                        then that server is no longer accepting documents.
                        Remove that server from the list, invalidate all 
                        its copies.  Then tell the client to find a new 
                        server and re-place the entire collection.  
                        Schedule this notification to occur at the end of the
                        audit cycle or segment to avoid confusing the 
                        ongoing evaluation.  Auditor informs client: oops,
                        you seem to be missing a server; and client takes
                        corrective action at that time.  
                        Send collectionID and serverID to clientID.
                        '''
    
                        ###if not okay ie server dead
                        if fTransferTime == False:
                            self.stDeadServerIDs.add((sServerID, 
                                self.sCollectionID))
                            lg.logInfo("AUDIT2", "dead server t|%10.3f| "
                                "doc|%s| aud|%s| cli|%s| coll|%s| svr|%s|" 
                                % (G.env.now, sDocID, self.ID, self.sClientID, 
                                self.sCollectionID, sServerID))
                        else:
                            ###log repair effected
                            NTRC.tracef(3, "AUD2", "proc AuditSegment4 repair "
                                "t|%10.3f| doc|%s| svr|%s| xfrtim|%f| type|%s|" 
                                % (G.env.now, sDocID, sServerID, fTransferTime, 
                                sRepair))
                            yield G.env.timeout(float(fTransferTime))
                            lg.logInfo("AUDIT2", "repair doc  t|%10.3f| "
                                "doc|%s| aud|%s| cli|%s| coll|%s| svr|%s| "
                                "from %s copies|%d|" 
                                % (G.env.now, sDocID, self.ID, self.sClientID, 
                                self.sCollectionID, sServerID, sRepair, 
                                nCopiesLeft))
    
                            ###count repair as type maj/min for audit and doc
                            # If repair succeeded, record and count it.
                            if sRepair == "majority":
                                self.mRecordDocumentMajorityRepair(sDocID)
                            else:
                                self.mRecordDocumentMinorityRepair(sDocID)
                # end foreach server that lost this doc
            # end foreach damaged doc

            lg.logInfo("AUDIT2", "end   segmt t|%10.3f| auditid|%s| "
                "cycle|%s| seg|%s| cli|%s| coll|%s| ndocs|%s|" 
                % (G.env.now, self.ID, self.nNumberOfCycles, mynThisSegment, 
                self.sClientID, self.sCollectionID, len(mylDocs)))
    
            # After all that, tell the caller we finished.
            myeCallerSyncEvent.succeed(value=mynThisSegment)
            lg.logInfo("AUDIT2", "rls network t|%10.3f| auditid|%s| "
                "cli|%s| coll|%s| seg|%s|" 
                % (G.env.now, self.ID, self.sClientID, self.sCollectionID, 
                mynThisSegment))
        # end network resource

        # If we saw any dead servers during this segment, inform the clients.
        for (sDeadServerID, sDeadCollectionID) in self.stDeadServerIDs:
            cCollection = G.dID2Collection[self.sCollectionID]
            cClient = G.dID2Client[cCollection.sClientID]
            NTRC.ntracef(3, "AUD2", "proc t|%10.3f| inform dead server "
                "auditid|%s| cli|%s| coll|%s| svr|%s| doc|%s|" 
                % (G.env.now, self.ID, self.sClientID, self.sCollectionID, 
                sServerID, sDocID))
            cClient.mServerIsDead(sDeadServerID, sDeadCollectionID)
        self.stDeadServerIDs = set()

    # end def

# A u d i t . m R e c o r d D o c u m e n t L o s t 
    @ntracef("AUD2")
    def mRecordDocumentLost(self,mysDocID):
        self.nPermanentLosses += 1          # WARNING: not idempotent.
        cDoc = G.dID2Document[mysDocID]
        cDoc.mMarkLost()
        return self.nPermanentLosses

# A u d i t . m I s D o c u m e n t L o s t 
    @ntracef("AUD2",level=5)
    def mIsDocumentLost(self,mysDocID):
        cDoc = G.dID2Document[mysDocID]
        return cDoc.mIsLost()

# A u d i t . m R e c o r d D o c u m e n t M a j o r i t y R e p a i r
    @ntracef("AUD2")
    def mRecordDocumentMajorityRepair(self,mysDocID):
        self.nRepairsMajority += 1          # WARNING: not idempotent.
        cDoc = G.dID2Document[mysDocID]
        cDoc.mMarkMajorityRepair()
        return self.nRepairsMajority
        
# A u d i t . m R e c o r d D o c u m e n t M i n o r i t y R e p a i r
    @ntracef("AUD2")
    def mRecordDocumentMinorityRepair(self,mysDocID):
        self.nRepairsMinority += 1          # WARNING: not idempotent.
        cDoc = G.dID2Document[mysDocID]
        cDoc.mMarkMinorityRepair()
        return self.nRepairsMinority

# A u d i t . m R e s c i n d D o c u m e n t M a j o r i t y R e p a i r 
    @ntracef("AUD2")
    def mRescindDocumentMajorityRepair(self,mysDocID):
        self.nRepairsMajority -= 1          # WARNING: not idempotent.
        cDoc = G.dID2Document[mysDocID]
        cDoc.mRescindMajorityRepair()
        return self.nRepairsMajority
        
# A u d i t . m R e s c i n d D o c u m e n t M i n o r i t y R e p a i r 
    @ntracef("AUD2")
    def mRescindDocumentMinorityRepair(self,mysDocID):
        self.nRepairsMinority -= 1          # WARNING: not idempotent.
        cDoc = G.dID2Document[mysDocID]
        cDoc.mRescindMinorityRepair()
        return self.nRepairsMinority

# C A u d i t . m C a l c S e g m e n t I n t e r v a l  
    @ntracef("AUD2")
    def mCalcSegmentInterval(self,mynCycleInterval,mynSegments):
        result = int(math.floor((1.0*mynCycleInterval-1.0)/mynSegments))
        return result

# C A u d i t 2 . m C a l c S e g m e n t S i z e 
    @ntracef("AUD2")
    def mCalcSegmentSize(self,mysCollectionID,mynSegments):
        cCollection = G.dID2Collection[mysCollectionID]
        nCollectionLength = len(cCollection.lDocIDs)
        result = int(math.ceil((1.0*nCollectionLength)/mynSegments))
        return result

# C A u d i t 2 . m I d e n t i f y S e g m e n t 
    @ntracef("AUD2")
    def mIdentifySegment(self,mysCollectionID,nSegments,nCurrentSegment):
        '''\
        Return list of document IDs in the collection.
        '''
        # For total audit, return the entire list.  
        cCollection = G.dID2Collection[mysCollectionID]
        lDocIDs = cCollection.mListDocuments()
        return lDocIDs

# C A u d i t . m R e t r i e v e D o c 
    @ntracef("AUD2")
    def mRetrieveDoc(self,mysDocID,mysServerID):
        '''\
        Get (copy of) doc back from server, if possible.
        Return the time required to transmit the doc.
        Ideally, would wait for transmission time, 
        but the waiting has to occur in the 
        parent loop.  
        '''
        """
        cDoc = G.dID2Document[mysDocID]
        if cDoc.bDocumentLost:
            return None
        else:
            nDocSize = cDoc.nSize
            fTransferTime = util.fnfCalcTransferTime(nDocSize,G.nBandwidthMbps)
            # Now that we know how long it would take to transfer,
            # test if the document is still there. 
            cServer = G.dID2Server[mysServerID] 
            bResult = cServer.mTestDocument(mysDocID)
            if bResult:
                return fTransferTime
            else:
                return None
        """
        cDoc = G.dID2Document[mysDocID]
        nDocSize = cDoc.nSize
        fTransferTime = util.fnfCalcTransferTime(nDocSize,G.nBandwidthMbps)
        # Now that we know how long it would take to transfer,
        # test if the document is still there. 
        cServer = G.dID2Server[mysServerID] 
        bResult = cServer.mTestDocument(mysDocID)
        if bResult:
            return fTransferTime
        else:
            return None

        
# C A u d i t . m R e p a i r D o c 
    @ntracef("AUD2")
    def mRepairDoc(self,mysDocID,mysServerID):
        ''' \
        Repair by sending new copy of original doc
        to the server.  Re-send the doc to the server
        and return the time it took to transfer.
        Ideally, the wait time to send doc rel to size
        would occur here, but it occurs in the parent loop.
        '''
        # How long will it take to transfer?
        cDoc = G.dID2Document[mysDocID]
        nDocSize = cDoc.nSize
        fTransferTime = util.fnfCalcTransferTime(nDocSize,G.nBandwidthMbps)
        # Re-send the doc to server.
        cServer = G.dID2Server[mysServerID] 
        result = cServer.mAddDocument(mysDocID,self.sClientID)
        # If AddDoc returns False, then the server is dead and cannot 
        #  accept any new docs.
        if result:
            self.nRepairsThisCycle += 1
            self.nRepairsTotal += 1
            return fTransferTime
        else:
            return False

# C A u d i t . m R e p o r t A u d i t S t a t s 
    @ntracef("AUD2")
    def mReportAuditStats(self):
        '''\
        Return list of stats.  Yes, you have to know the order.
        '''
        return(self.ID,self.sClientID,self.sCollectionID,"*"
            ,self.nNumberOfCycles,self.nRepairsTotal
            ,self.nPermanentLosses,self.nRepairsMinority)

# C A u d i t 2 . m d R e p o r t A u d i t S t a t s 
    @ntracef("AUD2")
    def mdReportAuditStats(self):
        '''\
        Return a dictionary of relevant stats.  Not positional crap anymore.
        '''
        #dd = cc.defaultdict(list)
        dd = dict()
        dd["sClientID"]         = self.sClientID
        dd["sCollectionID"]     = self.sCollectionID
        dd["nNumberOfCycles"]   = self.nNumberOfCycles
        dd["nRepairsThisCycle"] = self.nRepairsThisCycle
        dd["nRepairsTotal"]     = self.nRepairsTotal
        dd["nPermanentLosses"]  = self.nPermanentLosses
        dd["nRepairsMajority"]  = self.nRepairsMajority
        dd["nRepairsMinority"]  = self.nRepairsMinority
        dd["nFrequency"] = self.nCycleInterval
        dd["nSegments"] = self.nSegments
        return dd


''' \
Class CAudit overview:
Optimized version of total auditing (but retaining timing):
- Audit is specific to client, collection, and server.
- Retrieve doc.  
- If doc is absent, count copies on all servers.
- If no copies remain, then permanent loss of this doc.
- If >= majority still have copies, repair this doc.
- If < majority still have copies, then repair with forensics-required flag.
'''

'''\
Function/method breakdown:

mAuditCycle(cycleinterval)                          asyncprocess
    wait for random interval before starting
    loop forever
        wait one interval (yes, before first audit)
        get collectionid
        invoke asyncprocess mAuditCollection(cycleinterval,nsegments,collectionid)

mAuditCollection(cycleinterval,nsegments,collectionid) asyncprocess
    calc segmentinterval
    foreach currentsegment in range(nsegments)
        copieslist = mIdentifySegment(collectionid,nsegments,currentsegment)
        invoke asyncprocess mAuditSegment(copieslist)
        wait for segmentinterval

mAuditSegment(copieslist)                   oops, must also be an asyncprocess
    foreach copy in copieslist
        if copy still exists
            wait time to retrieve copy rel to size
            compare with original doc
            (always success now)
        else
            repair copy
            wait time to send new copy rel to size

mCalculateSegmentInterval(cycleinterval,nsegments)
    cyclinterval/nsegments 
    - provided that this is a plausible number
    - should check during setup for plausibility of cycleinterval given bandwidth

mCalculateSegmentSize(collectionID,nsegments)
    len(copieslist(collectionid)) / nsegments, ceiling thereof

Total.mIdentifySegment(collectionid,nsegments,currentsegment)
    get copieslist for collectionid
    - nsegments guaranteed == 1, so just return this
    - looks as though we should factor out this navigation, 
      but i don't want to clutter up the call args with a list instead
      of just the id, which is an understandable string.  leave as is.
    return it

Systematic.mIdentifySegment(collectionid,nsegments,currentsegment)
    get copieslist for collectionid
    how big is a segment based on nsegments
    careful with right end of list, since segmentsize is rounded up
    return subset of copieslist for currentsegment

Uniform.mIdentifySegment(collectionid,nsegments,currentsegment)
    get copieslist for collectionid
    how big is segment based on nsegments
    generate m uniforms with or without replacement
    return selected sublist of those indices from copieslist

Zipf.mIdentifySegment(collectionid,nsegments,currentsegment)
    get copieslist for collectionid
    - puzzlement here: I think we should lump docs into logarithmic-size
      bins and audit them according to the zipf frequency of the bin.
      Need to clear with Micah.  

'''

# Subclasses for various auditing strategies.


# c l a s s   C A u d i t 
# Just a copy of CAudit2 for use by the factory.  
class CAudit(CAudit2):
    def __init__(self, mysClientID, mysCollectionID, mynInterval):
        super(CAudit, self).__init__(mysClientID, mysCollectionID, 
                mynInterval)
        self.TYPE = "CAudit"


# c l a s s   C A u d i t _ T o t a l 
class CAudit_Total(CAudit):
    '''\
    Class CAudit contains all the procedures for CAudit_Total.
    Do not override anything in here.
    '''
    def __init__(self, mysClientID, mysCollectionID, mynInterval):
        super(CAudit_Total,self).__init__(mysClientID, mysCollectionID, 
                mynInterval)
        self.TYPE = "CAudit_Total"

# C A u d i t _ T o t a l . m I d e n t i f y S e g m e n t 
    ''' don't need it!
    @ntracef("AUD2")
    def mIdentifySegment(self,collectionid,nsegments,currentsegment):
        # Get list of document IDs in the collection
        cCollection = G.dID2Collection[mysCollectionID]
        lDocIDs = cCollection.mListDocuments()
        return lDocIDs
    '''
    

# c l a s s   C A u d i t _ S y s t e m a t i c 
class CAudit_Systematic(CAudit):
    ''' \
    Strategy Systematic: do n systematically-sampled subsets of collection
    on each cycle.
    - audit cycle, calls audit collection
    - sample size = ncollection / nsegments
    - sample interval = cycletime / nsegments
    - loop, starting at segment 0
      - calls audit segment
      - form subset by taking consecutive documents (or evenly spaced?)
        depending on subset number
      - sample subset of collection with usual rules
      - wait for next interval
      - bump subset number 
    - bump cycle number
    - wait for next cycle
    '''
    def __init__(self, mysClientID, mysCollectionID, mynInterval):
        super(CAudit_Systematic, self).__init__(mysClientID, mysCollectionID, 
                mynInterval)
        self.TYPE = "CAudit_Systematic"

# C A u d i t _ S y s t e m a t i c . m I d e n t i f y S e g m e n t 
    @ntracef("AUD2")
    def mIdentifySegment(self, mysCollectionID, mynSegments, iCurrentSegment):
        # Get list of document IDs in the collection
        cCollection = G.dID2Collection[mysCollectionID]
        lDocIDs = cCollection.mListDocuments()
        nDocs = len(lDocIDs)
        nDocsMaybe = self.mCalcSegmentSize(mysCollectionID,mynSegments)
        lDocsThisSegment = lDocIDs[(nDocsMaybe*iCurrentSegment) : 
            min(nDocsMaybe*(iCurrentSegment+1), nDocs)]
        return lDocsThisSegment


# c l a s s   C A u d i t _ U n i f o r m 
class CAudit_Uniform(CAudit):
    '''\
    Strategy Uniform: do n random subsets of collection on each cycle.
    - audit cycle, calls audit collection
    - sample size = ncollection / nsegments
    - sample interval = cycletime / nsegments
    - loop, starting at segment 0
      - calls audit segment
      - form subset of collection by uniform random choices, 
        with or without replacement as requested
        (only without replacement is implemented here currently)
      - sample subset of collection with usual rules
      - wait for next interval
    - bump cycle number
    - wait for next cycle

    Note that this is almost identical to systematic, except for how 
    the subset is formed.  
    '''
    def __init__(self, mysClientID, mysCollectionID, mynInterval):
        super(CAudit_Uniform, self).__init__(mysClientID, mysCollectionID, 
                mynInterval)
        self.TYPE = "CAudit_Uniform"

# C A u d i t _ U n i f o r m . m I d e n t i f y S e g m e n t 
    @ntracef("AUD2")
    def mIdentifySegment(self, mysCollectionID, mynSegments, iCurrentSegment):
        # Get list of document IDs in the collection
        cCollection = G.dID2Collection[mysCollectionID]
        lDocIDsRemaining = cCollection.mListDocumentsRemaining()
        nDocsRemaining = len(lDocIDsRemaining)
        # Beware the case where there are fewer docs remaining alive
        #  than are normally called for in the segment.  
        nDocsMaybe = min( 
                        self.mCalcSegmentSize(mysCollectionID, mynSegments), 
                        nDocsRemaining
                        )
        if 1: # Which method do we choose today?  
              # TRUE = generous assumptions, each segment will audit the 
              #  segment's size number of unique documents WITHOUT REPLACEMENT.
              # FALSE = naive assumptions, each segment will choose the 
              #  segment's size number of document WITH REPLACEMENT.  
            # Use set() to ensure that a doc is not sampled twice in a segment.
            #  This is sampling WITHOUT REPLACEMENT FOR A SEGMENT ONLY, to 
            #  ensure that the right portion of the population gets audited.  
            #  (I don't know what people who say, "audit one quarter of the 
            #  population every quarter" actually mean.  This is a plausible
            #  but optimistic guess.)
            #  Note that the cycle is still sampled WITH repacement overall, so 
            #  that some docs may be missed, say, quarter to quarter.  
            # For sampling with replacement, use a list and just append doc IDs
            #  to the list.  Then a doc might be sampled > once per segment, 
            #  which would be even more useless.  
            # Also, beware the case where there are no docs remaining.  
            #  Carefully return an empty list.
            setDocsThisSegment = set()
            while nDocsMaybe > 0 and len(setDocsThisSegment) < nDocsMaybe:
                idxChoose = int(util.makeunif(0, nDocsRemaining))
                sDocID = lDocIDsRemaining[idxChoose]
                cDoc = G.dID2Document[sDocID]
                # If the doc is not already permanently kaput, check it.
                if not cDoc.mIsLost():
                    setDocsThisSegment.add(sDocID)
            lDocsThisSegment = util.fnlSortIDList(list(setDocsThisSegment))
            sRandomType = "GENEROUS"
        else:
            # Do this the simple, stupid way: select a segment's size list
            #  of uniform random numbers and make that the audit list for 
            #  this segment.  Note that this will be SAMPLING WITH REPLACEMENT
            #  WITHIN A SEGMENT, so that the number of documents actually 
            #  audited during a segment will (almost certainly) be much less 
            #  than the naively-desired number due to balls-in-urns effects
            #  of replacement.  I think that this is what most people
            #  would actually implement naively for "random auditing."  
            #  The list may/will contain duplicates, and we don't care.  
            lDocsThisSegment = []
            while nDocsMaybe > 0 and len(lDocsThisSegment) < nDocsMaybe:
                idxChoose = int(util.makeunif(0, nDocsRemaining))
                sDocID = lDocIDsRemaining[idxChoose]
                cDoc = G.dID2Document[sDocID]
                # If the doc is not already permanently kaput, check it.
                if not cDoc.mIsLost():
                    lDocsThisSegment.append(sDocID)
            lDocsThisSegment = util.fnlSortIDList(list(set(lDocsThisSegment)))
            sRandomType = "NAIVE"
        lg.logInfo("AUDIT2", "choose seg  t|%10.3f| auditid|%s| seg|%s|of|%s| "
                "ndocsrem|%s| chosen|%s| type|%s|"
            % (G.env.now, self.ID, iCurrentSegment+1, mynSegments, 
                nDocsRemaining, len(lDocsThisSegment), sRandomType))
        return lDocsThisSegment


# c l a s s   C A u d i t _ Z i p f 
class CAudit_Zipf(CAudit):
    '''\
    This is the tricky one: 
    - group docs into a small number of bins based on (Zipf) frequency of access
    - i think
    - still need to work out details of this type
    '''
    def __init__(self, mysClientID, mysCollectionID, mynInterval):
        super(CAudit_Zipf,self).__init__(mysClientID, mysCollectionID, 
                mynInterval)
        self.TYPE = "CAudit_Zipf"
        raise ValueError, "Unimplemented Audit strategy: %s" % ("ZIPF")

# C A u d i t _ Z i p f . m C a l c S e g m e n t S i z e 
    @ntracef("AUD2")
    def mIdentifySegment(self, mysCollectionID, mynSegments, iCurrentSegment):
        # Get list of document IDs in the collection
        cCollection = G.dID2Collection[mysCollectionID]
        lDocIDs = cCollection.mListDocuments()
        nDocs = len(lDocIDs)
        
        # Dunno what to do here yet.
        raise ValueError, "Unimplemented Audit strategy: %s" % ("ZIPF")
        
        return 0

# C A u d i t _ Z i p f . m I d e n t i f y S e g m e n t 
    @ntracef("AUD2")
    def mIdentifySegment(self, mysCollectionID, mynSegments, iCurrentSegment):
        # Get list of document IDs in the collection
        cCollection = G.dID2Collection[mysCollectionID]
        lDocIDs = cCollection.mListDocuments()
        nDocs = len(lDocIDs)
        nDocsMaybe = self.mCalcSegmentSize(mysCollectionID, mynSegments)
        lDocsThisSegment = []
        return lDocsThisSegment


# f A u d i t _ S e l e c t 
# Stupid factory function to create the right class for this audit strategy.
@ntracef("AUD2")
def fAudit_Select(mysStrategy, mysClientID, mysCollectionID, mynCycleInterval):
    if mysStrategy == "TOTAL" or mysStrategy == "OFF":
        thing = CAudit_Total(mysClientID, mysCollectionID, mynCycleInterval)
    elif mysStrategy == "SYSTEMATIC":
        thing = CAudit_Systematic(mysClientID, mysCollectionID, mynCycleInterval)
    elif mysStrategy == "UNIFORM":
        thing = CAudit_Uniform(mysClientID, mysCollectionID, mynCycleInterval)
    elif mysStrategy == "ZIPF":
        thing = CAudit_Zipf(mysClientID, mysCollectionID, mynCycleInterval)
    else:
        # Forgiving version:
        thing = CAudit(mysClientID, mysCollectionID, mynCycleInterval)
        # Tight-ass version:`
        raise ValueError, "Unknown Audit strategy: %s" % (mysStrategy)
    return thing



'''\
- During the audit, for each doc with an error, how many copies 
  remain?
  - zero: permanent failure.
  - .ge. half of the servers: make the repair.  Odd numbers round up.
  - .lt. half of the servers: repair but with forensics required.
'''

'''\
Here is a brief description of the methods used here.  This is a 
 summary of the r3b.py test program that actually works properly.
SimPy is inherently asynchronous.  The tricky bit is to synchronize 
 with some processes and not others, so that the scheduling is done
 on a precise schedule.  In this case, collection synchronizes 
 to wait for the completion of each segment before starting the
 next segment.  

start:
- schedule process cycle, free-running, starting now.

cycle generator:
- yield timeout=offset 
        For this audit cycle, there is a small offset time 
         so that they don't all start at the same time.  
         Just like Ethernet CSMA/CD random backoff times.
- while 1
        Forever.
        In this test, maybe do only a few iterations.
-- yield timeout=cycletime
        Start next audit cycle one cycletime from beginning of current one.
-- make syncevent for collection
        To be passed to collection as argument.
        We could wait for this (yield it) to sync with the completion 
         of collection, but that would cause the next audit cycle's start
         to be offset one cycletime from the *end* of the previous one
         rather than the beginning.  Don't do that.
-- schedule process collection
        Collection will start as soon as this finishes.

collection generator:
- loop for segments
        Foreach loop to go thru all segments for this collection.
-- calc segmenttime, size
        Be sure segmenttime * nsegments can fit in cycletime.
         Round down.
-- make syncevent for segment
        To be passed to segment process as argument.
-- schedule process segment
        To start when this generator finishes.
-- yield syncevent for segment AND timeout segmenttime
        Wait for both the completion of the segment audit 
         *and* the segment time to expire.  It is possible
         that we didn't calculate the bandwidth and time 
         required so that a segment audit could run over
         time.
        Note that this is still inside the foreach loop.
- after loop, syncevent (from caller) succeed
        Tell the caller that we have finished.  

segment generator:
- with networkresource
        Seize the network resource.  Create a request for it
         and yield it.  Forces this process to wait until the
         resource is available.  
         The with statement will release the request when done.
        The scope of the network resource should be as wide
         as needed.  Right answer in this case = Client.  
         Each client has only so much network bandwidth available
         for use by real people and auditing processes, so that 
         only one audit (from this client to one server) should run
         at one time.  
- foreach loop for items
        Foreach loop over all the items in the segment.
        In real life, the list of items comes from somewhere else.
          Here, we use the same list over and over.  
-- yield time to retrieve or repair each item
        Each item takes some time to assess and/or repair.  
         yield timeout=doctime for each one.
-- after foreach loop, but still in with scope, syncevent from caller succeed
        Tell the caller that we have finished.
'''

'''\
# 50,000 foot level of an audit cycle for a complete audit:

# audit segment
- foreach client
    - foreach collection owned by the client
        how many segments in a cycle?
        - foreach segment in cycle
            identify subset list of docs in this segment
            # PHASE 1: Check copies on all servers, how many left?
            - foreach server used by the client for this collection
                - foreach document in the subset list
                    - if doc already permanently lost
                        proceed (abnormal case)
                    - else
                        - if server has a valid copy of doc
                            proceed (normal case)
                        - else
                            record doc lost on server (append to loss list)
                - end foreach doc
            - end foreach server
            # PHASE 2: Record severity of copy losses
            - foreach doc in list of losses
                # record and count type of loss
                - if no copies remain
                    record document permanently lost
                - else
                    - if majority of copies remain
                        record majority repair for this doc
                        count majority repairs
                    - if minority of copies remain
                        record minority repair for this doc
                        count minority repairs
                        # PHASE 3: Repair lost copies
                        - foreach server in loss-list
                            replace copy (takes time)
                        - end foreach server in loss-list
        - end foreach segment
        # stats for collection: docs lost, copies lost,
        # repair counts for doc (majority, minority)
    - end foreach collection
- end foreach client
# end of audit segment

'''

'''\
TODO (x=done):
    - RetrieveDoc: remove checking for doc lost at the front; low probability event
      should not be the first thing we always look at.
    - AuditSegment: remove checking for doc lost at the front: same reason.
    - 
    - Future: auditor maintains guaranteed copy of fixity info for use in auditing.  
      Might change the timing characteristics of auditing if we don't have to 
      retrieve the entire doc from the server each time.  Otherwise, not much impact.
'''



#Edit history:
# 20140715  RBL Original version.
# 20140924  RBL Add CAudit subclasses for various strategies.
#               Add subclass methods to identify copies in segments.
# 20141004  RBL Uncover oversight in assessment of minority/majority repairs.
# 20141007  RBL Rework scheduling of multi-segment audit cycles, so that
#                segments are properly timed and coordinated within cycles.
#               Add lots of commentary about how to manipulate SimPy async
#                processes for this coordination.  
# 20141109  RBL Restructure a lot for new auditing strategy.  
#               Bump revision number to 10 to start new series.
#               Restructure as single Audit2 object per collection.
# 20141114  RBL Add stats. 
#               Add dict return of stats.
#               Clean up lost doc detection/marking.
#               Add empty CAudit class on top of new CAudit2.
# 20141121  RBL Rework the scheduling and coordination of auditing segments.
#               Correct numerous typos and spellos in evaluation of
#                the health of document copies.  
# 20141128  RBL Correct counting of docs lost.  
# 20141201  RBL Remove and replace the preceding four lines to resolve 
#                a git conflict.  Gotta learn that someday.  
# 20141212  RBL Add random selection for auditing, distribution = 
#                uniform without replacement.  
#               One-plus logging around network grab-release to include
#                segment number.  
# 20141217  RBL Remove offset time before beginning audit cycles.
#                Since there is only one client, one collection, 
#                one audit, it seems superfluous.  
# 20150716  RBL Check for dead server (i.e., 100% glitch) during repair.
#                At end of audit segment, notify client that server
#                is no longer usable.
# 20150812  RBL Remove old AuditSegment code, which was commented out anyway.
# 20151207  RBL Fix old, old bug that attempted to repair doc even if
#                no copies remain.  This allocated space for a new copy, 
#                raised the high-water mark, and permitted the new phantom
#                copy to be damaged anew, biasing the loss count, yikes.
#                Unfortunately, this makes audit-segment even meaner, nastier,
#                and uglier than its previous pathetic state.
#               Improve slightly loop that informs clients of dead servers.
#               Also, consider factoring out Phase 2 of AuditSegment.
# 20161231  RBL Call CShock routine to check for dead servers before each 
#                segment of audit.
# 20160102  RBL PIP8-ify most of the trace and log lines. 
# 20171101  RBL Clarify comments about uniform random auditing: the several
#                segments are sampled WITH replacement across segments, but
#                each segment is sampled WITHOUT replacement so that the
#                segment size does match the naive arithmetic; e.g., each
#                quarter, one-quarter of the documents will be examined, but 
#                from quarter to quarter documents may be sampled more than
#                one time or zero times, depending on random choice.  
# 20180516  RBL Update to use only ntrace, ntracef, NTRC.
# 
# 

#END
