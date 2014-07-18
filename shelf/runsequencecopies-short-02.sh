#!/bin/sh
# runsequencecopies.sh

# Run shelf sim sequences for various numbers of copies.

if [ -z "$2" ] || [ "$1" = "help" ] || [ "$1" = "-help" ]
then
    echo "Usage: $0 <directory> <ber>"
    echo "Run simulations for several copies-instructions files"
    echo "in the <directory>.  "
    echo "<directory> is <family>/<specific>"
    echo "<ber> is part of the directory name and instruction filename. "
    exit 1
fi

#for copies in 01 02 03 04 05 08 10 14 16 20     # for complete runs, yikes.
#for copies in 01 02 03 04 05 08 10              # for medium runs
for copies in 01 02 03 04 05                    # for short runs
#for copies in 01 02                             # for testing
do
    echo "python runsequence-03.py $1/logb$2/c`echo $copies`b$2.txt --ncores=6"
    python runsequence-03.py $1/logb$2/c`echo $copies`b$2.txt --ncores=6
done

#END
