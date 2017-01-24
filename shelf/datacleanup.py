#!/usr/bin/python
# datacleanup.py

import  argparse
import  os
import  re
import  time
import  json
from    NewTraceFac     import NTRC,ntrace,ntracef
import  mongolib
import  csv
import  searchdatabase


@ntracef("CLI")
def fndCliParse(mysArglist):
    ''' Parse the mandatory and optional positional arguments, and the 
         many options for this run from the command line.  
        Return a dictionary of all of them.  
    '''
    sVersion = "0.0.2"
    cParse = argparse.ArgumentParser(description="Digital Library Preservation "+
        "Simulation DataCleanup, CLI v"+sVersion+"  "+
        "Process a file with the (single-line plus header line) results of a " + 
        "simulation run.  Add the result to the done collection of the database" +
        "(if not already there), append the single line to the giant output file," +
        "and then delete the input file so we don't bother to look at it again." +
        "" 
        , epilog="Defaults for args as follows: separator=blank, \n"
        , version=sVersion)
    
    # P O S I T I O N A L  arguments
    #cParse.add_argument('--something', type=, dest='', metavar='', help='')

    cParse.add_argument('sProgressCollectionName', type=str
                        , metavar='sPROGRESSCOLLECTIONNAME'
                        , help='Collection name in database of instructions '
                                'being processed.'
                        )

    cParse.add_argument('sDoneCollectionName', type=str
                        , metavar='sDONECOLLECTIONNAME'
                        , help='Collection name in database of instructions '
                                'that have been completed.'
                        )

    cParse.add_argument("sInputFilename", type=str
                        , metavar='sINPUTFILENAME'
                        , help='Input file containing output of a single '
                                'simulation run as one huge header line '
                                'and data line.'
                        )
        
    cParse.add_argument("sGiantOutputFilename", type=str
                        , metavar='sGIANTOUTPUTFILENAME'
                        , help='Giant output file to which we append '
                                'one line for each input file that is '
                                'processed (and was not previously done).'
                        )
        
    # - - O P T I O N S

    cParse.add_argument("--separator", type=str
                        , dest='sSeparator'
                        , metavar='sSEPARATORCHAR'
                        , nargs='?'
                        , help='Single-character separator for the '
                                'sort-of-CSV input file, and for appending '
                                'to the giant ouptput file.'
                        )
    
    # Other options that are not used for selection, 
    #  but only for overrides or testing.

    cParse.add_argument("--donotdelete", type=str
                        , dest='sDoNotDelete'
                        , choices=['YES','Y','NO','N']
                        , nargs='?'
                        , help='TESTING ONLY: do not delete the '
                                'input file after processing.'
                        )
    
    cParse.add_argument("--donotrecord", type=str
                        , dest='sDoNotRecord'
                        , choices=['YES','Y','NO','N']
                        , nargs='?'
                        , help='TESTING ONLY: do not record the line '
                                'in the done collection of the database.'
                        )

    if mysArglist:          # If there is a specific string, use it.
        (xx) = cParse.parse_args(mysArglist)
    else:                   # If no string, then parse from argv[].
        (xx) = cParse.parse_args()

    return vars(xx)


