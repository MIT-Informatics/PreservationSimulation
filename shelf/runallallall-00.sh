#!/bin/sh
# runallallall.sh
# Run all seeds, all copies, all lifetimes.
#                           RBLandau 20140808

if [ -z "$1" ] || [ "$1" = "help" ] || [ "$1" = "-help" ]
then
    echo "Usage: $0 <directory> "
    echo "Run simulations for *all* combinations of lifetimes, copies, and seeds"
    echo " in the target <directory>.  "
    echo "<directory> is <family>/<specific>, such as ../Q1/v3d50"
    echo "<liferange> values are "
    echo "WARNING: This could take a looooong time, many hours."
    exit 1
fi

# Check for plausible directory argument.
if [ ! -d $1 ]
then
    echo "Error: |$1| is not a directory."
    exit 2
fi


sh runsequencecopiesandlifetimes-base-00.sh $targetdir ones
sh runsequencecopiesandlifetimes-base-00.sh $targetdir tens
sh runsequencecopiesandlifetimes-base-00.sh $targetdir hundreds
sh runsequencecopiesandlifetimes-base-00.sh $targetdir thousands
sh runsequencecopiesandlifetimes-fillout-00.sh $targetdir ones
