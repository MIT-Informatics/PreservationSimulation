#!/usr/bin/python
# cliparse.py
# Parse CLI args with the argparse package and stuff the results 
# into the Params.  

sVersion = "0.0.1"
import argparse
from globaldata import *
from NewTraceFac import TRC,trace,tracef


@tracef("CLI")
def fnCliParse(mysArglist):
    cParse = argparse.ArgumentParser(prog='myTEST1',description="test1 of argparse lib",epilog="Defaults for args as follows:\n\
        simlen=100 khrs,\n\
        seed=1, \
        loglevel=NOTSET, \
        logfile=stdout, \
        family=.", version=sVersion)
    
    #cParse.add_argument('--something', type=, dest='', metavar='', help='')
    cParse.add_argument('sFamilydir', type=str, metavar='sFAMILYDIR', help='Family directory for test parameter files')
    cParse.add_argument('sSpecificdir', type=str, nargs="?", metavar='sSPECIFICDIR', help='Specific dir below Family dir for overriding parameter files')
    cParse.add_argument("nSimlength", type=int, nargs="?", metavar='nSIMLENGTH', help="Length of simulation in kilo-hours")
    cParse.add_argument("nRandomseed",type=int, nargs="?", metavar='nRANDOMSEED', help='Seed for random number generator, 0=use system clock')

    cParse.add_argument("--ncopies", type=int, dest='lCopies', metavar='nCOPIES', nargs='*', help='Number of copies to make (for value types from 1 up to 5), 0=no change')
    cParse.add_argument("--ber", "--blockerrrate", type=int, dest='lBER', metavar='nBER', nargs='*', help='Block error rate(s) for storage shelf (types from 1 up to 5) in kilo-hours, 0=no change')
    cParse.add_argument('--loglevel', type=str, dest='sLogLevel', choices=['INFO','DEBUG'], help='Logging level for this run')
    cParse.add_argument('--logfile', type=str, dest='sLogFile', metavar='sLOGFILE', help='Log file for output, - or absent for stdout')
    cParse.add_argument('--smalldoc', type=int, dest='nDocSmall', metavar='nDOCSML', help='Size MB of small docs in mix')
    cParse.add_argument('--largedoc', type=int, dest='nDocLarge', metavar='nDOCLRG', help='Size MB of large docs in mix')
    cParse.add_argument('--pctsmall', '--pctsmalldoc', type=int, dest='nDocSmallPct', metavar='nDOCSMLPCT', help='Percentage of small docs in mix')
    cParse.add_argument('--pctdocvar', type=int, dest='nDocPctSdev', metavar='nDOCPCTVAR', help='For doc size distribution, std dev is what percentage of mean')
    
    (xx) = cParse.parse_args(mysArglist)
    
    if xx.sFamilydir:       P.sFamilydir = xx.sFamilydir
    if xx.sSpecificdir:     P.sSpecificdir = xx.sSpecificdir
    if xx.nSimlength:       P.nSimlength = xx.nSimlength
    if xx.nRandomseed:      P.nRandomseed = xx.nRandomseed
    if xx.lBER:             P.lBER = xx.lBER
    if xx.lCopies:          P.lCopies = xx.lCopies
    if xx.sLogLevel:        P.sLogLevel = xx.sLogLevel
    if xx.sLogFile:         P.sLogFile = xx.sLogFile
    if xx.nDocSmall:        P.nDocSmall = xx.nDocSmall
    if xx.nDocLarge:        P.nDocLarge = xx.nDocLarge
    if xx.nDocSmallPct:     P.nDocSmall = xx.nDocSmallPct
    if xx.nDocPctSdev:      P.nDocPctSdev = xx.nDocPctSdev

    return vars(xx)
