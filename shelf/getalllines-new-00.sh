#!/bin/sh
# getalllines-new.sh

if [ -z "$1" ]
then
    echo "Usage: $0 <directorytree of log files>"
    exit 1
fi

export header=1
for filename in `find $1 -name '*.log' -print`
do
    #echo "for value $filename env value $header"
    python extractvalues-01.py extractinstructions.txt $filename
    unset header
done
