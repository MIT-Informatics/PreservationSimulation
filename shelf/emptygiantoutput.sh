#!/bin/bash
# emptygiantoutput.sh
# Must be run from shelf directory.  
# familydir required, but specific defaults to .

if [ -z "$1" -o "$1" == "-h" -o "$1" == "--help" ]
then
    echo "Usage: $0 [<familydir> [<specificdir>]]"
    echo "<specificdir> defaults to ."
    echo "Must be run from shelf dir."
    exit 1
fi

sFamilyDir="$1"
if [ -z "$2" ] 
then
    specificdir=.
else
    specificdir="$2"
fi

cp -v ./GiantOutput_HeaderOnly.txt $sFamilyDir/$specificdir/dat/GiantOutput_00.txt

#END
