#!/bin/bash
# getalllines-new.sh

if [ -z "$2" ]
then
    echo "Usage: $0 <directorytree of log files> <instructionsfile>"
    exit 1
fi

if [ ! -d "$1" ]
then
    echo "Error: \"$1\" is not a directory."
    exit 1
fi

# Instruction file now mandatory.
instructions="$2"

export header=1
for filename in `find $1 -name '*.log' -print`
do
    #echo "for value $filename env value $header"
    python extractvalues.py $instructions $filename
    unset header
done
