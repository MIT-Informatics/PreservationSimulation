#/bin/bash
# setupnumberofdocs.sh
#
#                               RBLandau 20180928
#
# Establish default files that set the number of documents for a simulation run
#  as either normal (10,000 docs) or shock simulations (10 docs).  

if [ -z "$1" -o "$1" = "-h" -o "$1" = "--help" -o "$1" = "help" ]
then
    echo "Usage: $0 <typestring>"
    echo "<typestring> is either 'NORMAL' or 'SHOCK'"
    exit 1
fi
sType="$1"

sDefaultDir="./defaults"

if [ "$sType" = "NORMAL" ]
then
    cp -v $sDefaultDir/clients_NORMAL.csv $sDefaultDir/clients.csv
elif [ "$sType" = "SHOCK" ]
then
    cp -v $sDefaultDir/clients_SHOCKSONLY.csv $sDefaultDir/clients.csv
else
    echo "Error: type must be NORMAL or SHOCK"
fi

echo "Done."

#END
