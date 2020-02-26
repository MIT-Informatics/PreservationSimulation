#!/usr/bin/python
'''
dbdumpdonekeys.py

List all the items in a collection of a database.  

@author: rblandau
'''
from NewTraceFac    import NTRC,ntrace,ntracef
import argparse
import searchdatabasemongo

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
    cParse = argparse.ArgumentParser(description="Digital Library Preservation "
            "Simulation DbDumpCollection MongoDB collection lister",
            epilog="Defaults for args as follows:\n"
            "(none), version=%s" % sVersion
        )

    # P O S I T I O N A L  arguments
    #cParse.add_argument('--something', type=, dest='', metavar='', help='')

    cParse.add_argument('sDatabaseName', type=str
                        , metavar='sDATABASENAME'
                        , help='Name of MongoDB database that pymongo will find.'
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
    sCollectionName = "done"
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
    lCollection = g.mdb.fnlGetDoneCollection()

    # Just print all the items in collection.
    print ("Found %d items:" % (len(lCollection)))
    for (nItem, dItem) in enumerate(lCollection):
        nItem += 1              # Humans are one-based, not zero-based.
        sDoneId = dItem["sDoneId"]
        dResults = dItem["info"]
        sCopies = dResults["copies"]
        sSeed = dResults["seed"]
        sLost = dResults["lost"]
        sTimestamp = dResults["timestamp"]
        sLifem = dResults["lifem"]
        sAuditFreq = dResults["auditfrequency"]
        sAuditSegs = dResults["auditsegments"]
        sShockFreq = dResults["shockfreq"]
        sShockImpact = dResults["shockimpact"]
        sShockSpan = dResults["shockspan"]
        sGlitchFreq = dResults["glitchfreq"]
        sGlitchImpact = dResults["glitchimpact"]
        #sGlitchSpan = dResults["glitchspan"]
        
        print (
        "#%4d cop %2s life %4s lost %4s audit %5s-%1s shock %s %s %s %s %s id|%s|" 
        % (nItem, sCopies, sLifem, sLost, sAuditFreq, sAuditSegs, 
        sShockFreq, sShockImpact, sShockSpan,
        sSeed, sTimestamp, sDoneId)
        )


# E n t r y   p o i n t . 
if __name__ == "__main__":
    g = CG()                # One instance of the global data.
    main()

# Edit history:
# 20170128  RBL Original version.
# 20181218  RBL Add sShockImpact and sDoneId to the output line.  
# 20200225  RBL Change incredibly misleading module name and other
#                leftovers in the comments.  Yikes.  
# 
# 

#END

