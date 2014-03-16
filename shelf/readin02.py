#!/usr/bin/python
# readin.py

import csv
from globaldata import *
from NewTraceFac07 import TRC,trace,tracef

@tracef("READ")
def fdGetClientParams(mysFile):
    lGuide = ["Institution",["Collection","Quality","Count"]]
    dParams = fdGetParams(mysFile,lGuide)
    return dParams

@tracef("READ")
def fdGetServerParams(mysFile):
    lGuide = ["Name",["Quality","ShelfSize"]]
    dParams = fdGetParams(mysFile,lGuide)
    return dParams

@tracef("READ")
def fdGetQualityParams(mysFile):
    lGuide = ["Rating",["SectorErrorMTTF","ShelfFailureMTTF"]]
    dParams = fdGetParams(mysFile,lGuide)
    return dParams

@tracef("READ")
def fdGetParamsParams(mysFile):
    ''' fdGetParamsParams()
        In the dict of params returned from this, the param values
        are nested two-deep in lists, e.g., 
            keyname : [[ value ]]
        so that the value must be referenced as 
            dictname[keyname][0][0]
        Sorry about that.  Such is the price of generality.  
    '''
    lGuide = ["Name",["Value"]]
    dParams = fdGetParams(mysFile,lGuide)
    return dParams

@tracef("READ")
def fdGetParams(mysFile,mylGuide):
    ''' fdGetParams()
        Return a dictionary of entries from a CSV file according
        to the specified format.  Generally, the dict has a string
        or int key and returns a list.  The list may contain more
        lists.
        Integers in this case drive me nucking futs.  Everything
        from a CSV file is a string, but some of the dict keys
        returned and many of the dict values returned are to be
        used as ints.  One must carefully convert anything that
        might look like an int to a real one.  
    '''
    dParams = dict()
    (sKey,lCols) = mylGuide
    with open(mysFile,"rb") as csvfile:
        rdr = csv.DictReader(csvfile)
        for dRow in rdr:
            dNewRow = dict()
            # Sanitize (i.e., re-integerize) the entire row dict, 
            # keys and values, and use the new version.
            for xKey in dRow:
                dNewRow[fnIntPlease(xKey)] = fnIntPlease(dRow[xKey])
            intKey = dNewRow[sKey]
            if intKey not in dParams:
                dParams[intKey] = []
            lVal = list()
            for sCol in lCols:
                # Many of the values might be ints.
                lVal.append(dNewRow[sCol])
            dParams[intKey].append(lVal)
            TRC.tracef(5,"READ","proc fdGetParams mylGuide|%s|dRow|%s|intKey|%s|lVal|%s|dParams|%s|" % (mylGuide,dRow,intKey,lVal,dParams))
        return dParams

@tracef("INTP",level=5)
def fnIntPlease(oldval):
    ''' fnIntPlease()
        If it looks like an int and walks like an int. . . 
    '''
    try:
        newval = int(oldval)
    except:
        newval = oldval
    return newval

