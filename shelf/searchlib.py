#!/usr/bin/python
# searchlib.py
# 
# 

'''
New theory for searchspace database rather than MongoDB: 
keep everything in a dictionary and back that up in a json file.
dict entry
    { str(id_key) : (str(instruction dict), timestamp when executed )}
    or maybe
    { str(id_key) : (instruction dict, timestamp when executed )}
e.g., 
    { 'efa338427818683d045cfb17e553810570c26195_3' : ( "'nShockSpan': 0, 
    'sAuditType': 'TOTAL', 'nAuditFreq': 0, 'nGlitchFreq': 0, 
 ...
    'nGlitchImpact': 0, 'nShockImpact': 0, 'nGlitchDecay': 0, 
    '_id': 'efa338427818683d045cfb17e553810570c26195_3'", 
    "20170118_002355")}
Note that getting the instruction dict requires a change to the signature.

Write the file every time a dictionary entry is entered or deleted:

We may still need a ClearCollection utility.
We can get rid of all the template expansion foolishness in newinstructions,
and quit worrying about toobig files.
We can get rid of the filtering foolishness that was hard to get just so, that
cried out for a comprehensive unittest that I never got around to writing.  
So rename newinstructions to OLDnewinstructions and let it rust.  
'''

from NewTraceFac import ntrace,ntracef,NTRC
import re
import sys
import itertools
import json
import copy
import os
import filelock
import time

# Always start the day with an empty database.
dDb = dict()
# WARNING: There is no error checking in this module, very fool-vulnerable.  


# f n d R e a d R e t r y L o c k 
def fndReadRetryLock(mysDbFilename, mynRetries=60):
    ''' 
    Read a json dict from file, with retries for file locking errors.
    FileLock does not seem to work perfectly on Windows/Cygwin, 
    so lets retry it a bunch of times before we give up entirely.
    '''
    while True:
        try:
            with open(mysDbFilename, 'r') as fh:
                dWhatever = json.load(fh)
                break       # When we get valid json, done.
        except:
            if mynRetries <= 0:
                raise 
        mynRetries -= 1
        time.sleep(1)
    return dWhatever

# f n o O p e n D b 
@ntracef("SRLB")
def fnoOpenDb(mysDbFilename):
    '''
    If the db file exists, read it.  If not, write an empty copy.
    '''
    global sDbName
    sDbName = mysDbFilename
    
    # First, make sure there is a place to put our file.
    sDirName = os.path.dirname(mysDbFilename)
    if not os.path.isdir(sDirName):
        os.mkdir(sDirName)
    
    if os.path.isfile(mysDbFilename) and os.path.getsize(mysDbFilename) > 0:
        NTRC.ntracef(3, "SRLB", "proc open json for read|%s|" 
            % (mysDbFilename))
        """
        with filelock.FileLock(mysDbFilename):
            # File present, try to read it as json.  
            fh = open(mysDbFilename, "r") 
            sDbContent = "".join(fh.readlines())
            NTRC.ntracef(3, "SRLB", "proc file content|%s|" 
                % (sDbContent))
            try: 
                dDb = json.loads(sDbContent)
            except ValueError:
                raise ValueError(("Error: file|%s| is not valid JSON" 
                    % (mysDbFilename)))
        """
        with filelock.FileLock(mysDbFilename):
            dDb = fndReadRetryLock(mysDbFilename)
    else:
        # File not there yet, write it.
            try:
                NTRC.ntracef(3, "SRLB", "proc open json for write|%s|" 
                    % (mysDbFilename))
                with filelock.FileLock(mysDbFilename):
                    fh = open(mysDbFilename, "wb") 
                    dDb = copy.deepcopy(dDbEmpty)
                    json.dump(dDb, fh)
            except IOError:
                raise IOError(("Error: cannot create new json file|%s|" 
                    % (mysDbFilename)))
    return dDb

# f n v C l e a r C o l l e c t i o n 
@ntracef("SRLB")
def fnvClearCollection(mysCollectionName):
    dDb[mysCollectionName] = {}

# f n i C o l l e c t i o n C o u n t 
@ntracef("SRLB")
def fniCollectionCount(mysCollectionName):
    with filelock.FileLock(sDbName):
        dDb = fndReadRetryLock(sDbName)
        return (len(dDb[mysCollectionName].keys()) 
            if mysCollectionName in dDb.keys() 
            else 0)

# f n s G e t F i l e n a m e 
@ntracef("SRLB")
def fnsGetFilename():
    return sDbName

@ntracef("SRLB")
def fniPutFileToDb(mysFilename, mysSeparator, myoCollection):
    raise NotImplementedError

# f n b N o t I g n o r e L i n e 
@ntracef("SRLB")
def fnbNotIgnoreLine(mysLine):
    ''' True if real line, i.e., not comment or blank line. '''
    return (not re.match("^\s*#",mysLine)) and (not re.match("^\s*$",mysLine))

# f n I n t P l e a s e 
@ntracef("SRLB")
def fnIntPlease(myString):
    ''' If it looks like an integer, make it one. '''
    try:
        return int(myString)
    except ValueError:
        return myString

@ntracef("SRLB")
def fnnPutIterToDb(myitHandle,mysSeparator,myoCollection):
    raise NotImplementedError
    return 'count of collection that got added to or maybe of records added'

@ntracef("SRLB")
def fngGetSet(myoDb, mysCollectionName, mydCriteria={}):
    raise NotImplementedError

