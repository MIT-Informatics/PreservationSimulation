#!/bin/bash
# getalllines.sh
# Get log data from icky log files into a reasonable form for data processing.  

# function to grep out all the NEWS lines for all numbers of copies.  
function getnumbers() {
#    echo getnumbers called: "$1"
    for copies in 01 02 03 04 05 08 10 14 16 20
    do
        echo "grep NEWS $1/c`echo $copies`*"
        grep NEWS $1/c`echo $copies`* | awk '/grep/ {print}; /BAD/ {print $1,$16}; /GOOD/ {print $1,"|0|"}'
    done
}
export getnumbers

if [ -z "$1" ]
then
    echo "Usage: $0 <directory>"
    echo "Get all the NEWS lines from log files in the entire directory tree."
    exit 1
fi

# Main line.  
find "$1" -type d -print            \
| while read dirfile; do  getnumbers $dirfile; done            \
| grep -v grep                      \
| sed 's/|//g'                      \
| sed 's/[\/:]/ /g'                 \
| awk '{x=$2; sub("v2d","",x); y=$3; sub("logb","",y); z=substr($4,2,2); print $1,$2,$3,x,y,z,$4,$5,$6}'           \
| awk 'BEGIN {print "family specific logdir docsize berid copies logfilename timestamp lost"}; {print}'




#END
