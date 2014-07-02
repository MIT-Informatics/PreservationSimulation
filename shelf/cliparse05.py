#!/usr/bin/python
# cliparse.py
# Parse CLI args with the argparse package and stuff the results 
# into the Params.  
# Recovered, we hope, after commit/delete screw-up.  

sVersion = "0.0.2"
import argparse
from globaldata import *
from NewTraceFac import TRC,trace,tracef


@tracef("CLI")
def fndCliParse(mysArglist):
    ''' Parse the mandatory and optional positional arguments, and the 
        many options for this run from the command line.  
        Return a dictionary of all of them.  Strictly speaking that is 
        not necessary, since most of them have already been decanted
        into the P params object.  
    '''
    cParse = argparse.ArgumentParser(description="Digital Library Preservation Simulation, Question 0",epilog="Defaults for args as follows:\n\
        simlen=100 Khrs,\n\
        seed=1, \
        shortlog=N, loglevel=NOTSET, \
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

    cParse.add_argument("--ber", "--blockerrrate", type=int
                        , dest='lBER'
                        , metavar='nBER'
                        , nargs='*'
                        , help='Block error rate(s) for storage shelf (types from 1 up to 5) in kilo-hours, 0=no change'
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
                        , help='Log file for output, - or absent for stdout'
                        )

    cParse.add_argument('--shortlog', type=str
                        , dest='sShortLogStr'
                        , choices=['Y','N']
                        , help='Log no detailed info for this run, params and results only.'
                        )

    cParse.add_argument('--smalldoc', type=int, dest='nDocSmall', 
                        metavar='nDOCSML'
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
    
    if mysArglist:          # If there is a specific string, use it.
        (xx) = cParse.parse_args(mysArglist)
    else:                   # If no string, then parse from argv[].
        (xx) = cParse.parse_args()

    return vars(xx)

# Moved all the data overwriting back to main.  Just return dictionary of 
# params found on command line.  

# END
