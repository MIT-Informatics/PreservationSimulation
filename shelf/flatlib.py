#!/usr/bin/python
# flatlib.py
'''
JUST A PLACEHOLDER for how.  No actual meaningful content.  
Will eventually contain a parallel version of mongolib that 
 scans a flat file, once, in one pass.
 Mimic mongolib interface and CDatabase interface in broker, 
 but do it with a CSV-ish flat file.  Well, two, one for 
 pending and one for done, separate collections in separate files. 
I just dumped a bunch of code into here from other places to see
 how I did these things the first time. 

'''

import  re
import  os
import  csv
from    NewTraceFac     import NTRC,ntrace,ntracef
import  argparse
from    time            import clock,localtime



#===========================================================
# f n d P a r s e I n p u t 
@ntracef("INPT")
def fnldParseInput(mysFilename):
    ''' Return tuple containing
        - the output template string, 
        - a list, one item per line, of dicts of column args from the 
          csv that contain instructions for getting variable values
          from lines.  
        Beware duck-type integers that become strings.

        Format of csv lines:        
        varname,regex to find line,split word number,regex to strip out value

        instruction file format:

        ##becomes comment in output
        ###send out this string as header for the output, no hashes
        =outputformat
        format string
        =variables
        varname,lineregex,wordnumber,valueregex (header)
        (lines of csv data)

    '''
    dParams = dict()
    with open(mysFilename,"rb") as fhInfile:
        # Remove comments.  
        lLines = filter( lambda sLine:                          \
                        not re.match("^ *#[^#]",sLine)          \
                        and not re.match("^ *$",sLine.rstrip()) \
                        , fhInfile )

        # Get the output template.  It may be longer than one line.  
        lTemplate = fnlLinesInRange(lLines,"^=template","^=variables")
        lTemplate = map( lambda sLine: sLine.rstrip().replace("###","").replace("##","#"), lTemplate )
        NTRC.tracef(3,"INPT","proc ParseInput template|%s|" % (lTemplate))

        # Fix the separator in the template according to the user spec.
        lAllTemplateNames = [lTemplateLine.split() for lTemplateLine in lTemplate]
        lNewTemplate = [g.sSeparator.join(lTemplateNamesOneLine) \
            for lTemplateNamesOneLine in lAllTemplateNames]

        # Now get the CSV args into a dictionary of dictionaries.
        lVarLines = fnlLinesInRange(lLines,"^=variables","^=thiswillnotbefound")
        lRowDicts = csv.DictReader(lVarLines)
        NTRC.tracef(5,"INPT","proc ParseInput lRowDicts all|%s|" % (lRowDicts))
        
        dParams = dict( map( lambda dRowDict:   \
            (dRowDict["varname"],dRowDict)      \
            , lRowDicts ))

    return (lNewTemplate,dParams)

@ntracef("INPT")
def fnlLinesInRange(mylLines,mysStart,mysStop):
    ''' Return open interval of lines from start string to stop string
        excluding both ends.
    '''
    lResults = list()
    bCollect = False
    for sLine in mylLines:
        if re.match(mysStop,sLine):  bCollect = False
        if bCollect: lResults.append(sLine)
        if re.match(mysStart,sLine): bCollect = True
    return lResults

