#!/usr/bin/python
# dumpuse.py

# Dump the servers' various usage stats to the log file.

from __future__ import absolute_import
from .NewTraceFac import NTRC,ntrace,ntracef
from . import logoutput as lg
from .globaldata import G,P
from . import util

    
#-----------------------------------------------------------
# d u m p S e r v e r U s e S t a t s 
@ntracef("DMPU")
def dumpServerUseStats():
    for sKey in sorted(G.dID2Shelf.keys()):
        cShelf = G.dID2Shelf[sKey]
        # Get vector of stats from shelf.
        (sID,sServerID,nQual,fExpolife,nCapacity,nHiWater,nCurrentUse) = \
            cShelf.mReportUseStats()
        lg.logInfo("MAIN", "SERVERUSE shelf|%s-%s| qual|%d| "
            "sectorexpolife|%.0f| size|%d| hiwater|%d| currentuse|%d| "
            "full%%|%d|" 
            % (sServerID, sID, nQual, fExpolife, nCapacity, nHiWater, 
            nCurrentUse, 100*nCurrentUse/nCapacity))
    return sServerID+"+"+sID

# d u m p S e r v e r E r r o r S t a t s 
@ntracef("DMPU")
def dumpServerErrorStats():
    (TnHits,TnEmptyHits,TnAboveHiWater,TnMultipleHits) = (0,0,0,0)
    for sKey in sorted(G.dID2Shelf.keys()):
        cShelf = G.dID2Shelf[sKey]
        # Get vector of stats.
        (sID, sServerID, nQual, nHits, nEmptyHits, bAlive, nAboveHiWater, 
            nMultipleHits) = cShelf.mReportErrorStats()
        lg.logInfo("MAIN", "SERVERERR1 shelf|%s-%s| qual|%d| totalhits|%d| "
            "nonempty|%d| empty|%d| alive|%s|" 
            % (sServerID, sID, nQual, nHits, (nHits-nEmptyHits), 
            nEmptyHits,bAlive))
        lg.logInfo("MAIN", "SERVERERR2 shelf|%s-%s| qual|%d| totalhits|%d| "
            "abovehiwater|%d| multiples|%d|" 
            % (sServerID, sID, nQual, nHits, nAboveHiWater, nMultipleHits))
        TnHits          += nHits
        TnEmptyHits     += nEmptyHits
        TnAboveHiWater  += nAboveHiWater
        TnMultipleHits  += nMultipleHits
    lg.logInfo("MAIN", "SERVERERRTOTALS totalhits|%d| abovehiwater|%d| "
        "nonempty|%d| empty|%d| multiples|%d|" 
        % (TnHits, TnAboveHiWater, (TnHits-TnEmptyHits), TnEmptyHits, 
        TnMultipleHits))
    lg.logInfo("MAIN","DEADSERVERS ALL n|%d| |%s|" 
        % (len(G.lDeadServers), util.fnlSortIDList(G.lDeadServers)))
    lg.logInfo("MAIN","DEADSERVERS ACTIVE n|%d| |%s|" 
        % (len(G.lDeadActiveServers), util.fnlSortIDList(G.lDeadActiveServers)))
    return sServerID+"+"+sID

# d u m p A u d i t S t a t s 
@ntracef("DMPU")
def dumpAuditStats():
    (TnNumberOfCycles, TnRepairsTotal, TnPermanentLosses, TnRepairsMajority,
        TnRepairsMinority) = (0,0,0,0,0)
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
            lg.logInfo("MAIN", "AUDITS id|%s| client|%s| coll|%s| server|%s| "
                "ncycles|%s| nrepairs|%s| nlosses|%s| nmajority|%s| "
                "nminority|%s|" 
                % (ID, sClientID, sCollectionID, sServerID, nNumberOfCycles, 
                nRepairsTotal, nPermanentLosses, nRepairsMajority, 
                nRepairsMinority))
    
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

    lg.logInfo("MAIN", "AUDITTOTALS ncycles|%s| nfrequency|%s| nsegments|%s| "
        "nrepairs|%s| nmajority|%s| nminority|%s| nlost|%s| " 
        % (TnNumberOfCycles, TnFrequency, TnSegments, TnRepairsTotal, 
        TnRepairsMajority, TnRepairsMinority, TnPermanentLosses))
    return 

# d u m p G l i t c h S t a t s 
@ntracef("DMPU")
def dumpGlitchStats():
    
    for sKey in sorted(G.dID2Lifetime.keys()):
        cLifetime = G.dID2Lifetime[sKey]
        dStats = cLifetime.mReportGlitchStats()
        lg.logInfo("MAIN", "LIFETIME shelf|%s| lifetime|%s| freq|%s| "
            "impact|%s| decay|%s| maxlife|%s| count|%s| time|%.3f|" 
        % (
        dStats["sShelfID"], dStats["sLifetimeID"], 
        dStats["nGlitchFreq"], dStats["nImpactReductionPct"], 
        dStats["nGlitchDecayHalflife"], dStats["nGlitchMaxlife"], 
        dStats["nGlitches"], dStats["fGlitchTime"]))
        
    lg.logInfo("MAIN","LIFETIME Total glitches|%d|" % (G.nGlitchesTotal))

# d u m p S h o c k S t a t s 
def dumpShockStats():
    lg.logInfo("MAIN","SHOCKS Total shocks|%d| deaths due to shock|%d: %s|" 
        % (G.nShocksTotal, G.nDeathsDueToShock, G.lDeathsDueToShock))

# d u m p C o l l e c t i o n S t a t s 
def dumpCollectionStats(mysCollID):
    cColl = G.dID2Collection[mysCollID]
    dStats = cColl.mdReportCollectionStats()

    (sCollIDx,sClientIDx,nServers,nDocs, nDocsOkay, nDocsInjured, 
        nDocsForensics, nDocsLost) = \
        (mysCollID, 
        dStats["sClientID"], dStats["nServers"], dStats["nDocs"], 
        dStats["nOkay"], dStats["nRepairsMajority"], dStats["nRepairsMinority"], 
        dStats["nLost"])

    lg.logInfo("MAIN", "COLLECTIONTOTALS client|%s| collection|%s| "
        "nservers|%s| ndocs|%s| nokay|%s| nmajority|%s| nminority|%s| "
        "nlost|%s| "
        % (sClientIDx, sCollIDx, nServers, nDocs, nDocsOkay, nDocsInjured, 
        nDocsForensics, nDocsLost))

# Edit History:
# 20160920  RBL Move these routines out of main.py.
# 20161231  RBL Add list of dead servers to report.  
# 20170102  RBL Add more shock stats.  
#               PEP8-ify some more lines.  
# 20170109  RBL Improve reporting of dead servers.  
# 20170520  RBL Clarify that shelf expolife is sector life.
# 
# 

#END
