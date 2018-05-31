#!/usr/bin/python
# main.py
from __future__ import absolute_import

''' ToDo:
- Eliminate all the onesy MaybeOverride calls with a 
  dictionary.update() call.
- Change all BER references to lifetimes.
'''

''' M A I N entry of the Shelf simulation
Blank page version of bookshelf preservation of documents.
Vague beginning of document preservation simulation.  

This really is an awful mess, and I apologize for that.  

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
from .NewTraceFac import NTRC,ntrace,ntracef
from .globaldata import G,P
from .client2 import CClient
from .server import CServer
from os import environ
from . import logoutput as lg
from .cliparse import fndCliParse
from time import clock, time
import profile
import cProfile
from . import getparams
from . import getcliargs
from . import dumpparams
from . import dumpuse
from . import makethings
from .shock import CShock


#-----------------------------------------------------------
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
        events.  We use only INFO and DEBUG levels.
    1. The params.csv param file can contain values for LOG_FILE
        and LOG_LEVEL that override the compiled defaults.  
    2. Environment variables LOG_FILE and LOG_LEVEL, if present, 
        override the compiled defaults.  
    3. CLI arg --logfile, if present, overrides LOG_FILE.  
    4. CLI arg --loglevel, if present, overrides LOG_LEVEL.  Note that this is
        a string only, not a numeric value.  
- Logical, yes, but too damned complicated.  
- NEW NEW NEW
- Ah, well, that was altogether too simple and easy to follow.  
   Let's make it much more complicated.  There shall be two
   levels of param files: a test family directory (first)
   and a test specific directory (second).  If a file exists in one
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
        CLI arg1 is now TEST_FAMILY
        CLI arg2 is now TEST_SPECIFIC
        CLI arg3 is now simulation length in hours.
        CLI arg4 is now randomseed, default=1, 0=use system clock.
    3. n/a (no longer implemented)
    4. Param files in the test family directory.
    5. Param files in the test specific directory.
    6. Environment variables that override any params.
    7. CLI args that override any params.  
- Whew!

'''

@ntracef("MAIN")
def main():

    NTRC.ntracef(0,"MAIN","proc Document Preservation simulation " 
        % ())

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
    # arg1 = family directory for param files.
    # arg2 = specific directory for param files.
    # arg3 = simulation length (hours)
    # arg4 = seed for random number generator.  zero means use clock. 
    # --logfile = logfile (relative or absolute)
    # --loglevel = loglevel string (INFO, DEBUG, NOTSET)
    # If the simulation length numeric arg is zero, the default 
    # value will be used. 
    getcliargs.getCliArgsForParamDirs()

    # Read parameter files for simulation.
    # Take CLI arg as the directory location of family param files.  
    getparams.getParamFiles(P.sFamilyDir)

    # And there may be test-specific param files in a child directory
    # of the family directory.  Default dir = "." (i.e., same).  
    # Take CLI arg if present as the directory location of specific param files.  
    if P.sSpecificDir and P.sSpecificDir != ".": 
        sChildDir = P.sFamilyDir + "/" + P.sSpecificDir
        getparams.getParamFiles(sChildDir)

    # ---------------------------------------------------------------
    # Check environment variables for parameters.  
    getparams.getEnvironmentParams()

    # ---------------------------------------------------------------
    # Now get the rest of the CLI options that may override whatever.  
    getcliargs.getCliArgsForEverythingElse()
    #  and try to weed out some arg combinations that won't work.
    bResult = getcliargs.fnbCheckBadCombinations()

    # ---------------------------------------------------------------
    # Start the Python logging facility.
    lg.logSetConfig(G.sLogLevel,G.sLogFile)

    # ---------------------------------------------------------------
    # Log a ton of information so that the log file can be used
    #  for analysis later, self-contained.
    dumpparams.dumpParamsIntoLog()

    # ---------------------------------------------------------------
    # Start the random number generator and the SimPy framework.   
    random.seed(G.nRandomSeed)
    env = simpy.Environment()
    G.env = env
    # Establish a non-shared resource for network bandwidth 
    # to be used during auditing.
    G.NetworkBandwidthResource = simpy.Resource(G.env,capacity=1)

    # ---------------------------------------------------------------
    # Populate servers, clients, collections of documents.
    makethings.makeServers(G.dServerParams)
    makethings.makeClients(G.dClientParams)
    makethings.makeShock(G.nShockFreq)
    dumpuse.dumpServerUseStats()

    # ---------------------------------------------------------------
    # Run the simulation. 
    NTRC.ntracef(0,"MAIN","proc Begin run time|%d|" % (env.now))
    lg.logInfo("MAIN","begin run")

    # If the user asks for short log file, then do not log 
    # any details during the run itself, only intro and conclusion.
    # Run the simulation in this envelope.  
    if G.bShortLog:
        G.bDoNotLogInfo = True
    tSimBegin = clock()
    env.run(until=G.nSimLength)

    CShock.cmAtEndOfRun()
    tSimEnd = clock()
    G.bDoNotLogInfo = False
    G.tSimCpuLen = tSimEnd - tSimBegin

    NTRC.ntracef(0,"MAIN","proc End simulation1 timenow|%d| cpusecs|%.6f| lastevent|%d| " 
        % (env.now,G.tSimCpuLen,G.nTimeLastEvent))
    NTRC.ntracef(0,"MAIN","proc End simulation2 hidoc|%s| hicoll|%s| hishelf|%s|" 
        % (G.nDocLastID,G.nCollLastID,G.nShelfLastID))
    NTRC.ntracef(0,"MAIN","proc End simulation3 hiserver|%s| hiclient|%s| hicopy|%s|" 
        % (G.nServerLastID,G.nClientLastID,G.nCopyLastID))
    lg.logInfo("MAIN","end run, simulated time|%d|" % (env.now))

