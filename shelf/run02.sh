#!/bin/sh

# Run shelf sim from the latest versions of files
#
# BZZZT: beware of line endings in Cygwin.  Even though this .sh
# file has UNIX-style line endings (no \r characters), the 
# names that come out of, apparently, ls do have CRs, so I 
# have to remove them manually (and *carefully*) with sed.
# Crapola.  I liked it better in previous versions of Cygwin
# when I had to worry about the line endings manually myself.
# Maybe there's a switch for this that I haven't read about.
# For the moment, hack.  

if [ "$1" = "help" ] || [ "$1" = "-help" ]
then
    echo "Usage: $0 [simlength [randomseed [csvdirectory]]]"
    exit 0
fi


#cp client02.py client.py
#cp server02.py server.py
#cp util01.py util.py
#cp main01.py main.py
#cp globaldata01.py globaldata.py
for ff in client server util readin main globaldata ; do
    newffull=$(ls $ff*.py | sort | tail -1 | sed s/\\r//);
    cp -v $newffull $ff.py ;
done

python main.py $1 $2 $3 $4 $5
