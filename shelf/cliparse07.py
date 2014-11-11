#!/usr/bin/python
# cliparse.py
# Parse CLI args with the argparse package and stuff the results 
# into the Params.  
# Recovered, we hope, after commit/delete screw-up.  

sVersion = "0.0.4"
import argparse
from NewTraceFac import TRC,trace,tracef


@tracef("CLI")
def fndCliParse(mysArglist):
    ''' Parse the mandatory and optional positional arguments, and the 
        many options for this run from the command line.  
        Return a dictionary of all of them.  Strictly speaking that is 
        not necessary, since most of them have already been decanted
        into the P params object.  
    '''
    cParse = argparse.ArgumentParser(description="Digital Library Preservation Simulation, Question 2",epilog="Defaults for args as follows:\n\
        simlen=100 Khrs,\n\
        seed=1, \
        shortlog=N, loglevel=NOTSET, \
        audit=0 (off), bandwidth=10Mbps \
        logfile=stdout", version=sVersion)
    
    # P O S I T I O N A L  arguments
    #cParse.add_argument('--something', type=, dest='', metavar='', help='')

    cParse.add_argument('sFamilydir', type=str
                        , metavar='sFAMILYDIR'
                        , help='Family directory for test parameter files'
                        )

    cParse.add_argument('sSpecificdir', type=str
                        , nargs="?"
                        , metavar='sSPECIFICDIR'
                        , help='Specific dir below Family dir for overriding parameter files, "." for none'
                        )

    cParse.add_argument("nSimLength", type=int
                        , nargs="?"
                        , metavar='nSIMLENGTH'
                        , help="Length of simulation in kilo-hours"
                        )

    cParse.add_argument("nRandomSeed",type=int
                        , nargs="?"
                        , metavar='nRANDOMSEED'
                        , help='Seed for random number generator, 0=use system clock'
                        )

    # - - O P T I O N S

    cParse.add_argument("--ncopies", type=int
                        , dest='lCopies'
                        , metavar='nCOPIES'
                        , nargs='*'
                        , help='Number of copies to make (for value types from 1 up to 5), 0=no change'
                        )

    cParse.add_argument("--lifek", "--lifetimekhours", type=int
                        , dest='lBER'
                        , metavar='nLIFEK'
                        , nargs='*'
                        , help='Sector mean lifetimes for storage shelf (types from 1 up to 5) in kilo-hours, 0=no change'
                        )

    cParse.add_argument("--shelfsize", type=int
                        , dest='lShelfSize'
                        , metavar='nShelfSize'
                        , nargs='*'
                        , help='Size(s) for storage shelf (types from 1 up to 5) in TB, 0=no change'
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

    cParse.add_argument('--shortlog', type=str
                        , dest='sShortLogStr'
                        , choices=['Y','N']
                        , help='Log no detailed info for this run, params and results only.'
                        )

    cParse.add_argument('--smalldoc', type=int
                        , dest='nDocSmall'
                        , metavar='nDOCSML'
                        , help='Size MB of small docs in mix'
                        )

    cParse.add_argument('--largedoc', type=int
                        , dest='nDocLarge'
                        , metavar='nDOCLRG'
                        , help='Size MB of large docs in mix'
                        )

    cParse.add_argument('--pctsmall', '--pctsmalldoc', type=int
                        , dest='nDocSmallPct'
                        , metavar='nDOCSMLPCT'
                        , help='Percentage of small docs in mix'
                        )

    cParse.add_argument('--pctdocvar', type=int
                        , dest='nDocPctSdev'
                        , metavar='nDOCPCTVAR'
                        , help='For doc size distribution, std dev is what percentage of mean'
                        )
    
    cParse.add_argument("--audit", type=int
                        , dest='nAuditCycleInterval'
                        , metavar='nAUDITCYCLEINTERVAL'
                        , help='Hours between auditing cycles; zero=none.'
                        )

    cParse.add_argument("--audittype", type=str
                        , dest='sAuditStrategy'
                        , choices=['SYSTEMATIC','UNIFORM','ZIPF']
#                        , metavar='sAUDITSTRATEGY'
                        , help='Strategy for auditing, default=SYSTEMATIC.'
                        )

    cParse.add_argument("--auditsegments", type=int
                        , dest='nAuditSegments'
                        , metavar='nAUDITSEGMENTS'
                        , help='Number of subsamples per audit cycle, default=1.'
                        )

    cParse.add_argument("--auditbins", type=int
                        , dest='nAuditZipfBins' 
                        , metavar='nAUDITZIPFBINS'
                        , help='Number of doc bins for Zipf frequency-based audits, default=5.'
                        )

    cParse.add_argument("--bandwidth", type=int
                        , dest='nBandwidthMbps'
                        , metavar='nBANDWIDTHMbps'
                        , help='Auditing/repair bandwidth in Mbps (mega-*bits* per second).'
                        )

    if mysArglist:          # If there is a specific string, use it.
        (xx) = cParse.parse_args(mysArglist)
    else:                   # If no string, then parse from argv[].
        (xx) = cParse.parse_args()

    return vars(xx)

# Moved all the data overwriting back to main.  Just return dictionary of 
# params found on command line.  

# END
