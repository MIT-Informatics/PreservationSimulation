#!/usr/bin/python
# getparams.py

# Get and organize info from all the parameter files, 
#  plus a few from the environment.  

from NewTraceFac import NTRC,ntrace,ntracef
import readin
from util import fnIntPlease
from os import environ, getenv
from globaldata import G,P

#-----------------------------------------------------------
# g e t P a r a m F i l e s 
@ntracef("GETP")
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
@ntracef("GETP")
def getEnvironmentParams():
    ''' In every case, keep default if no new envir var present.'''
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
    P.nPoliteTimer = fnIntPlease(getenv("NPOLITE", P.nPoliteTimer))
    G.nShockType = fnIntPlease(environ.get("SHELF_SHOCKTYPE", G.nShockType))
    # Have to resolve some of these from P to G before considering the 
    #  CLI params that may override them, so that they can be 
    #  reported correctly.  
    G.nSimLength = (P.nSimLength if P.nSimLength > 0 else P.nSimLengthDefault)
    G.nRandomSeed = P.nRandomSeed

# Edit History:
# 20160920  RBL Move these routines out of main.py.
# 20170109  RBL Add shock type to envir vars.  
#               And note that none of the other envir vars is used anymore.  
# 20181127  RBL Actually read POLITE timer if you're going to report it, duh.  
# 
# 

#END
