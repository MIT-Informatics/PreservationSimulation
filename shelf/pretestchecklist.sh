#!/bin/bash
# pretestchecklist.sh

# Check that all directories and files are in place for a run.  
# familydir required, but specific defaults to ./ (dot, working dir)
# 

if [ -z "$1" -o "$1" = "-h" -o "$1" = "--help" ]
then 
    echo "Usage: $0 [<familydir> [<specificdir>]]"
    echo "<specificdir> defaults to ."
    echo "Must be run from shelf dir."
    exit 1
fi


# Where the files should go for this generation.
sFamilyDir="$1"
if [ -z "$2" ] 
then
    sSpecificDir=.
else
    sSpecificDir="$2"
fi
sShelfDir=.
sInstructionDir=$sShelfDir/instructions


# Check all the important directories.
for needdir in $sFamilyDir $sFamilyDir/$sSpecificDir $sFamilyDir/$sSpecificDir/cmd $sFamilyDir/$sSpecificDir/act $sFamilyDir/$sSpecificDir/log $sFamilyDir/$sSpecificDir/ext $sFamilyDir/$sSpecificDir/dat  
do
    if [ ! -d "$needdir" ]
    then
        echo "Error: missing data directory $needdir"
        exit 1
    fi
done


# Is there a root file for the giant output to build on?
if [ ! -f "$sFamilyDir/$sSpecificDir/dat/GiantOutput_00.txt" ]
then
    echo "Error: missing file $sFamilyDir/$sSpecificDir/dat/GiantOutput_00.txt"
    exit 1
else
    filesize=$(cat "$sFamilyDir/$sSpecificDir/dat/GiantOutput_00.txt" | wc -l)
    if [ "$filesize" -gt 1 ]
    then
        echo "Warning: Output data file may contain stale data: $sFamilyDir/$sSpecificDir/dat/GiantOutput_00.txt"
    fi 
fi


# Do we have all the instruction files?
sTargetDir="$sInstructionDir"
for needfile in auditfreq.ins3 auditsegments.ins3 audittype.ins3 docsize.ins3 glitchmaxlife.ins3 glitchimpact.ins3 glitchfreq.ins3 glitchdecay.ins3 glitchspan.ins3 glitchignorelevel.ins3 lifem.ins3 ncopies.ins3 ndocuments.ins3 serverdefaultlife.ins3 shockfreq.ins3 shelfsize.ins3 shockimpact.ins3 shockmaxlife.ins3 shockspan.ins3 simlen.ins3 
do
    if [ ! -f "$sTargetDir/$needfile" ]
    then
        echo "Error: missing important instruction file $sTargetDir/$needfile"
        exit 1
    fi
done


# Do we have the db manipulation files?
sTargetDir="$sShelfDir"
for needfile in dbclearcollection.py dbdeletedatabase.py dbdumpcollection.py dbdumpdonekeys.py dblistcollections.py dblistdatabases.py mongolib.py searchspace.py searchdatabase.py searchdatabasemongo.py NewTraceFac.py 
do
    if [ ! -f "$sTargetDir/$needfile" ]
    then
        echo "Error: missing important mongodb management file $sTargetDir/$needfile"
        exit 1
    fi
done


# Do we have all the execution files?
sTargetDir="$sShelfDir"
for needfile in broker2.py newbroker3.py brokercli.py brokerformat.py brokergetcores.py catchex.py NewTraceFac.py broker2commandlist.txt client2.py cliparse.py main.py command.py fib.py extractvalues2.py hl-extractinstructions.txt datacleanup.py lifetime.py listactor.py 
do
    if [ ! -f "$sTargetDir/$needfile" ]
    then
        echo "Error: missing important execution file $sTargetDir/$needfile"
        exit 1
    fi
done


# Do we have all the simulation files?
sTargetDir="$sShelfDir"
for needfile in audit2.py bottle.py broker.py brokercli.py brokergroup_makeform.py brokergroupform.py catchex.py client2.py cliparse.py collection.py command.py datacleanup.py doccopy.py document.py dumpparams.py dumpuse.py getcliargs.py getparams.py globaldata.py logoutput.py main.py NewTraceFac.py logoutput.py readin.py repair.py server.py shelf.py shock.py util.py  
do
    if [ ! -f "$sTargetDir/$needfile" ]
    then
        echo "Error: missing important simulation file $sTargetDir/$needfile"
        exit 1
    fi
done


# Do we have all the web GUI files?
sTargetDir="$sShelfDir"
for needfile in brokergroupform.py brokergroupform_main.py brokergroupform_setup.py brokergroup_makeform.py 
do
    if [ ! -f "$sTargetDir/$needfile" ]
    then
        echo "Error: missing important web interface file $sTargetDir/$needfile"
        exit 1
    fi
done
sTargetDir="$sShelfDir/views"
for needfile in brokergroup_form_base.j2 brokergroup_form_insert.j2 brokergroup_setupform_base.j2 brokergroup_setupform_insert.j2 brokergroup_setupform_done.j2 
do
    if [ ! -f "$sTargetDir/$needfile" ]
    then
        echo "Error: missing important web interface file $sTargetDir/$needfile"
        exit 1
    fi
done


# Is mongod running?
count=$(ps | grep "mongod" | wc -l)
if [ -z "$count" ]
then
    echo "Error: MongoDB daemon mongod does not appear to be running."
    exit 1
fi


# Are there leftover files in the execution directories?  Should be empty.
sTargetDir="$sFamilyDir/$sSpecificDir"
for needemptydir in act cmd ext log
do 
    filecount=$(ls $sTargetDir/$needemptydir | wc -l)
    if [ $filecount -gt 0 ] 
    then
        echo "Error: Run directory is not empty: $sTargetDir/$needemptydir"
        exit 1
    fi
done


echo "Pretest checklist: Looks okay!"
#END