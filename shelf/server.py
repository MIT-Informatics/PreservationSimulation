#!/usr/bin/python
# server.py

import  simpy
from    NewTraceFac     import  NTRC, ntrace, ntracef
import  itertools
from    globaldata      import  G
from    math            import  exp, log
import  util
import  logoutput       as lg
from    catchex         import  catchex
from    shelf           import  CShelf
import  resettabletimer as rt
from    datetime        import  datetime


#===========================================================
# C l a s s  S E R V E R 
#-----------------------

class CServer(object):
    # Function to get a unique, autoincrementing ID for instances
    # of this class.  
    getID = itertools.count(1).next

    @ntracef("SHOW")
    @ntracef("SERV")
    def __init__(self,mysName,mynQual,mynShelfSize):
        self.sName = mysName
        self.nQual = mynQual
        self.nShelfSizeTB = mynShelfSize
        self.nShelfSize = self.nShelfSizeTB * 1000000    # Scale up from TB to MB.
        self.ID = "V" + str(self.getID())
        self.lShelfIDs = list()
        self.lDocIDs = list()       # Docs that still live in this server.
        self.dDocIDs = dict()       # Dictionary version of alive doc IDs, 
                                    #  for faster checking.
        self.lDocIDsComplete = list()  # All docs that were ever in this server.
        self.mListServer()
        G.nServerLastID = self.ID
        self.sClientID = None
        self.sCollectionID = None
        self.bInUse = False         # This server not yet used by client.
        self.bDead = False          # Server has not yet suffered a 100% glitch.
        self.fOriginalLifespan = (util.makeserverlife(G.fServerDefaultHalflife)
                                    if G.fServerDefaultHalflife > 0 else 0)
                                    # Server gets a random lifetime if there
                                    #  is supposed to be one today.
        self.fCurrentLifespan = self.fOriginalLifespan
                                    # Keep current lifespan value here so that 
                                    #  shock can find it and reduce it.
        self.oTimer = rt.CResettableTimer(G.env, self.fCurrentLifespan, 
                        fnTimerCall, fnTimerInt, (self, self.ID))
                                    # Max server lifetime, initially.
                                    # Context contains server instance and id.
                                    # TODO: the param is a halflife; need to 
                                    #  generate a random expo life from that
                                    #  rather than using a fixed number.
        self.tLastServerCreated = (mysName, mynQual, mynShelfSize)


# S e r v e r . m L i s t S e r v e r 
    @catchex
    @ntracef("SERV")
    def mListServer(self):
 
       G.dID2Server[self.ID] = self


# S e r v e r . m D e l i s t S e r v e r 
    @catchex
    @ntracef("SERV")
    def mDelistServer(self):
        if self.ID in G.dID2Server: del G.dID2Server[self.ID]


# S e r v e r . m K i l l S e r v e r
    @catchex
    @ntracef("SERV")
    def mKillServer(self):
        self.bDead = True
        G.lDeadServers.append(self.ID)
        if self.lShelfIDs:
            G.lDeadActiveServers.append(self.ID)
        for sShelfID in self.lShelfIDs:
            cShelf = G.dID2Shelf[sShelfID]
            cShelf.mKillShelf()


# S e r v e r . m b I s S e r v e r D e a d 
    @catchex
    @ntracef("SERV")
    def mbIsServerDead(self):
        ''' DO NOT MEMOIZE THIS FUNCTION!
        '''
        return self.bDead


# S e r v e r . m b I s S e r v e r I n U s e 
    def mbIsServerInUse(self):
        ''' DO NOT MEMOIZE THIS FUNCTION!
        '''
        return self.bInUse


# C S e r v e r . f n C o r r F a i l H a p p e n s T o A l l 
    @classmethod
    @catchex
    @ntracef("SERV")
    def fnCorrFailHappensToAll(cls, mynGlitchSpan):
        """Class method: kill a specified number of servers.
        BZZZT: I don't think we will use this routine here.  
        It is better if the management logic for killing a 
        subset of servers is in the shock module.
        """
        lVictims = cls.fnlSelectServerVictims(mynGlitchSpan)
        for sVictim in lVictims:
            cServer = G.dID2Server[sVictim] 
            cServer.mCorrFailHappensToMe()


