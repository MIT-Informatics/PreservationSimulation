#!/bin/sh
# q3-pretestchecklist.sh

# Check that all directories and files are in place for a run.  
# 

# Where the files should go for this generation.
sFamilyDir="../q3"
sSpecificDir=.

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
fi

# Do we have all the execution files?
for needfile in broker.py NewTraceFac.py brokercommandlist.txt mongolib.py main.py fib.py extractvalues.py q3-extractinstructions.txt datacleanup.py
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



echo "Looks okay!"
#END
