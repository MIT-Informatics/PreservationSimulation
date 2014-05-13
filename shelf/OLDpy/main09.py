#!/usr/bin/python
# main.py

''' M A I N entry of the Shelf simulation
Blank page version of bookshelf preservation of documents.
Vague beginning of document preservation simulation.  

The plan: 

Server
    collection of shelves
    list of documents
    find a shelf for document
        if out of space, create a shelf
    aging process for institutional failure

Shelf
    capacity
    free space
    reliability class
    birthdate
    list of documents
    list of copies
    aging process for small errors that hidden-damage a document
        pick a victim document to be damaged
    aging process for disk failure that can be rebuilt
    aging process for storage array failure that kills all documents

Document
    size
    value class
        determines shelf policy
        determines audit policy
    log of actions
    audit process

Copy of Document
    doc
    client
    server
    shelf
    location on shelf

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
create clients
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
from util import fnIntPlease
import logoutput as lg
from cliparse import *


# g e t P a r a m F i l e s 
@tracef("MAIN")
def getParamFiles(mysParamdir):
    # ---------------------------------------------------------------
    # Read the parameter files, whatever their formats.
    dResult =   readin.fdGetClientParams("%s/clients.csv"%(mysParamdir))
    if dResult: P.dClientParams = dResult
    dResult =   readin.fdGetServerParams("%s/servers.csv"%(mysParamdir))
    if dResult: P.dServerParams = dResult
    dResult =    readin.fdGetQualityParams("%s/quality.csv"%(mysParamdir))
    if dResult: P.dShelfParams = dResult
    dResult =   readin.fdGetParamsParams("%s/params.csv"%(mysParamdir))
    if dResult: P.dParamsParams = dResult
    dResult =   readin.fdGetDistnParams("%s/distn.csv"%(mysParamdir))
    if dResult: P.dDistnParams = dResult
    dResult =   readin.fdGetDocParams("%s/docsize.csv"%(mysParamdir))
    if dResult: P.dDocParams = dResult

    # ---------------------------------------------------------------
    # Process the params params specially.
    try:
        P.RANDOMSEED = fnIntPlease(P.dParamsParams["RANDOMSEED"][0][0])
    except KeyError:
        pass

    try:
        P.SIMLENGTH = fnIntPlease(P.dParamsParams["SIMLENGTH"][0][0])
    except KeyError:
        pass

    try:
        P.LOG_FILE = P.dParamsParams["LOG_FILE"][0][0]
    except KeyError:
        pass

    try:
        P.LOG_LEVEL = P.dParamsParams["LOG_LEVEL"][0][0]
    except KeyError:
        pass

# g e t E n v i r o n m e n t P a r a m s
@tracef("MAIN")
def getEnvironmentParams():
    try:
        P.RANDOMSEED = fnIntPlease(environ["RANDOMSEED"])
    except (KeyError,TypeError,ValueError):
        pass
    try:
        P.SIMLENGTH = fnIntPlease(environ["SIMLENGTH"])
    except (KeyError,TypeError,ValueError):
        pass
    try:
        P.LOG_FILE = environ["LOG_FILE"]
    except KeyError:
        pass
    try:
        P.LOG_LEVEL = environ["LOG_LEVEL"]
    except KeyError:
        pass

# g e t C l i A r g s F o r P a r a m D i r s
@tracef("MAIN")
def getCliArgsForParamDirs():
    # The only args we really want at this point are the 
    # Family and Child (Specific) directories.  But this
    # is just easier.  
    dCliDict = fndCliParse(None)

# g e t C l i A r g s F o r E v e r y t h i n g E l s e
@tracef("MAIN")
def getCliArgsForEverythingElse():
    # Let's gloss over the poor naming choices of early weeks.  
    # Copy everything from the Params object to the Global object, 
    # so we can override values in there to actually run with.  
    G.LOG_FILE = P.sLogFile
    G.LOG_LEVEL = P.sLogLevel
    G.dClientParams = P.dClientParams
    G.dServerParams = P.dServerParams
    G.dShelfParams = P.dShelfParams
    G.dDistnParams = P.dDistnParams
    G.dDocParams = P.dDocParams
    G.dParamsParams = P.dParamsParams
    
    G.sWorkingDir = P.sWorkingdir       # Even correct the intercapping.
    G.sFamilyDir = P.sFamilydir
    G.sSpecificDir = P.sSpecificdir
    
    G.runtime = P.nSimlength
    G.randomseed = P.nRandomseed

    # Now scan the command line again, this time overwriting anything
    # that came from the param files or environment.  
    dCliDict = fndCliParse(None)

    # Carefully insert any new CLI values into the Global object.
    





# d u m p P a r a m s I n t o L o g 
@tracef("MAIN")
def dumpParamsIntoLog():
    # We want a log file to be self-contained, so record all sorts
    #  of information in it about the parameters that resulted in
    #  the answers.
    lg.logInfo("MAIN","Simulation parameters")
    lg.logInfo("MAIN","Command line|%s|" % (argv[1:]))
    lg.logInfo("PARAMS","familydir|%s| specificdir|%s|" % (P.sFamilydir,P.sSpecificdir)) 
    lg.logInfo("PARAMS","begin simulation seed|%d| timelimit|%d|" % (G.randomseed,G.runtime))
    lg.logInfo("PARAMS","logfile|%s| loglevel|%s|" % (G.LOG_FILE,G.LOG_LEVEL)) 
    
    # Client params
    TRC.tracef(3,"MAIN","client params dict|%s|" % (P.dClientParams))
    for sClient in P.dClientParams:
        lCollections = P.dClientParams[sClient]
        for lCollection in lCollections:
            (sCollection,nQuality,nDocs) = lCollection
            lg.logInfo("PARAMS","CLIENT client|%s| collection|%s| quality|%d| ndocs|%d|" % (sClient,sCollection,nQuality,nDocs))

    # Server params
    TRC.tracef(3,"MAIN","server params dict|%s|" % (P.dServerParams))
    for sServer in P.dServerParams:
        (nQuality,nShelfSize) = P.dServerParams[sServer][0]
        lg.logInfo("PARAMS","SERVER server|%s| quality|%d| shelfsize|%d|" % (sServer,nQuality,nShelfSize))

    # Shelf params
    TRC.tracef(3,"MAIN","shelf params dict|%s|" % (P.dShelfParams))
    for nQuality in P.dShelfParams:
        (nSmallFailureRate,nShelfFailureRate) = P.dShelfParams[nQuality][0]
        lg.logInfo("PARAMS","SHELF quality|%d| smallfailrate|%d| shelffailrate|%d|" % (nQuality,nSmallFailureRate,nShelfFailureRate))

    # Distribution policy params.
    TRC.tracef(3,"MAIN","distn params dict|%s|" % (P.dDistnParams))
    for nValue in P.dDistnParams:
        (nQuality,nCopies) = P.dDistnParams[nValue][0]
        lg.logInfo("PARAMS","DISTRIBUTION value|%d| quality|%d| copies|%d|" % (nValue,nQuality,nCopies))

    # Document Size params.
    TRC.tracef(3,"MAIN","document params dict|%s|" % (P.dDistnParams))
    for nValue in P.dDocParams:
        for lMode in P.dDocParams[nValue]:
            (nPercent,nMean,nSdev) = lMode
            lg.logInfo("PARAMS","DOCUMENT value|%d| percent|%d| mean|%d| sd|%d|" % (nValue,nPercent,nMean,nSdev))


# m a k e S e r v e r s 
@tracef("MAIN")
@tracef("SVRS")
def makeServers(mydServers):
    for sServerName in mydServers:
        (nServerQual,nShelfSize) = mydServers[sServerName][0]
        cServer = CServer(sServerName,nServerQual,nShelfSize)
        sServerID = cServer.ID
        G.lAllServers.append(cServer)
        logInfo("MAIN","created server|%s| quality|%s| shelfsize|%s|" % (sServerID,nServerQual,nShelfSize))
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

# t e s t A l l C l i e n t s 
@tracef("CLI")
def testAllClients(mylClients):
    for cClient in mylClients:
        lDeadDocIDs = cClient.mTestClient()
        sClientID = cClient.ID
        if len(lDeadDocIDs) > 0:
            for sDocID in lDeadDocIDs:
                cDoc = G.dID2Document[sDocID]
                logInfo("MAIN","client |%s| lost doc |%s| size |%s|" % (sClientID,sDocID,cDoc.nSize))
            logInfo("MAIN","BAD NEWS: Total documents lost by client |%s| in all servers |%d|" % (sClientID,len(lDeadDocIDs)))
        else:
            logInfo("MAIN","GOOD NEWS: NO DOCUMENTS LOST by client |%s|!" % (sClientID))


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
       that overrides the compiled default.  (This currently does not
       exist, but you get the idea.)  
    2. Check command line params for specification of param files.  
       If present, that overrides the environment value.  
    3. Read the param files.  Values contained in the param files
       override the compiled-in defaults.
    4. Check the environment for values of specific parameters.  
       If present, they override the param files.  
    5. Check the command line for arguments values of specific
       runtime parameters.  If present, they override.  
- This also refers specifically to the choice of, name of, and 
   detail level of the log file, if any.  In this program, the log 
   is not being used for program function reports; it is used 
   exclusively for application-level reporting of simulated events.  
    0. The compiled defaults are LOG_FILE=console (the standard
        StreamHandler), LOG_LEVEL=NOTSET (which logs warning, error, 
        and critical events, none of which we use for application
        events.
    1. The params.csv param file can contain values for LOG_FILE
        and LOG_LEVEL that override the compiled defaults.  
    2. Environment variables LOG_FILE and LOG_LEVEL, if present, 
        override the compiled defaults.  
    3. CLI arg4, if present, overrides LOG_FILE.  
    4. CLI arg5, if present, overrides LOG_LEVEL.  Note that this is
        a string only, not a numeric value.  
- Logical, yes, but too damned complicated.  
- NEW NEW NEW
- Ah, well, let's make is much more complicated.  There shall be three 
   levels of param files: the current working directory, a test family 
   directory, and a test specific directory.  If a file exists in one
   of these directories, it is processed and its dictionary overrides
   what is currently in the P database.  This way, there can be generic
   parameters in the working directory, then params for the family of 
   tests being done in the family directory, then specific params for
   the test at hand in the specific directory, which is a child of the 
   family directory.  
- Processing order: 
    0. Compiled-in default param values, usually only examples.
    1. Environment variables for the locations of the param files.
        TEST_FAMILY
        TEST_SPECIFIC
    2. CLI arg values for the locations of the param files.  
        CLI arg3 is now TEST_FAMILY
        CLI arg4 is now TEST_SPECIFIC
        CLI arg5 is now LOG_FILE
        CLI arg6 is now LOG_LEVEL  
    3. Param files in the current working directory, which is typically "."
    4. Param files in the test family directory.
    5. Param files in the test specific directory.
    6. Environment variables that override any params.
    7. CLI args that override any params.  
- Whew!

'''

