#!/usr/bin/python
# document.py
# 
import simpy
from NewTraceFac import NTRC,ntrace,ntracef
import itertools
from globaldata import G
from audit2 import fAudit_Select
import util
import math
import logoutput as lg
import collections as cc
from    catchex         import  catchex


#===========================================================
# D O C U M E N T 
#----------------

class CDocument(object):
    getID = itertools.count(1).next

# 
    @ntracef("DOC")
    def __init__(self,size,mysClientID,mysCollectionID):
        self.ID = "D" + str(self.getID())
# BEWARE: if we have more than 10,000 docs, a fixed-length 
#  representation will have to change.  Bad idea; don't use it.
#  Change the sorting algorithm instead.
#        self.ID = "D" + "%04d"%(self.getID())
#  So, don't use it.
        G.dID2Document[self.ID] = self
        G.nDocLastID = self.ID
        self.nSize = size
        
        # Who owns this doc
        self.sClientID = mysClientID        # Doc owned by what client
        self.sCollID = mysCollectionID      # Doc lives in what collection
        NTRC.ntracef(3,"DOC","proc init client|%s| created doc|%s| size|%d|" % (self.sClientID,self.ID,self.nSize))
        
        # Where are copies of this doc stored
        self.lServerIDs = list()            # What servers currently have this doc
        self.lCopyIDs = list()              # What copy IDs are there of this doc
        self.setServerIDsAll = set([])      # What servers have ever had a copy
        
        # How has the doc fared in the storage wars
        self.bMajorityRepair = False        # True if ever repaired from majority of copies
        self.bMinorityRepair = False        # True if ever repaired from minority of copies
        self.bDocumentLost = False          # True if completely lost, all copies lost
        self.bDocumentOkay = True           # True if never repaired or lost
        self.nRepairsMajority = 0           # Number of repairs of doc from majority copies
        self.nRepairsMinority = 0           # Number of repairs of doc from minority copies

# D o c u m e n t . m C o p y P l a c e d O n S e r v e r 
    @ntracef("DOC")
    def mCopyPlacedOnServer(self,mysCopyID,mysServerID):
        self.lCopyIDs.append(mysCopyID)
        self.lServerIDs.append(mysServerID)
        self.setServerIDsAll.add(mysServerID)
        return self.ID+"+"+mysCopyID+"+"+mysServerID

# NEW NEW NEW replacement
# D o c u m e n t . m T e s t C o p i e s 
    @ntracef("DOC")
    def mTestCopies(self):
        '''\
        Return status of document: 
        - okay = all copies intact, 
        - injured = majority but not all copies intact, 
        - forensics required = nonzero minority of copies intact, 
        - lost = zero copies remaining intact.  
        '''
        cColl = G.dID2Collection[self.sCollID]
        (bOkay,bInjured,bForensics,bLost) = self.mEvaluateMe() #cColl.mEvaluateOneDoc(self.ID)
        # I think I meant to do something more here, but I forgot what.          
        return (bOkay,bInjured,bForensics,bLost)

# D o c u m e n t . m E v a l u a t e M e 
    @ntracef("DOC")
    def mEvaluateMe(self):
        '''\
        Return tuple of four bools stating doc status.
        How many copies do I have left (if any)?
        '''
        nCopiesLeft = len(
                        filter(
                            (lambda sServerID:
                                self.mTestOneServer(sServerID))
                            ,self.lServerIDs)
                         )
        # Are there any or enough copies left from which to repair the doc?
        nNumberOfServers = len(self.setServerIDsAll)
        nMajorityOfServers = (nNumberOfServers + 1) / 2
        # Include results from previous audits (if any).
        (bOkay, bMajority, bMinority, bLost) = (self.bDocumentOkay, self.bMajorityRepair,self.bMinorityRepair,self.bDocumentLost)
        NTRC.ntracef(3,"DOC","proc mEvaluateMe doc|%s| ncopies|%s| nservers|%s| okay|%s| majority|%s| minority|%s| lost|%s|" % (self.ID,nCopiesLeft,nNumberOfServers,bOkay,bMajority,bMinority,bLost))
        if nCopiesLeft > 0:
            # If there is a majority of copies remaining, 
            # then unambiguous repair is possible.
            if nCopiesLeft < nNumberOfServers and nCopiesLeft >= nMajorityOfServers:
                bMajority = True
                bOkay = False
            # Some copies left, but not enough for unambiguous repair.
            # Record that forensics are required for this doc repair. 
            elif nCopiesLeft < nMajorityOfServers:
                bMinority = True
                bOkay = False
        # There are no remaining copies of the doc, 
        # it cannot be repaired ever, oops.  Permanent loss.  
        else:
            bLost = True
            bOkay = False
        return (bOkay,bMajority,bMinority,bLost)

