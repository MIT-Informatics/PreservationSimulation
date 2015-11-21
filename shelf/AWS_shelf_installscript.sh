#!/bin/bash 
# AWS_shelf_installscript.sh
#               RBLandau 20151109
#
# Until we succeed in docker-izing this application, it must
#  be installed semi-automatically on an Ubuntu server.
#  Takes only a couple minutes on AWS Ubuntu.
#
# 20150727.1700
# 20150829.1530
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
#

echo "**************************************** Get Python packages"
# Get python packages
sudo apt-get --yes install python-pip
sudo apt-get update
sudo apt-get --yes install python-pip
sudo pip install --upgrade pip
sudo pip install virtualenv
sudo pip install simpy
sudo pip install pymongo
sudo apt-get --yes install build-essential python-dev

echo "**************************************** Install git and pull source code"
# Get Git.
sudo apt-get update
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
cd newinstructions
unzip newdblists.zip 
# This next step will take ten or fifteen minutes.  No kidding.  
#  Go get coffee.
python loadintodb.py newdb20150724glitch100 pending newdb20150724glitch100.txt

echo "**************************************** Quick setup and test"
# Quick setup and test of directories.
cd shelf
bash setupfamilydir.sh ../Q3 . 
bash emptygiantoutput.sh
bash pretestchecklist.sh
# Run one simple test of the simulation, and check the answer.
mkdir tmp
python main.py ../Q3 . 0 1 --ncopies=1 --lifek=1000000 --audit=0 >tmp/initialtest.log 2>&1
# The correct answer should be   "BAD NEWS: Total documents lost by client |T1| in all servers |49|"
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
cd ..
python broker.py newdb20150724glitch100 pending done --familydir=../Q3 --specificdir=. --auditfreq=2500 --glitchfreq=50000 --glitchimpact=100 --glitchdecay=0 --glitchmaxlife=0 --lifem='{"$gte":10,"$lte":1000}' --testlimit=2 --listonly=Y
# Should be 1134 cases to run.

echo "**************************************** Test broker"
# Until we expand to larger quarters, don't run too many at once.  
#  Xeon isn't *that* fast.
export NCORES=2
python broker.py newdb20150724glitch100 pending done --familydir=../Q3 --specificdir=. --auditfreq=2500 --glitchfreq=50000 --glitchimpact=100 --glitchdecay=0 --glitchmaxlife=0 --lifem='{"$gte":10,"$lte":1000}' --testlimit=4 --listonly=N

# If everything looks okay, remove or raise the --testlimit, 
#  raise the NCORES limit, and probably lower the NPOLITE interval,
#  and let 'er rip.  
#python broker.py newdb20150724glitch100 pending done --familydir=../Q3 --specificdir=. --auditfreq=2500 --glitchfreq=50000 --glitchimpact=100 --glitchdecay=0 --glitchmaxlife=0 --lifem='{"$gte":10,"$lte":1000}' --listonly=N

echo "**************************************** Done initial tests"

#END
