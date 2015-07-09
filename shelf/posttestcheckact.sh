#/bin/sh
# posttestcheckact.sh
# Look briefly at the act logs to see if any are very different in size, 
#  indicating a screwup of some sort during the run.  
# 
# Show the smallest and largest few files to see if they are oddly short or long.  

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

ls -l $sFamilyDir/$sSpecificDir/act|awk '{print $5, "  ", $9 }'| sort  >  /tmp/posttestcheckact.txt
head -6 /tmp/posttestcheckact.txt
echo ""
tail -5 /tmp/posttestcheckact.txt
rm -f /tmp/posttestcheckact.txt