# D o c u m e n t . m T e s t O n e S e r v e r 
    @ntracef("DOC")
    def mTestOneServer(self,mysServerID):
        cServer = G.dID2Server[mysServerID]
        bResult = cServer.mTestDocument(self.ID)
        return bResult

# D o c u m e n t . m D o c M a r k L o s t 
    @ntracef("DOC")
    def mMarkLost(self):
        self.bDocumentLost = True
        self.bDocumentOkay = False
        cCollection = G.dID2Collection[self.sCollID]
        cCollection.mMarkDocLost(self.ID)

# D o c u m e n t . m I s L o s t 
    @ntracef("DOC")
    def mIsLost(self):
        return self.bDocumentLost

# D o c u m e n t . m D o c M a r k M a j o r i t y R e p a i r 
    @ntracef("DOC")
    def mMarkMajorityRepair(self):
        self.bMajorityRepair = True
        self.nRepairsMajority += 1
        self.bDocumentOkay = False
        return self.nRepairsMajority

# D o c u m e n t . m D o c M a r k M i n o r i t y R e p a i r
    @ntracef("DOC")
    def mMarkMinorityRepair(self):
        self.bMinorityRepair = True
        self.nRepairsMinority += 1
        self.bDocumentOkay = False
        return self.nRepairsMinority

# D o c u m e n t . m D o c R e s c i n d M a j o r i t y R e p a i r 
    @ntracef("DOC")
    def mRescindMajorityRepair(self):
        self.bMajorityRepair = True
        self.nRepairsMajority -= 1
        self.bDocumentOkay = False
        return self.nRepairsMajority

# D o c u m e n t . m D o c R e s c i n d M i n o r i t y R e p a i r
    @ntracef("DOC")
    def mRescindMinorityRepair(self):
        self.bMinorityRepair = True
        self.nRepairsMinority -= 1
        self.bDocumentOkay = False
        return self.nRepairsMinority

# D o c u m e n t . m D e s t r o y C o p y 
    @catchex
    @ntracef("DOC")
    def mDestroyCopy(self,mysServerID,mysCopyID):
        '''\
        Remove Server's Copy of this Document.  
        
        Actually, just remove Server from the list of Servers with 
        copies of this Document.  
        '''
        self.lServerIDs.remove(mysServerID)
        self.lCopyIDs.remove(mysCopyID)

# Document.mMergeEvaluation
    @ntracef("DOC")
    def mMergeEvaluation(self,mybOkay,mybMajority,mybMinority,mybLost):
        '''\
        Carefully combine new doc info with old from audits, if any.
        
        E.g., finally okay only if was okay and still is okay; 
        finally lost if was lost or is now lost.  
        '''
        NTRC.ntracef(3,"DOC","proc merge in|%s|%s|%s|%s| with doc|%s|%s|%s|%s|" % (mybOkay,mybMajority,mybMinority,mybLost,self.bDocumentOkay,self.bMajorityRepair,self.bMinorityRepair,self.bDocumentLost))
        self.bDocumentOkay = self.bDocumentOkay and mybOkay
        self.bMajorityRepair = self.bMajorityRepair or mybMajority
        self.bMinorityRepair = self.bMinorityRepair or mybMinority
        self.bDocumentLost = self.bDocumentLost or mybLost
        return (self.bDocumentOkay,self.bMajorityRepair,self.bMinorityRepair,self.bDocumentLost)

# D o c u m e n t . m G e t R e p a i r C o u n t s 
    def mGetRepairCounts(self):
        return(self.nRepairsMajority,self.nRepairsMinority)

# D o c u m e n t . m R e p o r t D o c u m e n t S t a t s 
    @ntracef("DOC")
    def mdReportDocumentStats(self):
        '''\
        Return a dictionary of relevant stats.
        '''
        #dd = cc.defaultdict(list)
        dd = dict()
        dd["sDocID"]            = self.ID
        dd["sClientID"]         = self.sClientID
        dd["sCollectionID"]     = self.sCollID
        dd["nSize"]             = self.nSize
        dd["bMajorityRepair"]   = self.bMajorityRepair
        dd["bMinorityRepair"]   = self.bMinorityRepair
        dd["bDocumentLost"]     = self.bDocumentLost
        dd["nRepairsMajority"]  = self.nRepairsMajority
        dd["nRepairsMinority"]  = self.nRepairsMinority
        return dd

# Edit history:
# 20150812  RBL Remove class from client.py into its own file. 
# 20160224  RBL Remove spurious import of CServer.
# 
# 

#END

