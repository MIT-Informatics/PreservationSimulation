#!/bin/bash
# dbcleardone.sh
# Clear out moldy, old done records in some Mongo database.
# Cleans out brokeradmin by default.
# 

if [ "$1" = "-h" -o "$1" = "--help" ]
then 
    echo "Usage: $0 [<dbname>]"
    echo "<dbname> defaults to 'brokeradmin'"
    echo "Must be run from shelf dir."
    exit 1
fi

if [ -n "$1" ]
then
    sCollectionName="$1"
else
    sCollectionName="brokeradmin"
fi
python dbclearcollection.py "$sCollectionName" done

#END