# C S e r v e r . f n l L i s t L i v e S e r v e r I D s 
    @classmethod
    @catchex
    @ntracef("SERV")
    def fnlListLiveServerIDs(cls):
        """Class method: return list of IDs for 
            all servers that are still alive
            and being used."""
        lLiveOnes = [sid for sid,csrv in G.dID2Server.items() 
            if (not csrv.mbIsServerDead()) and csrv.bInUse]
        return lLiveOnes


# C S e r v e r . f n l L i s t A l l S e r v e r I D s 
    @classmethod
    @catchex
    @ntracef("SERV")
    def fnlListAllServerIDs(cls):
        """Class method: return list of IDs for 
            all servers."""
        lAllServers = [sid for sid,csrv in G.dID2Server.items() 
            if csrv.bInUse]
        return lAllServers


# C S e r v e r . f n l S e l e c t S e r v e r V i c t i m s 
    @classmethod
    @catchex
    @ntracef("SERV")
    def fnlSelectServerVictims(cls, mynHowManyVictims):
        """Class method: return list of N servers to kill.
        In the case of a shock, they are probably just rescheduled
        with shorter lifespans.
        """
        lPossibleVictims = CServer.fnlListLiveServerIDs()
        return lPossibleVictims[0: min(mynHowManyVictims, 
            len(lPossibleVictims))]


# C S e r v e r . f n s I n v e n t N e w S e r v e r 
    @classmethod
    @catchex
    @ntracef("SERV")
    def fnsInventNewServer(cls):
        '''Class method: Create another server on the fly.
        Use the info from some old one that is still alive to create
        a new one.  Change the long name to make it unique.  
        Return the new server ID.
        '''
        tnow = datetime.now()
        lLiveServerIDs = cls.fnlListLiveServerIDs()
        sServerID = lLiveServerIDs[0]
        cServer = G.dID2Server[sServerID]
        sNewName = (cServer.sName + "_" + util.fnsGetTimeStamp()
                     + "_" + tnow.strftime("%H%M%S.%f"))
        cNewServer = CServer(sNewName, cServer.nQual, cServer.nShelfSizeTB)
        lg.logInfo("SERVER", "created new server|%s| name|%s| "
            "quality|%s| size|%s|TB svrlife|%.0f|" 
            % (cNewServer.ID, sNewName, cNewServer.nQual, 
            cNewServer.nShelfSizeTB, cNewServer.mfGetMyLife()))
        return cNewServer.ID


# S e r v e r . m C o r r F a i l H a p p e n s T o M e
    @catchex
    @ntracef("SERV")
    def mCorrFailHappensToMe(self):
        for sShelfID in self.mListShelves():
            cShelf = G.dID2Shelf[sShelfID]
            cShelf.mCorrFailHappensToMe()
        self.oTimer.stop()


# S e r v e r . m f G e t O r i g i n a l M y L i f e
    @catchex
    @ntracef("SERV")
    def mfGetMyOriginalLife(self):
        ''' Return original lifespan number. '''
        return self.fOriginalLifespan


# S e r v e r . m f G e t M y C u r r e n t L i f e
    @catchex
    @ntracef("SERV")
    def mfGetMyCurrentLife(self):
        ''' Return current lifespan number. '''
        return self.fCurrentLifespan


# S e r v e r . m f G e t M y L i f e
    @catchex
    @ntracef("SERV")
    def mfGetMyLife(self):
        ''' Return current lifespan number. '''
        return self.mfGetMyCurrentLife()


# S e r v e r . m R e s c h e d u l e M y L i f e 
    @catchex
    @ntracef("SERV")
    def mRescheduleMyLife(self, mynNewLife):
        ''' Store new lifespan number. '''
        self.fCurrentLifespan = mynNewLife


# S e r v e r . m l L i s t S h e l v e s 
    @catchex
    @ntracef("SERV")
    def mlListShelves(self):
        """Return list all current shelves for this server."""
        return self.lShelfIDs


