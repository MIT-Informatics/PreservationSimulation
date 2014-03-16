#!/usr/bin/python
# main.py

''' M A I N entry of the Shelf simulation
Blank page version of bookshelf preservation of documents.
Vague beginning of document preservation simulation.  

The plan: 

Server
    collection of shelves
    find a shelf for document
        if out of space, create a shelf
    aging process for institutional failure

Shelf
    capacity
    free space
    reliability class
    birthdate
    list of documents
    aging process for small errors that damage a document
        pick a victim document to be damaged
    aging process for disk failure that can be rebuilt
    aging process for array failure that kills all documents

Document
    size
    value class
        determines shelf policy
        determines audit policy
    log of actions
    audit process

Collection
    create set of documents
    value class
    storage policy
    audit policy
    budget
    list of servers used

Client
    create set of collections
        different value classes
        distribution of document sizes

start logs
create servers
create client
run

Recent changes in terminology:
- A Server has a number of Sites where documents may be stored.  A Server may become unavailable due to failure of the institution, e.g., budget cut to zero.  
- A Site is a physical location.  A Site may become unavailable due to a physical catastrophe, such as fire, flood, earthquake, a plane falling on it, war, terrorism, etc.  Sites NYI.  
- A Site contains a number of Shelves on which documents are stored.  
- Shelves vary in their reliability characteristics; some are more reliable than others, and therefore more expensive to maintain and occupy.  (A Shelf is probably roughly equivalent to a RAID storage system including all its servers, controllers, and disks.  I prefer not to use a storage term such as "array" because of the implication of underlying technology.  "Shelf" is a fairly neutral term for a place where you put books to store them.)  
- A Shelf may contain a number of redundant components to enhance its reliability.  Generally, failure of a redundant component is handled internally by the Shelf and not reported to the outside, though internal repair of a redundant component may place the Shelf at a higher risk of total failure for a limited time.  A Shelf may become unavailable due to failure of a non-redundant component or simultaneous failure of a fatal number of redundant components.  
- A Shelf stores a set of documents.  
- A Document is a blob of data.  It has a size, a value, and a sensitivity to corruption.  Some documents are more sensitive to small corruptions than others, e.g., highly compressed or encrypted documents may become unavailable due to errors in small regions of data.  
- A Document may be encrypted or licensed, and therefore may become unavailable due to the loss of the encryption key or license key, generally a much smaller piece of data that may be stored elsewhere.  

Aging processes and their consequences:
- Shelf: small hidden failure.  Affects part(s) of one or more documents depending on error size and doc size.  Rate: cover range from manufacturers' MTBF dodwn one order of magnitude.  
- Shelf: device failure.  Does not impact documents, but renders the shelf vulnerable to total failure if another happens before it is repaired.  Rate: cover range from manufacturers' device MTBF numbers down an order of magnitude. 
- Shelf: total failure.  The entire shelf of documents is lost.  Rate: range based on server and controller MTBFs.  
- Site: temporary outage, e.g., due to power failure, major commnication outage, or similar transient condition.  Makes all Shelves in the site unavailable for some time.  Rate: range based on power and weather incident history.  
- Site: total permanent failure, due to physical loss.  Makes all Shelves in the site unavailable permanently.  
- Server: total permanent loss.  Makes all sites unavailable permanently.  

Implemented in the short term:
- One or more clients.  A client has one or more collections.
- A collection has a name, a value, and a target size.  The actual size is a random close to the target size.  Some number of documents get created, all with the stated value, and placed in the collection.  
- One or more servers.  A server has a quality rating and a shelf size.  The quality rating determines the value of documents that get placed in it.  The shelf size is a storage unit that can fail completely at some rate.  
- Currently servers have no size limit.
- The several servers can represent either (a) one institution with a number of sites with different quality (failure) characteristics, or (b) a number of institutions with one site each.  The choice of interpretations depends on whether one is modelling media quality risks, geographic risks, or institutional risks.  
- Several quality levels, which specify the MTTF of a sector and the MTTF of an entire shelf.  (Later this will include values for altering the failure rates of nearby sectors and shelves.)  
- Distribution policy?  Nothing fancy yet.  A client will send distributions only to servers (sites) with adequate quality ratings.  Currently a collection is sent to one site.
- Most early experiments will probably be done with one client, one collection, stored at one site with one quality rating.
- Storing a collection in multiple locations, repairing, and auditing come later.

'''

import simpy
import random
from NewTraceFac import TRC,trace,tracef
from sys import argv
from globaldata import *
from client import *
from server import *
import readin
from os import environ

# m a k e S e r v e r s 
@tracef("MAIN")
@tracef("SVRS")
def makeServers(mydServers):
    for sServerName in mydServers:
        (nServerQual,nShelfSize) = mydServers[sServerName][0]
        sServerID = CServer(sServerName,nServerQual,nShelfSize).ID
        logInfo("MAIN","created server|%s|" % (sServerID))
        # Invert the server list so that clients can look up 
        # all the servers that satisfy a quality criterion.  
        if nServerQual in G.dQual2Servers:
            G.dQual2Servers[nServerQual].append([sServerName,sServerID])
        else:
            G.dQual2Servers[nServerQual] = [[sServerName,sServerID]]
        TRC.tracef(5,"SVRS","proc makeServers dQual2Servers qual|%s| servers|%s|" % (nServerQual,G.dQual2Servers[nServerQual]))
    return G.dQual2Servers

