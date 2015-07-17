#!/usr/bin/python
# client2.py
# 
import simpy
from NewTraceFac import NTRC,ntrace,ntracef
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
    @ntracef("DOC")
    def __init__(self,size,mysClientID,mysCollectionID):
        self.ID = "D" + str(self.getID())
# BEWARE: if we have more than 10,000 docs, this fixed-length 
#  representation will have to change.  Bad idea.
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
    @ntracef("DOC")
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

# D o c u m e n t . m D e s t r o y C o p y 
    @ntracef("DOC")
    def mDestroyCopy(self,mysServerID):
        '''\
        Remove Server's Copy of this Document.  
        Actually, just remove Server from the list of Servers with 
        copies of this Document.  
        '''
        self.lServerIDs.remove(mysServerID)

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


#===========================================================
# C O L L E C T I O N 
#--------------------

class CCollection(object):
    getID = itertools.count(1).next

    @ntracef("COLL")
    def __init__(self,mysName,mynValue,mynSize,mysClientID):
        self.ID = "C" + str(self.getID())
        G.dID2Collection[self.ID] = self
        G.nCollLastID = self.ID

        self.sName = mysName
        self.nValue = mynValue
        self.sClientID = mysClientID
        self.lDocIDs = list()
        self.lDocIDsRemaining = list()
        self.lServerIDs = list()

        # Summary counters for document status at end of run.
        self.nDocsRemaining = 0
        self.nDocsOkay = 0
        self.nDocsMajorityRepair = 0
        self.nDocsMinorityRepair = 0
        self.nDocsLost = 0

        # Action: create all books in the collection.
        self.mMakeBooks(mynSize)
        
# C o l l e c t i o n . m M a k e B o o k s 
    @ntracef("COLL")
    def mMakeBooks(self,mynBooks):
        # A collection has lots of books
        for icoll in xrange(mynBooks):
            ndocsize = util.fnnCalcDocSize(self.nValue)
            cDoc = CDocument(ndocsize,self.sClientID,self.ID)
            self.lDocIDs.append(cDoc.ID)
            self.lDocIDsRemaining.append(cDoc.ID)
            self.nDocsRemaining += 1
        return self.ID

# C o l l e c t i o n . m L i s t D o c u m e n t s 
    @ntracef("COLL")
    def mListDocuments(self):
        NTRC.ntracef(5,"COLL","proc mListDocuments self|%s| returning |%s|" % (self,self.lDocIDs))
        return (self.lDocIDs)

# C o l l e c t i o n . m L i s t D o c u m e n t s R e m a i n i n g 
    @ntracef("COLL")
    def mListDocumentsRemaining(self):
        NTRC.ntracef(5,"COLL","proc mListDocuments self|%s| returning |%s|" % (self,self.lDocIDs))
        return (self.lDocIDsRemaining)

# NEW NEW NEW replacement
# C o l l e c t i o n . m T e s t C o l l e c t i o n
    @ntracef("COLL")
    def mTestCollection(self):
        ''' Return a list, maybe empty, of documents declared missing
            from this collection.  
        '''
        lDeadDocIDs = list()
        for sDocID in self.lDocIDs:
            cDoc = G.dID2Document[sDocID]
            (bOkay,bInjured,bForensics,bLost) = cDoc.mTestCopies()
            NTRC.ntracef(3,"COLL","proc TestColl1 coll|%s| tests doc|%s| okay|%s| injured|%s| forensics|%s| lost|%s|" % (self.ID,sDocID,bOkay,bInjured,bForensics,bLost))
            # Merge new info with old info from audits.
            (bOkay,bInjured,bForensics,bLost) = cDoc.mMergeEvaluation(bOkay,bInjured,bForensics,bLost)
            # Update stats of document statuses.  
            self.nDocsOkay += 1 if bOkay else 0
            self.nDocsMajorityRepair += 1 if bInjured else 0
            self.nDocsMinorityRepair += 1 if bForensics else 0
            self.nDocsLost += 1 if bLost else 0
            # Update lost list.
            if bLost:
                lDeadDocIDs.append(sDocID)
                NTRC.ntracef(3,"COLL","proc TestColl2 dead doc|%s| in coll|%s| " % (sDocID,self.ID))
            NTRC.ntracef(3,"COLL","proc TestColl3 coll|%s| doc|%s| okay|%s| majority|%s| minority|%s| lost|%s|" % (self.ID,sDocID,bOkay,bInjured,bForensics,bLost))
            if not bOkay:
                (nMajority,nMinority) = cDoc.mGetRepairCounts()
                lg.logInfo("DOCUMENT","doc injured cli|%s| coll|%s| doc|%s| majority|%s|%s| minority|%s|%s| lost|%s|" % (self.sClientID,self.ID,sDocID,bInjured,nMajority,bForensics,nMinority,bLost))
        return lDeadDocIDs