# S e r v e r . m A d d C o l l e c t i o n
    @catchex
    @ntracef("SERV")
    def mAddCollection(self, mysCollID, mysClientID):
        self.sClientId = mysClientID
        self.sCollectionID = mysCollID
        lTempDocIDs = list()
        cCollection = G.dID2Collection[mysCollID]
        lTempDocIDs = cCollection.mListDocumentsRemaining()
        for sDocID in lTempDocIDs:
            self.mAddDocument(sDocID, mysClientID)
        self.bInUse = True          # Server now in use
        # BZZZT: new mechanism for declaring server death; don't do this. 
        #self.oTimer.start()         #  and alive, can die.
        return len(lTempDocIDs)


# S e r v e r . m A d d D o c u m e n t 
    @catchex
    @ntracef("SERV")
    def mAddDocument(self, mysDocID, mysClientID):
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
                bResult = cShelf.mAcceptDocument(mysDocID, nSize, mysClientID)
                if bResult:
                    break       # True = doc has been stored
                else:
                    continue    # False = no, try another shelf, if any
            else:               # If no more shelves, create another and use it.
                sNewShelfID = self.mCreateShelf()
                self.lShelfIDs.append(sNewShelfID)
                cShelf = G.dID2Shelf[sNewShelfID]
                sShelfID = cShelf.ID    # TODO: #Why not just use sNewShelfID?
                result = cShelf.mAcceptDocument(mysDocID, nSize, mysClientID)
                
            # Record that the doc has been stored on this server.
            self.lDocIDsComplete.append(mysDocID)
            self.bInUse = True
            self.lDocIDs.append(mysDocID)
            self.dDocIDs[mysDocID] = mysClientID
            NTRC.tracef(3, "SERV", "proc mAddDocument serv|%s| id|%s| "
                "docid|%s| size|%s| assigned to shelfid|%s| remaining|%s|" 
                % (self.sName, self.ID, mysDocID, cDoc.nSize, sShelfID, 
                cShelf.nFreeSpace))
    
            return self.ID+"+"+sShelfID+"+"+mysDocID
        else:
            NTRC.ntracef(3,"SERV","proc mAddDocument1 dead server|%s| do not "
                "add doc|%s| for client|%s|" 
                % (self.ID, mysDocID, mysClientID))
            return False

# S e r v e r . m C r e a t e S h e l f 
    @catchex
    @ntracef("SERV")
    def mCreateShelf(self):
        ''' Add a new shelf of the standard size for this Server.
            Called as needed when a doc arrives too large for available space.  
        '''
        cShelf = CShelf(self.ID, self.nQual, self.nShelfSize)
        lg.logInfo("SERVER","server |%s| created storage shelf|%s| "
            "quality|%s| size|%s|TB svrlife|%.0f|" 
            % (self.ID, cShelf.ID, cShelf.nQual, self.nShelfSizeTB, 
            self.mfGetMyLife()))
        return cShelf.ID


# S e r v e r . m D e s t r o y C o p y 
    @catchex
    @ntracef("SERV")
    def mDestroyCopy(self,mysCopyID,mysDocID,mysShelfID):
        ''' Oops, a doc died, maybe just one or maybe the whole shelf.
        '''
        NTRC.tracef(3,"SERV","proc mDestroyCopy remove copy|%s| doc|%s| "
            "from shelf|%s|" 
            % (mysCopyID, mysDocID, mysShelfID))
        # Inform the client that the copy is gonzo.  
        cClient = G.dID2Client[self.dDocIDs[mysDocID]]
        cClient.mDestroyCopy(mysDocID, self.ID, mysCopyID)
        # Clear out local traces of the doc and copy.
        self.lDocIDs.remove(mysDocID)
        del self.dDocIDs[mysDocID]
        # The Shelf will nuke the copy, because it created it.  
        return self.ID + "-" + mysDocID


