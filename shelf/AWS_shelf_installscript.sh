#!/bin/bash 
# AWS_shelf_installscript.sh
#               RBLandau 20151109
#
# Until we succeed in docker-izing this application, it must
#  be installed semi-automatically on an Ubuntu server.
#  Takes only a couple minutes on AWS Ubuntu Server 14.04.3 LTS.
#
# 20150727.1700 First draft.
# 20150829.1530 Reorganize and comment.
# 20151113.1700 Add alias sh=bash to avoid problems with if-test
#                in scripts.  Grumble.  
# 20151113.1725 Nope, that doesn't work.  Change every sh foo
#                to bash foo.  Two grumbles.
# 20151114.0900 Add --yes options to the several apt-get installs
#                to avoid interactive prompts during the installation.  
# 20151121.1200 Add correctness test for initial simple simulation
#                test.  
#               Reorder some sections that were mistakenly 
#                in the wrong order, e.g., load db before 
#                initial test and possible exit.  
# 20151203.1800 Change single-run test to reflect re-scaling from 
#                mean exponential lifetime to half-life of sectors.
# 20151215.1700 Fix broker invocation commands to reflect new
#                y/n debug options.
# 20160119.1005 Fix changing to newinstructions dir and back.
#               Empty, if necessary, and rebuild output dir (../Q3 .).
#               Fix setup, empty, and pretest commands for new non-defaults.
#               Remove restriction on number of cores.
#               Force unzip to overwrite any leftovers.  
#               (If one uses sudo too much, some dirs end up owned 
#                by user=root and therefore cannot be used by 
#                user=ubuntu, oops.)
#               Don't use pushd, which doesn't exist in the bash shell, 
#                which, btw, is not the default.  More grumbling.
# 20160121  RBL Update apt-get before installing pip.  
# 20160123  RBL Reorganize to operate with lower privilege; remove as many
#                sudo calls as possible. Install everything (that can be) 
#                into a virtualenv.
#               Change "source" back to "." because vanilla sh doesn't 
#                have that verb.  Even more grumbling.  
# 20160204  RBL Add to end: build latest instruction db based on files
#                we just got from github.
# 20160205  RBL Add to end: create little shell script for users to 
#                begin work: activate shelfenv and goto shelf dir.
# 20160227  RBL Use hlinstructiontemplate.txt to build latest instr db
#                instead of q3... because of added param glitchspan.
#               In startup.sh, remind user about changing NCORES and NPOLITE.
# 20160228  RBL Harden a couple shell-if tests against empty strings.
#               Remove now-redundant emptygiantoutput call after setup.
# 20170130  RBL Change for new instruction location, and no need to build.
#               Change test familydir from ../Q3 to ../hl.
#               Change broker tests and examples.  
# 20170319  RBL Install jinja2 package for python.
#               Fix broker tests for new instruction generation.
#               Start the brokerform web app in the startup script.
#               Remove mentions of NCORES since broker now adapts to
#                the number of cores available
#               Add calc of number of cores to startup.sh script.
#               Add broker test3 that looks for correct resultof a single run,
#                from broker command all the way through to GiantOutput data.
# 20170420  RBL Add comments about not running this script with sudo.
#               Add setting NPOLITE to startup.  
# 20170610  RBL Fix broker test 3 to wait for the GiantOutput file to
#                contain something before trying to tail and analyze
#                the last line.  
# 20180409  RBL Fix all broker tests to include new --simlen=0 option.
#               Add new CLEAROLD option to erase previous installation.
# 20181001  RBL Add reminder to set the default number of documents for 
#                shocks vs normal runs before setting up directory
#                for runs.  
# 20181022  RBL Add now-required arg for start_brokerform.sh, oops.
# 20181113  RBL Change NPOLITE timer, now used for nCoreTimer in broker2.  
#                Do not override the default.  
# 20181127  RBL Turn on millisecond trace printing for broker2.  
# 
# 

