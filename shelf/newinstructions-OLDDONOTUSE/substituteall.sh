#!/bin/bash
# substituteall.sh
#                       RBLandau 20150417

# Make a series of substitutions into a template file that expands as a result. 
#  Output to stdout, for redirection.  
# Process the template multiple times to make all the substitutions specified
#  by the user command, one substitution file at a time.  Intermediate files
#  are used (and not garbage-collected), and the last output file is copied
#  to stdout.  

if [ -z "$2" ] 
then
    echo "Usage: $0 <templatefile> <substitutionfile> [<substitutionfile>...]"
    exit 1
fi

# Get latest version of python program(s) needed.
#for file in "expandtemplate"
#do
#    #cp -v `ls $file*.py | sort | tail -1` $file.py
#    cp  `ls $file*.py | sort | tail -1` $file.py
#done

# Check template file.
tmpfile=$1
shift
if [ ! -f "$tmpfile" ]
then
    echo "ERROR: file not found $tmpfile"
    exit 1
fi

# not a final version, just testing!
filenum=0
nexttemplate=$tmpfile
for insfile in $*
do
    # Check each insertion file.  
    if [ ! -f "$insfile" ]
    then
        echo "ERROR: file not found $insfile"
        exit 1
    fi

    # Insert this particular substitution file.
    outfile=exp$filenum.tmp
    python expandtemplate.py $nexttemplate $insfile > $outfile
    nexttemplate=$outfile
    filenum=`expr $filenum + 1`

done

cat $outfile

#END
