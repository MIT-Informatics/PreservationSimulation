#!/bin/bash
# start_brokerform.sh
#                       RBLandau 20170318
#                       revised  20170520
# Script to launch the broker web form.
# You must already be in the shelf directory with the 
#  'shelfenv' virtualenv activated, wherever that is.

# THIS SCRIPT MAY BE LAUNCHED WITH . OR source OR sh OR bash.  

# Accommodate Linux versions that do not specify NUMBER_OF_PROCESSORS.
if [ -z "$NUMBER_OF_PROCESSORS" ]
then
    export NUMBER_OF_PROCESSORS=$(cat /proc/cpuinfo | grep processor | wc -l)
fi

# Turn debug tracing off completely to save CPU time.
export TRACE_LEVEL=
export TRACE_PRODUCTION=YES
# And start new runs as quickly as possible.  
export NPOLITE=1

echo "Browse to localhost:8080 to access the broker form."
if "$1" = "here"
then
    # Start it locally so I can track its use and stop it if necessary.
    python brokergroupform.py
else
    python brokergroupform.py >tmp/brokergroupform.log 2<&1 &
    # NOTE WELL: The ampersand runs the form program in a subprocess.
    #  To terminate the program, you must first bring it forward with 
    #  'fg' and then issue the control-C.
    # Sending the output to a log file makes the process detachable, I hope.
fi
echo "Use ctrl-z, fg, bg, and jobs to manipulate the web server."
echo "And ctrl-c to terminate it when it is the foreground job."
jobs

#END