if [ -n "$1" -a "$1" != "CLEAROLD" -a "$1" != "TESTING" ]
then
    echo "Usage: $0 [CLEAROLD]    (note: upper case)"
    echo "Optional CLEAROLD will completely erase any previous installation"
    echo " in the working/ and shelfenv/ directory trees."
    echo " Use this option with extreme caution."
    echo " E.g., have you retrieved all the data and log files?"
    exit 1
fi
if [ -n "$1" -a "$1" = "TESTING" ]
then
    echo "rm -rf working/"
    echo "rm -rf shelfenv/"
    echo "If I had actually done those commands, you would behosed.  Your data would be gonzo."
    exit 1
fi
if [ -n "$1" -a "$1" = "CLEAROLD" ]
then
    rm -rf working/
    rm -rf shelfenv/
    echo "Old installation cleared."
fi

echo "============================================"
echo "   DO ***NOT*** RUN THIS SCRIPT WITH SUDO   "
echo "============================================"

echo "**************************************** Beginning installation"
echo ""
echo "**************************************** Get Python packages"
# Get python packages
sudo apt-get update
sudo apt-get --yes install build-essential python-dev
sudo apt-get --yes install python-pip
sudo pip install --upgrade pip
sudo apt-get install python-virtualenv
# Restrict python packages to this user, to operate with lower privilege.
virtualenv shelfenv
. shelfenv/bin/activate
pip install simpy
pip install pymongo
pip install jinja2
sudo pip3 install pymongo

echo "**************************************** Install git and pull source code"
# Get Git.
sudo apt-get --yes install git
# Setup working directory with files from github.
mkdir working
cd working
git init
git pull https://github.com/MIT-Informatics/PreservationSimulation.git

echo "**************************************** Installing MongoDB"
# Installing mongodb is a little tricky.
# Google "install mongodb on ubuntu" and read it.
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
# The MongoDB instance stores its data files in /var/lib/mongodb 
#  and its log files in /var/log/mongodb by default, 
#  and runs using the mongodb user account. 
# Ubuntu starts MongoDB as a daemon (mongod).

echo "**************************************** Installing zip and perf tools"
sudo apt-get --yes install unzip 
sudo apt-get --yes install zip
sudo apt-get --yes install htop
sudo apt-get --yes install sysstat

echo "**************************************** END INSTALLS"
echo ""

echo "**************************************** Quick setup and simple test"
# Quick setup and test of directories.
cd shelf
# Remove any leftovers from possible previous deployment.
sudo rm --force --recursive ../hl
bash setupnumberofdocs.sh NORMAL
bash setupfamilydir.sh ../hl a0 
bash pretestchecklist.sh ../hl a0 

# M A I N   T E S T   1 
# Run one simple test of the simulation, and check the answer.
sudo rm --force --recursive tmp
mkdir tmp
python main.py ../hl a0 0 1 --ncopies=1 --lifek=693147 --audit=0 --ndocuments=10000 --smalldoc=50 --largedoc=50 --pctsmalldoc=0 >tmp/initialtest.log 2>&1
# The correct answer should be   "BAD NEWS: Total documents lost by 
#  client |T1| in all servers |49|".
# (The crazy half-life number in the command is 1,000,000 * ln(2), 
#  which is the half-life that corresponds to 1 million khour 
#  mean lifetime.)
nTestLost=$(grep NEWS tmp/initialtest.log |awk '{print $16}' |sed 's/|//g')
if [ -n "$nTestLost" -a "$nTestLost" -eq 49 ]
then
    echo "SUCCESS: Initial test okay!"
    echo "Proceeding..."
else
    echo "ERROR: Initial test failed!"
    echo "STOPPING here."
    exit 1
fi

echo "**************************************** Test broker CLI and instruction db"
# Set a plausible number of cores if the environment won't tell us.
if [ -z "$NUMBER_OF_PROCESSORS" ]
then
    export NUMBER_OF_PROCESSORS=$(cat /proc/cpuinfo | grep processor | wc -l)
fi

# B R O K E R   T E S T   1 
# Broker should find exactly one test case to run.
python3 broker2.py installtest done --familydir=../hl --specificdir=a0 \
    --serverdefaultlife=0 --glitchfreq=0 --shockfreq=0 \
    --ncopies=1 --lifem=1000 --auditfreq=0 \
    --docsize=50 --ndocuments=10000 --shelfsize=1 --simlen=0 --nseeds=1 \
    --redo --listonly > tmp/brokertest.log 2>&1
