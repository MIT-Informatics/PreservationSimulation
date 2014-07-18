#!/bin/bash
# getv3lines.sh
# Process log data from icky log files into a reasonable form for data processing.  


#| awk 'BEGIN {print "family specific logdir docsize berid copies logfilename timestamp lost"}; {print}'

awk '{print $1, $16}'   \
| sed 's/\/v/ v/'       \
| sed 's/\/logb/ logb/' \
| sed 's/|//g'          \
| awk '{ds=gensub("v.d","",1,$2); ber=gensub("logb","",1,$3); sub("/.*","",ber); nc=substr(gensub(".*/c","",1,$3),1,2); print $1,$2,$3,ds,ber,nc,$4}'   \
| awk 'BEGIN {print "family specific logfilename docsize berid copies lost"}; {print}'


#| awk '{ds=gensub("v.d","",1,$2); ber=gensub("logb","",1,$3); sub("/.*","",ber); cp=gensub(".*/c","",1,$3); sub("b.*","",cp); print $1,$2,$3,ds,ber,cp,$4}'


#END