#===========================================================
# m a i n ( ) 
@ntracef("MAIN")
def main(mysInstructionsFileName,mysLogFileName):
    (lTemplate,g.dVars) = fnldParseInput(mysInstructionsFileName)
    lLines = list()
    with open(mysLogFileName,"r") as fhLogFile:

        '''\
        get list of tuples: lines that match some lineregex, for which var

        foreach line, 
            if matches any lineregex
                extract value, 
                put varname and value in dictionary

        be careful never to form a list of lines of the input log file, 
         or of anything that is big-O of that.  filter first.
        '''

        # Form list of all lines that match some var.
        nLineNr = 0
        lLinesSelectedRaw = list()
        for sLine in fhLogFile:
            nLineNr += 1                # Need line nr only for debugging.
            for sVarname in g.dVars.keys():
                tResult = fntDoesLineMatchThisVar(sLine, nLineNr, sVarname)
                # If line matches any var, save the line and the varname.
                if tResult[0]: 
                    lLinesSelectedRaw.append(tResult)
        NTRC.tracef(3,"MN2","proc lLinesSelectedRaw len|%s| all|%s|" % (len(lLinesSelectedRaw),lLinesSelectedRaw))

    # Eliminate duplicates.  Should not be any if the lineregexes are 
    #  specific enough.  
    lLinesSelected = list(set(lLinesSelectedRaw))
    NTRC.tracef(5,"MN3","proc lLinesSelected len|%s| all|%s|" % (len(lLinesSelected),lLinesSelected))

    # Extract variable value from each matching line.
    # List of lines selected is actually a list of triples.
    lResults = map( lambda (omatch, sLine, sVarname): 
                fntMatchValue(sLine, g.dVars[sVarname])
                , lLinesSelected )
    # Returned list of (name,val) tuples for vars in lines selected.
    #  Make a dictionary.  
    dValues = dict(lResults)

    # In case we did not find the line for a variable, dummy up a value.
    for sKey in g.dVars: 
        dValues.setdefault(sKey,"nolinefound")

    # And in case we didn't even find a rule for some variable that
    #  will be used in the template, dummy up a value for it, too.  
    sTemplateHeader = "\n".join(lTemplate).replace("{","").replace("}","").replace("\n"," ")
    lTemplateVars = sTemplateHeader.split()
    for sTemplateVar in lTemplateVars: 
        dValues.setdefault(sTemplateVar,"norulefound")

    # Add the synthetic variables to the value dictionary.
    dSyntho = fndGetSyntheticVars()
    dValues.update(dSyntho)

    # Fill in the template with values and print.  
    # Template is allowed to be multiple lines.
    sTemplate = "\n".join(lTemplate)
    sLineout = makeCmd(sTemplate,dValues)
    if g.bHeader or os.environ.get("header",None):
        # Header is a single line concatenation of all the substitutions
        #  in the template.
        #  If the template is longer than one line, well, you can't read 
        #  the data with a simple header anyway.  Oops.  
        sHeader = sTemplateHeader
        print sHeader
    # Newline already pasted on the end of template; don't add another.
    print sLineout,
    # Done.  

# f n t D o e s L i n e M a t c h T h i s V a r 
@ntracef("MCHT",level=5)
def fntDoesLineMatchThisVar(mysLine, mynLineNr, mysVarname):
    '''\
    Check line against lineregex of var.
    Return tuple (matchobject, line, varname).
    '''
    dVar = g.dVars[mysVarname]
    sLineregex = dVar["lineregex"]
    oMatch = re.search(sLineregex,mysLine)
    NTRC.tracef(5,"MTLN","proc MatchLine try regex|%s| var|%s| nr|%s| line|%s| match|%s|" % (sLineregex,mysVarname,mynLineNr,mysLine,oMatch))
    if oMatch:
        NTRC.tracef(3,"LINE","proc MatchLine found line|%s|=|%s| var|%s| regex|%s|" % (mynLineNr,mysLine,mysVarname,sLineregex))
    return (oMatch, mysLine, mysVarname)

# f n M a t c h V a l u e 
@ntracef("MCHV")
def fntMatchValue(mysLine,mydVar):
    '''\
    Extract value from line according to valueregex for var.
     If no value found, supply suitably disappointing string.  
    Get the right word from the line.
     If asked for word zero, use the whole line.  
     Makes the extraction harder, but sometimes necessary.
    '''
    sWordnumber = mydVar["wordnumber"]
    nWordnumber = int(sWordnumber)
    lWords = mysLine.split()
    if nWordnumber == 0:
        sWord = mysLine
    elif nWordnumber <= len(lWords):
        sWord = lWords[nWordnumber-1]
    else: 
        sWord = "nowordhere_indexoutofrange"
    sValueregex = mydVar["valueregex"]
    sVarname = mydVar["varname"]
    oMatch = re.search(sValueregex,sWord)
    NTRC.tracef(5,"MCHV","proc MatchValue matching word var|%s| word|%s| valueregex|%s| matchobj|%s|" % (sVarname,sWord,sValueregex,oMatch))
    if oMatch:
        # Word matches the valueregex.  Save the value.
        sValue = oMatch.group(1)
        NTRC.tracef(3,"MCHV","proc addvalue name|%s| val|%s|" % (sVarname,sValue))
    else:
        # If not found, at least supply something conspicuous for printing.
        sValue = "novaluefound"
    return (sVarname,sValue)

# f n d G e t S y n t h e t i c V a r s 
@ntracef("SNTH")
def fndGetSyntheticVars():
    dTemp = dict()

    dTemp["logfilename"] = g.sLogFileName
    dTemp["logfilesize"] =  os.stat(g.sLogFileName).st_size
    dTemp["instructionfilename"] = g.sInstructionsFileName

    (yr,mo,da,hr,mins,sec,x,y,z) = localtime()
    sAsciiT = "%4d%02d%02d_%02d%02d%02d" \
        % (yr,mo,da,hr,mins,sec)
    dTemp["todaysdatetime"] = sAsciiT

    dTemp["extractorversion"] = "0.5"

    return dTemp


