#!/bin/bash
# start_brokerform.sh
#                       RBLandau 20170318
# Script to launch the broker web form.
# THIS MAY BE LAUNCHED WITH . OR source OR sh OR bash.  

# Turn debug tracing off completely to save CPU time.
export TRACE_LEVEL=
export TRACE_PRODUCTION=YES

echo "Browse to localhost:8080 to access the broker form."
python brokergroupform.py

#END
