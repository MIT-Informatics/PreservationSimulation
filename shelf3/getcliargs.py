#/usr/bin/python
# getcliargs.py

# Get args that came in the CLI and put them into the global
#  dictionary G, overriding defaults, for this run.  


''' ToDo:
- Eliminate all the onesy MaybeOverride calls with a 
  dictionary.update() call.
- Change all BER references to lifetimes.
'''
from __future__ import absolute_import


from .NewTraceFac import NTRC,ntrace,ntracef
from .globaldata import G,P
from .cliparse import fndCliParse
import copy


#----------------------------------------------------
# g e t C l i A r g s F o r P a r a m D i r s
@ntracef("GCLI")
def getCliArgsForParamDirs():
    # The only args we really want at this point are the 
    # Family and Child (Specific) directories.  But this
    # is just easier.  
    dCliDict = fndCliParse(None)
    
    if dCliDict["sFamilydir"]:      P.sFamilyDir = dCliDict["sFamilydir"]
    if dCliDict["sSpecificdir"]:    P.sSpecificDir = dCliDict["sSpecificdir"]
    return P.sFamilyDir + "+" + P.sSpecificDir

# g e t C l i A r g s F o r E v e r y t h i n g E l s e
@ntracef("GCLI")
def getCliArgsForEverythingElse():
    # Let's gloss over the poor naming choices of early weeks.  
    # Copy everything from the Params object to the Global object, 
    # so we can override values in there to actually run with.  
    G.sLogFile = P.sLogFile
    G.sLogLevel = P.sLogLevel

    G.dClientParams =   copy.deepcopy(P.dClientParams)
    G.dServerParams =   copy.deepcopy(P.dServerParams)
    G.dShelfParams =    copy.deepcopy(P.dShelfParams)
    G.dDistnParams =    copy.deepcopy(P.dDistnParams)
    G.dDocParams =      copy.deepcopy(P.dDocParams)
    G.dAuditParams =    copy.deepcopy(P.dAuditParams)
    G.dParamsParams =   copy.deepcopy(P.dParamsParams)

    G.sWorkingDir = P.sWorkingDir       # Even correct the intercapping.
    G.sFamilyDir = P.sFamilyDir
    G.sSpecificDir = P.sSpecificDir

    G.nRandomSeed = P.nRandomSeed
    G.nSimLength = P.nSimLength
    G.nSimLengthDefault = P.nSimLengthDefault

    # Now scan the command line again, this time overwriting anything
    # that came from the param files or environment.  
    dCliDict = fndCliParse(None)

    # Carefully insert any new CLI values into the Global object.
    ''' We may be able to eliminate all this foolishness and use
        just one G.update(dCliDict) call in the future, but I
        have to check that this would not also have some 
        unhappy side effects with names.
    '''
    fnMaybeOverride("nRandomSeed",dCliDict,G)
    fnMaybeOverride("sLogLevel",dCliDict,G)
    fnMaybeOverride("sLogFile",dCliDict,G)
    
    fnMaybeOverride("nDocSmall",dCliDict,G)
    fnMaybeOverride("nDocLarge",dCliDict,G)
    fnMaybeOverride("nDocSmallPct",dCliDict,G)
    fnMaybeOverride("nDocPctSdev",dCliDict,G)

    # A CLI value of zero for sim length means don't override whatever
    #  has already been determined by defaults, params, and environment vars.  
    if dCliDict["nSimLength"] is not None and dCliDict["nSimLength"] > 0:
        fnMaybeOverride("nSimLength",dCliDict,G)

