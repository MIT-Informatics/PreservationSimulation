#!/bin/sh
# q3-pretestchecklist.sh

# Check that all directories and files are in place for a run.  
# 

# Where the files should go for this generation.
sFamilyDir="../q3"
sSpecificDir=.
sShelfDir=.
sInstructionDir=$sShelfDir/newinstructions

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
for needfile in makecompletetemplate.sh substituteall.sh expandtemplate.py mongolib.py NewTraceFac.py q3instructiontemplate.txt 
do
    if [ ! -f "$sTargetDir/$needfile" ]
    then
        echo "Error: missing important file $sTargetDir/$needfile"
        exit 1
    fi
done
sTargetDir="$sInstructionDir/ins"
for needfile in simlen.ins glitchignorelevel.ins audittype.ins auditsegments.ins docsize.ins shelfsize.ins glitchmaxlife.ins glitchimpact.ins glitchfreq.ins glitchdecay.ins auditfreq.ins lifem.ins ncopies.ins randomseed.ins 
do
    if [ ! -f "$sTargetDir/$needfile" ]
    then
        echo "Error: missing important file $sTargetDir/$needfile"
        exit 1
    fi
done

# Do we have the db manipulation files?
sTargetDir="$sShelfDir"
for needfile in dbclearcollection.py dbdumpcollection.py mongolib.py NewTraceFac.py 
do
    if [ ! -f "$sTargetDir/$needfile" ]
    then
        echo "Error: missing important file $sTargetDir/$needfile"
        exit 1
    fi
done


# Do we have all the execution files?
sTargetDir="$sShelfDir"
for needfile in broker.py NewTraceFac.py brokercommandlist.txt mongolib.py main.py fib.py extractvalues.py q3-extractinstructions.txt datacleanup.py NewTraceFac.py 
do
    if [ ! -f "$sTargetDir/$needfile" ]
    then
        echo "Error: missing important file $sTargetDir/$needfile"
        exit 1
    fi
done

# Do we have all the simulation files?
sTargetDir="$sShelfDir"
for needfile in audit2.py client2.py cliparse.py globaldata.py logoutput.py main.py NewTraceFac.py readin.py repair.py server.py util.py 
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