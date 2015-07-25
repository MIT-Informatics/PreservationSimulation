#!/bin/sh
# emptygiantoutput.sh
# Must be run from shelf directory.  
# Defaults to Q3 family and . specific, but can be overridden by args 1 and 2

if [ "$1" == "-h" ]
then
    echo "Usage: $0 [<familydir> [<specificdir>]]"
    echo "Defaults to ../Q3 and ."
    exit 1
fi

if [ -z "$1" ] 
then
    familydir=../Q3
else
    familydir="$1"
fi
if [ -z "$2" ] 
then
    specificdir=.
else
    specificdir="$2"
fi

cp -v ./GiantOutput_HeaderOnly.txt $familydir/$specificdir/dat/GiantOutput_00.txt

#END