# class   C G   f o r   g l o b a l   d a t a 
class CG(object):
    ''' Global data.
    '''
    nTestLimit = 0          # max nr of runs for a test run, 0=infinite
    sTestCommand = "NO"     # just echo commands instead of executing them?

    sFamilyDir = '../q3'
    sSpecificDir = '.'

    # SearchDatabase info
    sSearchDbFile = "./searchspacedb/searchdb.json"
    sdb = None              # Instance of SearchDatabase to use
    sDoneCollectionName = None
    sProgressCollectionName = None

    sSeparator = ' '        # CSV-ish separator for input and output files.
    sInputFilename = None
    sGiantOutputFilename = None
    sDoNotDelete = "N"
    sDoNotRecord = "N"

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
@ntracef("DCLN")
def main():
    '''
    Process:
    Open the file given on the command line.
    Open the database given on the command line.
    Read the two lines from the file.
    If the sDoneId(=mongoid) already appears in the done collection 
     of the database, 
    Then    end.
    Else    dictionary-ify the data (maybe csvreader already did that for us).
            add the dict to the done collection, including the sDoneId field.
            end.
    '''
    NTRC.ntracef(0,"DCLN","datacleanup Begin.")
    # Get args from CLI and put them into the global data
    dCliDict = fndCliParse("")
    # Carefully insert any new CLI values into the Global object.
    dCliDictClean = {k:v for k,v in dCliDict.items() if v is not None}
    g.__dict__.update(dCliDictClean)

    # Get data from the extract file: one line of header, one line of data.
    with open(g.sInputFilename,'r') as fhInput:
        oReader = csv.reader(fhInput, delimiter=g.sSeparator)
        lHeader = oReader.next()
        lValues = oReader.next()
        NTRC.tracef(3, "DCLN", "proc lHeader|%s|" % (lHeader))
        NTRC.tracef(3, "DCLN", "proc lValues|%s|" % (lValues))
    dValues = dict(zip(lHeader, lValues))
    NTRC.tracef(3, "DCLN", "proc dValues|%s|" % (dValues))
    
    # Open the SearchDatabase for done and progress records.
    g.sdb = searchdatabase.CSearchDatabase(g.sSearchDbFile, 
            g.sProgressCollectionName, 
            g.sDoneCollectionName)
    # Construct database query for this invocation.  
    sInstructionId = dValues["mongoid"]
    sLineOut = g.sSeparator.join(lValues)
    NTRC.tracef(0,"DCLN","proc looking for done recd|%s|" 
        % (sInstructionId))
    # Is this extract already stored in the database?
    bIsItDone = g.sdb.fnbIsItDone(sInstructionId)
    if not bIsItDone:
        # Always add a line of data to the giant output file.
        NTRC.tracef(0, "DCLN", "proc line appended to output \nsLineOut|%s|" 
            % (sLineOut))
        with open(g.sGiantOutputFilename,'a') as fhOutput:
            fhOutput.write(sLineOut + "\n")
            NTRC.tracef(3, "DCLN", "proc wroteline|%s|" 
                % (sLineOut))

        # Maybe record the done record in db.
        if g.sDoNotRecord.startswith("Y"):
            NTRC.tracef(0, "DCLN", "proc Done not recorded.")
        else:
            dResult = g.sdb.fndInsertDoneRecord(sInstructionId, dValues)

        # Maybe delete the extract file.
        if g.sDoNotDelete.startswith("Y"):
            NTRC.tracef(0, "DCLN", "proc Input file not deleted.")
        else:
            os.remove(g.sInputFilename)
            NTRC.tracef(3,"DCLN", "proc fileremoved|%s|" 
                % (g.sInputFilename))
            # And remove its in-progress record from the search db.
            g.sdb.fndDeleteProgressRecord(sInstructionId)
    else:
        # Duplicate instruction; do not add line to output file.
        NTRC.tracef(0, "DCLN", "proc line NOT appended to output file \n"
            "sLineOut|%s|" 
            % (sLineOut))

    NTRC.ntracef(0,"DCLN","datacleanup End.")


# E n t r y   p o i n t . 
if __name__ == "__main__":
    g = CG()
    main()

# Edit history:
# 2016xxxx  RBL Original version.
# 20170121  RBL Adapt to new searchdatabasae to hold done and progress records.
# 20170124  RBL Change ntrace facility name to DCLN to make some post-process
#                bug-checking easier.  
# 


#END

'''

cleaner:
foreach two-line extract file in holding dir
  append data line to combined results file
    if it has not already been done
  add _id to done tbl of db
  delete one-liner
  delete progress record
'''
