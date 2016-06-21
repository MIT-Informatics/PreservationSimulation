#!/usr/bin/python
# main.py

''' ToDo:
- Eliminate all the onesy MaybeOverride calls with a 
  dictionary.update() call.
- Change all BER references to lifetimes.
'''

''' M A I N entry of the Shelf simulation
Blank page version of bookshelf preservation of documents.
Vague beginning of document preservation simulation.  

This really is an awful mess, and I apologize for that.  

The plan: 

Server
    collection of shelves
    list of documents
    find a shelf for document
        if out of space, create a shelf
    aging process for institutional failure

Shelf
    capacity
    free space
    reliability class
    birthdate
    list of documents
    list of copies
    aging process for small errors that hidden-damage a document
        pick a victim document to be damaged
    aging process for disk failure that can be rebuilt
    aging process for storage array failure that kills all documents

Document
    size
    value class
        determines shelf policy
        determines audit policy
    log of actions
    audit process

Copy of Document
    doc
    client
    server
    shelf
    location on shelf

Collection
    create set of documents
    value class
    storage policy
    audit policy
    budget
    list of servers used

Client
    create set of collections
        different value classes
        distribution of document sizes

start logs
create servers
create clients
run

Recent changes in terminology:
- A Server has a number of Sites where documents may be stored.  A Server may become unavailable due to failure of the institution, e.g., budget cut to zero.  
- A Site is a physical location.  A Site may become unavailable due to a physical catastrophe, such as fire, flood, earthquake, a plane falling on it, war, terrorism, etc.  Sites NYI.  
- A Site contains a number of Shelves on which documents are stored.  
- Shelves vary in their reliability characteristics; some are more reliable than others, and therefore more expensive to maintain and occupy.  (A Shelf is probably roughly equivalent to a RAID storage system including all its servers, controllers, and disks.  I prefer not to use a storage term such as "array" because of the implication of underlying technology.  "Shelf" is a fairly neutral term for a place where you put books to store them.)  
- A Shelf may contain a number of redundant components to enhance its reliability.  Generally, failure of a redundant component is handled internally by the Shelf and not reported to the outside, though internal repair of a redundant component may place the Shelf at a higher risk of total failure for a limited time.  A Shelf may become unavailable due to failure of a non-redundant component or simultaneous failure of a fatal number of redundant components.  
- A Shelf stores a set of documents.  
- A Document is a blob of data.  It has a size, a value, and a sensitivity to corruption.  Some documents are more sensitive to small corruptions than others, e.g., highly compressed or encrypted documents may become unavailable due to errors in small regions of data.  
- A Document may be encrypted or licensed, and therefore may become unavailable due to the loss of the encryption key or license key, generally a much smaller piece of data that may be stored elsewhere.  

Aging processes and their consequences:
- Shelf: small hidden failure.  Affects part(s) of one or more documents depending on error size and doc size.  Rate: cover range from manufacturers' MTBF dodwn one order of magnitude.  
- Shelf: device failure.  Does not impact documents, but renders the shelf vulnerable to total failure if another happens before it is repaired.  Rate: cover range from manufacturers' device MTBF numbers down an order of magnitude. 
- Shelf: total failure.  The entire shelf of documents is lost.  Rate: range based on server and controller MTBFs.  
- Site: temporary outage, e.g., due to power failure, major commnication outage, or similar transient condition.  Makes all Shelves in the site unavailable for some time.  Rate: range based on power and weather incident history.  
- Site: total permanent failure, due to physical loss.  Makes all Shelves in the site unavailable permanently.  
- Server: total permanent loss.  Makes all sites unavailable permanently.  

Implemented in the short term:
- One or more clients.  A client has one or more collections.
- A collection has a name, a value, and a target size.  The actual size is a random close to the target size.  Some number of documents get created, all with the stated value, and placed in the collection.  
- One or more servers.  A server has a quality rating and a shelf size.  The quality rating determines the value of documents that get placed in it.  The shelf size is a storage unit that can fail completely at some rate.  
- Currently servers have no size limit.
- The several servers can represent either (a) one institution with a number of sites with different quality (failure) characteristics, or (b) a number of institutions with one site each.  The choice of interpretations depends on whether one is modelling media quality risks, geographic risks, or institutional risks.  
- Several quality levels, which specify the MTTF of a sector and the MTTF of an entire shelf.  (Later this will include values for altering the failure rates of nearby sectors and shelves.)  
- Distribution policy?  Nothing fancy yet.  A client will send distributions only to servers (sites) with adequate quality ratings.  Currently a collection is sent to one site.
- Most early experiments will probably be done with one client, one collection, stored at one site with one quality rating.
- Storing a collection in multiple locations, repairing, and auditing come later.
'''

