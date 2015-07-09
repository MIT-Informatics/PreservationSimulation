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


"""
# m A u d i t C y c l e 
    @tracef("REP")
    def mAuditCycle(self):
        # wait for a while, then auditnext
        pass

# m A u d i t N e x t C o l l e c t i o n 
    @tracef("REP")
    def mAuditNextCollection(self):
        self.sCollIDLastAudited = self.lCollectionIDs[(index(self.sCollIDLastAudited) + 1) % len(self.lCollections)]
        self.mAuditCollection(self.sCollIDLastAudited)
        return self.sCollIDLastAudited

# m A u d i t C o l l e c t i o n 
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

# m D o c A u d i t A l l D o c s O n S e r v e r 
    @tracef("REP")
    def mDocAuditAllDocsOnServer(self,mysCollectionID,mysServerID):
        pass
        
# m D o c A u d i t O n A l l S e r v e r s 
    @tracef("REP")
    def mDocAuditOnAllServers(self,mysDocID):
        pass
        
# m D o c A u d i t O n e D o c O n S e r v e r 
    @tracef("REP")
    def mDocAuditOneDocOnServer(self,mysCollectionID):
        pass
"""


# END
