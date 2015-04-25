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
    sVersion = "0.0.2"
    cParse = argparse.ArgumentParser(description="Digital Library Preservation Simulation LoadIntoDb instruction file database loader",epilog="Defaults for args as follows:\n\
        (none), version=%s" % sVersion
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


# M A I N 
@ntrace
def main():
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

#END