import simpy
import random
from NewTraceFac import TRC,trace,tracef
from NewTraceFac import NTRC,ntrace,ntracef
from sys import argv
from globaldata import G,P
from client2 import CClient
from server import CServer
import readin
from os import environ
from util import fnIntPlease
import logoutput as lg
from cliparse import fndCliParse
import copy
from time import clock, time
import profile

#-----------------------------------------------------------
# g e t P a r a m F i l e s 
@tracef("MAIN")
def getParamFiles(mysParamdir):
    # ---------------------------------------------------------------
    # Read the parameter files, whatever their formats.
    dResult =   readin.fdGetClientParams("%s/clients.csv"%(mysParamdir))
    if dResult: P.dClientParams = dResult
        
    dResult =   readin.fdGetServerParams("%s/servers.csv"%(mysParamdir))
    if dResult: P.dServerParams = dResult
        
    dResult =   readin.fdGetQualityParams("%s/quality.csv"%(mysParamdir))
    if dResult: P.dShelfParams = dResult
        
    dResult =   readin.fdGetParamsParams("%s/params.csv"%(mysParamdir))
    if dResult: P.dParamsParams = dResult
        
    dResult =   readin.fdGetDistnParams("%s/distn.csv"%(mysParamdir))
    if dResult: P.dDistnParams = dResult
        
    dResult =   readin.fdGetDocParams("%s/docsize.csv"%(mysParamdir))
    if dResult: P.dDocParams = dResult

    dResult =   readin.fdGetAuditParams("%s/audit.csv"%(mysParamdir))
    if dResult: P.dAuditParams = dResult

    # ---------------------------------------------------------------
    # Process the params params specially.  Unpack them into better names.
    try:
        P.nRandomSeed = fnIntPlease(P.dParamsParams["RANDOMSEED"][0][0])
    except KeyError:
        pass

    try:
        P.nSimLength = fnIntPlease(P.dParamsParams["SIMLENGTH"][0][0])
    except KeyError:
        pass

    try:
        P.sLogFile = P.dParamsParams["LOG_FILE"][0][0]
    except KeyError:
        pass

    try:
        P.sLogLevel = P.dParamsParams["LOG_LEVEL"][0][0]
    except KeyError:
        pass

    '''
    try:
        P.nBandwidthMbps = fnIntPlease(P.dParamsParams["BANDWIDTH"][0][0])
    except KeyError:
        pass
    '''

    '''
    # ---------------------------------------------------------------
    # Process the audit params specially.  Maybe they override defaults.  
    try:
        fnMaybeOverride("nAuditCycleInterval",P.dAuditParams,G)
        fnMaybeOverride("nBandwidthMbps",P.dAuditParams,G)
    except:
        pass
    '''
    '''
    try:
        P.nAuditCycleInterval = fnIntPlease(P.dAuditParams["nAuditCycleInterval"][0][0])
    except KeyError:
        pass
    '''


#-----------------------------------------------------------
# g e t E n v i r o n m e n t P a r a m s
@tracef("MAIN")
def getEnvironmentParams():
    try:
        P.nRandomSeed = fnIntPlease(environ["RANDOMSEED"])
    except (KeyError,TypeError,ValueError):
        pass
    try:
        P.nSimLength = fnIntPlease(environ["SIMLENGTH"])
    except (KeyError,TypeError,ValueError):
        pass
    try:
        P.sLogFile = environ["LOG_FILE"]
    except KeyError:
        pass
    try:
        P.sLogLevel = environ["LOG_LEVEL"]
    except KeyError:
        pass

#-----------------------------------------------------------
# g e t C l i A r g s F o r P a r a m D i r s
@tracef("MAIN")
def getCliArgsForParamDirs():
    # The only args we really want at this point are the 
    # Family and Child (Specific) directories.  But this
    # is just easier.  
    dCliDict = fndCliParse(None)
    
    if dCliDict["sFamilydir"]:      P.sFamilyDir = dCliDict["sFamilydir"]
    if dCliDict["sSpecificdir"]:   P.sSpecificDir = dCliDict["sSpecificdir"]
    return P.sFamilyDir + "+" + P.sSpecificDir

