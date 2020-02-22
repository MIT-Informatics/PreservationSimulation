#!/usr/bin/python
# searchspace.py
# 
# Supply an instruction stream for the broker by combining all the 
#  individual instruction files and filtering according the the 
#  user's request.  
# Eliminate possibly redundant instructions.
# Check to see that the user's restrictions were not too strong.
# 
# The dictionaries get rather badly mangled because of Python's method
#  of call by object reference.  In several cases, it is necessary to 
#  make deepcopies of the input arguments to prevent leakage.  
# 

import re
import os
import copy
import json
from NewTraceFac import NTRC, ntrace, ntracef
import util
import itertools
import hashlib
import csv


# f n d R e a d A l l I n s F i l e s 
@ntracef("SRCH")
def fndReadAllInsFiles(mysDir, mysTyp):
    ''' 
    Get contents of all the instruction files into a dictionary.
    Use the new new new instruction format, 3 columns, and extract
     and reformat the value info from that.
    '''
    dInstructions = dict()
    for sFile in os.listdir(mysDir):
        if sFile.endswith(mysTyp):
            (sName, _, lValueList) = fntReadOneFileForGUI(mysDir+'/'+sFile)
            dInstructions[sName] = [util.fnIntPlease(item["value"]) 
                                        for item in lValueList]
    if len([k for k in dInstructions.keys()]) == 0:
        raise ValueError("No instruction files for type|%s|" % (mysTyp))
    return dInstructions


# f n t R e a d O n e F i l e 
@ntracef("SRCH")
def fntReadOneFile(mysFilespec):
    '''
    Read one instruction file into a list with separate header name.
    All the values in the list are integer-ized where possible.  
    
    WARNING: the single-column instruction files and this routine are
     OBSOLETE.  Fatal error if called.  
    '''
    
    raise NotImplementedError("Old-format .ins files are now obsolete.")
    
    with open(mysFilespec, "r") as fhInsfile:
        lLines = [sLine.rstrip() for sLine in fhInsfile 
            if not re.match("^\s*$", sLine) and not re.match("^\s*#", sLine)]
    sName = lLines.pop(0)
    lValueList = [util.fnIntPlease(line) for line in lLines]
    return (sName, lValueList)


# f n d R e a d A l l I n s F i l e s F o r G U I 
@ntracef("SRCH")
def fndReadAllInsFilesForGUI(mysDir, mysTyp):
    ''' 
    Get contents of all the instruction files into a dictionary.
    '''
    dInstructions = dict()
    for sFile in os.listdir(mysDir):
        if sFile.endswith(mysTyp):
            (sName, sHeading, lValueList) = (
                    fntReadOneFileForGUI(mysDir+'/'+sFile))
            dInstructions[sName] =  {
                                    "varname" : sName, 
                                    "heading" : sHeading, 
                                    "lValueList" : lValueList
                                    }
    if len([k for k in dInstructions.keys()]) == 0:
        raise ValueError("No instruction files for type|%s|" % (mysTyp))
    return dInstructions


# f n t R e a d O n e F i l e F o r G U I 
@ntracef("SRCH")
def fntReadOneFileForGUI(mysFilespec):
    '''
    Read one instruction file into a list with separate header name.
    Return a list of dicts for substitution as options.
    Instruction file format:
        - Blank lines and comment lines ignored.
        - First line is name of parameter, e.g., "nAuditFreq".
        - Second line is heading text for GUI.  
        - Third line is CSV headings for the data that follows, 
            e.g., "value,label,selected".
        - All remaining lines are data to match the 
    '''
    with open(mysFilespec, "r") as fhInsfile:
        lLines = [sLine.rstrip() for sLine in fhInsfile 
            if not re.match("^\s*$", sLine) and not re.match("^\s*#", sLine)]
    sName = lLines.pop(0)       # First line is name
    sHeading = lLines.pop(0)    # Second line is heading info for GUI.  
    ldRowDicts = csv.DictReader(lLines)
    ldValues = []
    for dValue in ldRowDicts:
#        dValue["varname"] = sName
#        dValue["heading"] = sHeading
        ldValues.append(dValue)
    return (sName, sHeading, ldValues)


