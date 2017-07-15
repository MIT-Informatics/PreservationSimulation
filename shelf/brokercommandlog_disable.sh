#!/bin/bash
# brokercommandlog_disable.sh
# Set up file to capture broker commands.  If there is an existing file, 
#  append its data to a history file and make a new empty log file.  
# Must be run from shelf directory.  
# 

# Save any data, if any, in the old GiantOutput file

sLogfileDir="tmp"
sLogfileName="BrokerCommands.log"
sLogfileFullname="$sLogfileDir/$sLogfileName"

if [ "$1" = "-h" -o "$1" = "--help" ]
then
    echo "Usage: $0 "
    echo "Sets up $sLogfileFullname file to capture command history."
    echo "Must be run from shelf dir."
    exit 1
fi

# Preserve contents of BrokerCommands file, if any, by appending to backup file.
if [ -f "$sLogfileFullname" ]
then
    echo "Appending previous BrokerCommands log to backup file."
    touch "$sLogfileFullname"".history"
    touch "$sLogfileFullname"
    cat "$sLogfileFullname" >> "$sLogfileFullname"".history"
fi
echo "Removing BrokerCommands log file."
# Make an empty file.
rm -f "$sLogfileFullname"
#touch "$sLogfileFullname"

#END