# The number of the last case should be "1.1".
sTestCases=$(grep "run|" tmp/brokertest.log | tail -1 | sed 's/.*run|//' | sed 's/|.*//')
if [ -n "$sTestCases" -a "$sTestCases" = "1.1" ]
then
    echo "SUCCESS: broker/instructions test case 1 looks okay!"
    echo "Proceeding..."
else
    echo "ERROR: broker/instructions test case 1 failed!"
    echo "STOPPING here."
    exit 1
fi

# B R O K E R   T E S T   2 
# And fifteen cases here.
python3 broker2.py installtest done --familydir=../hl --specificdir=a0 \
    --serverdefaultlife=0 --glitchfreq=0 \
    --ncopies='{"$gte":1,"$lte":5}' --lifem='[100,200,300]' \
    --auditfreq=10000 --audittype=TOTAL --auditsegments='[1]' \
    --docsize=50 --ndocuments=10000 --shelfsize=1 --simlen=0 --nseeds=1 \
    --redo --listonly  >tmp/brokertest.log 2>&1
sTestCases=$(grep "run|" tmp/brokertest.log | tail -1 | sed 's/.*run|//' | sed 's/|.*//')
if [ -n "$sTestCases" -a "$sTestCases" = "15.1" ]
then
    echo "SUCCESS: broker/instructions test case 2 looks okay!"
    echo "Proceeding..."
else
    echo "ERROR: broker/instructions test case 2 failed!"
    echo "STOPPING here."
    exit 1
fi

echo "**************************************** Test broker result"
# B R O K E R   T E S T   3 
# And one right answer here.
sudo rm --force --recursive ../hl
bash setupfamilydir.sh ../hl installtest
bash pretestchecklist.sh ../hl installtest
python dbclearcollection.py installtest done
python3 broker2.py installtest done --familydir=../hl --specificdir=installtest \
    --ncopies=1 --lifem=1000 --auditfreq=0 --auditsegments=0 \
    --audittype=TOTAL --glitchfreq=0 --glitchimpact=0 \
    --glitchdecay=0 --glitchmaxlife=0 --glitchspan=0 \
    --serverdefaultlife=0 --shockfreq=0 --shockimpact=0 \
    --shockmaxlife=0 --shockspan=0 --shelfsize=1 \
    --docsize=50 --ndocuments=10000 --simlen=0 --nseeds=1 --redo 
sResultFile="../hl/installtest/dat/GiantOutput_00.txt"
nWaitTime=5
while true
do
    if [ -s "$sResultFile" ]
    then
        sDataLine=$(tail -1 "$sResultFile")
        sField1=$(echo $sDataLine | cut -d " " -f 1)
        if [ ! "$sField1" = "timestamp" ]
        then
            break               # Data line has been written.
        fi
    else
        echo "Waiting $nWaitTime sec. . . "
        sleep "$nWaitTime"
    fi
done
sSeed=$(echo $sDataLine | cut -d " " -f 7)
sLost=$(echo $sDataLine | cut -d " " -f 8)
if [ -n "$sSeed" -a "$sSeed" = "919028296" -a -n "$sLost" -a "$sLost" = "42" ]
then
    echo "SUCCESS: broker/results test case 3 looks okay!"
    echo "Proceeding..."
else
    echo "ERROR: broker/results test case 3 failed!"
    echo "STOPPING here."
    exit 1
fi

# Clean out Mongo databases.
python dbclearcollection.py installtest done
# And set up new working directories for these runs.  
bash setupfamilydir.sh ../hl testing
python3 broker2.py installtest done --familydir=../hl \
    --specificdir=testing --serverdefaultlife=0 --glitchfreq=0 \
    --ncopies='{"$gte":1,"$lte":5}' --lifem='[100,200,300]' \
    --auditfreq=10000 --audittype=TOTAL --auditsegments=1 \
    --docsize=50 --ndocuments=10000 --shelfsize=1 --nseeds=2 \
    --redo --testlimit=4 