# g e t C l i A r g s F o r E v e r y t h i n g E l s e
@tracef("MAIN")
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

    # Now scan the command line again, this time overwriting anything
    # that came from the param files or environment.  
    dCliDict = fndCliParse(None)

    # Carefully insert any new CLI values into the Global object.
    ''' We may be able to eliminate all this foolishness and use
        just one G.update(dCliDict) call in the future, but I
        have to check that this would not also have some 
        unhappy side effects with names.
    '''
    fnMaybeOverride("nSimLength",dCliDict,G)
    fnMaybeOverride("nRandomSeed",dCliDict,G)
    fnMaybeOverride("sLogLevel",dCliDict,G)
    fnMaybeOverride("sLogFile",dCliDict,G)
    
    fnMaybeOverride("nDocSmall",dCliDict,G)
    fnMaybeOverride("nDocLarge",dCliDict,G)
    fnMaybeOverride("nDocSmallPct",dCliDict,G)
    fnMaybeOverride("nDocPctSdev",dCliDict,G)
    
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

    fnMaybeOverride("sMongoId",dCliDict,G)

    # Override ncopies if present on the command line.  
    if getattr(G,"lCopies",None):
        TRC.tracef(3,"MAIN","proc CliEverythingElse1bef before G.dDistnParams|%s| G.lCopies|%s|" % (G.dDistnParams,G.lCopies))
        for nKey in G.dDistnParams:
            lValue = G.dDistnParams[nKey][0]
            # Substitute the second item in the list, which is the 
            #  number of copies to make.
            if len(G.lCopies) >= nKey:
                lValue[1] = G.lCopies[nKey - 1]
        TRC.tracef(3,"MAIN"," proc CliEverythingElse1aft after  G.dDistnParams|%s|" % (G.dDistnParams))

    ''' TODO:
        If the user supplies lifem instead of lifek on the command line, 
         then scale it up into the lifek value and let that proceed as usual.
    '''

    # Override lber block err rates if present on the command line.  
    ''' Have to fix the param files and cli to refer to lifetimes
        instead of BERs now.
    '''
    if getattr(G,"lBER",None):
        TRC.tracef(3,"MAIN","CliEverythingElse2bef before G.lBER|%s| G.dShelfParams|%s|" % (G.lBER,G.dShelfParams))
        for nKey in G.dShelfParams:
            lValue = G.dShelfParams[nKey][0]
            # Substitute the first item in the list, which is the 
            #  small block error rate.
            if len(G.lBER) >= nKey:
                lValue[0] = G.lBER[nKey - 1]
        TRC.tracef(3,"MAIN","CliEverythingElse2aft after  G.lBER|%s|" % (G.lBER))

    # Override shelf sizes if present on the command line.  
    if getattr(G,"lShelfSize",None):
        TRC.tracef(3,"MAIN","CliEverythingElse3bef before G.lShelfSize|%s|" % (G.lShelfSize))
        for nKey in G.dServerParams:
            lValue = G.dServerParams[nKey][0]
            # The first item in the list is the quality level; the 
            # second item is the shelf size.  Update shelf size to match
            # quality level of the server.  
            if len(G.lShelfSize) >= lValue[0]:
                lValue[1] = G.lShelfSize[lValue[0] - 1]
        TRC.tracef(3,"MAIN","CliEverythingElse3aft after  G.lShelfSize|%s|" % (G.lShelfSize))

    # Override doc size params if present on the command line.  
    # This !@#$%^&*() data structure is waaay too complicated.  
    TRC.tracef(3,"MAIN","CliEverythingElse4bef before G.dDocParams|%s|" % (G.dDocParams))
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
    TRC.tracef(3,"MAIN","CliEverythingElse4aft after  G.dDocParams|%s|" % (G.dDocParams))

    # Override bShortLog if the user says to.
    TRC.tracef(3,"MAIN","CliEverythingElse5bef before G.sShortLogStr|%s|" % (G.sShortLogStr))
    if 'Y' in G.sShortLogStr:
        G.bShortLog = True

# f n M a y b e O v e r r i d e 
@tracef("MAIN")
def fnMaybeOverride(mysArg,mydDict,mycClass):
    ''' Strange function to override a property in G if there is a 
        version in the command line (or other) dictionary.  
        TODO: simplify this a lot
    '''
    try:
        if mydDict[mysArg]:
            setattr( mycClass, mysArg, mydDict[mysArg] )
    except KeyError:
            if not getattr(mycClass,mysArg,None):
                setattr( mycClass, mysArg, None )
    return getattr(mycClass,mysArg,"XXXXX")


