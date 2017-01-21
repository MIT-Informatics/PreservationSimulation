#!/usr/bin/python
# searchlib.py
# 
# 
# ideas from http://api.mongodb.org/python/current/tutorial.html


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
    'nGlitchMaxlife': 0, 'nLifem': 1000, 'nShockMaxlife': 0, 
    'nCopies': 1, 'nGlitchIgnorelevel': 0, 'nGlitchSpan': 0, 
    'nAuditSegments': 0, 'nShockFreq': 0, 'nSimlen': 100000, 
    'nRandomseed': 141246882, 'nShelfSize': 1, 'nDocSize': 50, 
    'nServerDefaultLife': 0, 
    'sBaseId': 'efa338427818683d045cfb17e553810570c26195', 
    'nGlitchImpact': 0, 'nShockImpact': 0, 'nGlitchDecay': 0, 
    '_id': 'efa338427818683d045cfb17e553810570c26195_3'", 
    "20170118_002355")}
The string might be better than dict because it is immutable.  
Note that getting the instruction dict requires a change to the signature.

Question: do we need to keep DbName?  Since the pending list is calculated
from the user params at the instant rather than selected from a large
set calculated in advance, there really is no interesting db.  Hmmm.  

Write the file every time a dictionary entry is entered or deleted:
e.g., 
>>> dd = {1:11, 2:22}
>>> with open("tmp/test1.json", "w") as fh:
...   json.dump(dd,fh)

Read the file in if it's not already in memory:
e.g., 
>>> with open("tmp/test1.json", "r") as fh:
...  xx = json.load(fh)
...
>>> xx
{u'1': 11, u'2': 22}
landau@RicksYoga2 ~
$ cat tmp/test2.json
{"1": 11, "2": 22}
landau@RicksYoga2 ~
$ cat tmp/test1.json
{"1": 11, "2": 22}
landau@RicksYoga2 ~
#Note that the key is ALWAYS a string.
>>> xx[1]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
KeyError: 1
>>> xx['1']
11
>>>

Clear collection = write file with empty (approx) dict.

Open = read dict in.

GetFilename = e-z

PutFileToDb = for input dict, make entries in output dict.

PutIterToDb = much the same, I hope.

GetSet
GetPendingWork
Hmmm, tricky.  Perhaps we need to structure the json dict differently, with 
nested dictionaries for collections.  This is approximately what mongo feels
like.  
{
    str(collection name) : dictofitemsincollection, 
    str(another collection) : dict of those items
}
This way, both pending and done can remain in use.  
Dump all pending into the dict when we get the iterator from searchspace.
Put done items in when they occur.  Leave the pending items, as we do now.
E.g., 
{
    "pending" : {
                "id of first" : {instruction dict}, 
                "id of next" : {instruction dict}
                }
    "done" : {
                "id of first done" :    (
                                        "id",
                                        "timestamp"
                                        )
            }
}

We may still need a ClearCollection utility.
We probably won't need a LoadCollection utility.  
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


# Always start the day with an empty database.
dDb = dict()
# WARNING: no error checking in this module, very fool-vulnerable.  
# If you don't open the db, e.g., you will get nonsense.


# f n o O p e n D b 
@ntracef("SRLB")
def fnoOpenDb(mysDbFilename):
    '''
    If the db file exists, read it.  If not, write an empty copy.
    '''
    global sDbName
    sDbName = mysDbFilename
    if os.path.isfile(mysDbFilename) and os.path.getsize(mysDbFilename) > 0:
        NTRC.ntracef(3, "SRLB", "proc open json for read|%s|" 
            % (mysDbFilename))
        with open(mysDbFilename, "r") as fh:
            # File present, try to read it as json.  
            sDbContent = "".join(fh.readlines())
            NTRC.ntracef(3, "SRLB", "proc file content|%s|" 
                % (sDbContent))
            try: 
                dDb = json.loads(sDbContent)
            except ValueError:
                raise ValueError, ("Error: file|%s| is not valid JSON" 
                    % (mysDbFilename))
    else:
        # File not there yet, write it.
            try:
                NTRC.ntracef(3, "SRLB", "proc open json for write|%s|" 
                    % (mysDbFilename))
                with open(mysDbFilename, "w") as fh:
                    dDb = copy.deepcopy(dDbEmpty)
                    json.dump(dDb, fh)
            except IOError:
                raise IOError, ("Error: cannot create new json file|%s|" 
                    % (mysDbFilename))
    return dDb

# f n v C l e a r C o l l e c t i o n 
@ntracef("SRLB")
def fnvClearCollection(mysCollectionName):
    dDb[mysCollectionName] = {}

# f n i C o l l e c t i o n C o u n t 
@ntracef("SRLB")
def fniCollectionCount(mysCollectionName):
    with open(sDbName, "r") as fh:
        dDb = json.load(fh)
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
    with open(sDbName, "r") as fh:
        dDb = json.load(fh)
    with open(sDbName, "w") as fh:
        if mysCollectionName not in dDb.keys():
            dDb[mysCollectionName] = dict()
        dDb[mysCollectionName][mysKey] = mysVal
        json.dump(dDb, fh)
    return dDb[mysCollectionName]

# f n o G e t O n e 
@ntracef("SRLB")
def fnoGetOne(mysCollectionName, mysKey):
    with open(sDbName, "r") as fh:
        dDb = json.load(fh)
        if mysCollectionName in dDb and mysKey in dDb[mysCollectionName]:
            oVal = dDb[mysCollectionName][mysKey]
        else:
            oVal = None
    return oVal

# f n v D e l e t e O n e 
@ntracef("SRLB")
def fndDeleteOne(mysCollectionName, mysKey):
    with open(sDbName, "r") as fh:
        dDb = json.load(fh)
    with open(sDbName, "w") as fh:
        if mysCollectionName in dDb and mysKey in dDb[mysCollectionName]:
            del dDb[mysCollectionName][mysKey]
        json.dump(dDb, fh)
    return dDb[mysCollectionName]

# f n v D e l e t e C o l l e c t i o n 
@ntracef("SRLB")
def fnvDeleteCollection(mysCollectionName):
    with open(sDbName, "r") as fh:
        dDb = json.load(fh)
    if mysCollectionName in dDb:
        with open(sDbName, "w") as fh:
            del dDb[mysCollectionName]
            json.dump(dDb, fh)

@ntracef("SRLB")
def fngGetPendingWork(mydCriteria):
    raise NotImplementedError

@ntracef("SRLB")
def fnvFlushDb():
    # If I use with properly, this should not be necessary.
    pass

sDbName = "./tmp/test1.json"
dDbEmpty =   {  "nocollection" : {"noentry" : "novalue"},  
                "pending" : {}, 
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
# 
# 


#END
