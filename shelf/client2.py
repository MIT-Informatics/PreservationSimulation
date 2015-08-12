#!/usr/bin/python
# client2.py
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
from    collection      import  CCollection


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
        self.lCollectionIDs = list()
        # Establish a non-shared resource for network bandwidth 
        # to be used during auditing.
        self.NetworkBandwidthResource = simpy.Resource(G.env,capacity=1)
        self.lServersToUse = list()
        self.nServerReplacements = 0
        # Create the collections for this client.
        for lCollectionParams in mylCollections:
            (sCollName,nCollValue,nCollSize) = lCollectionParams
            cColl = CCollection(sCollName,nCollValue,nCollSize, self.ID)
            sCollID = cColl.ID
            self.lCollectionIDs.append(sCollID)
            # Put the collection in all the right places.  
            self.mPlaceCollection(sCollID)

        #self.cRepair = CRepair(self.ID)

# C l i e n t . m P l a c e C o l l e c t i o n
    @catchex
    @ntracef("CLI")
    def mPlaceCollection(self,mysCollID):
        '''\
        Get list of servers available at the right quality level.
        
        Select the policy-specified number of them.
        Send the collection to each server in turn.  
        '''
        cColl = G.dID2Collection[mysCollID]
        nCollValue = cColl.nValue
        lServersForCollection = self.mSelectServersForCollection(nCollValue)
        # The distribution params have already limited the 
        # set of servers in the select-for-collection routine.
        self.lServersToUse = lServersForCollection
        ''' If there aren't servers enough at this level, 
            the Select method will raise an exception.
        '''
        NTRC.ntracef(3,"CLI","proc mPlaceCollection1 client|%s| place coll|%s| to|%d|servers" % (self.ID,mysCollID,len(self.lServersToUse)))

        # Distribute collection to a set of servers.
        for sServerID in self.lServersToUse:
            NTRC.ntracef(3,"CLI","proc mPlaceCollection2 client|%s| send coll|%s| to server|%s|" % (self.ID,mysCollID,sServerID))
            NTRC.ntracef(3,"SHOW","proc mPlaceCollection2 client|%s| send coll|%s| to server|%s|" % (self.ID,mysCollID,sServerID))
            
            # Send copy of collection to server.
            self.mPlaceCollectionOnServer(mysCollID, sServerID)

        # Initialize the auditing process for this collection.
        if G.nAuditCycleInterval > 0:
            self.cAudit = fAudit_Select(G.sAuditStrategy,self.ID,mysCollID,G.nAuditCycleInterval)

        return self.lServersToUse

# C l i e n t . m S e l e c t S e r v e r s F o r C o l l e c t i o n
    @catchex
    @ntracef("CLI")
    def mSelectServersForCollection(self,mynCollValue):
        '''\
        Get list of servers at this quality level.
        
        Return a random permutation of the list of servers.
        Oops, not any more.  Just a list of usable ones.  
        '''
        # Get list of all servers at this quality level.
        # Value level translates to quality required and nr copies.
        (nQuality,nCopies) = G.dDistnParams[mynCollValue][0]
        lServersAtLevel = [ll[1] for ll in G.dQual2Servers[nQuality]]
        '''\
        For most questions, all servers are functionally 
         identical.  Just take the right number of them.  We used
         to take a random permutation of the list of servers and 
         choose from those, hence the name "Perm", but don't waste
         the effort any more.  
        NEW: return only servers that are not already in use and not broken.
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
    @catchex
    @ntracef("CLI")
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
    @catchex
    @ntracef("CLI")
    def mTestClient(self):
        '''\
        Return list, maybe empty, of all documents missing from 
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
    @catchex
    @ntracef("CLI")
    def mListCollectionIDs(self):
        return self.lCollectionIDs

# C l i e n t . m D e s t r o y C o p y 
    @catchex
    @ntracef("CLI")
    def mDestroyCopy(self,mysDocID,mysServerID,mysCopyID):
        '''\
        The Server says that it no longer has a copy of the doc.
        
        Tell the Document that the copy was lost.
        The Collection keeps only Server-level, not Doc-level stats.  
        '''
        cDoc = G.dID2Document[mysDocID]
        cDoc.mDestroyCopy(mysServerID,mysCopyID)

# C l i e n t . m S e r v e r I s D e a d 
    @catchex
    @ntracef("CLI")
    def mServerIsDead(self, mysServerID, mysCollID):
        '''\
        Auditor calls us: a server is dead, no longer 
         accepting documents.  Remove server from active list, 
         find a new server, populate it.  
        '''
        NTRC.ntracef(3,"CLI","proc deadserver1 client|%s| place coll|%s| to|%d|servers" % (self.ID,mysCollID,len(self.lServersToUse)))
        lg.logInfo("CLIENT", "server died cli|%s| removed svr|%s| coll|%s| " % (self.ID, mysServerID, mysCollID))

        cColl = G.dID2Collection[mysCollID]
        cColl.lServerIDs.remove(mysServerID)
        nCollValue = cColl.nValue
        lServersForCollection = self.mSelectServersForCollection(nCollValue)
        # The distribution params have already limited the 
        # set of servers in the select-for-collection routine.
        sServerToUse = lServersForCollection.pop(0)
        lg.logInfo("CLIENT", "client|%s| assign new server|%s| to replace|%s|" % (self.ID, sServerToUse, mysServerID))
        self.mPlaceCollectionOnServer(mysCollID, sServerToUse)
        self.nServerReplacements += 1


# Edit History (recent, anyway): 
# 20141121  RBL Original client201.py version.  
# 20141216  RBL client202 version.  
# 20150112  RBL client203 version.  
# 20150711  RBL straight client.py version for git's use.  
# 20150716  RBL Add code to deal with 100% glitches = server failures.  
#                Auditor calls in to declare server dead.  
#                Refactor placing collection onto server.  
#                Remove dead server from list, get a new one, repopulate.  
# 20150812  RBL Move CDocument and CCollection classes to their own files.  
# 

# END