#-----------------------------------------------------------
# d u m p P a r a m s I n t o L o g 
@tracef("MAIN")
def dumpParamsIntoLog():
    # We want a log file to be self-contained, so record all sorts
    #  of information in it about the parameters that resulted in
    #  the answers.
    lg.logInfo("MAIN","Simulation parameters")
    lg.logInfo("MAIN","Command line|%s|" % (argv[1:]))
    lg.logInfo("PARAMS","familydir|%s| specificdir|%s|" % (G.sFamilyDir,G.sSpecificDir)) 
    lg.logInfo("PARAMS","begin simulation seed|%d| timelimit|%d|hr=|%d|yr" % (G.nRandomSeed,G.nSimLength,G.nSimLength/8766))
    lg.logInfo("PARAMS","logfile|%s| loglevel|%s|" % (G.sLogFile,G.sLogLevel)) 

    # C l i e n t  params
    TRC.tracef(3,"MAIN","client params dict|%s|" % (G.dClientParams))
    for sClient in G.dClientParams:
        lCollections = G.dClientParams[sClient]
        for lCollection in lCollections:
            (sCollection,nQuality,nDocs) = lCollection
            lg.logInfo("PARAMS","CLIENT client|%s| collection|%s| quality|%d| ndocs|%d|" % (sClient,sCollection,nQuality,nDocs))

    # S e r v e r  params
    TRC.tracef(3,"MAIN","server params dict|%s|" % (G.dServerParams))
    for sServer in G.dServerParams:
        (nQuality,nShelfSize) = G.dServerParams[sServer][0]
        lg.logInfo("PARAMS","SERVER server|%s| quality|%d| shelfsize|%d|TB" % (sServer,nQuality,nShelfSize))

    # S h e l f  params
    TRC.tracef(3,"MAIN","shelf params dict|%s|" % (G.dShelfParams))
    for nQuality in G.dShelfParams:
        (nSmallFailureRate,nShelfFailureRate) = G.dShelfParams[nQuality][0]
        lg.logInfo("PARAMS","SHELF quality|%d| smallfailrate|%d|Khr=|%d|yr shelffailrate|%d|Khr=|%d|yr" % (nQuality,nSmallFailureRate,nSmallFailureRate*1000/8766, nShelfFailureRate,nShelfFailureRate*1000/8766))

    # D i s t r i b u t i o n  policy params.
    TRC.tracef(3,"MAIN","distn params dict|%s|" % (G.dDistnParams))
    for nValue in G.dDistnParams:
        (nQuality,nCopies) = G.dDistnParams[nValue][0]
        lg.logInfo("PARAMS","DISTRIBUTION value|%d| quality|%d| copies|%d|" % (nValue,nQuality,nCopies))

    # D o c u m e n t  S i z e  params.
    TRC.tracef(3,"MAIN","document params dict|%s|" % (G.dDistnParams))
    for nValue in G.dDocParams:
        for lMode in G.dDocParams[nValue]:
            (nPercent,nMean,nSdev) = lMode
            lg.logInfo("PARAMS","DOCUMENT value|%d| percent|%d| meanMB|%d| sd|%d|" % (nValue,nPercent,nMean,nSdev))

    # A u d i t  params.
    lg.logInfo("PARAMS","AUDIT interval hours|%s| segments|%s| type|%s| bandwidth Mbps|%s|" % (G.nAuditCycleInterval,G.nAuditSegments,G.sAuditStrategy,G.nBandwidthMbps)) 

    # G l i t c h  params.
    lg.logInfo("PARAMS","GLITCH freq|%d| impact|%d| decay|%d| maxlife|%d| ignorelimit|%.3f|" 
        % (G.nGlitchFreq, G.nGlitchImpact, G.nGlitchDecay, G.nGlitchMaxlife, 
        G.fGlitchIgnoreLimit))

    # S h o c k   params.
    lg.logInfo("PARAMS","SHOCKS freq|%d| impact|%d| span|%d| " 
        % (G.nShockFreq, G.nShockImpact, G.nShockSpan ))

    
# d u m p S e r v e r U s e S t a t s 
@tracef("MAIN")
def dumpServerUseStats():
    for sKey in sorted(G.dID2Shelf.keys()):
        cShelf = G.dID2Shelf[sKey]
        # Get vector of stats.
        (sID,sServerID,nQual,fExpolife,nCapacity,nHiWater,nCurrentUse) = cShelf.mReportUseStats()
        lg.logInfo("MAIN","SERVERUSE shelf|%s-%s| qual|%d| expolife|%s| size|%d| hiwater|%d| currentuse|%d| full%%|%d|" % (sServerID,sID,nQual,fExpolife,nCapacity,nHiWater,nCurrentUse,100*nCurrentUse/nCapacity))
    return sServerID+"+"+sID

