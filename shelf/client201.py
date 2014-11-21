#!/usr/bin/python
# client2.py
# 
import simpy
from NewTraceFac import TRC,trace,tracef
import itertools
from globaldata import G
from server import CServer
from audit2 import fAudit_Select
from repair import CRepair
import util
import math
import logoutput as lg
import collections as cc


#===========================================================
# D O C U M E N T 
#----------------

class CDocument(object):
    getID = itertools.count(1).next

# 
    @tracef("DOC")
    def __init__(self,size,mysClientID,mysCollectionID):
        self.ID = "D" + str(self.getID())
        G.dID2Document[self.ID] = self
        G.nDocLastID = self.ID
        self.nSize = size
        
        # Who owns this doc
        self.sClientID = mysClientID        # Doc owned by what client
        self.sCollID = mysCollectionID      # Doc lives in what collection
        TRC.tracef(3,"DOC","proc init client|%s| created doc|%s| size|%d|" % (self.sClientID,self.ID,self.nSize))
        
        # Where are copies of this doc stored
        self.lServerIDs = list()            # What servers have this doc
        self.lCopyIDs = list()              # What copy IDs of this doc
        
        # How has the doc fared in the storage wars
        self.bMajorityRepair = False        # True if ever repaired from majority of copies
        self.bMinorityRepair = False        # True if ever repaired from minority of copies
        self.bDocumentLost = False          # True if completely lost, all copies lost
        self.bDocumentOkay = True           # True if never repaired or lost
        self.nRepairsMajority = 0           # Number of repairs of doc from majority copies
        self.nRepairsMinority = 0           # Number of repairs of doc from minority copies

# D o c u m e n t . m C o p y P l a c e d O n S e r v e r 
    @tracef("DOC")
    def mCopyPlacedOnServer(self,mysCopyID,mysServerID):
        self.lCopyIDs.append(mysCopyID)
        self.lServerIDs.append(mysServerID)
        return self.ID+"+"+mysCopyID+"+"+mysServerID

