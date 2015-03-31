#!/bin/sh

# Get NEWS lines from log files.

if [ -z "$1" ] || [ "$1" == "help" ] || [ "$1" == "-h" ] || [ "$1" == "--help" ]
then
    echo "Usage: $0 <directory>"
    echo "grep the results lines out of all the log files"
    echo "in the directory."
    exit 0
fi

if ! [ -d "$1" ] 
then
    echo "ERROR: $1 is not a directory."
    exit 1
fi

for copies in 01 02 03 04 05 06 07 08 09 10 14 16 20
do

nfiles=`ls $1/c$copies* | wc -l`
nmid1=`expr $nfiles + 1`
nmid=`expr $nmid1 / 2`

echo "grep NEWS $1/c$copies*"
grep NEWS $1/c$copies*                   \
| awk '/grep/ {print}; /BAD/ {print $16}; /GOOD/ {print "|0|"}' \
| sed 's/|//g'                                  \
| sort -n                                       \
| head -$nmid | tail -1

done