# f n v I n s e r t O n e 
@ntracef("SRLB")
def fndInsertOne(mysCollectionName, mysKey, mysVal):
    with filelock.FileLock(sDbName):
        dDb = fndReadRetryLock(sDbName)
        fh = open(sDbName, "wb")
        if mysCollectionName not in dDb.keys():
            dDb[mysCollectionName] = dict()
        dDb[mysCollectionName][mysKey] = mysVal
        json.dump(dDb, fh)
        return dDb[mysCollectionName]

# f n o G e t O n e 
@ntracef("SRLB")
def fnoGetOne(mysCollectionName, mysKey):
    with filelock.FileLock(sDbName):
        dDb = fndReadRetryLock(sDbName)
        if mysCollectionName in dDb and mysKey in dDb[mysCollectionName]:
            oVal = dDb[mysCollectionName][mysKey]
        else:
            oVal = None
        return oVal

# f n v D e l e t e O n e 
@ntracef("SRLB")
def fndDeleteOne(mysCollectionName, mysKey):
    with filelock.FileLock(sDbName):
        dDb = fndReadRetryLock(sDbName)
        fh = open(sDbName, "wb")
        if mysCollectionName in dDb and mysKey in dDb[mysCollectionName]:
            del dDb[mysCollectionName][mysKey]
        json.dump(dDb, fh)
        return dDb[mysCollectionName]

# f n v D e l e t e C o l l e c t i o n 
@ntracef("SRLB")
def fnvDeleteCollection(mysCollectionName):
    with filelock.FileLock(sDbName):
        dDb = fndReadRetryLock(sDbName)
        if mysCollectionName in dDb:
            fh = open(sDbName, "wb")
            del dDb[mysCollectionName]
            json.dump(dDb, fh)


sDbName = "./tmp/test1.json"
dDbEmpty =   {  "nocollection" : {"noentry" : "novalue"},  
                "progress" : {}, 
                "done" : {}
            }
dDb = dict()

''' Put the tests that used to be in main in a proper unittest. '''



##################### leftovers from mongo #######################
"""
Idioms for MongoDB: 

client = MongoClient()
print client.database_names()
db = client.test_database       # that's its name
print db.collection_names()
collection = db.collectionname  # creates it for you
collection.count()

collection.remove(partialdict)  # removes matching record(s)
collection.remove()             # removes all records
db.drop_collection('collectionname')    # nukes the collection
client.drop_database('databasename')    # nukes the database files

for foo,bar in (db.command({"dbstats":1})).items(): print foo,"     ",bar
for foo,bar in (db.command({"collstats":"posts"})).items(): print foo,"     ",bar

post = {"author": "Mike",
        "text": "My first blog post!",
        "tags": ["mongodb", "python", "pymongo"],
        "date": datetime.datetime.utcnow()}
posts = db.posts
post_id = posts.insert_one(post).inserted_id
post_id
db.collection_names(include_system_collections=False) [u'posts']
posts.find_one()
posts.find_one({"author": "Mike"})
posts.find_one({"author": "Eliot"})
post_id
posts.find_one({"_id": post_id})
post_id_as_str = str(post_id)
posts.find_one({"_id": post_id_as_str}) # No result
new_posts = [{"author": "Mike",
              "text": "Another post!",
              "tags": ["bulk", "insert"],
              "date": datetime.datetime(2009, 11, 12, 11, 14)},
             {"author": "Eliot",
              "title": "MongoDB is fun",
              "text": "and pretty easy too!",
              "date": datetime.datetime(2009, 11, 10, 10, 45)}]
result = posts.insert_many(new_posts)
result.inserted_ids

listx = posts.find({'name': {'$regex': "Mike"}})    # using match or search?
for post in posts.find():
    post
for post in posts.find({"author": "Mike"}):
    post

posts.count()
posts.find({"author": "Mike"}).count()

# update a record in place
person = people.find_one({'food':'ham'})
person['food'] = 'eggs'
people.save(person)

# clear out record
for person in people.find():
    people.remove(person)
    
# convert from id string back to searchable ObjectId
from bson.objectid import ObjectId
# The web framework gets post_id from the URL and passes it as a string
def get(post_id):
    # Convert from string to ObjectId:
    document = client.db.collection.find_one({'_id': ObjectId(post_id)})
"""

# Edit history:
# 20170120  RBL Original version.
# 20170122  RBL Windows/Cygwin file locking apparently does not fully work, 
#                so I may have to abandon this line of coding.  
#               Try adding the FileLock mechanism from Evan Fosmark that I 
#                found on stackoverflow.  Writes a temporary lockfile 
#                using os.open.  Seems to work.  
#                Well, after some testing, it may work well enough, on 
#                Windows, at least.  Extensive testing required.  
#               After considerable testing, the verdict is bad.  The FileLock
#                mechanism just doesn't work perfectly on Windows/Cygwin.  
#                Revert.  
# 20170123  RBL Well, try another approach to FileLock, doing retries of
#                the json conversion inside a retry loop.  If a writer 
#                sneaks in and changes it, we don't really care so long
#                as the result is correct syntactic json.  All of the 
#                insert/delete/get operations, at the level of the broker
#                and datacleanup utilities, are sort of idempotent.  
# 20170128  RBL After sad experience, this approach to file locking does 
#                not work on Windows 10, period.  Maybe some other variation
#                does, but I don't have the energy anymore.  Revert to MongoDB.
#               Ensure that there is a directory into which to put the
#                json file, according to the caller's filespec.  
# 
# 

#END
