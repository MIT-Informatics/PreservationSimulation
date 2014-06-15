#!/usr/bin/python
# readin.py

''' 
Read the parameter files into dictionaries.
'''

import csv
from globaldata import *
from NewTraceFac import TRC,trace,tracef
from util import fnIntPlease
import re


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
def fdGetDistnParams(mysFile):
    lGuide = ["Value",["Quality","Copies"]]
    dDistn = fdGetParams(mysFile,lGuide)
    return dDistn

@tracef("READ")
def fdGetDocParams(mysFile):
    lGuide = ["Level",["Percent","Mean","Sdev"]]
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
    # If there is no file of the right name, then return None.
    try:
        fh = open(mysFile,"r")
        fh.close()
    except (ValueError, IOError):
        TRC.tracef(3,"READ","proc fdGetParams1 file not found |%s|" % (mysFile))
        dParams = None

    # If there is such a file, then parse it and return its dictionary.
    (sKey,lCols) = mylGuide
    if dParams == None:
        pass
    else:
        with open(mysFile,"rb") as fhInfile:
            lLines = fhInfile.readlines()
            # Remove comments and blank lines.  
            for sLine in lLines[:]:
                if re.match("^ *#",sLine) \
                or re.match("^ *$",sLine.rstrip()):
                    lLines.remove(sLine)
                    TRC.tracef(3,"READ","proc fdGetParams3 remove comment or blank line |%s|" % (sLine.strip()))
            # Now get the CSV args into a list of dictionaries.
            lRowDicts = csv.DictReader(lLines)
            for dRow in lRowDicts:
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
                TRC.tracef(5,"READ","proc fdGetParams2 mylGuide|%s|dRow|%s|intKey|%s|lVal|%s|dParams|%s|" % (mylGuide,dRow,intKey,lVal,dParams))
    return dParams

# END