# G l o b a l   d a t a 
class CG(object):
    bHeader = False
    sInstructionsFileName = "instructions.txt"
    sLogFileName = "logfile.txt"
    sSeparator = " "
    dVars = dict()
    

# M a i n   l i n e 
if "__main__" == __name__:
    g = CG()                # Global dict for options.
    # Read filename and options from cli
    dCliDict = fndCliParse("")
    dCliDictClean = {k:v for k,v in dCliDict.items() if v is not None}
    g.__dict__.update(dCliDictClean)
    timestart = clock()
    main(g.sInstructionsFileName,g.sLogFileName)
    timestop = clock()
#    NTRC.tracef(0,"MAIN","proc cputime|%s|" % (timestop-timestart))

# Edit history:
# 2014sometime  RBL Original version.
# 20150729  RBL Recode main loop entirely to avoid forming list of all lines.
#                (This required 800MB of RAM to process an 80MB log file, oops.)
#                Filter first to isolate the few lines that match any
#                lineregex, then you can take your time.  
#                Couldn't find a reasonable way to do this with all functional
#                forms without that giant list again.  
#
# 20150809  RBL Minor cleanup revisions.
#               Added a few comments, docstrings.  
#               After testing, this is about 2x faster than the original 
#                version, and uses an almost fixed <10MB of memory.  
# 

#END















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


# f n b D o e s L i n e M a t c h D i c t 
def fnbDoesLineMatchDict(mydLine,mydDict):
    '''\
    Return bool: does the dictionary of the line (from CSV or similar)
    match all key-value pairs of the criterion dictionary?
    
    Ignore the key 'action' if present.  
    '''
    bMatch = True
    for (key, val) in mydDict.items():
        if key != 'action':
            if mydLine[key] != val:
                bMatch = False
                break
    return bMatch

def fnbDoesLineMatchDict(mydLine,mydDict):
    '''\
    Return bool: does the dictionary of the line (from CSV or similar)
    match all key-value pairs of the criterion dictionary?
    
    Ignore the key 'action' if present.  
    # Alternative version, maybe more Pythonic but maybe less clear.
    '''
    for (key, val) in mydDict.items():
        if key != 'action':
            if mydLine[key] != val:
                break
    else:
        return True
    return False












#=================================================
# c l a s s   C D a t a b a s e 
class CDatabase(object):
    '''
    Isolate all the Mongo-specific stuff here.  
    '''
    @ntracef("DB")
    def __init__(self,mysDatabaseName, mysPendingCollectionName, mysDoneCollectionName):
        self.ID = mysDatabaseName
        self.oDb = mongolib.fnoOpenDb(mysDatabaseName)
        self.oPendingCollection = self.oDb[mysPendingCollectionName]
        self.oDoneCollection = self.oDb[mysDoneCollectionName]
        nPendingCount = self.oPendingCollection.count()
        NTRC.ntracef(0,"DB","proc main pending nRecs|{}|".format(nPendingCount))

    @catchex
    @ntracef("DB")
    def fnitGetInstructionIterator(self,mydQuery):
        '''
        Query pending instructions to get subset of work for today.
        '''
        itCurrentSet = self.oPendingCollection.find(mydQuery)
        '''
        MongoDB tends to time out cursors if they are kept too long.  
         Max number of runs we get is just over 100 before the timeout.  
        Don't want to disable the timeout completely, so collect the entire
         instruction stream into a list up front.  Icky.  Try to be a good
         citizen and what does it get you.  Try to keep the instruction set
         reasonable size, like under a million.  
        '''
        ldAllInstructions = list(itCurrentSet)
        NTRC.ntracef(0,"DB","proc main nInstructionsqueried|{}|".format(len(ldAllInstructions)))
        return ldAllInstructions

    @catchex
    @ntracef("DB")
    def fnbIsItDone(self,mysInstructionId):
        '''
        Does this sDoneId(=mongoid) value already appear in the done collection?
        '''
        dIsItDone = { "sDoneId" : mysInstructionId }
        lMaybeDone = list(self.oDoneCollection.find(dIsItDone))
        NTRC.ntracef(3,"DB","proc check donelist id|%s| list|%s|" % (mysInstructionId, lMaybeDone))
        return len(lMaybeDone) > 0

    @catchex
    @ntracef("DB")
    def fnbDeleteDoneRecord(self,mysInstructionId):
        dIsItDone = { "sDoneId" : mysInstructionId }
        result = self.oDoneCollection.remove(dIsItDone)
        NTRC.ntracef(3,"DB","proc DeleteDone result|%s|" % (result))
        return result["ok"] != 0