# m a k e C l i e n t s 
# Create all clients; give them their params for the simulation.
@tracef("MAIN")
@tracef("CLI")
def makeClients(mydClients):
    for sClientName in mydClients:
        cClient = CClient(sClientName,mydClients[sClientName])
        G.lAllClients.append(cClient)
        logInfo("MAIN","created client|%s|" % (cClient.ID))
    return G.lAllClients


# M A I N   L I N E
#------------------
''' 
New philosophy on run parameters.
- The precedence order of parameters shall be, from lowest to highest, 
    - compiled-in default data structures
    - parameter files read from disk at startup
    - environment variables set by the user
    - command line arguments
- Tricky bit: the location of parameter files, as well as specs 
   overriding the content of parameter files, may be stated in 
   environment variables or on the command line.  Oops.  So some 
   of this will require two passes.
    0. A default value for location of param files is compiled in.  
    1. Check environment for specification of param files.  If present, 
       that overrides the compiled default.
    2. Check command line params for specification of param files.  
       If present, that overrides the environment value.  
    3. Read the param files.  Values contained in the param files
       override the compiled-in defaults.
    4. Check the environment for values of specific parameters.  
       If present, they override the param files.  
    5. Check the command line for arguments values of specific
       runtime parameters.  If present, they override.  
- Logical, yes, but too damned complicated.  
'''

def main():

    TRC.tracef(0,"MAIN","proc Document Preservation simulation " % ())

    # Read parameter files for simulation.
    # They may be in another directory.  Default dir = "." (i.e., here).  
    # Take CLI arg3 as the directory location of all param files.  
    if len(argv) > 3:
        sParamdir = argv[3]
    else:
        sParamdir = "."
    P.dClientParams =   readin.fdGetClientParams("%s/clients.csv"%(sParamdir))
    P.dServerParams =  readin.fdGetServerParams("%s/servers.csv"%(sParamdir))
    P.dShelfParams =    readin.fdGetQualityParams("%s/quality.csv"%(sParamdir))
    P.dParamsParams =   readin.fdGetParamsParams("%s/params.csv"%(sParamdir))

    # Allow CLI arguments to override some params.
    # arg1 = simulation length (hours)
    # arg2 = seed for random number generator.  zero means use clock. 
    # arg3 = directory for param files.
    # arg4 = logfile (relative or absolute)
    # If the simulation length numeric arg is zero, the default 
    # value will be used. 
    G.runtime = int(P.dParamsParams["SIMLENGTH"][0][0]) if len(argv) <=1 or int(argv[1]) == 0        else int(argv[1])
    G.randomseed = int(P.dParamsParams["RANDOMSEED"][0][0]) if len(argv) <=2 else int(argv[2])

    try:
        G.sLogfile = P.dParamsParams["LOGFILE"]
    except KeyError:
        G.sLogfile = None
    if len(argv) <= 4:
        if G.sLogfile == None:
            environ["LOG_TARGET"] = ""       
            environ.pop("LOG_TARGET")       
    else:
        G.sLogfile = argv[4]
        environ["LOG_TARGET"] = G.sLogfile
    # We have to fudge the environment before importing 
    #  the logging module.
    from logoutput import logInfo

    random.seed(G.randomseed)
    env = simpy.Environment()
    G.env = env

    # Log a ton of information so that the log file can be used
    #  for analysis later, self-contained.
    logInfo("MAIN","Simulation parameters")
    logInfo("PARAMS","begin simulation paramdir|%s| seed|%d| timelimit|%d|" % (sParamdir,G.randomseed,G.runtime))
    # Client params
    TRC.tracef(3,"MAIN","client params dict|%s|" % (P.dClientParams))
    for sClient in P.dClientParams:
        lCollections = P.dClientParams[sClient]
        for lCollection in lCollections:
            (sCollection,nQuality,nDocs) = lCollection
            logInfo("PARAMS","client|%s| collection|%s| quality|%d| ndocs|%d|" % (sClient,sCollection,nQuality,nDocs))
    # Server params
    TRC.tracef(3,"MAIN","server params dict|%s|" % (P.dServerParams))
    for sServer in P.dServerParams:
        (nQuality,nShelfSize) = P.dServerParams[sServer][0]
        logInfo("PARAMS","server|%s| quality|%d| shelfsize|%d|" % (sServer,nQuality,nShelfSize))
    # Shelf params
    TRC.tracef(3,"MAIN","shelf params dict|%s|" % (P.dShelfParams))
    for nQuality in P.dShelfParams:
        (nSmallFailureRate,nShelfFailureRate) = P.dShelfParams[nQuality][0]
        logInfo("PARAMS","quality|%d| smallfailrate|%d| shelffailrate|%d|" % (nQuality,nSmallFailureRate,nShelfFailureRate))

    # Populate servers, clients, collections of documents.
    makeServers(P.dServerParams)
    makeClients(P.dClientParams)

    # Run the simulation. 
    TRC.tracef(0,"MAIN","proc Begin run time|%d|" % (env.now))
    logInfo("MAIN","begin run")
    env.run(until=G.runtime)

    TRC.tracef(0,"MAIN","proc End simulation timenow|%d| lastevent|%d| hidoc|%s| hicoll|%s| hishelf|%s|" % (env.now,G.nTimeLastEvent,G.nDocLastID,G.nCollLastID,G.nShelfLastID))
    logInfo("MAIN","end run, simulated time|%d|" % (env.now))

# If this is the main program, run it now.  
if __name__ == "__main__":
    main()

# END
