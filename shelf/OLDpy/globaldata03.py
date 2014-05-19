#!/usr/bin/python
# globaldata.py
    
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
    lServers = list()
    lAllClients = list()
    dQual2Servers = dict() # key=quality level; val=[sServerName,sServerID]

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
    dServerParams =    { "Amazon East":[1,2000]
                        , "Amazon West":[1,3000]
                        , "Google Drive":[2,4000]
                        , "AWS Euro Premium":[3,2000]
                        }
    # Shelf has an MTTF for each quality level.
    # quality : [ sector error rate, shelf error rate ] 
    dShelfParams =      { 1 : [ 10, 100 ]
                        , 2 : [ 20, 200 ]
                        }

    #   { collectionvaluelevel : [ serverqualitylevel, numberofcopies ] , ... }
    dDistnParams =      { 1 : [ 1, 5 ]
                        , 2 : [ 2, 4 ]
                        , 3 : [ 3, 3 ] 
                        }

    # Directory where the parameter files for the run are to be found.  
    sParamdir = "."

    # Log file location and level.
    LOG_LEVEL = "NOTSET"
    LOG_FILE = "-"

    # Seed for random number generators.  Use a constant by default
    #  to permit consistent regression testing.
    RANDOMSEED = 1

    # Length of simulation, in hours.  Default = one year.
    SIMLENGTH = 10000

# END