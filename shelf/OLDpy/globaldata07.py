#!/usr/bin/python
# globaldata.py
# Recovered, we hope, after commit/delete screw-up.  

# G L O B A L  D A T A 
#---------------------

class G(object):
    ''' Global r/w data, of which we are sure there is only one copy.
        Use this only for truly global data that would be just
        too painful to pass around all the time.  
        Never instantiated; used only as a dictionary.
        Not everything is pre-declared here; some is added later.  
    '''
    env = None
    lAllServers = list()    # object pointers, not IDs
    lAllClients = list()    # object pointers, not IDs
    dQual2Servers = dict()  # key=quality level; val=[sServerName,sServerID]

    nDocLastID = None   # scalar
    nCollLastID = None  # scalar
    nShelfLastID = None # scalar
    nCopyLastID = None
    nServerLastID = None
    nClientLastID = None
    nTimeLastEvent = 0

    dID2Client = dict()
    dID2Collection = dict()
    dID2Document = dict()   # key=ID; val=instance
    dID2Copy = dict()
    dID2Server = dict()
    dID2Shelf = dict()
    dID2Repair = dict()
    
    sShortLogStr = ""
    bShortLog = False
    bDoNotLogInfo = False
    
    nAuditCycleInterval = 0     # auditing turned off by default
    nBandwidthMbps = 10         # vanilla ethernet speed or cheap ISP
    fSecondsPerHour = float(60.0 * 60.0)    # conversion constant


class P(object):
    ''' Parameters r/o for the simulation run. 
        In an adult world, all this would be read from txt or json files.
        This area might not be quite 100% read-only.  For instance, we might 
        overwrite these from a file or command-line arguments.  
        
        WARNING: what you see here is fiction.  
        Currently these dictionaries are replaced entirely by data read 
        from CSV files at startup.
    '''
    # Client has a name and a list of collections.
    # Collection has a name, a value, and a target size.
    dClientParams =     { "MIT":[ ["Mags",1,10], ["Books",2,5] ]
                        , "Harvard":[ ["Cheap",1,20], ["Rare",3,10] ]
                        }
    # Server has a name, a quality rating, and a shelf size.
    # Shelf size is stored here in Terabytes, scaled up to MB when used in servers.  
    dServerParams =    { "Amazon East":[1,20]
                        , "Amazon West":[1,30]
                        , "Google Drive":[2,40]
                        , "AWS Euro Premium":[3,20]
                        }
    # Shelf has an MTTF for each quality level.
    # quality : [ sector error rate, shelf error rate ] 
    # Rates are stored in kilohours here, scaled up to hours when used in servers.
    dShelfParams =      { 1 : [ 10, 100 ]
                        , 2 : [ 20, 200 ]
                        }

    # Distribution parameters: how many copies to make of what value doc.
    #   { collectionvaluelevel : [ serverqualitylevel, numberofcopies ] , ... }
    dDistnParams =      { 1 : [ 1, 5 ]
                        , 2 : [ 2, 4 ]
                        , 3 : [ 3, 3 ] 
                        , 4 : [ 4, 2 ] 
                        , 5 : [ 5, 1 ] 
                        }

    # Document size distribution: multimodel Gaussian, mix percentages and params.
    # { quality : [ pct, mean, sdev ], . . . }
    # where the pct values for a quality level must add up to 100%.
    dDocParams =    { 1 : [ [ 50, 5, 2 ], [ 50, 5000, 2000 ] ]
                    , 2 : [ [ 50, 5, 2 ], [ 50, 5000, 2000 ] ]
                    , 3 : [ [ 50, 5, 2 ], [ 50, 5000, 2000 ] ]
                    , 4 : [ [ 50, 5, 2 ], [ 50, 5000, 2000 ] ]
                    , 5 : [ [ 50, 5, 2 ], [ 50, 5000, 2000 ] ]
                    }
 
    dParamsParams = { "RANDOMSEED"  : [[ 1 ]]
                    , "SIMLENGTH"   : [[ 10000 ]]
                    , "LOG_FILE"    : [[ "-" ]]
                    , "LOG_LEVEL"   : [[ "NOTSET" ]]
                    }
 
    # Directory where the parameter files for the run are to be found. 
    sWorkingDir = "." 
    sFamilyDir = "."
    sSpecificDir = "."

    # Log file location and level.
    sLogLevel = "NOTSET"
    sLogFile = "-"

    # Seed for random number generators.  Use a constant by default
    #  to permit consistent regression testing.
    #RANDOMSEED = 1
    nRandomSeed = 1

    # Length of simulation, in hours.  Default = one year.
    #SIMLENGTH = 100000
    nSimLength = 100000

# END
