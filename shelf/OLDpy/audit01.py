#!/usr/bin/python
# audit.py
#

''' TODO (x=done):
    x- Put bandwidth into G.
    x- Put hours conversion const into G.
    x- Put audit frequency into G.
    x- Add Server to specificity of Audit.
    x- Add traces.
    x- Use docs only, not copies.  Clients don't know copies.  
    x- Actually replace the doc using the standard function to repair it.
    x- Add logging so we can see it working.
    x- Audit on a regular schedule, not n hours after the last one finishes.
    x- Add counters of repairs.
    - Do we really want to start audits at random times?
    x- Cycles might overlap.  They need to compete for bandwidth as a resource.
    - Do we want to avoid possible cycle overlap by doing auditing sequentially?
      No, I think: might want different auditing criteria for different servers.  
      Some servers are better than others.  Certainly we might have different
      auditing strategies for servers that can compute checksums with nonces.
    - Do we need separate upload and download bandwidths?  Upload usually slower.
    x- Do not reuse disk space that has already suffered a failure.
'''
'''
audit cycle invoked once every x hours:
    foreach client
        foreach collection
            foreach document
                retrieve doc from server
                if doc still exists
                    wait time to retrieve doc rel to size
                    compare with original doc
                    (always success now)
                else
                    repair by sending new copy of doc
                    wait time to send doc rel to size
                
need one async process per client to schedule audit cycles.
need one async process for retrieving doc from server
and for replacing doc in server, since they share bandwidth.

const for interval between audits
const for speed of network while transmitting docs
const for second of time

client creates an audit object for collection
that init starts an async process for the auditing
wait for a random time, so that all client audits do not happen simultaneously
when audit cycle done, wait for next standard interval
'''

from globaldata import G
import itertools
from util import makeunif,fnfCalcTransferTime
from logoutput import logInfo
from NewTraceFac import TRC,trace,tracef