# f n t P r o c e s s A l l U s e r R u l e s 
@ntracef("SRCH")
def fntProcessAllUserRules(mydUserRuleDict, mysInstructionDict):
    '''
    Trim the instruction space using all the rules in the user's dictionary.  
    '''
    dOldInstructionDict = copy.deepcopy(mysInstructionDict)
    dWorkingInstructionDict = copy.deepcopy(mysInstructionDict)
    for (sName, xRule) in mydUserRuleDict.items():
        fndProcessOneUserRule(dWorkingInstructionDict, sName, xRule)
    return (dWorkingInstructionDict, dOldInstructionDict)


# f n d P r o c e s s O n e U s e r R u l e 
@ntracef("SRCH")
def fndProcessOneUserRule(mydInstructionDict, mysName, myxRule):
    '''
    Use one user rule to remove value options from instructions.
    '''
    try:
        lInsVals = mydInstructionDict[mysName]
    except KeyError:
        raise KeyError("Error: Unknown parameter name|%s|" % (mysName))
    try:
#        sRule = str(myxRule).encode('ascii', 'ignore').replace('u"', '"')
        sRule = str(myxRule).replace('u"', '"')
        xResult = json.loads(sRule)
    except ValueError:
        raise ValueError("Error: Query string is not valid JSON|%s|" % (sRule))
    
    # One last fixup: Maybe the rule is a string that did not get integer-ified.
    if not xResult:
        xResult = util.fnIntPlease(myxRule)
    
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
                raise NotImplementedError("$in")
            elif "$nin" in xResult:
                raise NotImplementedError("$nin")
    else:
        lNewVals = ["rule type not found"] 
        raise ValueError("Error: unknown comparison operator|%s|" % (xResult))
    
    mydInstructionDict[mysName] = lNewVals
    return mydInstructionDict


# f n d F i l t e r R e s u l t s 
@ntracef("SRCH")
def fndFilterResults(mydOldInstructions):
    ''' 
    Remove redundant cases that would result in wasted effort.  
    If, e.g., no shocks, then don't test for various frequencies.
    '''
    dInstructions = copy.deepcopy(mydOldInstructions)
    
    """
    # First, nuke the special cases that are caused by the dynamic display.  
    dInstructions["nCopiesMax"] = [0]
    dInstructions["nCopiesMin"] = [0]
    dInstructions["nLifemMax"] = [0]
    dInstructions["nLifemMin"] = [0]
    """
    
    # If glitch frequency is zero, clear all the other glitch lists.
    if mydOldInstructions["nGlitchFreq"] == [0]:
        (dInstructions["nGlitchSpan"], dInstructions["nGlitchImpact"], 
            dInstructions["nGlitchDecay"], dInstructions["nGlitchMaxlife"], 
            dInstructions["nGlitchIgnorelevel"],) = [0], [0], [0], [0], [0]
    # ORDER DEPENDENCY: test server life before shock frequency.
    # If servers have infinite default life, then shocks do not matter.  
    if mydOldInstructions["nServerDefaultLife"] == [0]:
        dInstructions["nShockFreq"] = [0]
    # If shock frequency is zero, clear all the other shock lists.  
    if (mydOldInstructions["nShockFreq"] == [0]
        or dInstructions["nShockFreq"] == [0]):
        (dInstructions["nShockSpan"], dInstructions["nShockImpact"], 
        dInstructions["nShockMaxlife"],) = [0], [0], [0] 
    # END ORDER DEPENDENCY.
    # If audit type is TOTAL, then audit segments reduce to one.  
    if mydOldInstructions["sAuditType"] == ["TOTAL"]:
        dInstructions["nAuditSegments"] = [1]
    # If audit frequency is zero, reduce all the other audit options.  
    if mydOldInstructions["nAuditFreq"] == [0]:
        dInstructions["nAuditSegments"] = [0]
        dInstructions["sAuditType"] = ["TOTAL"]
    """
    # If auditing=systematic at high frequency, make sure there are enough
    #  documents for each segment.  
    nMinDocs = util.fnIntPlease(dInstructions["nAuditSegments"]) * 2
    if mydOldInstructions["nDocuments"] < nMinDocs:
        dInstructions["nDocuments"] = nMinDocs
    """
    return dInstructions


# f n v T e s t R e s u l t s 
@ntracef("SRCH")
def fnvTestResults(mydInstructions, mydOldInstructions):
    '''
    If any of the dimensions is empty, the cross product would be empty, 
    i.e., no instructions because the user's criteria are too strict.
    '''
    for sKey, lVal in mydInstructions.items():
        if len(lVal) == 0:
            raise ValueError("Error: instructions too restrictive, \n"
                            "no values remain for param|%s|; \n"
                            "original value set=|%s|\n"
                             % (sKey, mydOldInstructions[sKey], 
                                ))


