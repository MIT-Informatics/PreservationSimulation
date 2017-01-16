#!/usr/bin/python
# searchspace.py
# 
# Supply an instruction stream for the broker by combining all the 
#  individual instruction files and filtering according the the 
#  user's request.  

'''

cross product the dimensions and yield out
use itertools.product()




read all files:
    for all files in dir
        if right type
            read one fiile
                make instruction dictionary entry 
                of returned tuple(name,listvalue)
    return instructiondict

read one file
    with file open
        read all lines into list
        if first line a string intercapped
            first line = name
        read all lines into list
        if first line is intercapped string
            first line is name
            rest of lines are list value
    return tuple of name, list

process all user rules
    foreach item in rule dictionary
        process one rule

process one rule
weed the instructions according to the selection dictionary
    foreach item in selection dictionary
        if = delete all others
        if != delete that one
        if gt delete those lte
        if gte delete those lt
        if lt delete those gte
        if lte delete those gt

combine results
    foreach item in instruction dictionary
        if valuelist is empty
            raise exception oops on too-restrictive rule
            print all valid values that the user could have specified
            (requires having an original copy of the instruction dictionary)
    calc cross-product of all remaining items
    generator-yield them out one by one

filter results
    for glitch
        if freq == 0
            reduce span, impact, decay, maxlife, ignorelevel to single values
    for servermaxlife
        if == 0
            reduce shock freq to 0 
    for shock
        if freq == 0
            reduce span, impact, maxlife to single values
    for audit
        if freq == 0
            reduce segments, type to single values

doall(userruledict):
    oldinstructiondict = readallfiles(dir)
    newinstructiondict = processallrules(userruledict)
    return combineresults(newinstructiondict,oldinstructiondict)


'''

import re
import os
import copy
import json
from NewTraceFac import NTRC, ntrace, ntracef
import util


@ntracef("SRCH")
def fndReadAllInsFiles(mysDir, mysTyp):
    dInstructions = dict()
    for sFile in os.listdir(mysDir):
        if sFile.endswith(mysTyp):
            (sName, lValueList) = fntReadOneFile(mysDir+'/'+sFile)
            dInstructions[sName] = lValueList
    return dInstructions

@ntracef("SRCH")
def fntReadOneFile(mysFilespec):
    with open(mysFilespec, "r") as fhInsfile:
        lLines = [sLine.rstrip() for sLine in fhInsfile 
            if not re.match("^\s*$", sLine) and not re.match("^\s*#", sLine)]
    sName = lLines.pop(0)
    lValueList = [util.fnIntPlease(line) for line in lLines]
    return (sName, lValueList)

@ntracef("SRCH")
def fntProcessAllUserRules(mydUserRuleDict, mysInstructionDict):
    dOldInstructionDict = copy.deepcopy(mysInstructionDict)
    dWorkingInstructionDict = copy.deepcopy(mysInstructionDict)
    for (sName, xRule) in mydUserRuleDict.items():
        fndProcessOneUserRule(dWorkingInstructionDict, sName, xRule)
    return (dWorkingInstructionDict, dOldInstructionDict)

@ntracef("SRCH")
def fndProcessOneUserRule(mydInstructionDict, mysName, myxRule):
    try:
        lInsVals = mydInstructionDict[mysName]
    except KeyError:
        raise KeyError, "Error: Unknown parameter name|%s|" % (mysName)
    try:
        xResult = json.loads(myxRule)
    except ValueError:
        raise ValueError, "Error: Query string is not valid JSON|%s|" % (myxRule)
    
    if isinstance(xResult, int):
        lNewVals = [item for item in lInsVals 
                    if item == xResult]
    elif isinstance(xResult, list):
        lNewVals = [item for item in lInsVals 
                    if item in xResult]
    elif isinstance(xResult, dict):
        lCleanResult = [(k,util.fnIntPlease(v)) 
                        for (k,v) in xResult.items()]
        lNewVals = copy.deepcopy(lInsVals)
        for k,v in lCleanResult:
            if "$eq" == k:
                lNewVals = [item for item in lNewVals 
                            if item == v]
            elif "$ne" == k:
                lNewVals = [item for item in lNewVals 
                            if item != v]
            elif "$lt" == k:
                lNewVals = [item for item in lNewVals 
                            if item < v]
            elif "$lte" == k:
                lNewVals = [item for item in lNewVals 
                            if item <= v]
            elif "$gt" == k:
                lNewVals = [item for item in lNewVals 
                            if item > v]
            elif "$gte" == k:
                lNewVals = [item for item in lNewVals 
                            if item >= v]
            
            elif "$in" in xResult:
                raise NotImplementedError, "$in"
            elif "$nin" in xResult:
                raise NotImplementedError, "$nin"
    else:
        lNewVals = ["rule type not found"] 
        raise ValueError, "Error: unknown comparison operator|%s|" % (xResult)
    
    mydInstructionDict[mysName] = lNewVals
    return mydInstructionDict

@ntracef("SRCH")
def fnlgCombineResults(mydNewInstructionDict, mydOldInstructionDict):
    pass
    yield

@ntracef("SRCH")
def fnlgGetSearchSpace(mysDir, mydUserRuleDict):
    pass
    return




