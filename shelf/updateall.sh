#!/bin/sh
# updateall.sh
# Remove the version number identifiers from various files
#  (by making copies, of course, not renaming)
#  to minimize interdependencies.  
# Has to be done for all .py, all .sh, and some .txt files.

# P y t h o n 
# Get latest version of Python program(s) needed.
for file in audit2 broker client2 cliparse datacleanup dbclearcollection dbdumpcollection extractvalues fib globaldata listactor logoutput main mongolib NewTraceFac readin repair runsequence server util
do
    echo "cp -v `ls $file*.py | sort | tail -1` $file.py"
    cp -v `ls $file*.py | sort | tail -1` $file.py
done

# b a s h 
# Get latest version of shell scripts.
# Do not include all the old-science instruction runners. 
for ff in getalllines-new
do
    echo "cp -v $(ls $ff*.sh | sort | tail -1) $ff.sh"
    cp -v $(ls $ff*.sh | sort | tail -1) $ff.sh
done

# T e x t 
# Get latest version of text files used for various lists.
for ff in brokercommandlist q3-extractinstructions
do
    echo "cp -v $(ls $ff*.txt | sort | tail -1) $ff.txt"
    cp -v $(ls $ff*.txt | sort | tail -1) $ff.txt
done