# S e r v e r . m T e s t D o c u m e n t 
    @catchex
    @ntracef("SERV")
    def mTestDocument(self,mysDocID):
        ''' Do we still have a copy of this document?  Y/N
            DO NOT MEMOIZE THIS FUNCTION!
        '''
        #bResult = mysDocID in self.lDocIDs
        # Oops, item-in-list is incredibly slow, linear search.
        # It doesn't know that the list is sorted.
        # Try dictionary lookup, which is lots faster.  
        # (The dictionary is maintained by Add and Destroy.)
        bResult = mysDocID in self.dDocIDs and not self.mbIsServerDead()
        # Might someday want to do something other than just return T/F.
        if bResult:
            return True
        else:
            return False


# S e r v e r . m S e r v e r D i e s 
    @catchex
    @ntracef("SERV")
    def mServerDies(self):
        if not self.bDead:
            self.bDead = True
            # Destroy all doc ids so that audit will not find any.
#            TODO: #mark all documents as injured
            NTRC.ntracef(3,"SERV","proc mServerDies kill ndocs|%s|" 
                % (len(self.lDocIDs)))
#            self.lDocIDs = list()
#            self.dDocIDs = dict()
            # Shall we destroy all the shelves, too, or will that also 
            #  cause a problem?
            for sShelfID in self.lShelfIDs:
                G.dID2Shelf[sShelfID].mDestroyShelf()
#               TODO: #mark all shelves as not bAlive
        pass


# S e r v e r . f n T i m e r C a l l 
@catchex
@ntracef("SERV")
def fnTimerCall(objTimer, xContext):
    '''\
    Server life-span timer has completed, and the server must die.
    Set the timer event to release any process waiting for it.
    Declare the server to be el croako.  
    '''
    NTRC.trace(3,"callback %s delay %s called from %s at %s." 
        % (xContext, objTimer.delay, objTimer, G.env.now))
    objTimer.setevent()
    cServer = xContext[0]
    cServer.mKillServer
    lg.logInfo("SERVER","timercalled t|%6.0f| context|%s| delay|%s|" 
        % (G.env.now, xContext, objTimer.delay))
    return (objTimer, xContext)

# S e r v e r . f n T i m e r I n t 
@catchex
@ntracef("SERV")
def fnTimerInt(objTimer, xContext):
    '''\
    Server life-span timer was interrupted to reschedule it, 
    probably by a shock, and presumably to a shorter life.
    But the server is still alive.
    '''
    NTRC.trace(3,"interrupt %s delay %s called from %s at %s." 
        % (xContext, objTimer.delay, objTimer, G.env.now))
    lg.logInfo("SERVER","interrupted t|%6.0f| context|%s| delay|%s|" 
        % (G.env.now, xContext, objTimer.delay))
    return (objTimer, xContext)



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
#               Add r/o properties for instance objects looked up from 
#                self.sxxxIDs.
# 20150812  RBL Remove CShelf, CCopy, and CLifetime classes into 
#                their own files.  
# 20151223  RBL Add tiny methods to keep track of live servers using the 
#                same old global data structures:
#                mListServer, mDelistServer, mKillServer, mbIsServerDead, 
#                mlListLiveServerIDs, mlSelectServerVictims.  
# 20160224  RBL Add correlated failure propagation routines: 
#                (class)fnCorrFailHappensToAll, mCorrFailHappensToMe.
#               Change names of all classmethods to begin with fn instead of m.
#                Yes, they could be static methods or completely external.  
# 20161118  RBL Add ResettableTimer set for infinite life to start with.
#               Start timer when collection is placed, and kill server 
#                when timer expires.
#               And ensure that all documents report lost if server dead.  
# 20161205  RBL Add getter routine for lifetime.  
# 20161222  RBL Add routines to get current and original lifetimes.  
# 20161231  RBL When killing a server, add to the dead server list.
#               BZZZT: When adding a collection, be careful only to add
#                the documents that still exist.  Use Collection's
#                ListDocumentsRemaining method.
# 20170101  RBL Return number of docs when placing collection. 
# 20170102  RBL PEP8-ify most of the long lines.  
# 20170109  RBL Track servers that die, active or otherwise.  
# 20180516  RBL Update to ntrace, ntracef, NTRC.
#               And PEP8-ify a few stragglers.  
# 20180928  RBL Save info on last server created for use in making
#                dynamic servers when we run out of fixed ones.  
# 
# 

#END
