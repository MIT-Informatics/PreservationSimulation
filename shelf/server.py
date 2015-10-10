#!/usr/bin/python
# server.py

import  simpy
from    NewTraceFac     import  TRC, trace, tracef, NTRC, ntrace, ntracef
import  itertools
from    globaldata      import  G
from    math            import  exp, log
import  util
import  logoutput       as lg
from    catchex         import  catchex
from    shelf           import  CShelf


#===========================================================
# C l a s s  S E R V E R 
#-----------------------

class CServer(object):
    # Function to get a unique, autoincrementing ID for instances
    # of this class.  
    getID = itertools.count(1).next

    @tracef("SHOW")
    @tracef("SERV")
    def __init__(self,mysName,mynQual,mynShelfSize):
        self.sName = mysName
        self.nQual = mynQual
        self.nShelfSize = mynShelfSize * 1000000    # Scale up from TB to MB.
        self.ID = "V" + str(self.getID())
        self.lShelfIDs = list()
        self.lDocIDs = list()           # Docs that still live in this server.
        self.dDocIDs = dict()           # Dictionary version of alive doc IDs, for fast checking.
        self.lDocIDsComplete = list()   # All docs that were ever in this server.
        G.dID2Server[self.ID] = self
        G.nServerLastID = self.ID
        self.sClientID = None
        self.sCollectionID = None
        self.bInUse = False             # This server not yet used by client.
        self.bDead = False              # Server has not yet suffered a 100% glitch.

# S e r v e r . m A d d C o l l e c t i o n
    @catchex
    @tracef("SERV")
    def mAddCollection(self,mysCollID,mysClientID):
        self.sClientId = mysClientID
        self.sCollectionID = mysCollID
        lTempDocIDs = list()
        cCollection = G.dID2Collection[mysCollID]
        lTempDocIDs = cCollection.mListDocuments()
        for sDocID in lTempDocIDs:
            self.mAddDocument(sDocID,mysClientID)
        self.bInUse = True
        return mysCollID

# S e r v e r . m A d d D o c u m e n t 
    @catchex
    @tracef("SERV")
    def mAddDocument(self,mysDocID,mysClientID):
        ''' Find a shelf with room for the doc, or create one.
            Put the doc on the shelf, decrement the remaining space.
        '''
        # If the server is already dead, do not accept any documents.
        if not self.bDead:
            cDoc = G.dID2Document[mysDocID]
            nSize = cDoc.nSize
            # Find a shelf with sufficient empty space and place the doc there. 
            cShelf = None
            for sShelfID in self.lShelfIDs:
                cShelf = G.dID2Shelf[sShelfID]
                bResult = cShelf.mAcceptDocument(mysDocID,nSize,mysClientID)
                if bResult:
                    break       # True = doc has been stored
                else:
                    continue    # False = no, try another shelf, if any
            else:               # If no more shelves, create another and use that one.
                sNewShelfID = self.mCreateShelf()
                self.lShelfIDs.append(sNewShelfID)
                cShelf = G.dID2Shelf[sNewShelfID]
                sShelfID = cShelf.ID    # TODO: #Why not just use sNewShelfID?
                result = cShelf.mAcceptDocument(mysDocID,nSize,mysClientID)
                
            # Record that the doc has been stored on this
            self.lDocIDsComplete.append(mysDocID) server.
            self.bInUse = True
            self.lDocIDs.append(mysDocID)
            self.dDocIDs[mysDocID] = mysClientID
            TRC.tracef(3,"SERV","proc mAddDocument serv|%s| id|%s| docid|%s| size|%s| assigned to shelfid|%s| remaining|%s|" % (self.sName,self.ID,mysDocID,cDoc.nSize,sShelfID,cShelf.nFreeSpace))
    
            return self.ID+"+"+sShelfID+"+"+mysDocID
        else:
            NTRC.ntracef(3,"SERV","proc mAddDocument1 dead server|%s| do not add doc|%s| for client|%s|" % (self.ID, mysDocID, mysClientID))
            return False

