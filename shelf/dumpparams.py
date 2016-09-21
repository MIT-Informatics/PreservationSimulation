#!/usr/bin/python
# dumpparams.py

# Print params for this run into the log file.

from NewTraceFac import NTRC,ntrace,ntracef
import logoutput as lg
from sys import argv
from globaldata import G,P


#-----------------------------------------------------------
# d u m p P a r a m s I n t o L o g 
@ntracef("DMPP")
def dumpParamsIntoLog():
    # We want a log file to be self-contained, so record all sorts
    #  of information in it about the parameters that resulted in
    #  the answers.
    lg.logInfo("MAIN","Simulation parameters")
    lg.logInfo("MAIN","Command line|%s|" % (argv[1:]))
    lg.logInfo("PARAMS","familydir|%s| specificdir|%s|" % (G.sFamilyDir,G.sSpecificDir)) 
    lg.logInfo("PARAMS","begin simulation seed|%d| timelimit|%d|hr=|%d|metricyr" 
        % (G.nRandomSeed,G.nSimLength,G.nSimLength/10000))
    lg.logInfo("PARAMS","logfile|%s| loglevel|%s|" % (G.sLogFile,G.sLogLevel)) 

    # C l i e n t  params
    NTRC.ntracef(3,"MAIN","client params dict|%s|" % (G.dClientParams))
    for sClient in G.dClientParams:
        lCollections = G.dClientParams[sClient]
        for lCollection in lCollections:
            (sCollection,nQuality,nDocs) = lCollection
            lg.logInfo("PARAMS","CLIENT client|%s| collection|%s| quality|%d| ndocs|%d|" % (sClient,sCollection,nQuality,nDocs))

    # S e r v e r  params
    NTRC.ntracef(3,"MAIN","server params dict|%s|" % (G.dServerParams))
    for sServer in G.dServerParams:
        (nQuality,nShelfSize) = G.dServerParams[sServer][0]
        lg.logInfo("PARAMS","SERVER server|%s| quality|%d| shelfsize|%d|TB" % (sServer,nQuality,nShelfSize))

    # S h e l f  params
    NTRC.ntracef(3,"MAIN","shelf params dict|%s|" % (G.dShelfParams))
    for nQuality in G.dShelfParams:
        (nSmallFailureRate,nShelfFailureRate) = G.dShelfParams[nQuality][0]
        lg.logInfo("PARAMS","SHELF quality|%d| smallfailrate|%d|Khr=|%d|yr shelffailrate|%d|Khr=|%d|yr" % (nQuality,nSmallFailureRate,nSmallFailureRate*1000/8766, nShelfFailureRate,nShelfFailureRate*1000/8766))

    # D i s t r i b u t i o n  policy params.
    NTRC.ntracef(3,"MAIN","distn params dict|%s|" % (G.dDistnParams))
    for nValue in G.dDistnParams:
        (nQuality,nCopies) = G.dDistnParams[nValue][0]
        lg.logInfo("PARAMS","DISTRIBUTION value|%d| quality|%d| copies|%d|" % (nValue,nQuality,nCopies))

    # D o c u m e n t  S i z e  params.
    NTRC.ntracef(3,"MAIN","document params dict|%s|" % (G.dDistnParams))
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

#END