# f n l g C o m b i n e R e s u l t s 
@ntracef("SRCH")
def fndgCombineResults(mydInstructions):
    '''
    Expand the cross product of remaining instruction values.
    '''
    lKeyNames = [k for k in mydInstructions.keys()]
    for lInstruction in itertools.product(*[mydInstructions[sKey] 
                                        for sKey in lKeyNames]):
        dInstruction = dict(zip(lKeyNames, lInstruction)) 
        # Add unique id, as Mongo does, so we can find jobs already done.
###        dInstruction["_id"] = hashlib.sha1(str(dInstruction)).hexdigest()
        dInstruction["_id"] = (
            hashlib.sha1(str(dInstruction).encode('ascii')).hexdigest()
                                )
        NTRC.ntracef(3, "SRCH", "proc CombineResults:dInstruction|%s|" 
            % (dInstruction))
        yield dInstruction
    
    '''
    BZZZT!
    the right alg appears to be to do this with two list comprehensions.
    e.g.,    
    a=[1]
    b=[2,3]
    c=[4,5,6]
    dd = {'a':a, 'b':b, 'c':c}
    lk = [k for k in dd.keys()]
    lvv = [dd[x] for x in dd.keys()]
    for x in itertools.product(*lvv): print x
    for x in itertools.product(*[dd[y] for y in lk]): print x
    then zip the names and values together into a dictionary.
    '''


# f n l G e t S e a r c h S p a c e N a m e s 
@ntracef("SRCH")
def fnlGetSearchSpaceNames(mydInstructions):
    lKeyNames = [k for k in mydInstructions.keys()]
    lKeyNames = [k for k in mydInstructions.keys()]
    return lKeyNames


# f n l g G e t S e a r c h S p a c e 
@ntracef("SRCH")
def fndgGetSearchSpace(mysDir, mysTyp, mydUserRuleDict):
    '''
    Produce instruction stream from instruction files and user rules.
    '''
    dFullDict = fndReadAllInsFiles(mysDir, mysTyp)
    (dTrimmedDict,dOriginalDict) = fntProcessAllUserRules(mydUserRuleDict, 
                                    dFullDict)
    dFilteredDict = fndFilterResults(dTrimmedDict)
    fnvTestResults(dFilteredDict, dFullDict)
    NTRC.ntracef(3, "SRCH", "proc GetSearchSpace:FilteredDict|%s|" 
        % (dFilteredDict))
    return fndgCombineResults(dFilteredDict)


'''
original pseudocode:

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

test results
    if any instruction list is empty, that means the cross-product
     will also be empty.  wrongo.  raise error.  

doall(userruledict):
    oldinstructiondict = readallfilfes(dir)
    newinstructiondict = processallrules(userruledict)
    return combineresults(newinstructiondict,oldinstructiondict)

Acceptable types of things to specify, just examples.  Be careful with quotes.
--ncopies=5                         number
--ncopies='{"$eq":5}'               number not in quote
--audittype=TOTAL                   string
--audittype='{"$eq":"SYSTEMATIC"}'  string in quotes
--auditsegments='[2,4]'             list in quotes
--ncopies='["$lte":5]'              half-range
--lifem='{"$gte":10,"$lte":1000}'   range

'''

# Edit history:
# 20170113  RBL Original version.  
# 20170114  RBL Change Get... function to return full dictionary instruction.
# 20170129  RBL Fix bug in Filter that looked at old dict instead of new and
#                did not zero out shock attribs correctly.  
# 20170201  RBL If auditing type is TOTAL, then permit only one segment.
# 20170213  RBL Add "ForGUI" versions of read routines to process .ins3 files.
# 20170216  RBL Change all read routines to use .ins3 files.
#               Make sure that strings containing ints become ints.  
#               Raise fatal error if no instruction files get translated.
# 20181116  RBL Remove min/max for copies and lifem.  No longer needed
#                with multiselect.
# 20190118  RBL Ensure that there are enough documents to be divided into
#                the number of auditing segments requested.  This may increase
#                nDocuments for the runs, something we have not done before.  
# 20190121  RBL Disable that last check for nDocuments.  Find a better way.  
# 20200221  RBL Clean up a few comments.  PEP8-ify a little.  
#
# 

#END
