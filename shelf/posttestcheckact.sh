#/bin/bash
# posttestcheckact.sh
# familydir required, but specific defaults to .
# Look briefly at the act logs to see if any are very different in size, 
#  indicating a screwup of some sort during the run.  
# 
# Show the smallest and largest few files to see if they are oddly short or long.  

if [ -z "$1" -o "$1" = "-h" -o "$1" = "--help" ]
then
    echo "Usage: $0 [<familydir> [<specificdir>]]"
    echo "<specificdir> defaults to ."
    echo "Must be run from shelf dir."
    exit 1
fi

# Where the files should go for this generation.
sFamilyDir="$1"
if [ -z "$2" ] 
then
    sSpecificDir=.
else
    sSpecificDir="$2"
fi
sFullDir=$sFamilyDir/$sSpecificDir

if [ 0 -lt $(ls $sFullDir/ext/ | wc -l) ]
then
    echo ""
    echo "WARNING! The $sFullDir/ext/ is not empty, but should be."
    echo ""
fi

if [ $(ls $sFullDir/act | wc -l) -ne $(ls $sFullDir/log | wc -l) ] 
then
    echo ""
    echo "WARNING! The $sFullDir/act and .../log dirs contain different numbers of files."
    echo ""
fi

echo "Check visually that the size range of ..._actor.log files is very narrow."
ls -l $sFamilyDir/$sSpecificDir/act|awk '{print $5, "  ", $9 }'| sort  >  /tmp/posttestcheckact.txt
head -6 /tmp/posttestcheckact.txt
echo ""
echo "  (smallest  ^^^    to    largest  vvv)"
echo ""
tail -5 /tmp/posttestcheckact.txt
rm -f /tmp/posttestcheckact.txt
