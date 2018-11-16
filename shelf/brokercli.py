#!/usr/bin/python
# brokercli.py
# CLI processing for broker.py


import argparse
from NewTraceFac import NTRC, ntrace, ntracef


@ntracef("CLI")
def fndCliParse(mysArglist):
    ''' Parse the mandatory and optional positional arguments, and the 
         many options for this run from the command line.  
        Return a dictionary of all of them.  
    '''
    sVersion = "0.0.9"
    cParse = argparse.ArgumentParser(
        description="Digital Library Preservation Simulation "
        "Instruction Broker CLI "
        "v"+sVersion+"  "
        "For each selection variable, enter either a value "
        "or a MongoDB dictionary spec " 
        "that is a valid JSON dictionary string.  \n" 
        "Note that special characters such as $ { } must be escaped "
        "or single-quoted to protect them from the shell.  " 
        "" 
        ""
        ,epilog="Defaults for args as follows: (none)\n"
        )
    
    # P O S I T I O N A L  arguments
    #cParse.add_argument('--something', type=, dest='', metavar='', help='')

    cParse.add_argument('sSearchDbProgressCollectionName', type=str
                        , metavar='sPROGRESSCOLLECTIONNAME'
                        , help='Collection name within the search database '
                        'of the instructions in progress for this broker run.'
                        )

    cParse.add_argument('sSearchDbDoneCollectionName', type=str
                        , metavar='sDONECOLLECTIONNAME'
                        , help='Collection name within the database '
                        'of the instructions that have been completed.'
                        )

    # - - O P T I O N S

    cParse.add_argument("--ncopies", type=str
                        , dest='nCopies'
                        , metavar='nCOPIES'
                        , nargs='?'
                        , help='Number of copies in session.'
                        )

    cParse.add_argument("--lifem", "--lifetimemegahours", type=str
                        , dest='nLifem'
                        , metavar='nLIFE_Mhrs'
                        , nargs='?'
                        , help='Sector mean lifetime for storage shelf.'
                        )

    cParse.add_argument("--auditfreq", type=str
                        , dest='nAuditFreq'
                        , metavar='nAUDITCYCLEINTERVAL_hrs'
                        , nargs='?'
                        , help='Hours between auditing cycles; zero=no auditing.'
                        )

    cParse.add_argument("--audittype", type=str
                        , dest='sAuditType'
                        #, choices=['TOTAL','OFF']
                        , nargs='?'
                        , help='Strategy for auditing, default=TOTAL.'
                        )

    cParse.add_argument("--auditsegments", type=str
                        , dest='nAuditSegments'
                        , metavar='nAUDITSEGMENTS'
                        , nargs='?'
                        , help='Number of subsamples per audit cycle, default=1.'
                        )

    cParse.add_argument("--glitchfreq", type=str
                        , dest='nGlitchFreq'
                        , metavar='nGLITCHFREQ_hrs'
                        , nargs='?'
                        , help='Half-life of intervals between glitches; '
                        '0=never happens.'
                        )

    cParse.add_argument("--glitchimpact", type=str
                        , dest='nGlitchImpact'
                        , metavar='nGLITCHIMPACT_pct'
                        , nargs='?'
                        , help='Percent reduction in sector lifetime due to '
                        'glitch; 100%%=fatal to shelf.'
                        )

    cParse.add_argument("--glitchdecay", type=str
                        , dest='nGlitchDecay'
                        , metavar='nGLITCHDECAY_hrs'
                        , nargs='?'
                        , help='Half-life of glitch impact exponential decay; '
                        'zero=infinity.'
                        )

    cParse.add_argument("--glitchspan", type=str
                        , dest='nGlitchSpan'
                        , metavar='nGLITCHSPAN'
                        , nargs='?'
                        , help='Number of servers affected by a glitch; '
                        'default=1.'
                        )

    cParse.add_argument("--glitchmaxlife", type=str
                        , dest='nGlitchMaxlife'
                        , metavar='nGLITCHMAXLIFE_hrs'
                        , nargs='?'
                        , help='Maximum duration of glitch impact, '
                        'which ceases after this interval; zero=infinity.'
                        )

    cParse.add_argument("--shockfreq", type=str
                        , dest='nShockFreq'
                        , metavar='nSHOCKFREQ_hrs'
                        , nargs='?'
                        , help='Half-life of intervals between economic '
                        'slumps; 0=never happens.'
                        )

    cParse.add_argument("--shockimpact", type=str
                        , dest='nShockImpact'
                        , metavar='nSHOCKIMPACT_pct'
                        , nargs='?'
                        , help='Percent reduction in sector lifetime due to '
                        'slump; 100%%=fatal to shelf.'
                        )

    cParse.add_argument("--shockspan", type=str
                        , dest='nShockSpan'
                        , metavar='nSHOCKSPAN_nservers'
                        , nargs='?'
                        , help='Number of servers affected by slump.'
                        )

    cParse.add_argument("--shockmaxlife", type=str
                        , dest='nShockMaxlife'
                        , metavar='nSHOCKMAXLIFE_hrs'
                        , nargs='?'
                        , help='Maximum duration of shock impact, '
                        'which ceases after this interval; zero=infinity.'
                        )

    cParse.add_argument("--serverdefaultlife", type=str
                        , dest='nServerDefaultLife'
                        , metavar='nSERVERDEFAULTLIFE_hrs'
                        , nargs='?'
                        , help='Half life of distribution from which servers\' '
                        'lifespans are drawn at birth; zero=infinity.  Shocks '
                        'reduce these lifespans.  '
                        )

    cParse.add_argument("--nseeds", type=str
                        , dest='nRandomSeeds'
                        , metavar='nRANDOMSEEDS'
                        , nargs='?'
                        , help='Number of random seeds to be used for  '
                        'repeated trials of each parameter setup.  '
                        'Range 1 to 1000.'
                        )

    cParse.add_argument("--simlen", type=str
                        , dest='nSimLength'
                        , metavar='nSIMULATIONLENGTH'
                        , nargs='?'
                        , help='Length of simulated time in hours.  '
                        'One year=10,000 hours; '
                        'ten years (default) = 100,000 hours.  '
                        )

    cParse.add_argument("--shelfsize", type=str
                        , dest='nShelfSize'
                        , metavar='nSHELFSIZE_TB'
                        , nargs='?'
                        , help='Size for storage shelf in TB.'
                        )
   
    cParse.add_argument("--docsize", type=str
                        , dest='nDocSize'
                        , metavar='nDOCSIZE_MB'
                        , nargs='?'
                        , help='Document size in MB.'
                        )
    
    cParse.add_argument("--ndocuments", type=str
                        , dest='nDocuments'
                        , metavar='nDOCUMENTS'
                        , nargs='?'
                        , help='Number of documents in a collection.  '
                        )
    