def main():

    TRC.tracef(0,"MAIN","proc Document Preservation simulation " % ())

    # ---------------------------------------------------------------
    '''
        NEW NEW NEW
        parse cli
        read params from familydir
        if specificdir not absent and not . 
        then read params from familydir/specificdir
        read environment variables
        use cli options to override params
    '''

    # ---------------------------------------------------------------
    # Allow CLI arguments to override some params.
    # arg1 = simulation length (hours)
    # arg2 = seed for random number generator.  zero means use clock. 
    # arg3 = family directory for param files.
    # arg4 = specific directory for param files.
    # arg5 = logfile (relative or absolute)
    # arg6 = loglevel string (INFO, DEBUG, NOTSET)
    # If the simulation length numeric arg is zero, the default 
    # value will be used. 
    getCliArgsForParamDirs()

    # Read parameter files for simulation.
    # Take CLI arg as the directory location of family param files.  
    getParamFiles(P.sFamilydir)
    # And there may be test-specific param files in a child directory
    # of the family directory.  Default dir = "." (i.e., same).  
    # Take CLI arg if present as the directory location of specific param files.  
    if P.sSpecificdir and P.sSpecificdir <> ".": 
        sChilddir = P.sFamilydir + "/" + P.sSpecificdir
        getParamFiles(sChilddir)

    # ---------------------------------------------------------------
    # Check environment variables for parameters.  
    getEnvironmentParams()

    # ---------------------------------------------------------------
    # Now get the rest of the CLI options that may override whatever.  
    getCliArgsForEverythingElse ()

    # ---------------------------------------------------------------
    # Start the Python logging facility.
    lg.logSetConfig(P.sLogLevel,P.sLogFile)

    # ---------------------------------------------------------------
    # Log a ton of information so that the log file can be used
    #  for analysis later, self-contained.
    dumpParamsIntoLog()

    # ---------------------------------------------------------------
    # Start a couple things.  
    random.seed(G.randomseed)
    env = simpy.Environment()
    G.env = env

    # ---------------------------------------------------------------
    # Populate servers, clients, collections of documents.
    makeServers(P.dServerParams)
    makeClients(P.dClientParams)

    # ---------------------------------------------------------------
    # Run the simulation. 
    TRC.tracef(0,"MAIN","proc Begin run time|%d|" % (env.now))
    logInfo("MAIN","begin run")
    
    env.run(until=G.runtime)

    TRC.tracef(0,"MAIN","proc End simulation timenow|%d| lastevent|%d| hidoc|%s| hicoll|%s| hishelf|%s|" % (env.now,G.nTimeLastEvent,G.nDocLastID,G.nCollLastID,G.nShelfLastID))
    TRC.tracef(0,"MAIN","proc hiserver|%s| hiclient|%s| hicopy|%s|" % (G.nServerLastID,G.nClientLastID,G.nCopyLastID))
    logInfo("MAIN","end run, simulated time|%d|" % (env.now))


def evaluate():
    ''' Assess the damage to the collection(s) during the run.  
        Audit all the docs and see if any have been permanently lost.  
        Current verison has no repair.
        Current version question (Q0): Is there at least one valid copy left?
    '''
    testAllClients(G.lAllClients)


# ---------------------------------------------------------------
# If this is the main program, run it now.  
if __name__ == "__main__":
    main()
    evaluate()


# END
