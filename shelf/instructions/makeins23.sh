# makeins23.sh
# Translate all *.ins files to *.ins3 files, which 
#  still need editing to insert
# - Caption text for display; 
# - 1 instead of 0 for option to be selected in the pulldown box.

if [ -z "$1" ]
then
    echo Usage: "$0 <filespec-maybe-wildcard>"
    exit 1
fi
#for ff in $(ls "$1")
for ff in $*
do 
    echo "****** translating ${ff} to ${ff}3"
    awk -f ins23.awk $ff > ${ff}3
done


