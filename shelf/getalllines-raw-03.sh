#!/bin/bash
# getalllines.sh
# Get log data from icky log files into a reasonable form for data processing.  

# function to grep out all the NEWS lines for all numbers of copies.  
function getnumbers() {
    #echo inside getnumbers called: "$*"
    searchme="NEWS"
    if [ -n "$2" ] 
    then
         searchme="$2"
    fi
    #echo getnumbers: searchstring is "$searchme"
    for copies in 01 02 03 04 05 06 07 08 09 10 14 16 20
    do
        echo "egrep $searchme $1/c`echo $copies`*"
        egrep $searchme $1/c`echo $copies`*   
    done
}

if [ -z "$2" ]
then
    echo "Usage: $0 <parentdirectory> <specificdirectory> [searchstring]"
    echo "Get all the NEWS lines from log files in the entire directory tree."
    exit 1
fi

# Main line.  
find "$1/$2" -type d -print            \
| while read dirfile;               \
  do                                \
    #echo calling getnumbers $dirfile "$3"
    getnumbers $dirfile "$3";            
  done                              \
| grep -v grep                      \
| grep -v asdf

#| awk 'BEGIN {print "family specific logdir docsize berid copies logfilename timestamp lost"}; {print}'

#| sed 's/|//g'                      \
#| sed 's/[\/:]/ /g'                 \
#| awk '{x=$2; sub("v3d","",x); y=$3; sub("logb","",y); z=substr($4,2,2); print $1,$2,$3,x,y,z,$4,$5,$6}'           \


#END
