#/bin/bash
# narrowallfiles.sh
#                               RBLandau 20190119
#
if [ -z "$1" -o "$1" = "-h" -o "$1" = "--help" ]
then
    echo "Usage: $0 <datadir>"
    echo "Reduce size of all GiantOutput_*.txt files in target dir"
    echo " and sort the files into 'wide' and 'narrow' subdirs."
    echo "Must be run from shelf dir."
    exit 1
fi

# Where are the files to be narrowed?
sDataDir="$1"

if [ ! -d "$sDataDir/wide" ] 
then
    echo "Creating $sDataDir/wide."
    mkdir "$sDataDir/wide"
fi
if [ ! -d "$sDataDir/narrow" ] 
then
    echo "Creating $sDataDir/narrow."
    mkdir "$sDataDir/narrow"
fi

for ff in $sDataDir/GiantOutput_*.txt 
do
    echo "Working on $ff in $DataDir . . . "
    ffname=$(basename $ff)
    ffnameonly=${ffname%%.*}
    ffextn=${ffname##*.}
    echo "python narrowfile.py $ff > $sDataDir/narrow/$ffnameonly-naro.$ffextn"
    python narrowfile.py $ff > $sDataDir/narrow/$ffnameonly-naro.$ffextn
#    mv "$sDataDir/$ff" "$sDataDir/wide/$ff"
    cp "$sDataDir/$ffname" "$sDataDir/wide/$ffname"
done
exit 0

# shell subs, just as reminders:
#${variable%pattern}
#  Trim the shortest match from the end
#${variable##pattern}
#  Trim the longest match from the beginning
#${variable%%pattern}
#  Trim the longest match from the end
#${variable#pattern}
#  Trim the shortest match from the beginning

#END
