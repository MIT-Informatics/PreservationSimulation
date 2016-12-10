#!/usr/bin/python
# cliparse.py
# Parse CLI args with the argparse package and stuff the results 
# into the Params.  
# Recovered, we hope, after commit/delete screw-up.  

sVersion = "0.0.10"
import argparse
from NewTraceFac import TRC,trace,tracef


@tracef("CLI")
def fndCliParse(mysArglist):
    ''' \
    Parse the mandatory and optional positional arguments, and the 
    many options for this run from the command line.  
    Return a dictionary of all of them.  Strictly speaking that is 
    not necessary, since most of them have already been decanted
    into the P params object.  
    '''
    cParse = argparse.ArgumentParser(
    description="Digital Library Preservation Simulation CLI "
    "v"+sVersion,
    epilog="Defaults for args as follows:\n"
        "simlen=100 Khrs,\n"
        "seed=1, "
        "shortlog=N, loglevel=NOTSET, "
        "audit=0 (off), bandwidth=10Mbps "
        "logfile=stdout, glitchfreq=0 (never), \n"
        "shockfreq=0 (never), shockspan=1" 
        , version=sVersion)
    
    # P O S I T I O N A L  arguments
    #cParse.add_argument('--something', type=, dest='', metavar='', help='')

    cParse.add_argument('sFamilydir', type=str
                        , metavar='sFAMILYDIR'
                        , help='Family directory for test parameter files'
                        )

    cParse.add_argument('sSpecificdir', type=str
                        #, nargs="?"
                        , metavar='sSPECIFICDIR'
                        , help='Specific dir below Family dir for overriding'
                        ' parameter files, "." for none'
                        )

    cParse.add_argument("nSimLength", type=int
                        #, nargs="?"
                        , metavar='nSIMLENGTH'
                        , help="Length of simulation in kilo-hours"
                        )

    cParse.add_argument("nRandomSeed",type=int
                        #, nargs="?"
                        , metavar='nRANDOMSEED'
                        , help='Seed for random number generator, 0=use'
                        ' system clock'
                        )

    # - - O P T I O N S

    cParse.add_argument("--ncopies", type=int
                        , dest='lCopies'
                        , metavar='nCOPIES'
                        , nargs='*'
                        , help='Number of copies to make (for value types'
                        ' from 1 up to 5), 0=no change'
                        )

    cParse.add_argument("--lifek", "--halflifekhours", type=int
                        , dest='nLifek'
                        , metavar='nHALFLIFE_Khrs'
                        , nargs='?'
                        , help='Sector half-life for storage shelf in'
                        ' kilo-hours.  If both lifek and lifem are given,'
                        ' lifek takes precedence.  '
                        )

    cParse.add_argument("--lifem", "--halflifemegahours", type=int
                        , dest='nLifem'
                        , metavar='nHALFLIFE_Mhrs'
                        , nargs='?'
                        , help='Sector half-life for storage shelf in '
                        'mega-hours.  May be overridden by lifek.'
                        )
    
    cParse.add_argument("--shelfsize", type=int
                        , dest='lShelfSize'
                        , metavar='nSHELFSIZE_TB'
                        , nargs='*'
                        , help='Size(s) for storage shelf (types from 1 '
                        'up to 5) in TB, 0=no change'
                        )

    cParse.add_argument('--loglevel', type=str
                        , dest='sLogLevel'
                        , choices=['INFO','DEBUG']
                        , help='Logging level for this run'
                        )

    cParse.add_argument('--logfile', type=str
                        , dest='sLogFile'
                        , metavar='sLOGFILE'
                        , help='Log file for output; - or absent for stdout'
                        )

    cParse.add_argument('--shortlog'
                        , action='store_const', const="Y"
                        , dest='sShortLogStr'
                        , help='Log no detailed info for this run, params '
                        'and results only.'
                        )

    cParse.add_argument('--smalldoc', type=int
                        , dest='nDocSmall'
                        , metavar='nDOCSML_MB'
                        , help='Size MB of small docs in mix'
                        )

    cParse.add_argument('--largedoc', type=int
                        , dest='nDocLarge'
                        , metavar='nDOCLRG_MB'
                        , help='Size MB of large docs in mix'
                        )

    cParse.add_argument('--pctsmall', '--pctsmalldoc', type=int
                        , dest='nDocSmallPct'
                        , metavar='nDOCSML_pct'
                        , help='Percentage of small docs in mix'
                        )

    cParse.add_argument('--pctdocvar', type=int
                        , dest='nDocPctSdev'
                        , metavar='nDOCPCTVAR'
                        , help='For doc size distribution, std dev is what '
                        'percentage of mean'
                        )
    
    cParse.add_argument("--audit", type=int
                        , dest='nAuditCycleInterval'
                        , metavar='nAUDITCYCLEINTERVAL_hrs'
                        , help='Hours between auditing cycles; zero=none.'
                        )

    cParse.add_argument("--audittype", type=str
                        , dest='sAuditStrategy'
                        , choices=['TOTAL','OFF','SYSTEMATIC','UNIFORM','ZIPF']
#                        , metavar='sAUDITSTRATEGY'
                        , help='Strategy for auditing, default=SYSTEMATIC.'
                        )

    cParse.add_argument("--auditsegments", type=int
                        , dest='nAuditSegments'
                        , metavar='nAUDITSEGMENTS'
                        , help='Number of subsamples per audit cycle, default=1.'
                        )

    """
    cParse.add_argument("--auditbins", type=int
                        , dest='nAuditZipfBins' 
                        , metavar='nAUDITZIPFBINS'
                        , help='Number of doc bins for Zipf frequency-based '
                        'audits, default=5.'
                        )
    """

    cParse.add_argument("--bandwidth", type=int
                        , dest='nBandwidthMbps'
                        , metavar='nBANDWIDTH_Mbps'
                        , help='Auditing/repair bandwidth in Mbps (mega-*bits* '
                        'per second).'
                        )

    cParse.add_argument("--glitchfreq", type=int
                        , dest='nGlitchFreq'
                        , metavar='nGLITCHFREQ_hrs'
                        , help='Half-life of intervals between glitches; '
                        '0=never happen.'
                        )

    cParse.add_argument("--glitchimpact", type=int
                        , dest='nGlitchImpact'
                        , metavar='nGLITCHIMPACT_pct'
                        , help='Percent reduction in sector lifetime due to glitch; 100%%=fatal to shelf.'
                        )

    cParse.add_argument("--glitchdecay", type=int
                        , dest='nGlitchDecay'
                        , metavar='nGLITCHDECAY_hrs'
                        , help='Half-life of glitch impact exponential decay; '
                        '0=infinity.'
                        )

    cParse.add_argument("--glitchmaxlife", type=int
                        , dest='nGlitchMaxlife'
                        , metavar='nGLITCHMAXLIFE_hrs'
                        , help='Maximum duration of glitch impact, which '
                        'ceases after this interval; 0=infinity.'
                        )

    cParse.add_argument("--glitchspan", type=int
                        , dest='nGlitchSpan'
                        , metavar='nGLITCHSPAN'
                        , help='Number of servers affected by a glitch.'
                        )

    cParse.add_argument("--shockfreq", type=int
                        , dest='nShockFreq'
                        , metavar='nSHOCKFREQ_hrs'
                        , help='Half-life of intervals between economic slumps;'
                        ' 0=never happen.'
                        )

    cParse.add_argument("--shockimpact", type=int
                        , dest='nShockImpact'
                        , metavar='nSHOCKIMPACT_pct'
                        , help='Percent reduction in server lifetime '
                        'due to slump; 100%%=immediately fatal to server.'
                        )

    cParse.add_argument("--shockspan", type=int
                        , dest='nShockSpan'
                        , metavar='nSHOCKSPAN_nservers'
                        , help='Number of servers affected by '
                         'slump.  0=>default=1.'
                        )

    cParse.add_argument("--mongoid", type=str
                        , dest='sMongoId'
                        , metavar='sMONGOID'
                        , nargs='?'
                        , help='Id for instruction item in MongoDB database.'
                        )
    
    if mysArglist:          # If there is a specific string, use it.
        (xx) = cParse.parse_args(mysArglist)
    else:                   # If no string, then parse from argv[].
        (xx) = cParse.parse_args()

    return vars(xx)

# Moved all the data overwriting back to main.  Just return dictionary of 
# params found on command line.  

# Edit History:
# 2014-1015 RBL Many changes from original version, some of them even 
#                visible in the git history.  Sorry about that.  
# 20160115  RBL Change lifek and lifem to accept only a single value.  
#                The business of seach quality type with a separate 
#                parameter is no longer operative.  
# 20160126  RBL Make all positional arguments mandatory.  
#               Remove value requirement (Y,N) from --shortlog.
# 20160216  RBL Add glitchspan option. 
#               Remove auditzipfbins option, never used. 
# 20160617  RBL Remove glitch span.
#               Add economic slump with half-life, impact level, and span.
#               Fix up some 80-character-ness.
# 

# END
