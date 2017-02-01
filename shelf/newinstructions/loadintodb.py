#!/usr/bin/python
'''
loadintodb.py

Load a file into a collection of a database.  

Format of instruction file (all the processing is done in mongolib):
- Blank lines ignored.
- Comment lines, beginning with # ignored.
- One header line, space separated, containing field names.
- Lines containing field values.  

@author: rblandau
'''
from NewTraceFac    import NTRC,ntrace,ntracef
import argparse
import mongolib

# C l i P a r s e 
@ntracef("CLI")
def fndCliParse(mysArglist):
    ''' Parse the mandatory and optional positional arguments, and the 
        many options for this run from the command line.  
        Return a dictionary of all of them.  Strictly speaking that is 
        not necessary, since most of them have already been decanted
        into the P params object.  
    '''
    sVersion = "0.0.3"
    cParse = argparse.ArgumentParser(description="Digital Library "
        "Preservation Simulation LoadIntoDb instruction file database loader",
        epilog="Defaults for args as follows:\n"
        "(none), version=%s \n" 
        "Envir var TRACE_PROGRESS=n will generate progress dots every "
        "n*1000 writes to mongodb."
        % sVersion
        )

    # P O S I T I O N A L  arguments
    #cParse.add_argument('--something', type=, dest='', metavar='', help='')

    cParse.add_argument('sDatabaseName', type=str
                        , metavar='sDATABASENAME'
                        , help='Name of MongoDB database that pymongo will find.'
                        )

    cParse.add_argument('sCollectionName', type=str
                        , metavar='sCOLLECTIONNAME'
                        , help='Collection name within the database.'
                        )

    cParse.add_argument('sInstructionsFile', type=str
                        , metavar='sINSTRUCTIONFILE'
#                        , nargs="?"
                        , help='File with sequence of commands.'
                        )

    # - - O P T I O N S
    # None today in this simplified version.  

    if mysArglist:          # If there is a specific string, use it.
        (xx) = cParse.parse_args(mysArglist)
    else:                   # If no string, then parse from argv[].
        (xx) = cParse.parse_args()
    return vars(xx)

# C G   c l a s s   f o r   g l o b a l   d a t a 
class CG(object):
    ''' Global data.
    '''
    sInstructionsFile = "instructions.txt"
    sDatabaseName = "test_database"
    sCollectionName = "t3"

# f n M a y b e O v e r r i d e 
@ntrace
def fnMaybeOverride(mysCliArg,mydDict,mycClass):
    ''' Strange function to override a property in a global dictionary
        if there is a version in the command line dictionary.  
    '''
    try:
        if mydDict[mysCliArg]:
            setattr( mycClass, mysCliArg, mydDict[mysCliArg] )
    except KeyError:
            if not getattr(mycClass,mysCliArg,None):
                setattr( mycClass, mysCliArg, None )
    return getattr(mycClass,mysCliArg,"XXXXX")


# M A I N 
@ntrace
def main():
    NTRC.ntrace(0,"Begin.")
    g = CG()                # One instance of the global data.
    # Get args from CLI and put them into the global data
    dCliDict = fndCliParse("")
    # Carefully insert any new CLI values into the Global object.
    fnMaybeOverride("sInstructionsFile", dCliDict, g)
    fnMaybeOverride("sDatabaseName", dCliDict, g)
    fnMaybeOverride("sCollectionName", dCliDict, g)

    # Inject the instructions file into the db where specified.
    oDb = mongolib.fnoOpenDb(g.sDatabaseName)
    betterbezero = mongolib.fniClearCollection(oDb, g.sCollectionName)
    oCollection = oDb[g.sCollectionName]
    nRecordCount = mongolib.fniPutFileToDb(g.sInstructionsFile, " ", oCollection)
    NTRC.ntrace(0,"nRecs stored|{}|".format(nRecordCount))


# E n t r y   p o i n t . 
if __name__ == "__main__":
    main()


# Edit history:
# 2015xxxx  RBL Original version, date lost in history.
# 20170110  RBL Add CLI help about envir var for progress bar.  
# 
# 

#END