#===========================================================
# C l a s s   C A u d i t 
#-------------------------
class CAudit(object):
    ''' Procedures for auditing collections kept on 
        remote servers.  Clients will create one instance
        of this class for each collection on each server.  
        Collection audits run asynchronously.  
    '''
    getID = itertools.count(1).next

    @tracef("AUD")
    def __init__(self,mysClientID,mysCollectionID,mysServerID,mynInterval=G.nAuditCycleInterval):
        self.ID = "A" + str(self.getID())
        self.sClientID = mysClientID
        self.sServerID = mysServerID
        self.sCollectionID = mysCollectionID
        self.nCycleInterval = mynInterval

        self.nRepairsThisCycle = 0
        self.nRepairsTotal = 0

        # Start the free-running process of audit cycles for 
        # this collection.
        G.env.process(self.mAuditCycle(self.nCycleInterval))

    # C A u d i t . m A u d i t C y c l e 
    @tracef("AUD")
    def mAuditCycle(self,mynInterval):
        ''' SimPy generator to schedule audit cycles for this collection.
            Starts an async process that ticks every 
            audit cycle forever.
        '''
        # Initially, wait for some small random interval
        # so that client audit cycles are not synchronized. 
        nRandTime = makeunif(0,mynInterval/10)
        yield G.env.timeout(nRandTime)
        
        while True:
            yield G.env.timeout(mynInterval)
            logInfo("AUDIT","begin cycle t|%9.3f| auditid|%s| cli|%s| coll|%s svr|%s|" % (G.env.now,self.ID,self.sClientID,self.sCollectionID,self.sServerID))
            self.nRepairsThisCycle = 0
            G.env.process(self.mAuditCollection(self.sCollectionID))

    # C A u d i t . m A u d i t C o l l e c t i o n 
    @tracef("AUD")
    def mAuditCollection(self,mysCollectionID):
        ''' SimPy generator to audit an entire collection.
            foreach copy in the collection
                audit copy
                retrieve copy from server
                if copy still exists
                    wait time to retrieve copy rel to size
                    compare with original doc
                    (always success now)
                else
                    repair copy
                    wait time to send new copy rel to size
        '''
        fTimeCycleBegin = G.env.now
        # Seize the network resource so this audit cycle 
        # can use it exclusively.
        # The "with" should take care of releasing it
        with G.NetworkBandwidthResource.request() as reqnetwork:
            fNetworkWaitBegin = G.env.now
            result = yield reqnetwork
            fNetworkWaitEnd = G.env.now
            fNetworkWaitTime = fNetworkWaitEnd - fNetworkWaitBegin
            # Log event if we had to wait for the network to be free.  
            if fNetworkWaitTime > 0.0:
                logInfo("AUDIT","waitnetwork t|%9.3f| auditid|%s| cli|%s| coll|%s svr|%s| delay|%9.3f|" % (G.env.now,self.ID,self.sClientID,self.sCollectionID,self.sServerID,fNetworkWaitTime))
                # And restart the duration clock after the unproductive wait.
                fTimeCycleBegin = G.env.now
            # Now do some actual work.
            # Get the document IDs and check them all.
            cCollection = G.dID2Collection[mysCollectionID]
            lDocIDs = cCollection.mListDocuments()
            for sDocID in lDocIDs:
                fTransferTime = self.mRetrieveDoc(sDocID)
                if fTransferTime:
                    yield G.env.timeout(fTransferTime)
                    # Here we would test the document contents
                    # for validity, that is, if our documents
                    # had contents.  
                else:
                    # Repair the doc, currently missing.  
                    fTransferTime = self.mRepairDoc(sDocID)
                    #TRC.tracef(5,"AUD","proc repair time before yield t|%13.6f|" % (G.env.now))
                    yield G.env.timeout(fTransferTime)
                    #TRC.tracef(5,"AUD","proc repair time after  yield t|%13.6f|" % (G.env.now))
                    logInfo("AUDIT","repair doc  t|%9.3f| auditid|%s| cli|%s| coll|%s| svr|%s| doc|%s| rprhr|%8.6f|" % (G.env.now,self.ID,self.sClientID,self.sCollectionID,self.sServerID,sDocID,fTransferTime))

            fTimeCycleEnd = G.env.now
            fTimeCycleLength = fTimeCycleEnd - fTimeCycleBegin
            logInfo("AUDIT","end cycle   t|%9.3f| auditid|%s| cli|%s| coll|%s svr|%s| repairs|%d| total|%d| duration|%9.3f|" % (G.env.now,self.ID,self.sClientID,self.sCollectionID,self.sServerID,self.nRepairsThisCycle,self.nRepairsTotal,fTimeCycleLength))

    # C A u d i t . m R e t r i e v e D o c 
    @tracef("AUD")
    def mRetrieveDoc(self,mysDocID):
        ''' Get (copy of) doc back from server, if possible.
            Return the time required to transmit the doc.
            Ideally, would wait for transmission time, 
            but the waiting has to occur in the 
            parent loop.  
        '''
        cDoc = G.dID2Document[mysDocID]
        nDocSize = cDoc.nSize
        fTransferTime = fnfCalcTransferTime(nDocSize,G.nBandwidthMbps)
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
        ''' Repair by sending new copy of original doc
            to the server.  Re-send the doc to the server
            and return the time it took to transfer.
            Ideally, the wait time to send doc rel to size
            would occur here, but it occurs in the parent loop.
        '''
        # How long will it take to transfer?
        cDoc = G.dID2Document[mysDocID]
        nDocSize = cDoc.nSize
        fTransferTime = fnfCalcTransferTime(nDocSize,G.nBandwidthMbps)
        # Re-send the doc to server.
        cServer = G.dID2Server[self.sServerID] 
        cServer.mAddDocument(mysDocID,self.sClientID)
        self.nRepairsThisCycle += 1
        self.nRepairsTotal += 1
        return fTransferTime

#END
