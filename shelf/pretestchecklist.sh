#!/bin/bash
# pretestchecklist.sh

# Check that all directories and files are in place for a run.  
# familydir required, but specific defaults to .
# 

if [ -z "$1" -o "$1" == "-h" -o "$1" == "--help" ]
then 
    echo "Usage: $0 [<familydir> [<specificdir>]]"
    echo "<specificdir> defaults to ."
    echo "Must be run from shelf dir."
    exit 1
fi

# Where the files should go for this generation.
sFamilyDir="$1"
if [ -z "$2" ] 
then
    sSpecificDir=.
else
    sSpecificDir="$2"
fi
sShelfDir=.
sInstructionDir=$sShelfDir/instructions

# Check all the important directories.
for needdir in $sFamilyDir $sFamilyDir/$sSpecificDir $sFamilyDir/$sSpecificDir/cmd $sFamilyDir/$sSpecificDir/act $sFamilyDir/$sSpecificDir/log $sFamilyDir/$sSpecificDir/ext $sFamilyDir/$sSpecificDir/dat  
do
    if [ ! -d "$needdir" ]
    then
        echo "Error: missing directory $needdir"
        exit 1
    fi
done

# Is there a root file for the giant output to build on?
if [ ! -f "$sFamilyDir/$sSpecificDir/dat/GiantOutput_00.txt" ]
then
    echo "Error: missing file $sFamilyDir/$sSpecificDir/dat/GiantOutput_00.txt"
    exit 1
else
    filesize=$(cat "$sFamilyDir/$sSpecificDir/dat/GiantOutput_00.txt" | wc -l)
    if [ "$filesize" -gt 1 ]
    then
        echo "Warning: Output data file may contain stale data: $sFamilyDir/$sSpecificDir/dat/GiantOutput_00.txt"
    fi 
fi

# Do we have all the instruction files?
sTargetDir="$sInstructionDir"
for needfile in simlen.ins3 glitchignorelevel.ins3 audittype.ins3 auditsegments.ins3 docsize.ins3 shelfsize.ins3 glitchmaxlife.ins3 glitchimpact.ins3 glitchfreq.ins3 glitchdecay.ins3 glitchspan.ins3 auditfreq.ins3 lifem.ins3 ncopies.ins3  
do
    if [ ! -f "$sTargetDir/$needfile" ]
    then
        echo "Error: missing important file $sTargetDir/$needfile"
        exit 1
    fi
done

# Do we have the db manipulation files?
sTargetDir="$sShelfDir"
for needfile in dbclearcollection.py dbdumpcollection.py dbdumpdonekeys.py mongolib.py searchspace.py searchdatabase.py searchdatabasemongo.py NewTraceFac.py 
do
    if [ ! -f "$sTargetDir/$needfile" ]
    then
        echo "Error: missing important file $sTargetDir/$needfile"
        exit 1
    fi
done


# Do we have all the execution files?
sTargetDir="$sShelfDir"
for needfile in broker.py brokercli.py catchex.py NewTraceFac.py brokercommandlist.txt client2.py cliparse.py main.py command.py fib.py extractvalues2.py hl-extractinstructions.txt datacleanup.py lifetime.py listactor.py 
do
    if [ ! -f "$sTargetDir/$needfile" ]
    then
        echo "Error: missing important file $sTargetDir/$needfile"
        exit 1
    fi
done

# Do we have all the simulation files?
sTargetDir="$sShelfDir"
for needfile in audit2.py client2.py cliparse.py collection.py command.py doccopy.py document.py dumpparams.py dumpuse.py getcliargs.py getparams.py globaldata.py logoutput.py main.py catchex.py NewTraceFac.py logoutput.py readin.py repair.py server.py shelf.py shock.py util.py 
do
    if [ ! -f "$needfile" ]
    then
        echo "Error: missing important file $needfile"
        exit 1
    fi
done

# Is mongod running?
count=$(ps | grep "mongod" | wc -l)
if [ -z "$count" ]
then
    echo "MongoDB daemon mongod does not appear to be running."
    exit 1
fi

# Are there leftover files in the execution directories?  Should be empty.
sTargetDir="$sFamilyDir/$sSpecificDir"
for needemptydir in act cmd ext log
do 
    filecount=$(ls $sTargetDir/$needemptydir | wc -l)
    if [ $filecount -gt 0 ] 
    then
        echo "Run directory is not empty: $sTargetDir/$needemptydir"
        exit 1
    fi
done



echo "Looks okay!"
#END