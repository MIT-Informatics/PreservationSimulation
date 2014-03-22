#!/usr/bin/python
# repair.py

import simpy
from NewTraceFac import TRC,trace,tracef
import itertools
from globaldata import *
from logoutput import logInfo


# C l a s s   C R e p a i r 
class CRepair(object):
    getID = itertools.count().next

    @tracef("REP")
    def __init__(self,mysClientID):
        self.ID = "R" + str(self.getID())
        G.dID2Repair[self.ID] = self

        self.sClientID = mysClientID
        self.cClient = G.dID2Client[self.sClientID]
    
        pass




    @tracef("REP")
    def mAuditCycle(self):
        # wait for a while, then auditnext
        pass

    @tracef("REP")
    def mAuditNextCollection(self):
        self.sCollIDLastAudited = self.lCollectionIDs[(index(self.sCollIDLastAudited) + 1) % len(self.lCollections)]
        self.mAuditCollection(self.sCollIDLastAudited)
        return self.sCollIDLastAudited

    @tracef("REP")
    def mAuditCollection(self,mysCollectionID):
        # find server with a copy of collection to audit
        
        for cDoc in G.dID2Collection[mysCollectionID].lDocumentIDs:
            # Ask for validation of each doc.
            # In this case, the only quesiton is if the server
            #  still has a copy, that is, if a sector error has
            #  not caused a hidden failure in the document.  
            # If not valid, initiate repair.
            pass

    @tracef("REP")
    def mDocAuditAllDocsOnServer(self,mysCollectionID,mysServerID):
        pass
        
    @tracef("REP")
    def mDocAuditOnAllServers(self,mysDocID):
        pass
        
    @tracef("REP")
    def mDocAuditOneDocOnServer(self,mysCollectionID):
        pass


# END