# If everything looks okay, remove or raise the --testlimit, 
#  raise the NCORES limit, and probably lower the NPOLITE interval,
#  and let 'er rip.  
#export NCORES=32       # Max 32 cores on Amazon.
#export NPOLITE=1       # Wait 2 seconds between process end and start another. 
# This command will run thirty individual simulation tests, which will take
#  more than a couple minutes. 
#python3 broker2.py inprogress done --familydir=../hl --specificdir=testing --serverdefaultlife=0 --glitchfreq=0 --ncopies='{"$gte":1,"$lte":5}' --lifem='[100,200,300]' --auditfreq=10000 --audittype=TOTAL --auditsegments=1 --nseeds=20 --redo 

echo "**************************************** Done initial tests"

echo "**************************************** Create startup.sh script in ~"
cd ~
cat >startup.sh <<\EOFEOF
if [ -z "$NUMBER_OF_PROCESSORS" ]
then
    export NUMBER_OF_PROCESSORS=$(cat /proc/cpuinfo | grep processor | wc -l)
fi
. shelfenv/bin/activate
export NPOLITE=20
export TRACE_TIME=Y
cd working/shelf
bash start_brokerform.sh detached $NPOLITE 
bash brokercommandlog_enable.sh

echo ""
echo "********************************************************"
echo "*** Ready to run 'shelf' simulations.                ***"
echo "***  The shelfenv virtualenv should be activated,    ***"
echo "***  the correct directory should be set,            ***" 
echo "***  and the broker web application running          ***" 
echo "***  on localhost:8080.                              ***" 
echo "***                                                  ***" 
echo "***  The simulation broker will exploit all the      ***" 
echo "***   CPU cores (and hyperthreads) available.        ***" 
echo "***   The number of cores available is sensed        ***" 
echo "***   automatically, but you may wish to impose      ***" 
echo "***   a lower limit on CPU use.                      ***" 
echo "***  Example:                                        ***" 
echo "***      export NCORES=8                             ***" 
echo "***  or similar, appropriate values.                 ***" 
echo "***                                                  ***" 
echo "*** The easiest intro is to browse to localhost:8080 ***" 
echo "***  (or to someipaddress:8080 from another system)  ***" 
echo "***  and fill out the form (and leave the TESTONLY   ***" 
echo "***  box checked).  This way, you can see the set    ***" 
echo "***  of runs that will be executed for a given range ***" 
echo "***  of your instructions.                           ***" 
echo "***                                                  ***" 
echo "*** For those who like typing CLI commands,          ***" 
echo "***  try   python main.py -h                         ***"
echo "***  or    python3 broker2.py -h                     ***" 
echo "*** for help.                                        ***"
echo "***                                                  ***" 
echo "***    I M P O R T A N T  R E M I N D E R            ***" 
echo "***                                                  ***" 
echo "*** If you are simulating for SHOCKS ONLY,           ***" 
echo "***  remember to set the number of documents         ***" 
echo "***  down with the command                           ***" 
echo "***     bash setupnumberofdocs.sh SHOCK              ***" 
echo "*** Otherwise, you waste a *lot* of CPU time         ***" 
echo "***  moving empty docs around for no benefit.        ***" 
echo "*** This must be done *before* setting up the        ***" 
echo "***  output directory for a run.                     ***" 
echo "***                                                  ***" 
echo "*** HowTo info can be found in the 'docs' directory. ***"
echo "********************************************************"
echo ""
EOFEOF

echo "**************************************** I N S T R U C T I O N S"
echo "**************************************** "
echo "*** To begin the shelf simulations,  *** "
echo "*** enter the command:               *** "
echo "***                                  *** "
echo "***      . startup.sh                *** "
echo "***                                  *** "
echo "*** (Yes, that is                    *** "
echo "***     dot space startup.sh)        *** "
echo "***                                  *** "
echo "*** Happy hunting!                   *** "
echo "***                                  *** "
echo "**************************************** "
echo ""
echo "**************************************** DONE!"

#END