# C C o l l e c t i o n . m H o w M a n y C o p i e s L e f t 
    @ntracef("COLL")
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
    @ntracef("COLL")
    def mIsDocInServer(self,mysDocID,mysServerID):
        ''' Return t/f is this doc present on that server. '''
        cServer = G.dID2Server[mysServerID]
        bResult = cServer.mTestDocument(mysDocID)
        return bResult

# C o l l e c t i o n . m H o w M a n y C o p i e s L e f t O f T h i s O n e D o c 
    @ntracef("COLL",level=5)
    def mHowManyCopiesLeftOfThisOneDoc(self,mysDocID):
        ''' Return (scalar) the number of copies that exist of this doc. '''
        nLeftNow = len(                                             \
                    filter(                                         \
                        (lambda sServerID:                          \
                            self.mIsDocInServer(mysDocID,sServerID)), \
                        self.lServerIDs))
        return nLeftNow

# C o l l e c t i o n . m M a r k D o c L o s t 
    @ntracef("COLL")
    def mMarkDocLost(self,mysDocID):
        self.nDocsRemaining -= 1
        if mysDocID in self.lDocIDsRemaining:
            self.lDocIDsRemaining.remove(mysDocID)

# C o l l e c t i o n . m E v a l u a t e O n e D o c 
    @ntracef("COLL")
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
    @ntracef("COLL")
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
        dd["nDocsRemaining"]    = self.nDocsRemaining
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

    @ntracef("CLI")
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
    @ntracef("CLI")
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
            the Select method will raise an exception.
        '''
        NTRC.ntracef(3,"CLI","proc mPlaceCollection1 client|%s| place coll|%s| to|%d|servers" % (self.ID,mysCollID,len(lServersToUse)))

        # Distribute collection to a set of servers.
        for sServerID in lServersToUse:
            NTRC.ntracef(3,"CLI","proc mPlaceCollection2 client|%s| send coll|%s| to server|%s|" % (self.ID,mysCollID,sServerID))
            NTRC.ntracef(3,"SHOW","proc mPlaceCollection2 client|%s| send coll|%s| to server|%s|" % (self.ID,mysCollID,sServerID))
            
            # Send copy of collection to server.
            self.mPlaceCollectionOnServer(mysCollID, sServerID)
            """
            cServer = G.dID2Server[sServerID]
            cServer.mAddCollection(mysCollID,self.ID)

            # Record that this server has a copy of this collection.
            cColl.lServerIDs.append(sServerID)
            lg.logInfo("CLIENT","client|%s| placed collection|%s| to server|%s|" % (self.ID,mysCollID,sServerID))
            """

        # Initialize the auditing process for this collection.
        if G.nAuditCycleInterval > 0:
            self.cAudit = fAudit_Select(G.sAuditStrategy,self.ID,mysCollID,G.nAuditCycleInterval)

        return lServersToUse

# C l i e n t . m S e l e c t S e r v e r s F o r C o l l e c t i o n
    @ntracef("CLI")
    def mSelectServersForCollection(self,mynCollValue):
        ''' Get list of servers at this quality level.
            Return a random permutation of the list of servers.
        '''
        # Get list of all servers at this quality level.
        # Value level translates to quality required and nr copies.
        (nQuality,nCopies) = G.dDistnParams[mynCollValue][0]
        lServersAtLevel = [ll[1] for ll in G.dQual2Servers[nQuality]]
        '''
        # For most questions, all servers are functionally 
        #  identical.  Just take the right number of them.  We used
        #  to take a random permutation of the list of servers and 
        #  choose from those, hence the name "Perm", but don't waste
        #  the effort any more.  
        # NEW: return only servers that are not already in use and not broken.
        '''
        lPermChosenAlive = [svr for svr in lServersAtLevel if not G.dID2Server[svr].bDead]
        lPermChosenFull = [svr for svr in lPermChosenAlive if not G.dID2Server[svr].bInUse]
        NTRC.ntracef(3,"CLI","proc servers chosen level|%s| alive|%s| full|%s|" % (lServersAtLevel, lPermChosenAlive, lPermChosenFull))
        # Just make sure there are enough of them to meet the client's needs.
        if len(lPermChosenAlive) < nCopies:
            raise IndexError('Not enough servers left alive to satisfy client requirements')
        lPermChosen = lPermChosenFull[0:nCopies]
        return lPermChosen

# C l i e n t . m P l a c e C o l l e c t i o n O n S e r v e r 
    def mPlaceCollectionOnServer(self, mysCollID, mysServerID):
        # Send copy of collection to server.
        cServer = G.dID2Server[mysServerID]
        cServer.mAddCollection(mysCollID,self.ID)
        # Record that this server has a copy of this collection.
        cColl = G.dID2Collection[mysCollID]
        cColl.lServerIDs.append(mysServerID)
        lg.logInfo("CLIENT","client|%s| placed collection|%s| to server|%s|" % (self.ID,mysCollID,mysServerID))
        return

# C l i e n t . m T e s t C l i e n t 
    @ntracef("CLI")
    def mTestClient(self):
        ''' Return list, maybe empty, of all documents missing from 
            this client.  All collections appended together.
        '''
        lDeadDocIDs = list()
        for sCollID in self.lCollectionIDs:
            cColl = G.dID2Collection[sCollID]
            lResult = cColl.mTestCollection()
            NTRC.ntracef(3,"CLI","proc TestClient1 client|%s| tests coll|%s| result|%s|" % (self.ID,sCollID,lResult))
            if len(lResult) > 0:
                lDeadDocIDs.extend(lResult)
                NTRC.ntracef(3,"CLI","proc TestClient2 client |%s| coll|%s| lost docs|%s|" % (self.ID,sCollID,lResult))
        return lDeadDocIDs

# C l i e n t . m L i s t C o l l e c t i o n I D s 
    @ntracef("CLI")
    def mListCollectionIDs(self):
        return self.lCollectionIDs

# C l i e n t . m D e s t r o y C o p y 
    @ntracef("CLI")
    def mDestroyCopy(self,mysDocID,mysServerID):
        '''
        The Server says that it no longer has a copy of the doc.
        Tell the Document that the copy was lost.
        The Collection keeps only Server-level, not Doc-level stats.  
        '''
        cDoc = G.dID2Document[mysDocID]
        cDoc.mDestroyCopy(mysServerID)

# C l i e n t . m S e r v e r I s D e a d 
    @ntracef("CLI")
    def mServerIsDead(self, mysServerID, mysCollID):
        ''' Auditor calls us: a server is dead, no longer 
            accepting documents.  Remove server from active list, 
            find a new server, populate it.  
        '''
        """
        BZZZT NO, NOT THIS WAY!  deliberate syntax error until coded
        cColl = G.dID2Collection[mysCollID]
        nCollValue = cColl.nValue
        lServersForCollection = self.mSelectServersForCollection(nCollValue)
        # The distribution params have already limited the 
        # set of servers in the select-for-collection routine.
        lServersToUse = lServersForCollection
        ''' If there aren't servers enough at this level, 
            the Select method will raise an exception.
        '''
        """
        NTRC.ntrace(0,"CLI","DO NOTHING YET FOR Client.mServerIsDead")
        
        NTRC.ntracef(3,"CLI","proc mPlaceCollection1 client|%s| place coll|%s| to|%d|servers" % (self.ID,mysCollID,len(lServersToUse)))

        pass
        


# Edit History (recent, anyway): 
# 20141121  RBL Original client201.py version.  
# 20141216  RBL client202 version.  
# 20150112  RBL client203 version.  
# 20150711  RBL straight client.py version for git's use.  
# 20150716  RBL Add code to deal with 100% glitches = server failures.  
#                Auditor calls in to declare server dead.  
#                Refactor placing collection onto server.  
#                Remove dead server from list, get a new one, repopulate.  
# 

# END
