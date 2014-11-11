#!/usr/bin/python
# client2.py
# 
import simpy
from NewTraceFac import TRC,trace,tracef
import itertools
from globaldata import G
from server import CServer
from audit2 import CAudit2
from repair import CRepair
import util
import math
import logoutput as lg


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
        self.sClientID = mysClientID        # Doc owned by what client
        self.sCollID = mysCollectionID      # Doc lives in what collection
        TRC.tracef(3,"DOC","proc init client|%s| created doc|%s| size|%d|" % (self.sClientID,self.ID,self.nSize))
        self.lServerIDs = list()            # What servers have this doc
        self.lCopyIDs = list()              # What copy IDs of this doc
        self.bMajorityRepair = False        # True if ever repaired from majority of copies
        self.bMinorityRepair = False        # True if ever repaired from minority of copies
        self.bDocumentLost = False          # True if completely lost, all copies lost
        self.nRepairsMajority = 0           # Number of repairs of doc from majority copies
        self.nRepairsMinority = 0           # Number of repairs of doc from minority copies

# D o c u m e n t . m C o p y P l a c e d O n S e r v e r 
    @tracef("DOC")
    def mCopyPlacedOnServer(self,mysCopyID,mysServerID):
        self.lCopyIDs.append(mysCopyID)
        self.lServerIDs.append(mysServerID)
        return self.ID+"+"+mysCopyID+"+"+mysServerID

# D o c u m e n t . m T e s t C o p i e s 
    @tracef("DOC")
    def mTestCopies(self):
        ''' Doc.mTestCopies
            Audit all the known copies of this doc.
            If any of the servers who are supposed to have
            a copy reports correctly, then return success.
            If one of the servers still has a copy, 
            then the document is lost forever.  Oops.  
        '''
        bAggregate = False
        for sServerID in self.lServerIDs:
            bResult = self.mDocTestOneServer(sServerID)
            bAggregate = bAggregate or bResult
            if bAggregate:
                break
        return bAggregate        

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
        (bOkay,bInjured,bForensics,bLost) = cColl.mEvaluateOneDoc(self.ID)
        # I think I meant to do something more here, but I forgot what.          
        return (bOkay,bInjured,bForensics,bLost)
        

# D o c u m e n t . m D o c T e s t O n e S e r v e r 
    @tracef("DOC")
    def mDocTestOneServer(self,mysServerID):
        cServer = G.dID2Server[mysServerID]
        bResult = cServer.mTestDocument(self.ID)
        return bResult



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
        self.nDocsInjured = 0
        self.nDocsForensics = 0
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

# C o l l e c t i o n . m T e s t C o l l e c t i o n
    @tracef("COLL")
    def mTestCollection(self):
        ''' Return a list, maybe empty, of documents declared missing
            from this collection.  
        '''
        lDeadDocIDs = list()
        for sDocID in self.lDocIDs:
            cDoc = G.dID2Document[sDocID]
            bResult = cDoc.mTestCopies()
            TRC.tracef(3,"COLL","proc TestColl1 coll|%s| tests doc|%s| result|%s|" % (self.ID,sDocID,bResult))
            if not bResult:
                lDeadDocIDs.append(sDocID)
                TRC.tracef(3,"COLL","proc TestColl2 dead doc|%s| in coll|%s| " % (sDocID,self.ID))
        return lDeadDocIDs

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
            self.nDocsInjured += 1 if bInjured else 0
            self.nDocsForensics += 1 if bForensics else 0
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
            if nCopiesLeft == nNumberOfServers:
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
    @tracef("SHOW")
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
            self.cAudit = CAudit2(self.ID,mysCollID,G.nAuditCycleInterval)

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


#--------- future

# 
    @tracef("CLI")
    def mDocFailedOnServer(self,mysDocID,mysServerID):
        ''' Client.mDocumentFailed
            Server calls this to inform owner that a document died
            probably due to a major storage failure.
            Find a valid copy of the document and re-add it to server.
        '''
        ### T E M P 
        return mysServerID +"-"+ mysDocID
        ### E N D   T E M P 

        lg.logDebug("CLIENT","Document failed on server doc|%s| svr|%s|" % (mysDocID,mysServerID))
        bResult = self.mDocFindValidCopy(mysDocID)
        if bResult:
            self.mDocReplaceOnServer(mysDocID,mysServerID)
        else:
            self.mDocPermanentFailure(mysDocID)
        return mysServerID +"-"+ mysDocID

# 
    @tracef("CLI")
    def mDocReplaceOnServer(self,mysDocID,mysServerID):
        ''' Client.mReplaceDocument
            Send the document back to the server that lost it.
            Push or pull does not matter at this level.  Use the
            standard method of distribution.  
        '''
        cServer = G.dID2Server[mysServerID]
        cServer.mAddDocument(mysDocID,self.ID)
        lg.logDebug("CLIENT","Document replaced on server doc|%s| svr|%s|" % (mysDocID,mysServerID))
        return mysServerID +"+"+ mysDocID

    def mCollectionTestAll(self,mysCollID):
        pass

# 
    @tracef("SHOW")
    @tracef("CLI")
    def mDocPermanentFailure(self,mysDocID):
        ''' We cannot find a good copy of the document anywhere, 
            ergo it is lost permanently.  Log this serious event.  
        '''
        lg.logError("CLIENT","Document lost, permanent failure |%s| at time |%s|" % (mysDocID,G.env.now))
        pass

# END
