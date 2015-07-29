#/bin/bash
# setupfamilydir.sh
#
#                               RBLandau 20150713
#
# Establish directory structure needed as a familydir for 
#  simulation runs.  
# Creates the family and specific directories and then all the 
#  subdirs needed by the broker.  Also copies the default CSV 
#  parameter files into the family dir.

if [ "$1" == "-h" -o "$1" == "--help" ]
then
    echo "Usage: $0 [<familydir> [<specificdir>]]"
    echo "Defaults to ../Q3 and ."
    echo "Must be run from shelf dir"
    exit 1
fi

# Where the files should go for this generation.
if [ -z "$1" ] 
then
    sFamilyDir=../Q3
else
    sFamilyDir="$1"
fi
if [ -z "$2" ] 
then
    sSpecificDir=.
else
    sSpecificDir="$2"
fi

if [ -d "$sFamilyDir" ] 
then
    echo "Family Dir $sFamilyDir already exists."
else
    echo "Creating dir $sFamilyDir"
    mkdir $sFamilyDir
fi

if [ -d "$sFamilyDir/$sSpecificDir" ] 
then
    echo "Specific Dir $sFamilyDir/$sSpecificDir already exists."
else
    echo "Creating dir $sFamilyDir/$sSpecificDir"
    mkdir $sFamilyDir/$sSpecificDir
fi

for dd in act cmd dat ext log 'done'
do
    if [ -d "$sFamilyDir/$sSpecificDir/$dd" ] 
    then
        echo "Dir $sFamilyDir/$sSpecificDir/$dd already exists."
    else
        echo "Creating dir $sFamilyDir/$sSpecificDir/$dd"
        mkdir $sFamilyDir/$sSpecificDir/$dd
    fi
done
echo "Copying default param files to $sFamilyDir"
cp ./defaults/* $sFamilyDir/$sSpecificDir

#END
