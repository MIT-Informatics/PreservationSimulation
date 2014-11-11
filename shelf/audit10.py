#!/usr/bin/python
# audit.py
#

'''\
See commentary at end about actual algorithms. 
'''
from globaldata import G
import itertools
import util
import logoutput as lg
from NewTraceFac import TRC,trace,tracef
import math
import collections as cc


#===========================================================
# C l a s s   C A u d i t 
#-------------------------
class CAudit(object):
    '''\
    Procedures for auditing collections kept on 
    remote servers.  Clients will create one instance
    of this class for each collection on each server.  
    Collection audits run asynchronously.  
    '''
    getID = itertools.count(1).next

    @tracef("AUD")
    def __init__(self,mysClientID,mysCollectionID,mysServerID,mynInterval=G.nAuditCycleInterval):
        self.ID = "A" + str(self.getID())
        G.dID2Audit[self.ID] = self
        self.sClientID = mysClientID
        self.sServerID = mysServerID
        self.sCollectionID = mysCollectionID
        self.nCycleInterval = mynInterval

        self.nNumberOfCycles = 0
        self.nRepairsThisCycle = 0
        self.nRepairsTotal = 0
        self.nPermanentLosses = 0
        self.nForensicsRequired = 0
        
        self.lDocsThisSegment = list()
        self.dlDocsDamagedOnServers = cc.defaultdict(list)
        self.lDocsRepairedMajority = list()
        self.lDocsRepairedMinority = list()
        self.lDocsPermanentlyLost = list()
        self.dDocsAlreadyLost = dict()

        # Start the free-running process of audit cycles for 
        # this collection.
        G.env.process(self.mAuditCycle(self.nCycleInterval))


    # NEW NEW NEW
    # C A u d i t . m A u d i t C y c l e 
    @tracef("AUD")
    def mAuditCycle(self,mynCycleInterval):
        '''\
        SimPy generator to schedule audit cycles for this collection.
        Starts an async process that ticks every 
        audit cycle forever.
        '''
        # Initially, wait for some small random interval
        # so that client audit cycles are not synchronized,
        # like Ethernet collision retry waits. 
        nRandTime = util.makeunif(0,mynCycleInterval/20)
        yield G.env.timeout(nRandTime)
        
        while True:
            yield G.env.timeout(mynCycleInterval)
            lg.logInfo("AUDIT","begin cycle t|%9.3f| auditid|%s| cycle|%s| cli|%s| coll|%s svr|%s|" % (G.env.now,self.ID,self.nNumberOfCycles,self.sClientID,self.sCollectionID,self.sServerID))
            self.nRepairsThisCycle = 0
            eSyncEvent = G.env.event()
            G.env.process(self.mAuditCollection(mynCycleInterval,G.nAuditSegments,self.sCollectionID,eSyncEvent))
            lg.logInfo("AUDIT","end cycle   t|%9.3f| auditid|%s| cycle|%s| cli|%s| coll|%s svr|%s| repairs|%d| total|%d| perms|%d| forensics|%d|" % (G.env.now,self.ID,self.nNumberOfCycles,self.sClientID,self.sCollectionID,self.sServerID,self.nRepairsThisCycle,self.nRepairsTotal,self.nPermanentLosses,self.nForensicsRequired))

    # NEW NEW NEW 
    # C A u d i t . m A u d i t C o l l e c t i o n 
    @tracef("AUD")
    def mAuditCollection(self,mynCycleInterval,mynSegments,mysCollectionID,myeCallerSyncEvent):
        '''\
        SimPy generator to audit an entire collection.
        Divide the collection into segments and audit
        each segment in turn.
        '''
        fTimeCycleBegin = G.env.now
        lg.logInfo("AUDIT","begin colln t|%9.3f| auditid|%s| cycle|%s| cli|%s| coll|%s svr|%s|" % (G.env.now,self.ID,self.nNumberOfCycles,self.sClientID,self.sCollectionID,self.sServerID))
        self.nNumberOfCycles += 1

        for iThisSegment in range(mynSegments):
            nSegmentInterval = self.mCalcSegmentInterval(mynCycleInterval,mynSegments)
            bLastSegment = (iThisSegment == mynSegments-1)
            self.lDocsThisSegment = self.mIdentifySegment(mysCollectionID,mynSegments,iThisSegment)
            eSyncEvent = G.env.event()
            G.env.process(self.mAuditSegment(iThisSegment,lSegmentDocs,mysCollectionID,eSyncEvent))
            # Wait for completion of segment and its allotted time.
            yield G.env.all_of([G.env.timeout(nSegmentInterval),eSyncEvent])
        
        fTimeCycleEnd = G.env.now
        self.fTimeCycleLength = fTimeCycleEnd - fTimeCycleBegin
        lg.logInfo("AUDIT","end colln   t|%9.3f| auditid|%s| cycle|%s| cli|%s| coll|%s svr|%s| repairs|%d| total|%d| perms|%d| forensics|%d| duration|%9.3f|" % (G.env.now,self.ID,self.nNumberOfCycles,self.sClientID,self.sCollectionID,self.sServerID,self.nRepairsThisCycle,self.nRepairsTotal,self.nPermanentLosses,self.nForensicsRequired,self.fTimeCycleLength))
        # Tell the caller that we finished.
        myeCallerSyncEvent.succeed(value=self.nNumberOfCycles)
        return

    # NOT VERY OLD NOT VERY OLD NOT VERY OLD
    # C A u d i t . m A u d i t S e g m e n t 
    @tracef("AUD")
    def mAuditSegment(self,mynThisSegment,mylDocs,mysCollectionID,myeCallerSyncEvent):
        '''\
        SimPy generator to audit one segment of a collection.
        '''
        lg.logInfo("AUDIT","begin segment t|%9.3f| auditid|%s| cycle|%s| segment|%s| cli|%s| coll|%s svr|%s|" % (G.env.now,self.ID,self.nNumberOfCycles,mynThisSegment,self.sClientID,self.sCollectionID,self.sServerID))

        # Seize the network resource so this audit cycle 
        # can use it exclusively.
        # The "with" should take care of releasing it
        cClient = G.dID2Client[self.sClientID]
        with cClient.NetworkBandwidthResource.request() as reqnetwork:
            fNetworkWaitBegin = G.env.now
            result = yield reqnetwork
            fNetworkWaitEnd = G.env.now
            fNetworkWaitTime = fNetworkWaitEnd - fNetworkWaitBegin
            # Log event if we had to wait, or not, for the network to be free.  
            lg.logInfo("AUDIT","grabnetwork t|%9.3f| auditid|%s| cli|%s| coll|%s svr|%s| delay|%9.3f|" % (G.env.now,self.ID,self.sClientID,self.sCollectionID,self.sServerID,fNetworkWaitTime))
            # And restart the duration clock after the unproductive wait.
            fTimeCycleBegin = G.env.now

            # So much for timekeeping.  Now do some actual work.
            for sDocID in mylDocs:
                fTransferTime = self.mRetrieveDoc(sDocID)
    
                # Is the document still on this server?
                if fTransferTime:
                    yield G.env.timeout(fTransferTime)
                    # Here we would test the document contents
                    # for validity, that is, if our documents
                    # had contents.  
    
                # No, the document is absent.  Can we repair it?  
                else:
                    cCollection = G.dID2Collection[mysCollectionID]
                    #idx = cCollection.lDocIDs.index(sDocID)
                    #nCopiesLeft = self.lDocsHowManyCopiesLeft[idx]
                    nCopiesLeft = cCollection.mHowManyCopiesLeftOfThisOneDoc(sDocID)
                    nMajorityOfServers = (len(cCollection.lServerIDs)+1) / 2    
    
                    # Are there any or enough copies left from which to repair the doc?
                    if nCopiesLeft > 0:
    
                        # If there is a majority of copies remaining, 
                        # then unambiguous repair is possible.
                        if nCopiesLeft >= nMajorityOfServers:
                            # Repair the doc, currently missing.  
                            fTransferTime = self.mRepairDoc(sDocID)
                            yield G.env.timeout(fTransferTime)
                            lg.logInfo("AUDIT","repair doc  t|%9.3f| auditid|%s| cli|%s| coll|%s| svr|%s| doc|%s| from copies|%d|" % (G.env.now,self.ID,self.sClientID,self.sCollectionID,self.sServerID,sDocID,nCopiesLeft))
    
                        # Some copies left, but not enough for unambiguous repair.
                        # Record that forensics are required for this doc repair. 
                        else:
                            # Patch the doc from a minority copy. 
                            self.nForensicsRequired += 1 
                            fTransferTime = self.mRepairDoc(sDocID)
                            yield G.env.timeout(fTransferTime)
                            lg.logInfo("AUDIT","patch doc   t|%9.3f| auditid|%s| cli|%s| coll|%s| svr|%s| doc|%s| minority copies|%d|" % (G.env.now,self.ID,self.sClientID,self.sCollectionID,self.sServerID,sDocID,nCopiesLeft))
    
                    # There are no remaining copies of the doc, 
                    # we cannot repair it, oops.  Permanent loss.  
                    else:
                        if not sDocID in self.dDocsAlreadyLost:
                            self.nPermanentLosses += 1
                            self.dDocsAlreadyLost[sDocID] = (self.nNumberOfCycles)
                            self.mMarkDocumentLost(sDocID)
                            #TRC.tracef(3,"AUD","proc mAuditCollection no copy for repair doc|%s| idx|%d|" % (sDocID,idx))
                            lg.logInfo("AUDIT","lost doc    t|%9.3f| auditid|%s| cli|%s| coll|%s| svr|%s| doc|%s| copies left|%d|" % (G.env.now,self.ID,self.sClientID,self.sCollectionID,self.sServerID,sDocID,nCopiesLeft))
            # After all that, tell the caller we finished.
            myeCallerSyncEvent.succeed(value=mynThisSegment)
            
    @tracef("AUD",level=5)
    def mMarkDocumentLost(self,mysDocID):
        cDoc = G.dID2Document[mysDocID]
        cDoc.bDocumentLost = True

    @tracef("AUD",level=5)
    def mIsDocumentLost(self,mysDocID):
        cDoc = G.dID2Document[mysDocID]
        return cDoc.bDocumentLost

    # NEW NEW NEW 
    # C A u d i t . m A u d i t S e g m e n t 
    @tracef("AUD")
    def mAuditSegment(self,mynThisSegment,mylDocs,mysCollectionID,myeCallerSyncEvent):
        '''\
        SimPy generator to audit one segment of a collection.
        '''
        lg.logInfo("AUDIT","begin segment t|%9.3f| auditid|%s| cycle|%s| segment|%s| cli|%s| coll|%s svr|%s|" % (G.env.now,self.ID,self.nNumberOfCycles,mynThisSegment,self.sClientID,self.sCollectionID,self.sServerID))

        # Seize the network resource so this audit cycle 
        # can use it exclusively.
        # The "with" should take care of releasing it
        cClient = G.dID2Client[self.sClientID]
        with cClient.NetworkBandwidthResource.request() as reqnetwork:
            fNetworkWaitBegin = G.env.now
            result = yield reqnetwork
            fNetworkWaitEnd = G.env.now
            fNetworkWaitTime = fNetworkWaitEnd - fNetworkWaitBegin
            # Log event if we had to wait, or not, for the network to be free.  
            lg.logInfo("AUDIT","grabnetwork t|%9.3f| auditid|%s| cli|%s| coll|%s svr|%s| delay|%9.3f|" % (G.env.now,self.ID,self.sClientID,self.sCollectionID,self.sServerID,fNetworkWaitTime))
            # And restart the duration clock after the unproductive wait.
            fTimeCycleBegin = G.env.now

            # So much for timekeeping.  Now do some actual work.

            # Phase 1: Check servers for copies of docs, record losses.
            cCollection = G.dID2Collection[mysCollectionID]
            # foreach server used for this collection
            for sServerID in cCollection.lServerIDs:
                cServer = G.dID2Server[sServerID]
                # foreach doc in this segment
                for sDocID in self.lDocsThisSegment:
                    cDoc = G.dID2Document[sDocID]
                    # If doc already lost, never mind.
                    if self.mIsDocumentLost(sDocID):
                        bResult = cServer.mTestDocument(sDocID)
                        if not bResult:
                            # If doc missing here, save server in lost-list for doc
                            dlDocsDamagedOnServers[sDocID].append(sServerID)
                    # end foreach doc
            # end foreach server

            # Phase 2: Record severity of copy losses.
            nServers = cColl.lServerIDs
            nMajority = (len(cCollection.lServerIDs)+1) / 2     # int divide truncates
            # foreach doc with any losses
            for sDocID in sorted(self.dlDocsDamagedOnServers.keys()):
                lDocLostOnServers = self.dlDocsDamagedOnServers[sDocID]
                nCopiesLost = len(lDocLostOnServers)
                if nCopiesLeft = nServers - nCopiesLost
                cDoc = G.dID2Document[sDocID]
                # How many copies left: none, a lot, a few?
                if nCopiesLeft == 0:
                    self.mMarkDocumentLost(sDocID)
                elif nCopiesLeft >= nMajority:
                    cDoc.bMajorityRepair = True
                    cDoc.nRepairsMajority += 1
                else:
                    cDoc.bMinorityRepair = True
                    cDoc.nRepairsMinority += 1

                # Phase 3: Repair doc on servers where lost.
                nDocSize = cDoc.nSize
                if self.mIsDocumentLost(sDocID):
                    pass
                else:
                    for sServerID in lDocLostOnServers:
                        
                        fTransferTime = self.mRepairDoc(sDocID)
                        yield G.env.timeout(fTransferTime)
                        lg.logInfo("AUDIT","repair doc  t|%9.3f| auditid|%s| cli|%s| coll|%s| svr|%s| doc|%s| from copies|%d|" % (G.env.now,self.ID,self.sClientID,self.sCollectionID,self.sServerID,sDocID,nCopiesLeft))
                    





            for sDocID in mylDocs:
                fTransferTime = self.mRetrieveDoc(sDocID)
    
                # Is the document still on this server?
                if fTransferTime:
                    yield G.env.timeout(fTransferTime)
                    # Here we would test the document contents
                    # for validity, that is, if our documents
                    # had contents.  
    
                # No, the document is absent.  Can we repair it?  
                else:
                    cCollection = G.dID2Collection[mysCollectionID]
                    #idx = cCollection.lDocIDs.index(sDocID)
                    #nCopiesLeft = self.lDocsHowManyCopiesLeft[idx]
                    nCopiesLeft = cCollection.mHowManyCopiesLeftOfThisOneDoc(sDocID)
                    nMajorityOfServers = (len(cCollection.lServerIDs)+1) / 2    
    
                    # Are there any or enough copies left from which to repair the doc?
                    if nCopiesLeft > 0:
    
                        # If there is a majority of copies remaining, 
                        # then unambiguous repair is possible.
                        if nCopiesLeft >= nMajorityOfServers:
                            # Repair the doc, currently missing.  
                            fTransferTime = self.mRepairDoc(sDocID)
                            yield G.env.timeout(fTransferTime)
                            lg.logInfo("AUDIT","repair doc  t|%9.3f| auditid|%s| cli|%s| coll|%s| svr|%s| doc|%s| from copies|%d|" % (G.env.now,self.ID,self.sClientID,self.sCollectionID,self.sServerID,sDocID,nCopiesLeft))
    
                        # Some copies left, but not enough for unambiguous repair.
                        # Record that forensics are required for this doc repair. 
                        else:
                            # Patch the doc from a minority copy. 
                            self.nForensicsRequired += 1 
                            fTransferTime = self.mRepairDoc(sDocID)
                            yield G.env.timeout(fTransferTime)
                            lg.logInfo("AUDIT","patch doc   t|%9.3f| auditid|%s| cli|%s| coll|%s| svr|%s| doc|%s| minority copies|%d|" % (G.env.now,self.ID,self.sClientID,self.sCollectionID,self.sServerID,sDocID,nCopiesLeft))
    
                    # There are no remaining copies of the doc, 
                    # we cannot repair it, oops.  Permanent loss.  
                    else:
                        if not sDocID in self.dDocsAlreadyLost:
                            self.nPermanentLosses += 1
                            self.dDocsAlreadyLost[sDocID] = (self.nNumberOfCycles)
                            self.mMarkDocumentLost(sDocID)
                            #TRC.tracef(3,"AUD","proc mAuditCollection no copy for repair doc|%s| idx|%d|" % (sDocID,idx))
                            lg.logInfo("AUDIT","lost doc    t|%9.3f| auditid|%s| cli|%s| coll|%s| svr|%s| doc|%s| copies left|%d|" % (G.env.now,self.ID,self.sClientID,self.sCollectionID,self.sServerID,sDocID,nCopiesLeft))
            # After all that, tell the caller we finished.
            myeCallerSyncEvent.succeed(value=mynThisSegment)
            
    @tracef("AUD",level=5)
    def mMarkDocumentLost(self,mysDocID):
        cDoc = G.dID2Document[mysDocID]
        cDoc.bDocumentLost = True

    @tracef("AUD",level=5)
    def mIsDocumentLost(self,mysDocID):
        cDoc = G.dID2Document[mysDocID]
        return cDoc.bDocumentLost


    # NEW NEW NEW 
    # C A u d i t . m C a l c S e g m e n t I n t e r v a l  
    @tracef("AUD")
    def mCalcSegmentInterval(self,mynCycleInterval,mynSegments):
        result = int(math.floor((1.0*mynCycleInterval-1.0)/mynSegments))
        return result

    # NEW NEW NEW 
    # C A u d i t . m C a l c S e g m e n t S i z e 
    @tracef("AUD")
    def mCalcSegmentSize(self,mysCollectionID,mynSegments):
        cCollection = G.dID2Collection[mysCollectionID]
        nCollectionLength = len(cCollection)
        result = int(math.ceil((1.0*nCollectionLength)/mynSegments))
        return result

    # C A u d i t . m I d e n t i f y S e g m e n t 
    @tracef("AUD")
    def mIdentifySegment(self,mysCollectionID,nSegments,nCurrentSegment):
        # Get list of document IDs in the collection.
        # For total audit, return the entire list.  
        cCollection = G.dID2Collection[mysCollectionID]
        lDocIDs = cCollection.mListDocuments()
        return lDocIDs

    # C A u d i t . m R e t r i e v e D o c 
    @tracef("AUD")
    def mRetrieveDoc(self,mysDocID):
        '''\
        Get (copy of) doc back from server, if possible.
        Return the time required to transmit the doc.
        Ideally, would wait for transmission time, 
        but the waiting has to occur in the 
        parent loop.  
        '''
        cDoc = G.dID2Document[mysDocID]
        if cDoc.bDocumentLost:
            return None
        else:
            nDocSize = cDoc.nSize
            fTransferTime = util.fnfCalcTransferTime(nDocSize,G.nBandwidthMbps)
            # Now that we know how long it would take to transfer,
            # test if the document is still there. 
            cServer = G.dID2Server[self.sServerID] 
            bResult = cServer.mTestDocument(mysDocID)
            if bResult:
                return fTransferTime
            else:
                return None

    # C A u d i t . m R e p a i r D o c 
    @tracef("AUD")
    def mRepairDoc(self,mysDocID):
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
        cServer = G.dID2Server[self.sServerID] 
        cServer.mAddDocument(mysDocID,self.sClientID)
        self.nRepairsThisCycle += 1
        self.nRepairsTotal += 1
        return fTransferTime

    # C A u d i t . m R e p o r t A u d i t S t a t s 
    def mReportAuditStats(self):
        return(self.ID,self.sClientID,self.sCollectionID,self.sServerID
            ,self.nNumberOfCycles,self.nRepairsTotal
            ,self.nPermanentLosses,self.nForensicsRequired)

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

