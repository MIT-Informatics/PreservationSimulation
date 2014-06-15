#!/bin/sh

# Run shelf sim sequences for various numbers of copies.

if [ -z "$2" ] || [ "$1" = "help" ] || [ "$1" = "-help" ]
then
    echo "Usage: $0 <directory> <ber>"
    echo "Run simulations for all the copies-instructions files"
    echo "in the <directory>.  <ber> is part of the instruction filename. "
    exit 0
fi

#for copies in 01 02 03 04 05 08 10 14 16 20
for copies in 01 02 03 04 05    # for short runs
#for copies in 01 02            # for testing
do
    echo python runsequence-02.py "$1"/c`echo $copies`b`echo $2`_run1.txt --ncores=4
    python runsequence-02.py "$1"/c`echo $copies`b`echo $2`_run1.txt --ncores=4
done

