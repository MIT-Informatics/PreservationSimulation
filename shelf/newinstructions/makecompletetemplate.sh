#!/bin/bash
# makecompletetemplate.sh 
# Run this (with bash) to create the expanded flat instruction file
#  by crossing all the instruction files.  That flat file can then be 
#  loaded into a MongoDb database, or processed directly if one wants
#  to write the search function.  

if [ -z "$2" ]
then
    echo "Usage $0 <templatefile> <outputfile> ['filter']"
    echo "All the insertion files will be applied, in order from small to large."
    echo "If filter requested, uses realrulestext.txt file."
    exit 1
fi

if [ "$3" = "filter" ]
then
    filter=ON
else
    filter=OFF
fi

#for ff in "substituteall"
#do
#    #cp $(ls $ff*.sh | sort | tail -1) $ff.sh
#    cp $(ls $ff*.sh | sort | tail -1) $ff.sh
#done

date +%Y%m%d_%H%M%S.%3N
sh substituteall.sh "$1"    \
        ins/simlen.ins ins/glitchignorelevel.ins    > "$2.01"
echo -n "1 "
sh substituteall.sh "$2.01" \
        ins/audittype.ins ins/auditsegments.ins     > "$2.02"
echo -n "2 "
sh substituteall.sh "$2.02" \
        ins/docsize.ins ins/shelfsize.ins           > "$2.03"
echo -n "3 "
sh substituteall.sh "$2.03" \
        ins/glitchmaxlife.ins ins/glitchimpact.ins  > "$2.04"
echo -n "4 "
sh substituteall.sh "$2.04" \
        ins/glitchfreq.ins ins/glitchdecay.ins      > "$2.05"
echo -n "5 "
sh substituteall.sh "$2.05" \
        ins/auditfreq.ins ins/lifem.ins             > "$2.06"
echo -n "6 "
sh substituteall.sh "$2.06" \
        ins/glitchspan.ins ins/ncopies.ins          > "$2.07"
echo -n "7 "
sh substituteall.sh "$2.07" \
        ins/shockfreq.ins ins/shockimpact.ins       > "$2.08"
echo -n "8 "
sh substituteall.sh "$2.08" \
        ins/shockspan.ins ins/shockmaxlife.ins      > "$2.09"
echo -n "9 "
sh substituteall.sh "$2.09" \
        ins/serverdefaultlife.ins                   > "$2.10"

if [ "$filter" = "ON" ]
then
    echo -n "filtering "
    python useinstfilter.py realrulestext.txt \
        "$2.10"                                     > "$2.11"
else
    cp "$2.10" "$2.11"
fi
echo -n "10 "
cp "$2.11"   "$2" 
echo    " done"
date +%Y%m%d_%H%M%S.%3N

exit 0
#END

simlen
glitchignorelevel
audittype
auditsegments
docsize
shelfsize

glitchmaxlife
glitchimpact
glitchfreq
glitchdecay

shockfreq
shockimpact
shockspan
shockmaxlife
serverdefaultlife

auditfreq
lifem
glitchspan
ncopies
<filter applied in here, if requested>
randomseed      # really want this to be last because of its size