# NEW NEW NEW replacement
# D o c u m e n t . m T e s t C o p i e s 
    @tracef("DOC")
    def mTestCopies(self):
        ''' Return status of document: 
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
    @tracef("DOC")
    def mEvaluateMe(self):
        # Return tuple of four bools stating doc status.
        # How many copies do I have left (if any)?
        nCopiesLeft = len(
                        filter(
                            (lambda sServerID:
                                self.mTestOneServer(sServerID))
                            ,self.lServerIDs)
                         )
        # Are there any or enough copies left from which to repair the doc?
        nNumberOfServers = len(self.lServerIDs)
        nMajorityOfServers = (nNumberOfServers + 1) / 2
        # Include results from previous audits (if any).
        (bOkay, bMajority, bMinority, bLost) = (self.bDocumentOkay, self.bMajorityRepair,self.bMinorityRepair,self.bDocumentLost)
        TRC.tracef(3,"DOC","proc mEvaluateMe doc|%s| ncopies|%s| nservers|%s| okay|%s| majority|%s| minority|%s| lost|%s|" % (self.ID,nCopiesLeft,nNumberOfServers,bOkay,bMajority,bMinority,bLost))
        if nCopiesLeft > 0:
            # If there is a majority of copies remaining, 
            # then unambiguous repair is possible.
            if nCopiesLeft < nNumberOfServers and nCopiesLeft >= nMajorityOfServers:
                bMajority = True
            # Some copies left, but not enough for unambiguous repair.
            # Record that forensics are required for this doc repair. 
            elif nCopiesLeft < nMajorityOfServers:
                bMinority = True
        # There are no remaining copies of the doc, 
        # it cannot be repaired ever, oops.  Permanent loss.  
        else:
            bLost = True
        return (bOkay,bMajority,bMinority,bLost)

# D o c u m e n t . m T e s t O n e S e r v e r 
    @tracef("DOC")
    def mTestOneServer(self,mysServerID):
        cServer = G.dID2Server[mysServerID]
        bResult = cServer.mTestDocument(self.ID)
        return bResult

# D o c u m e n t . m D o c M a r k L o s t 
    @tracef("DOC")
    def mMarkLost(self):
        self.bDocumentLost = True
        self.bDocumentOkay = False

# D o c u m e n t . m D o c I s L o s t 
    @tracef("DOC")
    def mIsLost(self):
        return self.bDocumentLost

# D o c u m e n t . m D o c M a r k M a j o r i t y R e p a i r 
    @tracef("DOC")
    def mMarkMajorityRepair(self):
        self.bDocumentMajorityRepair = True
        self.nRepairsMajority += 1
        self.bDocumentOkay = False

# D o c u m e n t . m D o c M a r k M i n o r i t y R e p a i r
    @tracef("DOC")
    def mMarkMinorityRepair(self):
        self.bDocumentMinorityRepair = True
        self.nRepairsMinority += 1
        self.bDocumentOkay = False

# D o c u m e n t . m R e p o r t D o c u m e n t S t a t s 
    @tracef("DOC")
    def mdReportDocumentStats(self):
        '''\
        Return a dictionary of relevant stats.
        '''
        #dd = cc.defaultdict(list)
        dd = dict()
        dd["sDocID"]               = self.ID
        dd["sClientID"]         = self.sClientID
        dd["sCollectionID"]     = self.sCollID
        dd["nSize"]             = self.nSize
        dd["bMajorityRepair"]   = self.bMajorityRepair
        dd["bMinorityRepair"]   = self.bMinorityRepair
        dd["bDocumentLost"]     = self.bbDocumentLost
        dd["nRepairsMajority"]  = self.nRepairsMajority
        dd["nRepairsMinority"]  = self.nRepairsMinority
        return dd


#===========================================================
# C O L L E C T I O N 
#--------------------

class CCollection(object):
    getID = itertools.count(1).next

    @tracef("COLL")
    def __init__(self,mysName,mynValue,mynSize,mysClientID):
        self.ID = "C" + str(self.getID())
        G.dID2Collection[self.ID] = self
        G.nCollLastID = self.ID

        self.sName = mysName
        self.nValue = mynValue
        self.sClientID = mysClientID
        self.lDocIDs = list()
        self.lServerIDs = list()

        # Summary counters for document status at end of run.
        self.nDocsOkay = 0
        self.nDocsMajorityRepair = 0
        self.nDocsMinorityRepair = 0
        self.nDocsLost = 0

        # Action: create all books in the collection.
        self.mMakeBooks(mynSize)
        
# C o l l e c t i o n . m M a k e B o o k s 
    @tracef("COLL")
    def mMakeBooks(self,mynBooks):
        # A collection has lots of books
        for icoll in xrange(mynBooks):
            ndocsize = util.fnnCalcDocSize(self.nValue)
            cDoc = CDocument(ndocsize,self.sClientID,self.ID)
            self.lDocIDs.append(cDoc.ID)
        return self.ID

# C o l l e c t i o n . m L i s t D o c u m e n t s 
    @tracef("COLL")
    def mListDocuments(self):
        TRC.tracef(5,"COLL","proc mListDocuments self|%s| returning |%s|" % (self,self.lDocIDs))
        return (self.lDocIDs)

# NEW NEW NEW replacement
# C o l l e c t i o n . m T e s t C o l l e c t i o n
    @tracef("COLL")
    def mTestCollection(self):
        ''' Return a list, maybe empty, of documents declared missing
            from this collection.  
        '''
        lDeadDocIDs = list()
        for sDocID in self.lDocIDs:
            cDoc = G.dID2Document[sDocID]
            (bOkay,bInjured,bForensics,bLost) = cDoc.mTestCopies()
            TRC.tracef(3,"COLL","proc TestColl1 coll|%s| tests doc|%s| okay|%s| injured|%s| forensics|%s| lost|%s|" % (self.ID,sDocID,bOkay,bInjured,bForensics,bLost))
            # Update stats of document statuses.  
            self.nDocsOkay += 1 if bOkay else 0
            self.nDocsMajorityRepair += 1 if bInjured else 0
            self.nDocsMinorityRepair += 1 if bForensics else 0
            self.nDocsLost += 1 if bLost else 0
            # Update lost list.
            if bLost:
                lDeadDocIDs.append(sDocID)
                TRC.tracef(3,"COLL","proc TestColl2 dead doc|%s| in coll|%s| " % (sDocID,self.ID))
        return lDeadDocIDs


# C C o l l e c t i o n . m H o w M a n y C o p i e s L e f t 
    @tracef("COLL")
    def mHowManyCopiesLeft(self):
        ''' Return list for all docs of how many copies exist across all servers.
        '''
        lDocAliveCounts = map( 
            (lambda sDocID:                                         \
                len(                                                \
                    filter(                                         \
                        (lambda sServerID:                          \
                            self.mIsDocInServer(sDocID,sServerID)), \
                        self.lServerIDs))),                         \
            self.lDocIDs )
        return lDocAliveCounts

# C o l l e c t i o n . m I s D o c I n S e r v e r 
    @tracef("COLL")
    def mIsDocInServer(self,mysDocID,mysServerID):
        ''' Return t/f is this doc present on that server. '''
        cServer = G.dID2Server[mysServerID]
        bResult = cServer.mTestDocument(mysDocID)
        return bResult

# C o l l e c t i o n . m H o w M a n y C o p i e s L e f t O f T h i s O n e D o c 
    @tracef("COLL",level=5)
    def mHowManyCopiesLeftOfThisOneDoc(self,mysDocID):
        ''' Return (scalar) the number of copies that exist of this doc. '''
        nLeftNow = len(                                             \
                    filter(                                         \
                        (lambda sServerID:                          \
                            self.mIsDocInServer(mysDocID,sServerID)), \
                        self.lServerIDs))
        return nLeftNow

# C o l l e c t i o n . m E v a l u a t e O n e D o c 
    @tracef("COLL")
    def mEvaluateOneDoc(self,mysDocID):
        ''' Return status of document, four bools: 
            - okay = all copies intact, 
            - injured = majority but not all copies intact, 
            - forensics required = nonzero minority of copies intact, 
            - lost = zero copies remaining intact.  
        '''
        nCopiesLeft = self.mHowManyCopiesLeftOfThisOneDoc(mysDocID)
        nNumberOfServers = len(self.lServerIDs)
        nMajorityOfServers = (nNumberOfServers + 1) / 2
        bOkay = bInjured = bForensics = bLost = False
        
        # Are there any or enough copies left from which to repair the doc?
        if nCopiesLeft > 0:
            # If all copies remain, then doc is okay.
            if nCopiesLeft == nNumberOfServers :
                bOkay = True
            # If there is a majority of copies remaining, 
            # then unambiguous repair is possible.
            elif nCopiesLeft >= nMajorityOfServers:
                bInjured = True
            # Some copies left, but not enough for unambiguous repair.
            # Record that forensics are required for this doc repair. 
            else:
                bForensics = True
        # There are no remaining copies of the doc, 
        # it cannot be repaired ever, oops.  Permanent loss.  
        else:
            bLost = True
        
        return (bOkay,bInjured,bForensics,bLost)

# C o l l e c t i o n . m R e p o r t C o l l e c t i o n S t a t s 
    @tracef("COLL")
    def mReportCollectionStats(self):
        return (self.ID,self.sClientID,len(self.lServerIDs),len(self.lDocIDs), self.nDocsOkay,self.nDocsInjured,self.nDocsForensics,self.nDocsLost)

    def mdReportCollectionStats(self):
        '''\
        Return a dictionary of relevant stats.
        '''
        #dd = cc.defaultdict(list)
        dd = dict()
        dd["sClientID"]         = self.sClientID
        dd["sCollectionID"]     = self.ID
        dd["nDocs"]             = len(self.lDocIDs)
        dd["nServers"]          = len(self.lServerIDs)
        dd["nOkay"]             = self.nDocsOkay
        dd["nRepairsMajority"]  = self.nDocsMajorityRepair
        dd["nRepairsMinority"]  = self.nDocsMinorityRepair
        dd["nLost"]             = self.nDocsLost
        return dd


#===========================================================
# C L I E N T 
#------------

class CClient(object):
    sCollIDLastAudited = ""
    getID = itertools.count(1).next

    @tracef("CLI")
    def __init__(self,mysName,mylCollections):
        self.ID = "T" + str(self.getID())
        G.dID2Client[self.ID] = self
        G.nClientLastID = self.ID
        self.sName = mysName
        # Establish a non-shared resource for network bandwidth 
        # to be used during auditing.
        self.NetworkBandwidthResource = simpy.Resource(G.env,capacity=1)

        # Create the collections for this client.
        self.lCollectionIDs = list()
        for lCollectionParams in mylCollections:
            (sCollName,nCollValue,nCollSize) = lCollectionParams
            cColl = CCollection(sCollName,nCollValue,nCollSize, self.ID)
            sCollID = cColl.ID
            self.lCollectionIDs.append(sCollID)

            # Put the collection in all the right places.  
            self.mPlaceCollection(sCollID)

        #self.cRepair = CRepair(self.ID)

# C l i e n t . m P l a c e C o l l e c t i o n
    @tracef("CLI")
    def mPlaceCollection(self,mysCollID):
        ''' Client.mPlaceCollection()
            Get list of servers available at the right quality level.
            Select the policy-specified number of them.
            Send the collection to each server in turn.  
        '''
        cColl = G.dID2Collection[mysCollID]
        nCollValue = cColl.nValue
        lServersForCollection = self.mSelectServersForCollection(nCollValue)
        # The distribution params have already limited the 
        # set of servers in the select-for-collection routine.
        lServersToUse = lServersForCollection
        ''' If there aren't servers enough at this level, 
            it's an error.  
            We *could* go to a higher level, but this is only
            a simulation, not real life.  
        '''
        TRC.tracef(3,"CLI","proc mPlaceCollection1 client|%s| place coll|%s| to|%d|servers" % (self.ID,mysCollID,len(lServersToUse)))

        # Distribute collection to a set of servers.
        for (sServerName,sServerID) in lServersToUse:
            TRC.tracef(3,"CLI","proc mPlaceCollection2 client|%s| send coll|%s| to server|%s|" % (self.ID,mysCollID,sServerID))
            TRC.tracef(3,"SHOW","proc mPlaceCollection2 client|%s| send coll|%s| to server|%s|" % (self.ID,mysCollID,sServerID))
            
            # Send copy of collection to server.
            cServer = G.dID2Server[sServerID]
            cServer.mAddCollection(mysCollID,self.ID)

            # Record that this server has a copy of this collection.
            cColl.lServerIDs.append(sServerID)
            lg.logInfo("CLIENT","client|%s| placed collection|%s| to server|%s|" % (self.ID,mysCollID,sServerID))

        # Initialize the auditing process for this collection.
        if G.nAuditCycleInterval > 0:
            self.cAudit = fAudit_Select(G.sAuditStrategy,self.ID,mysCollID,G.nAuditCycleInterval)

        return lServersToUse

# C l i e n t . m S e l e c t S e r v e r s F o r C o l l e c t i o n
    @tracef("CLI")
    def mSelectServersForCollection(self,mynCollValue):
        ''' Get list of servers at this quality level.
            Return a random permutation of the list of servers.
        '''
        # Get list of all servers at this quality level.
        # Value level translates to quality required and nr copies.
        (nQuality,nCopies) = G.dDistnParams[mynCollValue][0]
        lServersAtLevel = G.dQual2Servers[nQuality]
        '''
        ### Old code now inoperative.
        # Pick a random set of servers.
        # For questions 0 and 1, this is not relevant, since all servers
        #  are identical.  Just take the right number of them.
        '''
        lPermChosenFull = lServersAtLevel
        lPermChosen = lPermChosenFull[0:nCopies]
        return lPermChosen

# C l i e n t . m T e s t C l i e n t 
    @tracef("CLI")
    def mTestClient(self):
        ''' Return list, maybe empty, of all documents missing from 
            this client.  All collections appended together.
        '''
        lDeadDocIDs = list()
        for sCollID in self.lCollectionIDs:
            cColl = G.dID2Collection[sCollID]
            lResult = cColl.mTestCollection()
            TRC.tracef(3,"CLI","proc TestClient1 client|%s| tests coll|%s| result|%s|" % (self.ID,sCollID,lResult))
            if len(lResult) > 0:
                lDeadDocIDs.extend(lResult)
                TRC.tracef(3,"CLI","proc TestClient2 client |%s| coll|%s| lost docs|%s|" % (self.ID,sCollID,lResult))
        return lDeadDocIDs

# C l i e n t . m L i s t C o l l e c t i o n I D s 
    @tracef("CLI")
    def mListCollectionIDs(self):
        return self.lCollectionIDs


# END
