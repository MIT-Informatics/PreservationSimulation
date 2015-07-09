#!/usr/bin/python
# mongolib.py
# ideas from http://api.mongodb.org/python/current/tutorial.html

'''
Interface of a few convenience functions for using pymongo.  
- OpenDb (someone else has already started the mongod server)
- ClearCollection: remove data from a collection in db
- PutFileToDb: add CSV (or blank, tab, etc.) data to db
- PutIterToDb: add any iterable file to db
- NotIgnoreLine: used to filter blank and comment lines from input file
- IntPlease: convert string to int if possible
- GetSet: find in db collection (table) using some criteria in dict
- GetPendingWork: generate items from pending table that are not in done table
(more to come)
'''

from NewTraceFac import ntrace,ntracef,NTRC
NTRC.ntrace(3, "Importing...")
from pymongo import MongoClient
import re
import sys
import itertools

@ntrace
def fnoOpenDb(mysDbName):
    client = MongoClient('localhost', 27017)
    db = client[mysDbName]         # Create db if not already there.
    NTRC.ntrace(3, "Connected to db.")
    return db

@ntrace
def fniClearCollection(myoDb,mysCollectionName):
    myoDb[mysCollectionName].remove()    # Clear outmoldy, old records. 
    NTRC.ntrace(3, "Cleared collection {}.".format(mysCollectionName))
    return myoDb[mysCollectionName].count()

@ntrace
def fnsGetFilename():
    if len(sys.argv) < 2:
        print "Usage: {} <filename> (required)".format(sys.argv[0])
        exit(1)
    return sys.argv[1]

@ntrace
def fniPutFileToDb(mysFilename, mysSeparator, myoCollection):
    '''
    Open file to iterable, then use that to add file to db.
    '''
    # Store fresh, new records into the collection.
    with open(mysFilename, "r") as fhInfile:
        NTRC.ntrace(3, "File {} opened.".format(mysFilename))
    
        nRec = fnnPutIterToDb(fhInfile,mysSeparator,myoCollection)
    return nRec

@ntrace
def fnbNotIgnoreLine(mysLine):
    # Ignore comment and blank lines.
    return (not re.match("^\s*#",mysLine)) and (not re.match("^\s*$",mysLine))

def fnIntPlease(myString):
    # If it looks like an integer, make it one.
    try:
        return int(myString)
    except ValueError:
        return myString

@ntrace
def fnnPutIterToDb(myitHandle,mysSeparator,myoCollection):
    '''
    Get lines of file from iterable, add to db.
    First line of file is header with field names.
    '''
    nNewRecs = 0
    lNames = []
    for sLine in itertools.ifilter(fnbNotIgnoreLine, myitHandle):
        # The first line is header containing field names.
        # All other lines are data.
        if lNames == []:
            lNames = sLine.strip().split(mysSeparator)
            NTRC.ntrace(3, "proc field names|{}|".format(lNames))
            continue
        lValues = map(fnIntPlease, sLine.strip().split(mysSeparator))
        # Combine names and values into a list, then into a dict.
        dLine = dict(zip(lNames,lValues))
        NTRC.ntrace(3, "proc line dict|{}|".format(dLine))
        # Store new record into db table (pardon me, collection).
        oNewID = myoCollection.insert_one(dLine).inserted_id
        nNewRecs += 1
        NTRC.ntrace(3, "proc stored line n|{}| post_id|{}|".format(nNewRecs, oNewID))
    NTRC.ntrace(3, "proc lines stored|{}|".format(myoCollection.count()))
    return myoCollection.count()

@ntrace
def fngGetSet(myoDb, mysCollectionName, mydCriteria={}):
    oCollection = myoDb[mysCollectionName]
    for dItem in oCollection.find(mydCriteria):
        yield dItem

@ntrace
def fngGetPendingWork(myoDb, mydCriteria):
    oWorkCollection = myoDb['pending']
    oDoneCollection = myoDb['done']
    
    # TODO: check here that the instruction is not already done.  
    #  This doesn't work as written now because I don't have the 
    #  item available to add to the done collection.
    #  Will have to use the str value of the _id to compare
    #  by converting the string back into an bson.ObjectId.  
    #  Oh, this is a mess.  
    yield itertools.ifilter(lambda item: item not in oDoneCollection, \
            fngGetSet(oWorkCollection,mydCriteria))


def main2(mysDbName):
    oDb = fnoOpenDb(mysDbName)
    for dItem in fngGetPendingWork(oDb, {}):
        print dItem

def main(mysDbName, mysCollectionName):
    oDb = fnoOpenDb(mysDbName)
    betterbezero = fniClearCollection(oDb, mysCollectionName)

    sFilename = fnsGetFilename()
    oCollection = oDb[mysCollectionName]
    nRecordCount = fniPutFileToDb(sFilename, " ", oCollection)
    dTmp = oCollection.find_one()
    NTRC.ntrace(0,"======\n{}\n======".format(dTmp))
    NTRC.ntrace(0,"nRecs stored|{}|".format(nRecordCount))


if __name__ == "__main__":
    NTRC.ntrace(0,"Begin...")

    sDbName = "test_database"
    sCollectionName = "t3"
    main(sDbName, sCollectionName)

    NTRC.ntrace(0,"End.")


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

#END
