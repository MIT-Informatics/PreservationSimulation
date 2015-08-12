#!/bin/bash
# expandtemplate.sh 

if [ -z "$2" ]
then
    echo "Usage $0 <templatefile> <outputfile>"
    echo "All the insertion files will be applied, in order from small to large."
    exit 1
fi

#for ff in "substituteall"
#do
#    #cp $(ls $ff*.sh | sort | tail -1) $ff.sh
#    cp $(ls $ff*.sh | sort | tail -1) $ff.sh
#done

sh substituteall.sh "$1" \
        ins/simlen.ins ins/glitchignorelevel.ins    > "$2.01"
sh substituteall.sh "$2.01" \
        ins/audittype.ins ins/auditsegments.ins     > "$2.02"
sh substituteall.sh "$2.02" \
        ins/docsize.ins ins/shelfsize.ins           > "$2.03"
sh substituteall.sh "$2.03" \
        ins/glitchmaxlife.ins ins/glitchimpact.ins  > "$2.04"
sh substituteall.sh "$2.04" \
        ins/glitchfreq.ins ins/glitchdecay.ins      > "$2.05"
sh substituteall.sh "$2.05" \
        ins/auditfreq.ins ins/lifem.ins             > "$2.06"
sh substituteall.sh "$2.06" \
        ins/ncopies.ins ins/randomseed.ins        > "$2"

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

auditfreq
lifem
ncopies
randomseed
