#!/usr/bin/python

''' shelf4.py
Blank page version of bookshelf preservation of documents.
Vague beginning of document preservation simulation.  

The plan: 

Library
    collection of shelves
    find a shelf for document
        if out of space, create a shelf
    aging process for institutional failure

Shelf
    capacity
    free space
    reliability class
    birthdate
    list of documents
    aging process for small errors that damage a document
        pick a victim document to be damaged
    aging process for disk failure that can be rebuilt
    aging process for array failure that kills all documents

Document
    size
    value class
        determines shelf policy
        determines audit policy
    log of actions
    audit process

Collection
    create set of documents
    value class
    storage policy
    audit policy
    budget
    list of libraries used

Client
    create set of collections
        different value classes
        distribution of document sizes

start logs
create libraries
create client
run

'''

import simpy
import random
from NewTraceFac07 import TRC,trace,tracef
from sys import argv
from math import sqrt
import itertools

# L I B R A R Y 
#--------------

class CLibrary(object):
    lShelves = list()
    lDocs = list()
    # Function to get a unique, autoincrementing ID for instances
    # of this class.  
    getID = itertools.count().next

    @tracef("LIB")
    def __init__(self,mysName,mynShelfSize):
        self.sName = mysName
        self.nShelfSize = mynShelfSize
        self.ID = self.getID()

    @tracef("LIB")
    def mAddCollection(self,cColl):
        for cDoc in cColl.lDocuments:
            self.mAddDocument(cDoc)

    @tracef("LIB")
    def mAddDocument(self,doc):
        ''' mAddDocument(doc)
            Find a shelf with room for the doc, or create one.
            Put the doc on the shelf, decrement the remaining space.
        '''
        for cs in self.lShelves:
            if cs.nFreeSpace >= doc.nSize:
                break
            else:
                continue
        else:
            cs = self.mCreateShelf()
            self.lShelves.append(cs)
#            cs.ID = len(self.lShelves)
        # Add the doc to this shelf and decrement the space available.
        self.lDocs.append(doc)
        cs.nFreeSpace -= doc.nSize
        TRC.tracef(3,"LIB","proc lib|%s| docid|%s| size|%s| assigned to shelf|%s| id|%s| remaining|%s|" % (self.sName,doc.ID,doc.nSize,cs,cs.ID,cs.nFreeSpace))

    @tracef("LIB")
    def mCreateShelf(self):
        ''' mCreateShelf()
            Add a new shelf of the standard size for this library.
            Called as needed when a doc arrives too large for available space.  
        '''
        cShelf = CShelf(self.nShelfSize)
        return cShelf

@tracef("LIBS")
def makeLibraries(mydLibs):
    for sLibName in mydLibs:
        (nLibQual,nShelfSize) = mydLibs[sLibName]
        cLib = CLibrary(sLibName,nShelfSize)
        # Invert the library list so that clients can look up 
        # all the libraries that satisfy a quality criterion.  
        if nLibQual in G.p_dQual2Libs:
            G.p_dQual2Libs[nLibQual].append([sLibName,cLib])
        else:
            G.p_dQual2Libs[nLibQual] = [[sLibName,cLib]]
        TRC.tracef(3,"LIBS","proc dQual2Libs qual|%s| libs|%s|" % (nLibQual,G.p_dQual2Libs[nLibQual]))

# S H E L F 
#----------

class CShelf(object):
    lDocuments = list()
    getID = itertools.count().next

    @tracef("SHLF")
    def __init__(self,mynCapacity):
        self.nCapacity = mynCapacity
        self.nFreeSpace = mynCapacity
        self.ID = self.getID()
        G.p_nShelfLastID = self.ID
        self.birthdate = G.env.now

    @tracef("SHLF")
    def mAge_sector(self,something):
        yield something
        pass

    @tracef("SHLF")
    def mAge_shelf(self,something):
        yield something
        pass

    def selectVictimDoc(self):
        pass

# D O C U M E N T 
#----------------

class CDocument(object):
    lActions = list()
    getID = itertools.count(100).next

    @tracef("DOC")
    def __init__(self,size):
        self.nSize = size
        self.ID = self.getID()
        G.p_nDocLastID = self.ID

    def mAudit(self):
        pass

# C O L L E C T I O N 
#--------------------