#    fnMaybeOverride("lBER",dCliDict,G)
#    fnMaybeOverride("lBERm",dCliDict,G)
    fnMaybeOverride("nLifek",dCliDict,G)
    fnMaybeOverride("nLifem",dCliDict,G)
    # Hack: convert m to k if k does not exist but m does.
    if (not getattr(G,"nLifek",0)) and (getattr(G,"nLifem",0)):
        G.nLifek = G.nLifem * 1000
    # And propagate this scalar life value to all the server quality entries.
    #  And get rid of this insane data structure someday soon.  
    for k,v in G.dShelfParams.items():
        G.dShelfParams[k][0][0] = G.nLifek
    
    fnMaybeOverride("lCopies",dCliDict,G)
    
    fnMaybeOverride("fServerDefaultHalflife",dCliDict,G)
    fnMaybeOverride("lShelfSize",dCliDict,G)
    
    fnMaybeOverride("sShortLogStr",dCliDict,G)
    
    fnMaybeOverride("sAuditStrategy",dCliDict,G)
    fnMaybeOverride("nAuditCycleInterval",dCliDict,G)
    fnMaybeOverride("nAuditSegments",dCliDict,G)
    fnMaybeOverride("nAuditZipfBins",dCliDict,G)
    fnMaybeOverride("nBandwidthMbps",dCliDict,G)

    fnMaybeOverride("nGlitchFreq",dCliDict,G)
    fnMaybeOverride("nGlitchImpact",dCliDict,G)
    fnMaybeOverride("nGlitchDecay",dCliDict,G)
    fnMaybeOverride("nGlitchMaxlife",dCliDict,G)
    fnMaybeOverride("nGlitchSpan", dCliDict, G)
    
    fnMaybeOverride("nShockFreq", dCliDict, G)
    fnMaybeOverride("nShockImpact", dCliDict, G)
    fnMaybeOverride("nShockSpan", dCliDict, G)
    fnMaybeOverride("nShockMaxlife", dCliDict, G)

    fnMaybeOverride("sMongoId",dCliDict,G)

    # Override ncopies if present on the command line.  
    if getattr(G,"lCopies",None):
        NTRC.ntracef(3,"MAIN","proc CliEverythingElse1bef before G.dDistnParams|%s| G.lCopies|%s|" 
            % (G.dDistnParams,G.lCopies))
        for nKey in G.dDistnParams:
            lValue = G.dDistnParams[nKey][0]
            # Substitute the second item in the list, which is the 
            #  number of copies to make.
            if len(G.lCopies) >= nKey:
                lValue[1] = G.lCopies[nKey - 1]
        NTRC.ntracef(3,"MAIN"," proc CliEverythingElse1aft after  G.dDistnParams|%s|" 
            % (G.dDistnParams))

    ''' TODO:
        If the user supplies lifem instead of lifek on the command line, 
         then scale it up into the lifek value and let that proceed as usual.
    '''

    # Override lber block err rates if present on the command line.  
    ''' Have to fix the param files and cli to refer to lifetimes
        instead of BERs now.
    '''
    if getattr(G,"lBER",None):
        NTRC.ntracef(3,"MAIN","CliEverythingElse2bef before G.lBER|%s| G.dShelfParams|%s|" 
            % (G.lBER,G.dShelfParams))
        for nKey in G.dShelfParams:
            lValue = G.dShelfParams[nKey][0]
            # Substitute the first item in the list, which is the 
            #  small block error rate.
            if len(G.lBER) >= nKey:
                lValue[0] = G.lBER[nKey - 1]
        NTRC.ntracef(3,"MAIN","CliEverythingElse2aft after  G.lBER|%s|" 
            % (G.lBER))

    # Override shelf sizes if present on the command line.  
    if getattr(G,"lShelfSize",None):
        NTRC.ntracef(3,"MAIN","CliEverythingElse3bef before G.lShelfSize|%s|" 
            % (G.lShelfSize))
        for nKey in G.dServerParams:
            lValue = G.dServerParams[nKey][0]
            # The first item in the list is the quality level; the 
            # second item is the shelf size.  Update shelf size to match
            # quality level of the server.  
            if len(G.lShelfSize) >= lValue[0]:
                lValue[1] = G.lShelfSize[lValue[0] - 1]
        NTRC.ntracef(3,"MAIN","CliEverythingElse3aft after  G.lShelfSize|%s|" 
            % (G.lShelfSize))

    # Override doc size params if present on the command line.  
    # This !@#$%^&*() data structure is waaay too complicated.  
    NTRC.ntracef(3,"MAIN","CliEverythingElse4bef before G.dDocParams|%s|" 
        % (G.dDocParams))
    for nKey in G.dDocParams:
        (lSmallValues,lLargeValues) = G.dDocParams[nKey]
        if getattr(G,"nDocSmall",None):
            lSmallValues[1] = G.nDocSmall
        if getattr(G,"nDocSmallPct",None):
            lSmallValues[0] = G.nDocSmallPct
            lLargeValues[0] = 100 - lSmallValues[0]
        if getattr(G,"nDocLarge",None):
            lLargeValues[1] = G.nDocLarge
        if getattr(G,"nDocPctSdev",None):
            lSmallValues[2] = int(lSmallValues[1] * G.nDocPctSdev / 100)
            lLargeValues[2] = int(lLargeValues[1] * G.nDocPctSdev / 100)
    NTRC.ntracef(3,"MAIN","CliEverythingElse4aft after  G.dDocParams|%s|" 
        % (G.dDocParams))

    # Override bShortLog if the user says to.
    NTRC.ntracef(3,"MAIN","CliEverythingElse5bef before G.sShortLogStr|%s|" 
        % (G.sShortLogStr))
    if 'Y' in G.sShortLogStr:
        G.bShortLog = True

#----------------------------------------------------
# f n M a y b e O v e r r i d e 
@ntracef("GCLI")
def fnMaybeOverride(mysArg,mydDict,mycClass):
    ''' Strange function to override a property in G if there is a 
        version in the command line (or other) dictionary.  
        TODO: simplify this a lot
    '''
    try:
        if mydDict[mysArg] is not None:
            setattr( mycClass, mysArg, mydDict[mysArg] )
    except KeyError:
            if not getattr(mycClass,mysArg,None):
                setattr( mycClass, mysArg, None )
    return getattr(mycClass,mysArg,"XXXXX")

#----------------------------------------------------
# fnbCheckBadCombinations
def fnbCheckBadCombinations():
    ''' Test some param combinations that don't make sense or would lead
        to misleading results.
    '''
    if G.sAuditStrategy == "TOTAL" and G.nAuditSegments > 1:
        raise ValueError("Audit params inconsistent: strategy=%s, segments=%s"
                        % (G.sAuditStrategy, G.nAuditSegments))
    if G.sAuditStrategy == "UNIFORM" and G.nAuditSegments == 1:
        raise ValueError("Audit params inconsistent: strategy=%s, segments=%s"
                        % (G.sAuditStrategy, G.nAuditSegments))

    return True

# Edit History:
# 20160920  RBL Move these routines out of main.py.
# 20161221  RBL Remember to include serverdefaultlife value in G, duh.
#               Fix some of the overlong lines.  
#               Allow MaybeOverride to place zero values.
# 20171101  RBL Add routine to check for nonsensical or dangerous params.
# 

#END
