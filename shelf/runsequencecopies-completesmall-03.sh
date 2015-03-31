#!/bin/sh
# runsequencecopies.sh

# Run shelf sim sequences for various numbers of copies.

if [ -z "$3" ] || [ "$1" = "help" ] || [ "$1" = "-help" ] || [ ! -d "$1/$2" ] 
then
    echo "Usage: $0 <familydir> <specificdir> <lifem>"
    echo "Run simulations for several copies-instructions files"
    echo "in the <familydir>/<specificdir> ."
    echo "<lifem> is a string, part of the directory name and "
    echo "instruction filename.  Be sure to INCLUDE THE LEADING ZEROS."
    echo "The NCORES environment variable will override the default (==6)."
    exit 1
fi

# Get latest versions of necessary files. 
for ff in runsequence ; do
    newffull=$(ls $ff*.py | sort | tail -1 | sed 's/\\r//');
    cp -v $newffull $ff.py ;
done

ncorestoday=6
if [ -n "$NCORES" ]
then
    ncorestoday=$NCORES
fi

#for copies in 01 02 03 04 05 08 10 14 16 20     # for complete runs, yikes.
#for copies in 01 02 03 04 05 08 10              # for medium runs
#for copies in 01 02 03 04 05                    # for short runs
for copies in 01 02 03 04 05 06 07 08 09 10     # for complete shaping runs
#for copies in 01 02                             # for testing
do
    echo "python runsequence.py $1/logb$2/c`echo $copies`b$2.txt --ncores=$ncorestoday"
    python runsequence.py $1/logb$2/c`echo $copies`b$2.txt --ncores=$ncorestoday
done

#END