@ntracef("MAIN")
def evaluate():
    ''' Assess the damage to the collection(s) during the run.  
        Audit all the docs and see if any have been permanently lost.  
        Current verison has no repair.
        Current version question (Q0): Is there at least one valid copy left?
    '''
    makethings.testAllClients(G.lAllClients)


##########################################################
@ntracef("MAIN")
def mainmain():
    tWallBegin = time()
    
    main()
    evaluate()
    dumpuse.dumpServerUseStats()
    dumpuse.dumpServerErrorStats()
    dumpuse.dumpAuditStats()
    dumpuse.dumpGlitchStats()
    dumpuse.dumpShockStats()

    # Make one instance of the global data.  Have to singleton this in globaldata.
    # G = CG()

    tWallEnd = time()
    G.tWallLen = tWallEnd - tWallBegin
    NTRC.ntracef(0,"MAIN","proc End time stats: wall|%8.3f| cpu|%8.3f|" 
        % (G.tWallLen,G.tSimCpuLen))
    NTRC.ntracef(0,"MAIN","ENDENDEND" 
        % ())

# ----------------------------------------------------------
# If this is the main program, run it now.  
if __name__ == "__main__":

    if environ.get("MONKEYPATCH", "NO") == "YES":
        from . import monkeypatch

    if environ.get("CPROFILE","NO") == "YES":
        NTRC.ntracef(0,"MAIN","proc CPROFILE=YES for this slow run " 
            % ())
        cProfile.run('mainmain()')
    else:
        if environ.get("PROFILE","NO") == "YES":
            NTRC.ntracef(0,"MAIN","proc PROFILE=YES for this ssslllooowww run " 
                % ())
            profile.run('mainmain()')
        else:
            mainmain()


# Edit History:
# 2014-2015 RBL Many changes but no explicit history, except 
#                what can be found in the old numbered versions
#                of this file and the git history.  Sorry about that.  
# 20160115  RBL Eliminate lBER references in favor of (scalars) lifek
#                and lifem.  Make lifek dominant if both are present.  
# 20160119  RBL Propagate lifek value into all quality values of 
#                the old quality (shelf params) data structure.
# 20160126  RBL Fix lifek-lifem calc to avoid hasattr().
# 20160216  RBL Add glitchspan to params and stats listings. 
# 20160617  RBL Remove glitchspan.
#               Add shocks to params and stats listings.
#               Gratuitously fix a few 80-character-ness things.
# 20160920  RBL Move routines to get params to separate module, getparams.
#               Move routines to get cli args to separate module, getcliargs.
#               Move routines to dump run params into log to 
#                separate module, dumpparams.
#               Move routines to dump server use stats into log to 
#                separate module, dumpuse.
#               Move server and client maker routines and client test
#                to separate module, makethings.
#               Upgrade all refs to NTRC and ntrace.  
#               Remove extraneous imports.  
# 20161221  RBL Add optional monkeypatch inclusion.
#               Fix some over-long lines.  
# 20171101  RBL Add check for nonsensical combinations of arguments.
# 20180529  RBL Remove ancient "<>" from code, yikes.  
# 20180531  RBL Add cProfile use.
# 
# 

# END
