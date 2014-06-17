#!/bin/sh
# makelogdirs.sh
# Create all the empty log dirs for a family/specific dir.
#                   RBLandau 20140613

if [ "$1" = "-h" ] || [ "$1" = "?" ] || [ -z "$2" ]
then
    echo "Usage: $0 <familydir> <specificdir>"
    echo "Creates empty subdirs for instruction and log files."
    exit 1
fi

wholedir=$1/$2
if [ ! -d $wholedir ]
then
    echo "ERROR: |$wholedir| is not a directory."
    exit 1
fi

# Make a pile of empty log directories.  
for berid in 0001 0002 0003 0005 0010 0020 0030 0050 0100 0200 0300 0500 1000 2000 3000 5000 10000
do
    echo "mkdir $wholedir/logb$berid"
    mkdir $wholedir/logb$berid
done

#END