# Other options that are not used for selection, but for overrides or testing.

    cParse.add_argument("--familydir", type=str
                        , dest='sFamilyDir'
                        , metavar='sFAMILYDIR'
                        , nargs='?'
                        , required=True
                        , help='Family directory for param and log files.'
                        )
    
    cParse.add_argument("--specificdir", type=str
                        , dest='sSpecificDir'
                        , metavar='sSPECIFICDIR'
                        , nargs='?'
                        , required=True
                        , help='Specific directory for param and log files.'
                        )
    
    cParse.add_argument("--testlimit", type=str
                        , dest='nTestLimit'
                        , metavar='nTESTLIMIT'
                        , nargs='?'
                        , help='TESTING ONLY: limit on number of runs to execute.  Each case is executed nseeds number of times.'
                        )
    
    cParse.add_argument("--testcommand"
                        , action='store_const', const="Y"
                        , dest='sTestCommand'
                        , help='TESTING ONLY: echo formatted commands only, '
                        'not execute.'
                        )
    
    cParse.add_argument("--testfib"
                        , action='store_const', const="Y"
                        , dest='sTestFib'
                        , help='TESTING ONLY: use fako Fibonacci '
                        'CPU intensive process instead of real stuff.'
                        )

    cParse.add_argument("--shortlog"
                        , action='store_const', const="Y"
                        , dest='sShortLog'
                        , help='Log only begin setup and end results, '
                        ' not all the error info in the middle.  '
                        )

    cParse.add_argument("--listonly"
                        , action='store_const', const="Y"
                        , dest='sListOnly'
                        , help='List all chosen cases to stdout.  '
                        'Do nothing else.'
                        )

    cParse.add_argument("--redo"
                        , action='store_const', const="Y"
                        , dest='sRedo'
                        , help='Force these cases to be redone, even if '
                        'they have been done before.'
                        )

    cParse.add_argument("--coretimer", type=str
                        , dest='nCoreTimer'
                        , metavar='nCORETIMER_msec'
                        , nargs='?'
                        , help='Time (msec) to wait for a core to '
                        'come available for computing.  '
                        'Range 10 to 1000 or so.  '
                        'Set high for long jobs, low for shocks.  '
                        )

    cParse.add_argument("--stucklimit", type=str
                        , dest='nStuckLimit'
                        , metavar='nSTUCKLIMIT'
                        , nargs='?'
                        , help='Number of times to wait (for nCoreTimer msec) '
                        'for a computing core to '
                        'come available.  '
                        'Set high for long jobs.  '
                        )

    if mysArglist:          # If there is a specific string, use it.
        xx = cParse.parse_args(mysArglist)
    else:                   # If no string, then parse from argv[].
        xx = cParse.parse_args()
    NTRC.ntracef(3, "BCLI", "proc namespace xx|%s|" % (xx))
    dxx = vars(xx)
    NTRC.ntracef(3, "BCLI", "proc dict-var dxx|%s|" % (dxx))
    dxx1 = {k : (v.replace('u"', '"') 
                    if (v is not None) 
                        and ('{' in v) and ('}' in v) 
                        and ('u"' in v) 
                    else v
                )
            for k, v in dxx.items()}
    return dxx1

# Edit history:
# 20170124  RBL Original version, removed from broker.py for legibility.  
# 20170127  RBL Add --shortlog, which somehow was forgotten long ago.
# 20180408  RBL Add --simlen option to catch simulation length from form
#                and pass it to main.py.  
# 20181111  RBL Add --coretimer and --stucklimit options to adjust time
#                constants for newbroker.  
# 
# 

#END
