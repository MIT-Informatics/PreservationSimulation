#!/usr/bin/python
'''
dbclearcollection.py

Clear out a collection of a database.  

@author: rblandau
'''
from __future__ import absolute_import
from .NewTraceFac    import NTRC,ntrace,ntracef
import argparse
from . import searchdatabasemongo

# C l i P a r s e 
@ntracef("CLI")
def fndCliParse(mysArglist):
    ''' Parse the mandatory and optional positional arguments, and the 
        many options for this run from the command line.  
        Return a dictionary of all of them.  
    '''
    sVersion = "0.0.2"
    cParse = argparse.ArgumentParser(description="Digital Library Preservation "
            "Simulation ClearCollection, MongoDB collection eraser\n"
            "Misspelled database and collection names will not be detected, "
            "due to MongoDB's extraordinary generosity.",
            epilog="Defaults for args as follows:\n"
            "(none), version=%s" 
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
    sDatabaseName = None
    sCollectionName = None
    mdb = None

# M A I N 
@ntrace
def main():
    NTRC.ntrace(0,"Begin.")
    # Get args from CLI and put them into the global data
    dCliDict = fndCliParse("")
    # Carefully insert any new CLI values into the Global object.
    dCliDictClean = {k:v for k,v in dCliDict.items() if v is not None}
    g.__dict__.update(dCliDictClean)

    # Since we're deleting an arbitrary collection from the db, 
    #  it doesn't matter if we pretend that it is a specific one
    #  with a different name today.  
    g.mdb = searchdatabasemongo.CSearchDatabase(g.sDatabaseName, 
                    g.sCollectionName, g.sCollectionName)
    g.mdb.fnvDeleteProgressCollection()

    NTRC.ntrace(0,"Cleared collection|{1}| in database|{0}|".format(g.sDatabaseName,g.sCollectionName))


# E n t r y   p o i n t . 
if __name__ == "__main__":
    g = CG()                # One instance of the global data.
    main()

#END