# d u m p S e r v e r E r r o r S t a t s 
@tracef("MAIN")
def dumpServerErrorStats():
    (TnHits,TnEmptyHits,TnAboveHiWater,TnMultipleHits) = (0,0,0,0)
    for sKey in sorted(G.dID2Shelf.keys()):
        cShelf = G.dID2Shelf[sKey]
        # Get vector of stats.
        (sID,sServerID,nQual,nHits,nEmptyHits,bAlive,nAboveHiWater,nMultipleHits) = cShelf.mReportErrorStats()
        lg.logInfo("MAIN","SERVERERR1 shelf|%s-%s| qual|%d| totalhits|%d| nonempty|%d| empty|%d| alive|%s|" % (sServerID,sID,nQual,nHits,(nHits-nEmptyHits),nEmptyHits,bAlive))
        lg.logInfo("MAIN","SERVERERR2 shelf|%s-%s| qual|%d| totalhits|%d| abovehiwater|%d| multiples|%d|" % (sServerID,sID,nQual,nHits,nAboveHiWater,nMultipleHits))
        TnHits          += nHits
        TnEmptyHits     += nEmptyHits
        TnAboveHiWater  += nAboveHiWater
        TnMultipleHits  += nMultipleHits
    lg.logInfo("MAIN","SERVERERRTOTALS totalhits|%d| abovehiwater|%d| nonempty|%d| empty|%d| multiples|%d|" % (TnHits,TnAboveHiWater,(TnHits-TnEmptyHits),TnEmptyHits,TnMultipleHits))
    return sServerID+"+"+sID

# d u m p A u d i t S t a t s 
@tracef("MAIN")
def dumpAuditStats():
    (TnNumberOfCycles,TnRepairsTotal,TnPermanentLosses,TnRepairsMajority,TnRepairsMinority) = (0,0,0,0,0)
    if G.nAuditCycleInterval:       # If there is any auditing in this run,...
        for sKey in sorted(G.dID2Audit.keys()):
            cAudit = G.dID2Audit[sKey]
            # Get vector of stats for one Audit instance.
            dStats = cAudit.mdReportAuditStats()
            (ID,sClientID,sCollectionID,sServerID
             ,nNumberOfCycles,nRepairsTotal
             ,nPermanentLosses,nRepairsMajority,nRepairsMinority) \
            = \
            (sKey,dStats["sClientID"],dStats["sCollectionID"],"*"
             ,dStats["nNumberOfCycles"],dStats["nRepairsTotal"]
             ,dStats["nPermanentLosses"],dStats["nRepairsMajority"]
             ,dStats["nRepairsMinority"]) 
            (nFrequency,nSegments) = (dStats["nFrequency"],dStats["nSegments"])
            lg.logInfo("MAIN","AUDITS id|%s| client|%s| coll|%s| server|%s| ncycles|%s| nrepairs|%s| nlosses|%s| nmajority|%s| nminority|%s|" % (ID,sClientID,sCollectionID,sServerID,nNumberOfCycles,nRepairsTotal,nPermanentLosses,nRepairsMajority,nRepairsMinority))
    
            # Accumulate totals.
            TnNumberOfCycles    +=  nNumberOfCycles
            TnRepairsTotal      +=  nRepairsTotal
            TnPermanentLosses   +=  nPermanentLosses
            TnRepairsMajority   +=  nRepairsMajority
            TnRepairsMinority   +=  nRepairsMinority
            # A couple of these are just declarations, not to be totalled.  
            TnFrequency         =   nFrequency
            TnSegments          =   nSegments

    else:                           # If no auditing in this run.
        TnNumberOfCycles = TnRepairsTotal = 0
        TnPermanentLosses = TnRepairsMajority = TnRepairsMinority = 0
        TnFrequency = TnSegments = 0

    lg.logInfo("MAIN","AUDITTOTALS ncycles|%s| nfrequency|%s| nsegments|%s| nrepairs|%s| nmajority|%s| nminority|%s| nlost|%s| " % (TnNumberOfCycles,TnFrequency,TnSegments,TnRepairsTotal,TnRepairsMajority,TnRepairsMinority,TnPermanentLosses))
    return 

