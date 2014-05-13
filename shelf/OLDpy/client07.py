#!/usr/bin/python
# client.py

import simpy
from NewTraceFac import TRC,trace,tracef
import itertools
from server import *
from globaldata import *
from repair import *
import math
from logoutput import logInfo,logDebug,logError


#===========================================================
# D O C U M E N T 
#----------------

class CDocument(object):
    getID = itertools.count(0).next

    @tracef("DOC")
    def __init__(self,size,mysClientID):
        self.ID = "D" + str(self.getID())
        G.dID2Document[self.ID] = self
        G.nDocLastID = self.ID
        self.nSize = size
        self.sClientID = mysClientID
        TRC.tracef(3,"DOC","proc init client|%s| created doc|%s| size|%d|" % (self.sClientID,self.ID,self.nSize))
        self.lServers = list()
        self.lCopies = list()

    @tracef("DOC")
    def mCopyPlacedOnServer(self,mysCopyID,mysServerID):
        self.lCopies.append(mysCopyID)
        self.lServers.append(mysServerID)
        return self.ID+"+"+mysCopyID+"+"+mysServerID


#===========================================================
# C O L L E C T I O N 
#--------------------

class CCollection(object):
    getID = itertools.count().next

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
    def mMakeBooks(self,nbooks):
        # A collection has lots of books
        nrandbooks = int(makennnorm(int(nbooks)))
        for icoll in xrange(nrandbooks):
            # T E M P
            ndocsize = makeunif(1,1000)
            # E N D   T E M P 
            cDoc = CDocument(ndocsize,self.sClientID)
            self.lDocIDs.append(cDoc.ID)
        return self.ID

# C o l l e c t i o n . m L i s t D o c u m e n t s 
    @tracef("COLL")
    def mListDocuments(self):
        TRC.tracef(5,"COLL","proc mListDocuments self|%s| returning |%s|" % (self,self.lDocIDs))
        return (self.lDocIDs)
        # tri it as an iterable
#        for sDocID in self.lDocIDs:
#            yield sDocID

#===========================================================
# C L I E N T 
#------------

class CClient(object):
    lCollectionIDs = list()
    sCollIDLastAudited = ""
    getID = itertools.count().next

    @tracef("CLI")
    def __init__(self,mysName,mylCollections):
        self.ID = "T" + str(self.getID())
        G.dID2Client[self.ID] = self
        G.nClientLastID = self.ID
        self.sName = mysName

        # Create the collections for this client.
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
        ''' Client.mSelectServersForCollection()
            Get list of servers at this quality level.
            Return a random permutation of the list of servers.
        '''
        # Get list of all servers at this quality level.
        lServersAtLevel = G.dQual2Servers[mynCollValue]
        # Pick a random number of a permutation.
        nNumPerms = math.factorial(len(lServersAtLevel))
        nPermChoice = int(makeunif(0,nNumPerms))
        # Make a list of all the permutations.  
        lPerms = list()
        for lPerm in itertools.permutations(lServersAtLevel):
            lPerms.append(lPerm)
        # Pick one of the permutations. 
        lPermChosenFull = lPerms[nPermChoice]
        # Now use he distribution params to select maybe
        # a subset of the available servers.
        (nQuality,nCopies) = P.dDistnParams[mynCollValue][0]
        lPermChosen = lPermChosenFull[0:(nCopies-1)]
        TRC.tracef(3,"CLI","proc mSelectServers perm|%d| of|%d| list|%s|" % (nPermChoice,nNumPerms,lPermChosen))
        return lPermChosen


    @tracef("CLI")
    def mDocFailedOnServer(self,mysDocID,mysServerID):
        ''' Client.mDocumentFailed
            Server calls this to inform owner that a document died
            probably due to a major storage failure.
            Find a valid copy of the document and re-add it to server.
        '''
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

    @tracef("CLI")
    def mDocFindValidCopy(self,mysDocID):
        ''' Client.mFindValidCopyOfDoc
            Audit all the known copies of the doc.
            If a majority of the servers who are supposed to have
            copies report correctly, then return success.
            If not enough of the servers agree about the doc 
            contents, then the document is lost forever.  Oops.  
        '''
        # T E M P 
        return True
        # E N D   T E M P 

    @tracef("SHOW")
    @tracef("CLI")
    def mDocPermanentFailure(self,mysDocID):
        ''' We cannot find a good copy of the document anywhere, 
            ergo it is lost permanently.  Log this serious event.  
        '''
        logError("CLIENT","Document lost, permanent failure |%s| at time |%s|" % (mysDocID,G.env.now))
        pass

# END
