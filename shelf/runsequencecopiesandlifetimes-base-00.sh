#!/bin/sh
# runsequencecopiesandlifetimes.sh
#                           RBLandau 20140808

# Run shelf sim sequences for various numbers of copies and lifetimes.
#  This could run for hours or days if there are enough samples.

if [ -z "$2" ] || [ "$1" = "help" ] || [ "$1" = "-help" ]
then
    echo "Usage: $0 <directory> <liferange>"
    echo "Run simulations for several copies-instructions files and lifetimes"
    echo " in the <directory>.  "
    echo "<directory> is <family>/<specific>, such as ../Q1/v3d50"
    echo "<liferange> values are "
    echo "  ones                0001, 0002, 0003, 0005"
    echo "  tens                0010, 0020, 0030, 0050"
    echo "  hundreds            0100, 0200, 0300, 0500"
    echo "  thousands           1000, 2000, 3000, 5000, 10000"
    exit 1
fi

# Check for plausible directory argument.
if [ ! -d $1 ]
then
    echo "Error: |$1| is not a directory."
    exit 2
fi

# Check for plausible liferange argument.
if [ $2 = "ones" ]
then 
    liferange="0001 0002 0003 0005"
    # lifetime=0001 is run only for document size = 5MB, else error rate too high.
    liferange="0002 0003 0005"
    echo "liferange = $liferange"
elif [ $2 = "tens" ]
then 
    liferange="0010 0020 0030 0050"
    echo "liferange = $liferange"
elif [ $2 = "hundreds" ]
then 
    liferange="0100 0200 0300 0500"
    echo "liferange = $liferange"
elif [ $2 = "thousands" ]
then 
    liferange="1000 2000 3000 5000 10000"
    echo "liferange = $liferange"
else
    echo "Error: |$2| is not a valid <liferange> value."
    exit 3
fi

# Get the latest version of any python files needed.
for rootname in  runsequence  ; do
    newffullname=$(ls $rootname*.py | sort | tail -1 | sed 's/\\r//');
    cp -v $newffullname $rootname.py ;
done

# Loop over set of lifetimes.
for lifem in $liferange
do 
    echo "Lifetime = $lifem"
    # Loop over set of copies.
    #for copies in 01 02 03 04 05 08 10 14 16 20     # for complete runs, yikes.
    for copies in 01 02 03 04 05 08 10              # for base (medium) runs
    #for copies in 14 16 20                          # for filling out base to long runs.
    #for copies in 01 02 03 04 05                    # for short runs
    #for copies in 01 02                             # for testing
    do
        # Don't even start if the instruction file is not present.
        instructionfilename=$1/logb$lifem/c`echo $copies`b$lifem.txt
        if [ ! -r "$instructionfilename" ]
        then
            echo "Error: no such instruction file |$instructionfilename|"
        else
            echo "python runsequence.py $instructionfilename --ncores=6"
            if [ -n "$3" ]
            then
                echo "Testing only..."
            else
                # Finally, execute something.
                python runsequence.py $instructionfilename --ncores=6
            fi
        fi
    done

done

#END