class CCollection(object):
    lDocuments = list()
    lLibraries = list()
    getID = itertools.count().next

    @tracef("COLL")
    def __init__(self,mysName,mynSize):
        self.mMakeBooks(mynSize)
        self.sName = mysName
        self.ID = self.getID()
        G.p_nCollLastID = self.ID

    @tracef("COLL")
    def mMakeBooks(self,nbooks):
        # A collection has lots of books
        nrandbooks = int(makennnorm(nbooks))
        for icoll in xrange(nrandbooks):
            ndocsize = makeunif(1,1000)
            cDoc = CDocument(ndocsize)
            self.lDocuments.append(cDoc)

    @tracef("COLL")
    def mListBooks(self):
        pass

# C L I E N T 
#------------

class CClient(object):
    lCollections = list()
    getID = itertools.count().next

    @tracef("CLI")
    def __init__(self,mysName,mylCollections):
        self.sName = mysName
        self.ID = self.getID()
        for lCollectionParams in mylCollections:
            (sCollName,nCollValue,nCollSize) = lCollectionParams
            cColl = CCollection(sCollName,nCollSize)
            self.lCollections.append(cColl)
            # select lib based on value

            # T E M P 
            # put collection into a cheap library
            lLibInfo = G.p_dQual2Libs[1]
            (sLibName,cLib) = lLibInfo[1]
            TRC.tracef(3,"CLI","proc assign collection|%s| named|%s| to libinfo|%s| named|%s|" % (cColl,cColl.sName,cLib,cLib.sName))
            cLib.mAddCollection(cColl)
            # E N D   T E M P 

# Create all clients; give them their params for the simulation.
@tracef("MAIN")
def makeClients(mydClients):
    for sClientName in mydClients:
        cClient = CClient(sClientName,mydClients[sClientName])
        G.p_lAllClients.append(cClient)


# U t i l i t i e s 
#------------------

def makeexpo(mean):
    ''' fn makeexpo(mean)
        return integer from exponential distribution with mean
    '''
    interval = int(random.expovariate(1.0/abs(mean)))
    return interval

def makeunif(lo,hi):
    ''' fn makeinfo(lo,hi)
        return integer from uniform distribution in range
    '''
    interval = int(random.uniform(lo,hi))
    return interval
    
def makennnorm(mean):
    ''' makennnorm(mean)
        return non-neg gaussian with mean and sd sqrt(mean)
     '''
    x = random.gauss(mean,sqrt(mean))
    return abs(x)
    
def getDocSerialID():
    ''' getDocSerialID()
        return a unique ID for each book that requests one
    '''
    G.p_nDocSerialID += 1
    return G.p_nDocSerialID


# G L O B A L  D A T A 
#---------------------

class G(object):
    ''' Global data, of which we are sure there is only one copy.
        Use this only for truly global data that would be just
        too painful to pass around all the time.  
        Never instantiated; used only as a dictionary.
        Not everything is pre-declared here; some is added later.  
    '''
    p_lLibraries = []
    p_nLibraries = 1
    p_nClients = 1
    p_nCollections = [3]
    p_lAllClients = list()
    # Client has a name and a list of collections.
    # Collection has a name, a value, and a target size.
    p_dClientParams = {
          "MIT":[ ["Mags",1,10], ["Books",2,5] ]
        , "Harvard":[ ["Cheap",1,20], ["Rare",3,10] ]
                    }
    # Library has a name and a quality rating.
    p_dLibraryParams = { "Barker":[1,2000]
                        , "Dewey":[1,3000]
                        , "Widener":[2,4000]
                        , "Houghton":[3,2000]
                    }
    p_dQual2Libs = dict()
    p_nDocLastID = 0
    p_nCollLastID = 0
    p_nShelfLastID = 0


# M A I N   L I N E
#------------------

if __name__ == "__main__":

    SIMLENGTH = 1000
    RANDOMSEED = 1

    TRC.tracef(0,"MAIN","proc Call center simulation " % ())

    random.seed(RANDOMSEED)
    env = simpy.Environment()
    G.env = env

    G.p_runtime = SIMLENGTH if len(argv) <=1 else int(argv[1])
    G.p_randomseed = RANDOMSEED if len(argv) <=1 else int(argv[1])

    makeLibraries(G.p_dLibraryParams)
    makeClients(G.p_dClientParams)

    TRC.tracef(0,"MAIN","proc End simulation time|%d| ndocs|%d| ncolls|%d| nshelves|%d|" % (env.now,G.p_nDocLastID+1,G.p_nCollLastID+1,G.p_nShelfLastID+1))

# END
