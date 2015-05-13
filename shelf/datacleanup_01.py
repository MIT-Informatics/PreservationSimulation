#!/usr/bin/python
# datacleanup.py

import  argparse
import  os
import  re
import  time
import  json
from    NewTraceFac     import NTRC,ntrace,ntracef
#import  mongolib
import  csv


@ntracef("CLI")
def fndCliParse(mysArglist):
    ''' Parse the mandatory and optional positional arguments, and the 
         many options for this run from the command line.  
        Return a dictionary of all of them.  
    '''
    sVersion = "0.0.1"
    cParse = argparse.ArgumentParser(description="Digital Library Preservation Simulation Instruction Broker CLI v"+sVersion+"  "+
        "Process a file with the (single-line plus header line) results of a .  " + 
        "simulation run.  Add the result to the done collection of the database" +
        "(if not already done), append the single line to the giant output file," +
        "and then delete the input file so we don't bother to look at it again." +
        "" 
        , epilog="Defaults for args as follows: separator=blank, \n"
        , version=sVersion)
    
    # P O S I T I O N A L  arguments
    #cParse.add_argument('--something', type=, dest='', metavar='', help='')

    cParse.add_argument('sDatabaseName', type=str
                        , metavar='sDATABASENAME'
                        , help='Name of MongoDB database that pymongo will find.'
                        )

    cParse.add_argument('sDoneCollectionName', type=str
                        , metavar='sDONECOLLECTIONNAME'
                        , help='Collection name within the database of the instructions that have been completed.'
                        )

    cParse.add_argument("sInputFilename", type=str
                        , metavar='sINPUTFILENAME'
                        , help='Input file containing output of a single simulation run as one huge header line and data line.'
                        )
        
    cParse.add_argument("sGiantOutputFilename", type=str
                        , metavar='sGIANTOUTPUTFILENAME'
                        , help='Giant output file to which we append one line for each input file that is processed (and was not previously done).'
                        )
        
    # - - O P T I O N S

    cParse.add_argument("--separator", type=str
                        , dest='sSeparator'
                        , metavar='sSEPARATORCHAR'
                        , nargs='?'
                        , help='Single-character separator for the sort-of-CSV input file, and for appending to the giant ouptput file.'
                        )
    
    # Other options that are not used for selection, but for overrides or testing.

    cParse.add_argument("--donotdelete", type=str
                        , dest='sDoNotDelete'
                        , choices=['YES','Y','NO','N']
                        , nargs='?'
                        , help='TESTING ONLY: do not delete the input file after processing.'
                        )
    

    if mysArglist:          # If there is a specific string, use it.
        (xx) = cParse.parse_args(mysArglist)
    else:                   # If no string, then parse from argv[].
        (xx) = cParse.parse_args()

    return vars(xx)

# f n M a y b e O v e r r i d e 
@ntracef("CLI")
def fnMaybeOverride(mysCliArg,mydDict,mycClass):
    ''' Strange function to override a property in a global dictionary
        if there is a version in the command line dictionary.  
    '''
    try:
        if mydDict[mysCliArg]:
            setattr( mycClass, mysCliArg, mydDict[mysCliArg] )
    except KeyError:
            if not getattr(mycClass, mysCliArg, None):
                setattr(mycClass, mysCliArg, None)
    return getattr(mycClass, mysCliArg, "XXXXX")

# f n I n t P l e a s e 
@ntracef("INT",level=5)
def fnIntPlease(myString):
    # If it looks like an integer, make it one.
    try:
        return int(myString)
    except ValueError:
        return myString


# class   C G   f o r   g l o b a l   d a t a 
class CG(object):
    ''' Global data.
    '''
    nTestLimit = 0          # max nr of runs for a test run, 0=infinite
    sTestCommand = "NO"     # should just echo commands instead of executing them?

    sFamilyDir = '../q3'
    sSpecificDir = '.'

    sDatabaseName = None
    sDoneCollectionName = None

    sSeparator = ' '        # CSV-ish separator for input and output files.
    sInputFilename = None
    sGiantOutputFilename = None
    sDoNotDelete = "N"

    '''
    Directory structure under the family/specific dir:
    cmd - command files for the listactor program
    log - log file output from the main simulation runs
    act - little bitty log files from the listactor program
    ext - the single line (plus heading) extracts from the log files
    dat - the combined output from appending all the extract files (less 
          redundant headers)
    '''


# M A I N 
@ntracef("MAIN")
def main():
    '''
    Process:
    Open the file given on the command line.
    Open the database given on the command line.
    Read the two lines from the file.
    If the mongoid appears in the done collection of the database, 
     then   end.
    Else    dictionary-ify the data (maybe csvreader already did that for us).
            add the dict to the done collection.
            end.
    
    '''
    NTRC.ntracef(0,"MAIN","Begin.")
    # Get args from CLI and put them into the global data
    dCliDict = fndCliParse("")
    # Carefully insert any new CLI values into the Global object.
    fnMaybeOverride("sDatabaseName", dCliDict, g)
    fnMaybeOverride("sDoneCollectionName", dCliDict, g)
    fnMaybeOverride("sInputFilename", dCliDict, g)

    NTRC.tracef(0,"MAIN","proc querydict|%s|" % ((dQuery)))
    # Query pending instructions to get subset of work for today.
    oDb = mongolib.fnoOpenDb(g.sDatabaseName)
    oDoneCollection = oDb[g.sDoneCollectionName]

    # Construct database query for this invocation.
    with open(g.sInputFilename,'r') as fhInput:
        oReader = csv.reader(fhInput, delimiter=g.sSeparator)
        lHeader = oReader.next()
        lValues = oReader.next()
    dValues = dict(zip(lHeader, lValues))
    dQuery = {"mongoid" : dValues["mongoid"]}

    lMatches = list(oDoneCollection.find(dQuery))
    NTRC.ntracef(0,"MAIN","proc main lMatches|{}|".format(lMatches))
    if len(lMatches) > 0:
        oDoneCollection.write(dValues)
        with open(g.sGiantOutputFile,'a') as fhOutput:
            fhOutput.write(g.sSeparator.join(lValues))
        os.remove(g.sInputFilename)

    NTRC.ntracef(0,"MAIN","End.")


#
# E n t r y   p o i n t . 
if __name__ == "__main__":
    g = CG()
    main()

#END

'''

cleaner:
poll every, oh, minute or so
foreach log file in some holding dir
  move log file to its permanent home
foreach single-line file in holding dir
  append line to combined results file
  add _id to done tbl of db
  delete one-liner

'''
