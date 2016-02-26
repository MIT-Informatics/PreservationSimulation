#!/usr/bin/python
# collection.py
# 
import  simpy
from    NewTraceFac     import  NTRC,ntrace,ntracef
import  itertools
from    globaldata      import  G
from    server          import  CServer
from    audit2          import  fAudit_Select
from    repair          import  CRepair
import  util
import  math
import  logoutput       as      lg
import  collections     as      cc
from    catchex         import  catchex
from    document        import  CDocument


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

# C o l l e c t i o n . m T e s t C o l l e c t i o n
    @ntracef("COLL")
    def mTestCollection(self):
        ''' Return a list, maybe empty, of documents declared missing
            from this collection.  
        '''
        bOldLogState = G.bDoNotLogInfo
        if G.bShortLog: G.bDoNotLogInfo = True
        lDeadDocIDs = list()
        for sDocID in self.lDocIDs:
            cDoc = G.dID2Document[sDocID]
            (bOkay,bInjured,bForensics,bLost) = cDoc.mTestCopies()
            NTRC.ntracef(3,"COLL","proc TestColl1 coll|%s| tests doc|%s| "
                "okay|%s| injured|%s| forensics|%s| lost|%s|" % 
                (self.ID,sDocID,bOkay,bInjured,bForensics,bLost))
            # Merge new info with old info from audits.
            (bOkay,bInjured,bForensics,bLost) = \
                cDoc.mMergeEvaluation(bOkay,bInjured,bForensics,bLost)
            # Update stats of document statuses.  
            self.nDocsOkay += 1 if bOkay else 0
            self.nDocsMajorityRepair += 1 if bInjured else 0
            self.nDocsMinorityRepair += 1 if bForensics else 0
            self.nDocsLost += 1 if bLost else 0
            # Update lost list.
            if bLost:
                lDeadDocIDs.append(sDocID)
                NTRC.ntracef(3,"COLL","proc TestColl2 dead doc|%s| in coll|%s| "
                    % (sDocID,self.ID))
            NTRC.ntracef(3,"COLL","proc TestColl3 coll|%s| doc|%s| okay|%s| "
                "majority|%s| minority|%s| lost|%s|" % 
                (self.ID,sDocID,bOkay,bInjured,bForensics,bLost))
            if not bOkay:
                (nMajority,nMinority) = cDoc.mGetRepairCounts()
                lg.logInfo("DOCUMENT","doc injured cli|%s| coll|%s| doc|%s| "
                    "majority|%s|%s| minority|%s|%s| lost|%s|" % 
                    (self.sClientID, self.ID,sDocID, bInjured, nMajority, 
                    bForensics, nMinority, bLost))
        G.bDoNotLogInfo = bOldLogState
        return lDeadDocIDs

# C C o l l e c t i o n . m H o w M a n y C o p i e s L e f t 
    @ntracef("COLL")
    def mHowManyCopiesLeft(self):
        ''' \
        Return list for all docs of how many copies exist across all servers.
        
        For a sDocID, return the length of the list of all servers that 
         claim to have a copy of the doc.
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
    @catchex
    @ntracef("COLL")
    def mMarkDocLost(self,mysDocID):
        self.nDocsRemaining -= 1
        if mysDocID in self.lDocIDsRemaining:
            self.lDocIDsRemaining.remove(mysDocID)

# C o l l e c t i o n . m E v a l u a t e O n e D o c 
    @ntracef("COLL")
    def mEvaluateOneDoc(self,mysDocID):
        ''' \
        Return status of document, four bools: 
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
#        dd["nServerReplacements"]   = self.nServerReplacements
        return dd

# Edit history:
# 20150812  RBL Moved from client.py to its own file.  
# 20160226  RBL Remove "doc injured" messages from shortlog.  
# 
# 

#END

