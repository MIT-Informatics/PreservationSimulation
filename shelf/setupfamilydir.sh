#/bin/sh
# setupfamilydir.sh
#
# Establish directory structure needed as a familydir for 
#  simulation runs.  

if [ "$1" == "-h" ]
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

mkdir $sFamilyDir
mkdir $sFamilyDir/$sSpecificDir

for dd in act cmd dat ext log 'done'
do
    mkdir $sFamilyDir/$sSpecificDir/$dd
done

cp ./defaults/* $sFamilyDir/$sSpecificDir

#END
