#!/bin/bash
# start_brokerform.sh
#                       RBLandau 20170318
#                       revised  20170520
#                       revised  20180928
#                       revised  20181002
#                       revised  20181007
# Script to launch the broker web form.
# You must already be in the shelf directory with the 
#  'shelfenv' virtualenv activated, wherever that is.

# THIS SCRIPT MAY BE LAUNCHED WITH . OR source OR sh OR bash.  

if [ -z "$1" -o "$1" = "-h" -o "$1" = "--help" -o "$1" = "help" ]
then
    echo "Usage: $0 [<whereloc> [<politetime>]]"
    echo "<whereloc> is either 'here' or '' "
    echo "politetime is integer milliseconds for NPOLITE"
    exit 1
fi

# Accommodate Linux versions that do not specify NUMBER_OF_PROCESSORS.
if [ -z "$NUMBER_OF_PROCESSORS" ]
then
    export NUMBER_OF_PROCESSORS=$(cat /proc/cpuinfo | grep processor | wc -l)
fi

# Turn debug tracing off completely to save CPU time.
export TRACE_LEVEL=
export TRACE_PRODUCTION=YES

if [ -z "$2" ]
then
    # And start new runs as quickly as possible.  
    export NPOLITE=1000
else
    export NPOLITE=$2
fi
echo "Politetimer set to $NPOLITE msec."

echo "Browse to localhost:8080 to access the broker form."
echo ""
echo "Use ctrl-z, fg, bg, and jobs to manipulate a detached web server."
echo "Use ctrl-c to terminate it when it is the foreground job."
if [ "$1" = "here" ]
then
    # Start it locally so I can track its use and stop it if necessary.
    echo "Starting brokergroupform locally."
    python brokergroupform.py
else
    echo "Starting brokergroupform detached."
    python brokergroupform.py >tmp/brokergroupform.log 2<&1 &
    # NOTE WELL: The ampersand runs the form program in a subprocess.
    #  To terminate the program, you must first bring it forward with 
    #  'fg' and then issue the control-C.
    # Sending the output to a log file makes the process detachable, I hope.
    jobs
fi

#END
