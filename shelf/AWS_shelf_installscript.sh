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
#

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
# The MongoDB instance stores its data files in /var/lib/mongodb and its log files in /var/log/mongodb by default, and runs using the mongodb user account. 

echo "**************************************** Installing zip and perf tools"
sudo apt-get --yes install unzip 
sudo apt-get --yes install zip
sudo apt-get --yes install htop
sudo apt-get --yes install sysstat

echo "**************************************** END INSTALLS"

echo "**************************************** Make new instructions db"
olddir=$(pwd)
cd shelf/newinstructions
cp newdblists.RENAMETOzip newdblists.zip
unzip -o newdblists.zip 
# This next step might take several minutes.  No kidding.  
#  Go get coffee.
cp newdb20160124.big newdb20160124.txt
python loadintodb.py newdb20160124 pending newdb20160124.txt
cd "$olddir"

echo "**************************************** Quick setup and simple test"
# Quick setup and test of directories.
cd shelf
# Remove any leftovers from possible previous deployment.
sudo rm --force --recursive ../Q3
bash setupfamilydir.sh ../Q3 . 
bash emptygiantoutput.sh  ../Q3 .
bash pretestchecklist.sh ../Q3 . 
# Run one simple test of the simulation, and check the answer.
sudo rm --force --recursive tmp
mkdir tmp
python main.py ../Q3 . 0 1 --ncopies=1 --lifek=693147 --audit=0 >tmp/initialtest.log 2>&1
# The correct answer should be   "BAD NEWS: Total documents lost by 
#  client |T1| in all servers |49|".
# (The crazy half-life number in the command is 1,000,000 * ln(2), 
#  which is the half-life that corresponds to 1 million khour 
#  mean lifetime.)
nTestLost=$(grep NEWS tmp/initialtest.log |awk '{print $16}' |sed 's/|//g')
if [ "$nTestLost" -eq 49 ]
then
    echo "SUCCESS: Initial test okay!"
    echo "Proceeding..."
else
    echo "ERROR: Initial test failed!"
    echo "STOPPING here."
    exit 1
fi

echo "**************************************** Test instructions db"
# Broker should find test cases to run.
python broker.py newdb20160124 pending done --glitchfreq=30000 --auditfreq=10000   --listonly >tmp/brokertest.log 2>&1
nTestCases=$(grep "run|" tmp/brokertest.log | tail -1 | sed 's/.*run|//' | sed 's/|.*//')
if [ "$nTestCases" -eq 1512 ]
then
    echo "SUCCESS: broker and instruction db look okay!"
    echo "Proceeding..."
else
    echo "ERROR: broker and instruction db test failed!"
    echo "STOPPING here."
    exit 1
fi

echo "**************************************** Test broker"
# Until we expand to larger quarters, don't run too many cores at once.  
#  Xeon isn't *that* fast.  Adjust as needed.  
#export NCORES=2        # Adjust this number, or remove for default.
python broker.py newdb20160124 pending done --familydir=../Q3 --specificdir=. --auditfreq=2500 --glitchfreq=30000 --glitchimpact=100 --glitchdecay=0 --glitchmaxlife=0 --lifem='{"$gte":10,"$lte":1000}' --testlimit=4 

# If everything looks okay, remove or raise the --testlimit, 
#  raise the NCORES limit, and probably lower the NPOLITE interval,
#  and let 'er rip.  
#export NCORES=32       # Max 32 cores on Amazon.
#export NPOLITE=2       # Wait 2 seconds between process end and start another.  
#python broker.py newdb20150724glitch100 pending done --familydir=../Q3 --specificdir=. --auditfreq=2500 --glitchfreq=50000 --glitchimpact=100 --glitchdecay=0 --glitchmaxlife=0 --lifem='{"$gte":10,"$lte":1000}' 

echo "**************************************** Done initial tests"
echo "**************************************** Build latest instruction database"
cd newinstructions
bash makecompletetemplate.sh q3instructiontemplate.txt latestinstructions.big filter
python loadintodb.py latest pending latestinstructions.big
cd ..

echo "**************************************** Instruction db 'latest' available for use"

echo "**************************************** Create startup.sh script"
cd ~
cat >startup.sh <<EOF
. shelfenv/bin/activate
cd working/shelf
echo ""
echo "*** Ready to run 'shelf' simulations.                ***"
echo "*** The shelfenv virtualenv should be activated,     ***"
echo "*** and the correct directory should be set.         ***" 
echo "*** Try   python main.py -h                          ***"
echo "*** or    python broker.py -h                        ***" 
echo "*** for help.                                        ***"
echo "*** HowTo info can be found in the 'docs' directory. ***"
echo ""
EOF

echo "**************************************** "
echo "*** To begin the shelf simulations,  *** "
echo "*** enter the command:               *** "
echo "***      . startup.sh                *** "
echo "*** (Yes, that is                    *** "
echo "***     dot space startup.sh )       *** "
echo "***                                  *** "
echo "*** Happy hunting!                   *** "
echo "***                                  *** "
echo "**************************************** "
echo ""
echo "**************************************** DONE!"

#END
