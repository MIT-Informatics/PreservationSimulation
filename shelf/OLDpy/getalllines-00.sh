#!/bin/sh
# getalllines.sh
# Get log data from icky log files into a reasonable form for data processing.  

if [ -z "$1" ]
then
    echo "Usage: $0 <directory>"
    echo "Get all the NEWS lines from log files in the entire directory tree."
    exit 1
fi

find "$1" -type d -print            \
| xargs -l sh get02-numbers.sh      \
| grep -v grep                      \
| sed 's/|//g'                      \
| sed 's/[\/:]/ /g'                 \
| awk '{x=$2; sub("v2d","",x); y=$3; sub("logb","",y); z=substr($4,2,2); print $1,$2,$3,x,y,z,$4,$5,$6}' \
| awk 'BEGIN {print "family specific logdir docsize berid copies logfilename timestamp lost"}; {print}'




#END
