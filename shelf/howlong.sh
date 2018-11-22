#!/bin/bash
# howlong.sh

if [ -z "$1" -o -z "$2" -o "$1" = "-h" -o "$1" = "--help" ]
then
    echo "Usage: $0 [<familydir> [<specificdir>]]"
    echo "<specificdir> defaults to ."
    echo "Must be run from shelf dir."
    exit 1
fi

# Where are the act/*_case.log files?
sFamilyDir="$1"
if [ -z "$2" ] 
then
    sSpecificDir=.
else
    sSpecificDir="$2"
fi


for ff in $(find $sFamilyDir/$sSpecificDir/act -name '*_case.log')
do
    awk -f caselog_howlong.awk $ff
done

#END
