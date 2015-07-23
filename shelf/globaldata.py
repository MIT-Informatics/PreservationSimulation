#!/usr/bin/python
# globaldata.py
# Recovered, we hope, after commit/delete screw-up.  

# G L O B A L  D A T A 
#---------------------

class ProtoG(object):
    ''' Global r/w data, of which we are sure there is only one copy.
        Use this only for truly global data that would be just
        too painful to pass around all the time.  
        Never instantiated; used only as a dictionary.
        Not everything is pre-declared here; some is added later.  
    '''
    env = None
    lAllServers = list()    # object pointers, not IDs
    lAllClients = list()    # object pointers, not IDs
    dQual2Servers = dict()  # key=quality level; val=[[sServerName,sServerID],...]

    nDocLastID = None       # scalar
    nCollLastID = None      # scalar
    nShelfLastID = None     # scalar
    nCopyLastID = None      # scalar
    nServerLastID = None    # scalar
    nClientLastID = None    # scalar
    nTimeLastEvent = 0      # scalar

    dID2Client = dict()
    dID2Collection = dict()
    dID2Document = dict()   # key=ID; val=instance
    dID2Copy = dict()
    dID2Server = dict()
    dID2Shelf = dict()
    dID2Audit = dict()
    dID2Repair = dict()
    dID2Lifetime = dict()
    
    sShortLogStr = ""
    bShortLog = False
    bDoNotLogInfo = False
    
    sAuditStrategy = "OFF"  # OFF, SYSTEMATIC, UNIFORM, ZIPF
    nAuditCycleInterval = 0 # Time between starts of audit cycles; 
                            #  zero = auditing turned off by default
    nAuditSegments = 1      # Number of systematic group samples; 
                            #  one = full audit
    bAuditWithReplacement = False   # For uniform random sample audits, 
                                    #  sample docs without or with replacement
    fAuditZipfParam = 1.0   # Power param for Zipf distn of docs
    fAuditZipfBins = 5      # Into how many bins to classify docs by popularity

    nBandwidthMbps = 10     # Vanilla ethernet speed or cheap ISP
    nBandwidthMbps = 1000   # Lots of bandwidth reqd to support 20 copies, wow.
    nAuditCycleLastCompleted = 0    # Last complete audit in this run.
    
    fSecondsPerHour = float(60.0 * 60.0)    # conversion constant.
    fInfinity = float(1.0E12)   # Infinitely far in the future.

    nGlitchFreq = 0         # Half-life of glitch-free intervals.
    nGlitchImpact = 0       # Percent reduction in sector lifetime.
    nGlitchDecay = 0        # Half-life of glitch duration, decays exponentially.
    nGlitchMaxlife = 0      # Max duration of a single glitch impact.  
    fGlitchIgnoreLimit = 0.05   # Level below which a glitch stops.
    nGlitchesTotal = 0      # Count of all glitches on all shelves.
    sMongoId = None         # MongoDB _id of the instruction for this run.

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
    # NEWS 20141221: change the default for quality 1 to be fixed size 50MB, 
    #  to avoid the most common pilot error when starting new tests.
    dDocParams =    { 1 : [ [ 100, 50, 0 ], [ 0, 50, 0 ] ]
                    , 2 : [ [ 50, 5, 2 ], [ 50, 5000, 2000 ] ]
                    , 3 : [ [ 50, 5, 2 ], [ 50, 5000, 2000 ] ]
                    , 4 : [ [ 50, 5, 2 ], [ 50, 5000, 2000 ] ]
                    , 5 : [ [ 50, 5, 2 ], [ 50, 5000, 2000 ] ]
                    }
 
    dParamsParams = { "RANDOMSEED"  : [[ 1 ]]
                    , "SIMLENGTH"   : [[ 100000 ]]
                    , "LOG_FILE"    : [[ "-" ]]
                    , "LOG_LEVEL"   : [[ "NOTSET" ]]
                    }
 
    dAuditParams =  { "sAuditStrategy"      :   [["SYSTEMATIC"]]
                    , "nAuditCycleInterval" :   [[0]]
                    , "nAuditSegments"      :   [[1]]
                    , "nBandwidthMbps"      :   [[10]]
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


# To start the gradual transition from using the class object G to 
#  using a more civilized class instance, we will try to make a 
#  singleton of the global data.
class Singleton(type):
    _instances = {}
    def __call__(cls,*args,**kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton,cls).__call__(*args,**kwargs)
            cls._provenance = "singleton instance of class %s" % cls._instances[cls]
        return cls._instances[cls]

class CG(ProtoG):
    __metaclass__ = Singleton
    _whatsit = "singleton instance of class CG"

# and eventually
G = CG()
# and then everyone can import this G (instance) instead of the old G (class).

# END