# d u m p G l i t c h S t a t s 
@tracef("MAIN")
def dumpGlitchStats():
    
    for sKey in sorted(G.dID2Lifetime.keys()):
        cLifetime = G.dID2Lifetime[sKey]
        dStats = cLifetime.mReportGlitchStats()
        lg.logInfo("MAIN","LIFETIME shelf|%s| lifetime|%s| freq|%s| impact|%s| decay|%s| maxlife|%s| count|%s| time|%.3f|" 
        % 
        (dStats["sShelfID"], dStats["sLifetimeID"], 
        dStats["nGlitchFreq"], dStats["nImpactReductionPct"], 
        dStats["nGlitchDecayHalflife"], dStats["nGlitchMaxlife"], 
        dStats["nGlitches"], dStats["fGlitchTime"]))
        
    lg.logInfo("MAIN","LIFETIME Total glitches|%d|" % (G.nGlitchesTotal))

# d u m p S h o c k S t a t s 
def dumpShockStats():
    lg.logInfo("MAIN","SHOCKS Total shocks|%d|" % (G.nShocksTotal))

# d u m p C o l l e c t i o n S t a t s 
def dumpCollectionStats(mysCollID):
    cColl = G.dID2Collection[mysCollID]
    dStats = cColl.mdReportCollectionStats()

    (sCollIDx,sClientIDx,nServers,nDocs, nDocsOkay,nDocsInjured,nDocsForensics,nDocsLost) = (mysCollID,dStats["sClientID"],dStats["nServers"],dStats["nDocs"],dStats["nOkay"],dStats["nRepairsMajority"],dStats["nRepairsMinority"],dStats["nLost"])

    lg.logInfo("MAIN","COLLECTIONTOTALS client|%s| collection|%s| nservers|%s| ndocs|%s| nokay|%s| nmajority|%s| nminority|%s| nlost|%s| " \
        % (sClientIDx,sCollIDx,nServers,nDocs, nDocsOkay,nDocsInjured,nDocsForensics,nDocsLost))


#-----------------------------------------------------------
# m a k e S e r v e r s 
@tracef("MAIN")
@tracef("SVRS")
def makeServers(mydServers):
    for sServerName in mydServers:
        (nServerQual,nShelfSize) = mydServers[sServerName][0]
        cServer = CServer(sServerName,nServerQual,nShelfSize)
        sServerID = cServer.ID
        G.lAllServers.append(cServer)
        lg.logInfo("MAIN","created server|%s| quality|%s| shelfsize|%s|TB name|%s|" % (sServerID,nServerQual,nShelfSize,sServerName))
        # Invert the server list so that clients can look up 
        # all the servers that satisfy a quality criterion.  
        if nServerQual in G.dQual2Servers:
            G.dQual2Servers[nServerQual].append([sServerName,sServerID])
        else:
            G.dQual2Servers[nServerQual] = [[sServerName,sServerID]]
        TRC.tracef(5,"SVRS","proc makeServers dQual2Servers qual|%s| servers|%s|" % (nServerQual,G.dQual2Servers[nServerQual]))
    return G.dQual2Servers

#-----------------------------------------------------------
# m a k e C l i e n t s 
# Create all clients; give them their params for the simulation.
@tracef("MAIN")
@tracef("CLI")
def makeClients(mydClients):
    for sClientName in mydClients:
        cClient = CClient(sClientName,mydClients[sClientName])
        G.lAllClients.append(cClient)
        lg.logInfo("MAIN","created client|%s|" % (cClient.ID))
    return G.lAllClients

# t e s t A l l C l i e n t s 
@tracef("CLI")
def testAllClients(mylClients):
    for cClient in mylClients:
        lDeadDocIDs = cClient.mTestClient()
        sClientID = cClient.ID
        if len(lDeadDocIDs) > 0:
            if G.bShortLog:
                G.bDoNotLogInfo = True
            for sDocID in lDeadDocIDs:
                cDoc = G.dID2Document[sDocID]
                lg.logInfo("MAIN","client |%s| lost doc|%s| size|%s|" % (sClientID,sDocID,cDoc.nSize))
            G.bDoNotLogInfo = False
            lg.logInfo("MAIN","BAD NEWS: Total documents lost by client |%s| in all servers |%d|" % (sClientID,len(lDeadDocIDs)))
        else:
            lg.logInfo("MAIN","GOOD NEWS: Total documents lost by client |%s| in all servers |%d|" % (sClientID,len(lDeadDocIDs)))
        
        # Now log stats for the all collections in the client.
        lCollectionIDs = cClient.mListCollectionIDs()
        for sCollID in lCollectionIDs:
            dumpCollectionStats(sCollID)


