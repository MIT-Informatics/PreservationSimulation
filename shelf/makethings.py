#!/usr/bin/python
# makethings.py

# Make servers and clients, and, oh, by the way, test clients when done.

from NewTraceFac import NTRC,ntrace,ntracef
from globaldata import G,P
import logoutput as lg
import client2 as client
import server
import dumpuse
import shock


#-----------------------------------------------------------
# m a k e S e r v e r s 
@ntracef("MAKE")
@ntracef("SVRS")
def makeServers(mydServers):
    for sServerName in mydServers:
        (nServerQual,nShelfSize) = mydServers[sServerName][0]
        cServer = server.CServer(sServerName,nServerQual,nShelfSize)
        sServerID = cServer.ID
        G.lAllServers.append(cServer)
        lg.logInfo("MAIN","created server|%s| quality|%s| shelfsize|%s|TB name|%s|" % (sServerID,nServerQual,nShelfSize,sServerName))
        # Invert the server list so that clients can look up 
        # all the servers that satisfy a quality criterion.  
        if nServerQual in G.dQual2Servers:
            G.dQual2Servers[nServerQual].append([sServerName,sServerID])
        else:
            G.dQual2Servers[nServerQual] = [[sServerName,sServerID]]
        NTRC.ntracef(5,"SVRS","proc makeServers dQual2Servers qual|%s| servers|%s|" % (nServerQual,G.dQual2Servers[nServerQual]))
    return G.dQual2Servers

#-----------------------------------------------------------
# m a k e C l i e n t s 
# Create all clients; give them their params for the simulation.
@ntracef("MAKE")
@ntracef("CLIS")
def makeClients(mydClients):
    for sClientName in mydClients:
        cClient = client.CClient(sClientName,mydClients[sClientName])
        G.lAllClients.append(cClient)
        lg.logInfo("MAIN","created client|%s|" % (cClient.ID))
    return G.lAllClients

# t e s t A l l C l i e n t s 
@ntracef("MAKE")
@ntracef("CLIS")
def testAllClients(mylClients):
    for cClient in mylClients:
        lDeadDocIDs = cClient.mTestClient()
        sClientID = cClient.ID
        if len(lDeadDocIDs) > 0:
            if G.bShortLog:
                G.bDoNotLogInfo = True
            for sDocID in lDeadDocIDs:
                cDoc = G.dID2Document[sDocID]
                lg.logInfo("MAIN","client |%s| lost doc|%s| size|%s|" % (sClientID,sDocID,cDoc.nSize))
            G.bDoNotLogInfo = False
            lg.logInfo("MAIN","BAD NEWS: Total documents lost by client |%s| in all servers |%d|" % (sClientID,len(lDeadDocIDs)))
        else:
            lg.logInfo("MAIN","GOOD NEWS: Total documents lost by client |%s| in all servers |%d|" % (sClientID,len(lDeadDocIDs)))
        
        # Now log stats for the all collections in the client.
        lCollectionIDs = cClient.mListCollectionIDs()
        for sCollID in lCollectionIDs:
            dumpuse.dumpCollectionStats(sCollID)

#-----------------------------------------------------------
# m a k e S h o c k
@ntracef("MAKE")
@ntracef("SHOK")
def makeShock(dunnoyet):
    G.oShock = shock.CShock(G.nShockFreq, G.nShockSpan, G.nShockImpact, G.nShockMaxlife)


# Edit History:
# 20160920  RBL Move these routines out of main.py.
# 20161121  RBL Import shock so we can someday call it.
# 20161205  RBL Call CShock with real args.  
# 20161205  RBL Add maxlife arg to shock.  
# 

#END
