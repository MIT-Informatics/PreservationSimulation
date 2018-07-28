#!/bin/bash
# emptygiantoutput.sh
# Must be run from shelf directory.  
# familydir required, but specific defaults to .

# Save any data, if any, in the old GiantOutput file

if [ -z "$1" -o "$1" = "-h" -o "$1" = "--help" ]
then
    echo "Usage: $0 [<familydir> [<specificdir>]]"
    echo "<specificdir> defaults to ."
    echo "Must be run from shelf dir."
    exit 1
fi

sFamilyDir="$1"
if [ -z "$2" ] 
then
    sSpecificDir=.
else
    sSpecificDir="$2"
fi

# Preserve contents of GiantOutput file, if any, by appending to backup file.
if [ -f "$sFamilyDir/$sSpecificDir/dat/GiantOutput_00.txt" ]
then
    echo "Appending previous GiantOutput data to backup file."
    touch "$sFamilyDir/$sSpecificDir/dat/GiantOutput_00.txt.prev"
    touch "$sFamilyDir/$sSpecificDir/dat/GiantOutput_00.txt"
    cat "$sFamilyDir/$sSpecificDir/dat/GiantOutput_00.txt" \
     >> "$sFamilyDir/$sSpecificDir/dat/GiantOutput_00.txt.prev"
fi
echo "Making new empty GiantOutput file."
# Make an empty file, which datacleanup will populate with the correct header.
rm -f "$sFamilyDir/$sSpecificDir/dat/GiantOutput_00.txt"
touch "$sFamilyDir/$sSpecificDir/dat/GiantOutput_00.txt"

#END