#-----------------------------------------------------------
# M A I N   L I N E
#------------------
''' 
New philosophy on run parameters.
- The precedence order of parameters shall be, from lowest to highest, 
    - compiled-in default data structures
    - parameter files read from disk at startup
    - environment variables set by the user
    - command line arguments
- Tricky bit: the location of parameter files, as well as specs 
   overriding the content of parameter files, may be stated in 
   environment variables or on the command line.  Oops.  So some 
   of this will require two passes.
    0. A default value for location of param files is compiled in.  
    1. Check environment for specification of param files.  If present, 
       that overrides the compiled default.  (This currently does not
       exist, but you get the idea.)  
    2. Check command line params for specification of param files.  
       If present, that overrides the environment value.  
    3. Read the param files.  Values contained in the param files
       override the compiled-in defaults.
    4. Check the environment for values of specific parameters.  
       If present, they override the param files.  
    5. Check the command line for arguments values of specific
       runtime parameters.  If present, they override.  
- This also refers specifically to the choice of, name of, and 
   detail level of the log file, if any.  In this program, the log 
   is not being used for program function reports; it is used 
   exclusively for application-level reporting of simulated events.  
    0. The compiled defaults are LOG_FILE=console (the standard
        StreamHandler), LOG_LEVEL=NOTSET (which logs warning, error, 
        and critical events, none of which we use for application
        events.  We use only INFO and DEBUG levels.
    1. The params.csv param file can contain values for LOG_FILE
        and LOG_LEVEL that override the compiled defaults.  
    2. Environment variables LOG_FILE and LOG_LEVEL, if present, 
        override the compiled defaults.  
    3. CLI arg --logfile, if present, overrides LOG_FILE.  
    4. CLI arg --loglevel, if present, overrides LOG_LEVEL.  Note that this is
        a string only, not a numeric value.  
- Logical, yes, but too damned complicated.  
- NEW NEW NEW
- Ah, well, that was altogether too simple and easy to follow.  
   Let's make it much more complicated.  There shall be two
   levels of param files: a test family directory (first)
   and a test specific directory (second).  If a file exists in one
   of these directories, it is processed and its dictionary overrides
   what is currently in the P database.  This way, there can be generic
   parameters in the working directory, then params for the family of 
   tests being done in the family directory, then specific params for
   the test at hand in the specific directory, which is a child of the 
   family directory.  
- Processing order: 
    0. Compiled-in default param values, usually only examples.
    1. Environment variables for the locations of the param files.
        TEST_FAMILY
        TEST_SPECIFIC
    2. CLI arg values for the locations of the param files.  
        CLI arg1 is now TEST_FAMILY
        CLI arg2 is now TEST_SPECIFIC
        CLI arg3 is now simulation length in hours.
        CLI arg4 is now randomseed, default=1, 0=use system clock.
    3. n/a (no longer implemented)
    4. Param files in the test family directory.
    5. Param files in the test specific directory.
    6. Environment variables that override any params.
    7. CLI args that override any params.  
- Whew!

'''

