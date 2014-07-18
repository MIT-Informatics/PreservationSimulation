#!/usr/bin/python
# audit.py
#

''' TODO:
    x- Put bandwidth into G.
    x- Put hours conversion const into G.
    x- Put audit frequency into G.
    x- Add Server to specificity of Audit.
    x- Add traces.
    - Use docs only, not copies.  Clients don't know copies.  
    - Actually replace the doc using the standard function to repair it.
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
when audit cycle done, wait for standard interval
'''

from globaldata import G
import itertools
from util import makeunif,fnfCalcTransferTime
from NewTraceFac import TRC,trace,tracef


# c l a s s   C A u d i t 
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
        # Start the free-running process of audit cycles for 
        # this collection.
        G.env.process(self.mAuditCycle(self.nCycleInterval))
        '''
        # TEMP TEMP TEMP TEMP TEMP TEMP
        G.nAuditCycleInterval = 10000
        G.nBandwidthMbps = 10
        G.fSecondsPerHour = float(60*60)
        # END TEMP END TEMP END TEMP END
        '''

    # C A u d i t . m A u d i t C y c l e 
    @tracef("AUD")
    def mAuditCycle(self,mynInterval):
        ''' SimPy generator to schedule audit cycles for this collection.
            Starts an async process that ticks every 
            audit cycle forever.
        '''
        # Initially, wait for some small random interval
        # so that client audit cycles are not synchronized. 
        nRandTime = makeunif(0,mynInterval/2)
        yield G.env.timeout(nRandTime)
        
        while True:
            yield G.env.timeout(mynInterval)
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
                fTransferTime = self.mRepairDoc(sDocID)
                yield G.env.timeout(fTransferTime)

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
        return fTransferTime

#END