mAuditSegment(copieslist)                           oops, must also be an asyncprocess
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

# NEW NEW NEW 
# c l a s s   C A u d i t _ T o t a l 
class CAudit_Total(CAudit):
    '''\
    Class CAudit contains all the procedures for CAudit_Total.
    Do not override anything in here.
    '''
    # NEW NEW NEW 
    # C A u d i t _ T o t a l . m I d e n t i f y S e g m e n t 
    ''' don't need it!
    @tracef("AUD")
    def mIdentifySegment(self,collectionid,nsegments,currentsegment):
        # Get list of document IDs in the collection
        cCollection = G.dID2Collection[mysCollectionID]
        lDocIDs = cCollection.mListDocuments()
        return lDocIDs
    '''
    
# NEW NEW NEW 
# c l aS s s   C A u d i t _ S y s t e m a t i c 
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
    # NEW NEW NEW 
    # C A u d i t _ S y s t e m a t i c . m I d e n t i f y S e g m e n t 
    @tracef("AUD")
    def mIdentifySegment(self,collectionid,nsegments,currentsegment):
        # Get list of document IDs in the collection
        cCollection = G.dID2Collection[mysCollectionID]
        lDocIDs = cCollection.mListDocuments()

        return []

# NEW NEW NEW 
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
      - sample subset of collection with usual rules
      - wait for next interval
      - bump subset number 
    - bump cycle number
    - wait for next cycle

    Note that this is almost identical to systematic, except for how 
    the subset is formed.  
    '''
    # NEW NEW NEW 
    # C A u d i t _ U n i f o r m . m I d e n t i f y S e g m e n t 
    @tracef("AUD")
    def mIdentifySegment(self,collectionid,nsegments,currentsegment):
        # Get list of document IDs in the collection
        cCollection = G.dID2Collection[mysCollectionID]
        lDocIDs = cCollection.mListDocuments()

        return []

# NEW NEW NEW 
# c l a s s   C A u d i t _ Z i p f 
class CAudit_Zipf(CAudit):
    '''\
    This is the tricky one: 
    - group docs into a small number of bins based on (Zipf) frequency of access
    - i think
    - still need to work out details of this type
    '''
    # NEW NEW NEW 
    # C A u d i t _ Z i p f . m C a l c S e g m e n t S i z e 
    @tracef("AUD")
    def mIdentifySegment(self,collectionid,nsegments,currentsegment):
        # Get list of document IDs in the collection
        cCollection = G.dID2Collection[mysCollectionID]
        lDocIDs = cCollection.mListDocuments()
        
        return []

# NEW NEW NEW 
# f A u d i t _ S e l e c t 
# Stupid factory function to create the right class for this audit strategy.
@tracef("AUD")
def fAudit_Select(mysStrategy):
    if mysStrategy == "TOTAL":
        thing = CAudit_Total()
    elif mysStrategy == "SYSTEMATIC":
        thing = CAudit_Systematic()
    elif mysStrategy == "UNIFORM":
        thing = CAudit_Uniform()
    elif mysStrategy == "ZIPF":
        thing = CAudit_Zipf()
    else:
        # Forgiving version:
        thing = CAudit()
        # Tight-ass version:
        #raise ValueError, "Unknown Audit strategy: %s" % (mysStrategy)
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
 summary of the r3b.py test program that acutally works properly.
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
#
#


#END