def main():

    TRC.tracef(0,"MAIN","proc Document Preservation simulation " % ())

    # ---------------------------------------------------------------
    '''
        NEW NEW NEW
        parse cli
        read params from familydir
        if specificdir not absent and not . 
        then read params from familydir/specificdir
        read environment variables
        use cli options to override params
    '''

    # ---------------------------------------------------------------
    # Allow CLI arguments to override some params.
    # arg1 = family directory for param files.
    # arg2 = specific directory for param files.
    # arg3 = simulation length (hours)
    # arg4 = seed for random number generator.  zero means use clock. 
    # --logfile = logfile (relative or absolute)
    # --loglevel = loglevel string (INFO, DEBUG, NOTSET)
    # If the simulation length numeric arg is zero, the default 
    # value will be used. 
    getCliArgsForParamDirs()

    # Read parameter files for simulation.
    # Take CLI arg as the directory location of family param files.  
    getParamFiles(P.sFamilyDir)

    # And there may be test-specific param files in a child directory
    # of the family directory.  Default dir = "." (i.e., same).  
    # Take CLI arg if present as the directory location of specific param files.  
    if P.sSpecificDir and P.sSpecificDir <> ".": 
        sChildDir = P.sFamilyDir + "/" + P.sSpecificDir
        getParamFiles(sChildDir)

    # ---------------------------------------------------------------
    # Check environment variables for parameters.  
    getEnvironmentParams()

    # ---------------------------------------------------------------
    # Now get the rest of the CLI options that may override whatever.  
    getCliArgsForEverythingElse()

    # ---------------------------------------------------------------
    # Start the Python logging facility.
    lg.logSetConfig(G.sLogLevel,G.sLogFile)

    # ---------------------------------------------------------------
    # Log a ton of information so that the log file can be used
    #  for analysis later, self-contained.
    dumpParamsIntoLog()

    # ---------------------------------------------------------------
    # Start the random number generator and the SimPy framework.   
    random.seed(G.nRandomSeed)
    env = simpy.Environment()
    G.env = env
    # Establish a non-shared resource for network bandwidth 
    # to be used during auditing.
    G.NetworkBandwidthResource = simpy.Resource(G.env,capacity=1)

    # ---------------------------------------------------------------
    # Populate servers, clients, collections of documents.
    makeServers(G.dServerParams)
    makeClients(G.dClientParams)
    dumpServerUseStats()

    # ---------------------------------------------------------------
    # Run the simulation. 
    TRC.tracef(0,"MAIN","proc Begin run time|%d|" % (env.now))
    lg.logInfo("MAIN","begin run")

    # If the user asks for short log file, then do not log 
    # any details during the run itself, only intro and conclusion.
    # Run the simulation in this envelope.  
    if G.bShortLog:
        G.bDoNotLogInfo = True
    tSimBegin = clock()
    env.run(until=G.nSimLength)
    tSimEnd = clock()
    G.bDoNotLogInfo = False
    G.tSimCpuLen = tSimEnd - tSimBegin

    TRC.tracef(0,"MAIN","proc End simulation1 timenow|%d| cpusecs|%s| lastevent|%d| " % (env.now,G.tSimCpuLen,G.nTimeLastEvent))
    TRC.tracef(0,"MAIN","proc End simulation2 hidoc|%s| hicoll|%s| hishelf|%s|" % (G.nDocLastID,G.nCollLastID,G.nShelfLastID))
    TRC.tracef(0,"MAIN","proc End simulation3 hiserver|%s| hiclient|%s| hicopy|%s|" % (G.nServerLastID,G.nClientLastID,G.nCopyLastID))
    lg.logInfo("MAIN","end run, simulated time|%d|" % (env.now))


def evaluate():
    ''' Assess the damage to the collection(s) during the run.  
        Audit all the docs and see if any have been permanently lost.  
        Current verison has no repair.
        Current version question (Q0): Is there at least one valid copy left?
    '''
    testAllClients(G.lAllClients)


##########################################################
def mainmain():
    tWallBegin = time()
    
    main()
    evaluate()
    dumpServerUseStats()
    dumpServerErrorStats()
    dumpAuditStats()
    dumpGlitchStats()
    dumpShockStats()

    # Make one instance of the global data.  Have to singleton this in globaldata.
    # G = CG()

    tWallEnd = time()
    G.tWallLen = tWallEnd - tWallBegin
    TRC.tracef(0,"MAIN","proc End time stats: wall|%8.3f| cpu|%s|" % (G.tWallLen,G.tSimCpuLen))

# ----------------------------------------------------------
# If this is the main program, run it now.  
if __name__ == "__main__":
    '''
    bAlreadyRan = False
    try:
        sProfileVar = environ["PROFILE"]
        if sProfileVar == "YES":
            profile.run('mainmain()')
            bAlreadyRan = True
    except (KeyError,TypeError,ValueError):
        pass
    if not bAlreadyRan:
        mainmain()
    '''
    if environ.get("PROFILE","NO") == "YES":
        TRC.tracef(0,"MAIN","proc PROFILE=YES for this ssslllooowww run " % ())
        profile.run('mainmain()')
    else:
        mainmain()


# Edit History:
# 2014-2015 RBL Many changes but no explicit history, except 
#                what can be found in the old numbered versions
#                of this file and the git history.  Sorry about that.  
# 20160115  RBL Eliminate lBER references in favor of (scalars) lifek
#                and lifem.  Make lifek dominant if both are present.  
# 20160119  RBL Propagate lifek value into all quality values of 
#                the old quality (shelf params) data structure.
# 20160126  RBL Fix lifek-lifem calc to avoid hasattr().
# 20160216  RBL Add glitchspan to params and stats listings. 
# 20160617  RBL Remove glitchspan.
#               Add shocks to params and stats listings.
#               Gratuitously fix a few 80-character-ness things.
# 
# 

# END
