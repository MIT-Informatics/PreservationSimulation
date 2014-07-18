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
    x- Do we want to avoid possible cycle overlap by doing auditing sequentially?
      No, I think: might want different auditing criteria for different servers.  
      Some servers are better than others.  Certainly we might have different
      auditing strategies for servers that can compute checksums with nonces.
    - Do we need separate upload and download bandwidths?  Upload usually slower.
    x- Do not reuse disk space that has already suffered a failure.
    - Yes, split bandwidth send/receive, especially for server-based checksum strategy.
    x- Do cross-server assessment for permanent losses at the end of each audit cycle.  
      Have to keep a record during the audit about failures and repairs.
      BZZZT: No, do the cross-server assessment at the beginning of each audit cycle.
      Use that to assess what documents need to be audited.  Yes, this messes up the 
      timekeeping, I think.  
    x- During audit, assess whether there is a majority of copies left so that 
      one can do an unambiguous repair; if not, record a "manual repair requiring forensics." 
      There is no master copy from which repairs can be done; even the owning client's 
      copy is among those being aged; the auditor owns no content.  
    - Don't do audits in lockstep, but random start times not required.
    x- Auditing strategy 1: complete.
    - Other auditing strategy 2: random subset.
    - Other auditing strategy 3: usage-based, probably based on Zipf distribution, audit
      more popular docs more frequently.  
    - Other auditing strategy 4: partitioned.  4A: server partition: audit each storage
      shelf separately.  4B: client partitioned: systematic portions of collection.  
    x- Optimize testing docs in servers, which happens waaay too frequently.
    x- Report auditing stats at end of run.  
    x- BUG: perm losses overcounted, every time they are seen.  Must do only once.
    x- BUG: sometimes a repair happens with ncopies==nservers.  Why is the doc 
      even called out for inspection if the number of servers is okay?  Aha, the 
      doc had an error between the beginning of the audit and now.  Okay, have to 
      reevaluate that single doc before attempting to repair.
    - Why bother to pre-evaluate the status of all docs at the start of an audit?
      If the doc is okay on my server, my audit is find.  Only if it is dead on 
      my server, do I bother to look at all the other servers to see if there
      are enough copies to repair.  Should be much faster.

    - Future: auditor maintains guaranteed copy of fixity info for use in auditing.  
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

''' Slightly more sophisticated view of auditing:
- The client does not have a reserve copy of a document, so any error
  with copies=1 is permanent.  
- For any doc that has an error in any copy, we need to know how many
  copies still exist.  If there is not a majority of the copies still
  available, then the repair is considered as "requiring forensics."
- At the beginning of each audit cycle, need to assess how many 
  copies exist for any document that has any errors on any server.  

- At the beginning of each audit cycle, survey all servers, make
  a list of how many copies exist for each doc.
- During the audit, for each doc with an error, how many copies 
  remain?
  - zero: permanent failure.
  - .ge. half of the servers: make the repair.  Odd numbers round up.
  - .lt. half of the servers: repair but with forensics required.

'''

''' Optimized version of total auditing (but retaining timing):
    - Audit is specific to client, collection, and server.
    - Retrieve doc.  
    - If doc is absent, count copies on all servers.
    - If no copies remain, then permanent loss of this doc.
    - If >= majority still have copies, repair this doc.
    - If < majority still have copies, then repair with forensics-required flag.
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
        
        self.dDocsAlreadyLost = dict()

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
            self.nNumberOfCycles += 1

            # So much for timekeeping.  Now do some actual work.
            # How many copies remain of each document (for majority voting on repairs).
            cCollection = G.dID2Collection[mysCollectionID]
            #self.lDocsHowManyCopiesLeft = cCollection.mHowManyCopiesLeft()
            # Get the list of document IDs and check them all.
            lDocIDs = cCollection.mListDocuments()
            for sDocID in lDocIDs:
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
                            logInfo("AUDIT","repair doc  t|%9.3f| auditid|%s| cli|%s| coll|%s| svr|%s| doc|%s| from copies|%d|" % (G.env.now,self.ID,self.sClientID,self.sCollectionID,self.sServerID,sDocID,nCopiesLeft))

                        # Some copies left, but not enough for unambiguous repair.
                        # Record that forensics are required for this doc repair. 
                        else:
                            # Patch the doc from a minority copy. 
                            self.nForensicsRequired += 1 
                            fTransferTime = self.mRepairDoc(sDocID)
                            yield G.env.timeout(fTransferTime)
                            logInfo("AUDIT","patch doc   t|%9.3f| auditid|%s| cli|%s| coll|%s| svr|%s| doc|%s| minority copies|%d|" % (G.env.now,self.ID,self.sClientID,self.sCollectionID,self.sServerID,sDocID,nCopiesLeft))

                    # There are no remaining copies of the doc, 
                    # we cannot repair it, oops.  Permanent loss.  
                    else:
                        if not sDocID in self.dDocsAlreadyLost:
                            self.nPermanentLosses += 1
                            self.dDocsAlreadyLost[sDocID] = (self.nNumberOfCycles)
                            #TRC.tracef(3,"AUD","proc mAuditCollection no copy for repair doc|%s| idx|%d|" % (sDocID,idx))
                            logInfo("AUDIT","lost doc    t|%9.3f| auditid|%s| cli|%s| coll|%s| svr|%s| doc|%s| copies left|%d|" % (G.env.now,self.ID,self.sClientID,self.sCollectionID,self.sServerID,sDocID,nCopiesLeft))

            fTimeCycleEnd = G.env.now
            fTimeCycleLength = fTimeCycleEnd - fTimeCycleBegin
            logInfo("AUDIT","end cycle   t|%9.3f| auditid|%s| cli|%s| coll|%s svr|%s| repairs|%d| total|%d| perms|%d| forensics|%d| duration|%9.3f|" % (G.env.now,self.ID,self.sClientID,self.sCollectionID,self.sServerID,self.nRepairsThisCycle,self.nRepairsTotal,self.nPermanentLosses,self.nForensicsRequired,fTimeCycleLength))

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

# CAudit.mReportAuditStats
    def mReportAuditStats(self):
        return(self.ID,self.sClientID,self.sCollectionID,self.sServerID
            ,self.nNumberOfCycles,self.nRepairsTotal
            ,self.nPermanentLosses,self.nForensicsRequired)

#END