# S e r v e r . m C r e a t e S h e l f 
    @catchex
    @tracef("SERV")
    def mCreateShelf(self):
        ''' Add a new shelf of the standard size for this Server.
            Called as needed when a doc arrives too large for available space.  
        '''
        cShelf = CShelf(self.ID,self.nQual,self.nShelfSize)
        lg.logInfo("SERVER","server |%s| created storage shelf|%s| quality|%s| size|%s|MB" % (self.ID,cShelf.ID,cShelf.nQual,cShelf.nCapacity))
        return cShelf.ID

# S e r v e r . m D e s t r o y C o p y 
    @catchex
    @tracef("SERV")
    def mDestroyCopy(self,mysCopyID,mysDocID,mysShelfID):
        ''' Oops, a doc died, maybe just one or maybe the whole shelf.
        '''
        TRC.tracef(3,"SERV","proc mDestroyCopy remove copy|%s| doc|%s| from shelf|%s|" % (mysCopyID,mysDocID,mysShelfID))
        # Inform the client that the copy is gonzo.  
        cClient = G.dID2Client[self.dDocIDs[mysDocID]]
        cClient.mDestroyCopy(mysDocID,self.ID,mysCopyID)
        # Clear out local traces of the doc and copy.
        self.lDocIDs.remove(mysDocID)
        del self.dDocIDs[mysDocID]
        # The Shelf will nuke the copy, because it created it.  
        return self.ID + "-" + mysDocID

# S e r v e r . m T e s t D o c u m e n t 
    @catchex
    @tracef("SERV")
    def mTestDocument(self,mysDocID):
        ''' Do we still have a copy of this document?  Y/N
        '''
        #bResult = mysDocID in self.lDocIDs
        # Oops, item-in-list is incredibly slow, linear search.
        # It doesn't know that the list is sorted.
        # Try dictionary lookup, which is lots faster.  
        # (The dictionary is maintained by Add and Destroy.)
        bResult = mysDocID in self.dDocIDs
        # Might someday want to do something other than just return T/F.
        if bResult:
            return True
        else:
            return False

# S e r v e r . m S e r v e r D i e s 
    @catchex
    @tracef("SERV")
    def mServerDies(self):
        if not self.bDead:
            self.bDead = True
            # Destroy all doc ids so that audit will not find any.
#            TODO: #mark all documents as injured
            NTRC.ntracef(3,"SERV","proc mServerDies kill ndocs|%s|" % (len(self.lDocIDs)))
#            self.lDocIDs = list()
#            self.dDocIDs = dict()
            # Shall we destroy all the shelves, too, or will that cause a problem?
            for sShelfID in self.lShelfIDs:
                G.dID2Shelf[sShelfID].mDestroyShelf()
#                TODO: #mark all shelves as not bAlive
        pass


# Edit History:
# 20150222  RBL Make imports explicit.
#               Add CLifetime class for correlated failures.
# 20150316  RBL Add glitches for associated failure.
#               Lifetime calculations are a bloody mess.
# 20150329  RBL Flesh out glitch code and counters.  
#               Clarify sector lifetime calculations and 
#                glitch deactivations for time limit and 
#                for fading.
#               Add logging glitch events.  
#               Add stats reporting.  
# 20150715  RBL Add server mortality for 100% glitches: 
#               - InUse and Dead flags for servers; 
#               - Destroy all resident docs on 100% glitch; 
#               - Refuse to accept more docs on that server.
#               - DO NOT USE % CHARACTER IN ANY OUTPUT STRINGS!
#                  IF YOU FORGET TO SAY %%, YOU GET A VERY OBSCURE ERROR
#                  ABOUT FLOAT REQUIRED INSTEAD OF STRING.
#               - Changed all the 100% references to 100pct.
#               Add r/o properties for instance objects looked up from self.sxxxIDs.
# 20150812  RBL Remove CShelf, CCopy, and CLifetime classes into their own files.  
# 

# END
