#!/bin/sh
# make-instructionfiles-all-bers.sh
# Create all the empty log dirs for a family/specific dir.
#                   RBLandau 20140613

if [ "$1" = "-h" ] || [ "$1" = "?" ] || [ -z "$3" ]
then
    echo "Usage: $0 <familyrootdir> <familydir> <specificdir>"
    echo "Creates instruction files for all BER levels in familyroot/family/specific."
    exit 1
fi

wholedir="$1/$2/$3"
if [ ! -d "$wholedir" ]
then
    echo "ERROR: <$wholedir> is not a directory."
    exit 1
fi

echo 'after dir test'    

# Create instruction files in the log dirs for all possible BER values.
#for berid in 0001 0002 #0003 0005 0010 0020 0030 0050 0100 0200 0300 0500 1000 2000 3000 5000 10000
for berid in 0001 0002 0003 0005 0010 0020 0030 0050 0100 0200 0300 0500 1000 2000 3000 5000 10000
do 
    echo "python makeinstructionfiles-02.py --familyroot=$1 --family=$2 --specific=$3  makeinstructions-b$berid.txt"
    python makeinstructionfiles-02.py --familyroot=$1 --family=$2 --specific=$3  makeinstructions-b$berid.txt

done

#END
