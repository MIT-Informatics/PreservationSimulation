#!/usr/bin/python
# client.py
# Recovered, we hope, after commit/delete screw-up.  

import simpy
from NewTraceFac import TRC,trace,tracef
import itertools
from server import *
from globaldata import *
from repair import *
from util import *
import math
from logoutput import logInfo,logDebug,logError


#===========================================================
# D O C U M E N T 
#----------------

class CDocument(object):
    getID = itertools.count(1).next

    @tracef("DOC")
    def __init__(self,size,mysClientID):
        self.ID = "D" + str(self.getID())
        G.dID2Document[self.ID] = self
        G.nDocLastID = self.ID
        self.nSize = size
        self.sClientID = mysClientID
        TRC.tracef(3,"DOC","proc init client|%s| created doc|%s| size|%d|" % (self.sClientID,self.ID,self.nSize))
        self.lServerIDs = list()
        self.lCopyIDs = list()

    @tracef("DOC")
    def mCopyPlacedOnServer(self,mysCopyID,mysServerID):
        self.lCopyIDs.append(mysCopyID)
        self.lServerIDs.append(mysServerID)
        return self.ID+"+"+mysCopyID+"+"+mysServerID

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
        self.lServers = list()

        # Create all books in the collection.
        self.mMakeBooks(mynSize)

# C o l l e c t i o n . m M a k e B o o k s 
    @tracef("COLL")
    def mMakeBooks(self,mynBooks):
        # A collection has lots of books
        for icoll in xrange(mynBooks):
            ndocsize = fnnCalcDocSize(self.nValue)
            cDoc = CDocument(ndocsize,self.sClientID)
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

        # Create the collections for this client.
        self.lCollectionIDs = list()
        for lCollectionParams in mylCollections:
            (sCollName,nCollValue,nCollSize) = lCollectionParams
            cColl = CCollection(sCollName,nCollValue,nCollSize, self.ID)
            sCollID = cColl.ID
            self.lCollectionIDs.append(sCollID)

            # Put the collection in all the right places.  
            self.mPlaceCollection(sCollID)

        self.cRepair = CRepair(self.ID)

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
            # Send copy of collection to server.
            TRC.tracef(3,"CLI","proc mPlaceCollection2 client|%s| send coll|%s| to server|%s|" % (self.ID,mysCollID,sServerID))
            TRC.tracef(3,"SHOW","proc mPlaceCollection2 client|%s| send coll|%s| to server|%s|" % (self.ID,mysCollID,sServerID))
            (G.dID2Server[sServerID]).mAddCollection(mysCollID,self.ID)
            # Record that this server has a copy of this collection.
            cColl.lServers.append(sServerID)
            logInfo("CLIENT","client|%s| placed collection|%s| to server|%s|" % (self.ID,mysCollID,sServerID))
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
        BZZZT!
        Cannot use itertools to generate a permutation for servers
        if there are too many servers.  It generates the actual list,
        which for 15 servers is 1.3 trillion long.  Oops.  
        Find another reasonable way to do this in the long term, 
        e.g., select randomly without replacement until nCopies is 
        fulfilled.    
        In the short term, don't care because for Question 0
        all servers are identical in configuration.  
        
        ### Old code now inoperative.
        # Pick a random number of a permutation.
        nNumPerms = math.factorial(len(lServersAtLevel))
        nPermChoice = int(makeunif(0,nNumPerms))
        # Make a list of all the permutations.  
        lPerms = list()
        for lPerm in itertools.permutations(lServersAtLevel):
            lPerms.append(lPerm)
        # Pick one of the permutations. 
        lPermChosenFull = lPerms[nPermChoice]
        # Now use the distribution params to select maybe
        # a subset of the available servers.
        # (I hate the syntax of slicing lists, the open interval 
        # on the right.)
        lPermChosen = lPermChosenFull[0:nCopies]
        TRC.tracef(5,"CLI","proc mSelectServers1 fulllist|%s| permlist|%s| choose|%d| chosen|%s|" % (lServersAtLevel,lPermChosenFull,nCopies,lPermChosen))
        TRC.tracef(3,"CLI","proc mSelectServers2 perm|%d| of|%d| list|%s|" % (nPermChoice,nNumPerms,lPermChosen))
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

#--------- future

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

        logDebug("CLIENT","Document failed on server doc|%s| svr|%s|" % (mysDocID,mysServerID))
        bResult = self.mDocFindValidCopy(mysDocID)
        if bResult:
            self.mDocReplaceOnServer(mysDocID,mysServerID)
        else:
            self.mDocPermanentFailure(mysDocID)
        return mysServerID +"-"+ mysDocID

    @tracef("CLI")
    def mDocReplaceOnServer(self,mysDocID,mysServerID):
        ''' Client.mReplaceDocument
            Send the document back to the server that lost it.
            Push or pull does not matter at this level.  Use the
            standard method of distribution.  
        '''
        cServer = G.dID2Server[mysServerID]
        cServer.mAddDocument(mysDocID,self.ID)
        logDebug("CLIENT","Document replaced on server doc|%s| svr|%s|" % (mysDocID,mysServerID))
        return mysServerID +"+"+ mysDocID

    def mCollectionTestAll(self,mysCollID):
        pass

    @tracef("SHOW")
    @tracef("CLI")
    def mDocPermanentFailure(self,mysDocID):
        ''' We cannot find a good copy of the document anywhere, 
            ergo it is lost permanently.  Log this serious event.  
        '''
        logError("CLIENT","Document lost, permanent failure |%s| at time |%s|" % (mysDocID,G.env.now))
        pass

# END
