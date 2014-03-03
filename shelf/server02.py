#!/usr/bin/python

import simpy
from NewTraceFac07 import TRC,trace,tracef
import itertools
from globaldata import *
from util import *
import copy


# C l a s s  L I B R A R Y 
#-------------------------

class CLibrary(object):
    # Function to get a unique, autoincrementing ID for instances
    # of this class.  
    getID = itertools.count().next

    @tracef("LIB")
    def __init__(self,mysName,mynQual,mynShelfSize):
        self.sName = mysName
        self.nQual = mynQual
        self.nShelfSize = mynShelfSize
        self.ID = "L" + str(self.getID())
        self.lShelves = list()
        self.lDocuments = list()
        G.dID2Library[self.ID] = self

# L i b r a r y . m A d d C o l l e c t i o n
    @tracef("LIB")
    def mAddCollection(self,cCollID):
        for cDocID in G.dID2Collection[cCollID].lDocuments:
            self.mAddDocument(cDocID)
        return cCollID

# L i b r a r y . m A d d D o c u m e n t 
    @tracef("LIB")
    def mAddDocument(self,myDocID):
        ''' mAddDocument(docid)
            Find a shelf with room for the doc, or create one.
            Put the doc on the shelf, decrement the remaining space.
        '''
        cDoc = G.dID2Document[myDocID]
        cShelf = None
        for shelfID in self.lShelves:
            cShelf = G.dID2Shelf[shelfID]
            if cShelf.nFreeSpace >= cDoc.nSize:
                break
            else:
                continue
        else:
            shelfID = self.mCreateShelf()
            self.lShelves.append(shelfID)
            cShelf = G.dID2Shelf[shelfID]
        # Add the doc to this shelf and decrement the space available.
        self.lDocuments.append(myDocID)
        cShelf.mAddDocument(myDocID)
        TRC.tracef(3,"LIB","proc mAddDocument lib|%s| id|%s| docid|%s| size|%s| assigned to shelfid|%s| remaining|%s|" % (self.sName,self.ID,myDocID,cDoc.nSize,shelfID,cShelf.nFreeSpace))
        return self.ID+"+"+shelfID+"+"+myDocID

# L i b r a r y . m C r e a t e S h e l f 
    @tracef("LIB")
    def mCreateShelf(self):
        ''' mCreateShelf()
            Add a new shelf of the standard size for this library.
            Called as needed when a doc arrives too large for available space.  
        '''
        cShelf = CShelf(self,self.nQual,self.nShelfSize)
        return cShelf.ID

# L i b r a r y . m R e p l a c e S h e l f 
# NYI

# L i b r a r y . m D e s t r o y D o c u m e n t 
    @tracef("LIB")
    def mDestroyDocument(self,mysDocID,mysShelfID):
        ''' Library.mDestroyDocument()
            Oops, a doc died, maybe just one or maybe the whole shelf.
        '''
        TRC.tracef(3,"LIB","proc mDestroyDocument remove doc|%s| from shelf|%s|" % (mysDocID,mysShelfID))
        self.lDocuments.remove(mysDocID)
        return self.ID + "-" + mysDocID

# m a k e L i b r a r i e s 
@tracef("LIBS")
def makeLibraries(mydLibs):
    for sLibName in mydLibs:
        (nLibQual,nShelfSize) = mydLibs[sLibName][0]
        sLibID = CLibrary(sLibName,nLibQual,nShelfSize).ID
        # Invert the library list so that clients can look up 
        # all the libraries that satisfy a quality criterion.  
        if nLibQual in G.dQual2Libs:
            G.dQual2Libs[nLibQual].append([sLibName,sLibID])
        else:
            G.dQual2Libs[nLibQual] = [[sLibName,sLibID]]
        TRC.tracef(5,"LIBS","proc makeLibraries dQual2Libs qual|%s| libs|%s|" % (nLibQual,G.dQual2Libs[nLibQual]))
    return G.dQual2Libs

# C l a s s  S H E L F 
#---------------------

class CShelf(object):
    getID = itertools.count().next

    @tracef("SHLF")
    def __init__(self,myiLib,mynQual,mynCapacity):
        self.ID = "H" + str(self.getID())
        G.nShelfLastID = self.ID
        G.dID2Shelf[self.ID] = self
        self.lDocuments = list()
        self.nCapacity = mynCapacity
        self.nFreeSpace = mynCapacity
        self.sLibID = myiLib.ID          # Library instance we belong to
        self.nQual = mynQual
        self.birthdate = G.env.now
        self.bAlive = True
        self.nSectorHits = 0
        self.nEmptySectorHits = 0
        self.bContig = True
        # Get error rate params and start aging processes
        (self.nSectorLife,self.nShelfLife) = P.dShelfParams[self.nQual][0]
        G.env.process(self.mAge_shelf(self.nShelfLife))
        G.env.process(self.mAge_sector(self.nSectorLife))

# S h e l f . m A d d D o c u m e n t 
    @tracef("SHLF")
    def mAddDocument(self,mysDocID):
        ''' mAddDocument(docID)
            Add a document to this shelf and record some information in 
            the document itself.
        '''
        self.lDocuments.append(mysDocID)
        cDoc = G.dID2Document[mysDocID]
        cDoc.nBlkBegin = self.nCapacity - self.nFreeSpace
        self.nFreeSpace -= cDoc.nSize
        cDoc.nBlkEnd = cDoc.nBlkBegin + cDoc.nSize - 1
        cDoc.sShelfID = self.ID
        cDoc.sLibID = self.sLibID
        TRC.tracef(5,"SHLF","proc mAddDocument add doc|%s| to shelf|%s| size|%d| remaining|%d|" % (mysDocID,self.ID,cDoc.nSize,self.nFreeSpace))
        
        return self.ID+"+"+mysDocID

# S h e l f . m A g e _ s e c t o r 
    @tracef("SHLF")
    def mAge_sector(self,mynLifeParam):
        ''' A sector in the shelf fails.  This corrupts a document.
            For the moment, assume that it destroys the document.  
            Eventually, it will have a probability of destroying the 
            documeht depending on the portion of the document 
            corrupted and the sensitivity of the document to corruption
            (e.g., compressed or encrypted).  
        '''
        # If the shelf has been emptied by a shelf failure, stop 
        # caring about sector failures.
        while self.bAlive:
            nSectorLife = makeexpo(mynLifeParam)
            TRC.tracef(3,"SHLF","proc mAge_sector time|%d| shelf|%s| next lifetime|%d|" % (G.env.now,self.ID,nSectorLife))
            yield G.env.timeout(nSectorLife)
            
            self.nSectorHits += 1
            TRC.tracef(3,"SHLF","proc mAge_sector time|%d| shelf|%s| Sector_error hits|%d| emptyhits|%d|" % (G.env.now,self.ID,self.nSectorHits,self.nEmptySectorHits))
            # Select a victim Document, probability proportional to size.
            # Small error, size=1.  What doc dies as a result?
            sDocVictimID = self.mSelectVictimDoc(mynErrorSize=1)
            if sDocVictimID:
                self.mDestroyDocument(sDocVictimID)
                G.dID2Library[self.sLibID].mDestroyDocument(sDocVictimID,self.ID)
            else:
                self.nEmptySectorHits += 1
                TRC.tracef(3,"SHLF","shelf|%s| sector error fell in empty space" % (self.ID))
            # Initiate a repair of the dead document.
            # NYI

# S h e l f . m S e l e c t V i c t i m D o c 
    @tracef("SHLF")
    def mSelectVictimDoc(self,mynErrorSize):
        ''' mSelectVictimDoc(errorsize)
            Which doc on this shelf, if any, was hit by this error?
            Throw a uniform dart at all the docs on the shelf, see 
            which one gets hit.  Doc size counts.  
        '''
        nRandomSpot = makeunif(1,self.nCapacity)
        nLoc = 0
        for idxDoc,sDocID in enumerate(self.lDocuments):
            cDoc = G.dID2Document[sDocID]
            iVictim = cDoc
            sVictimID = cDoc.ID
            if nRandomSpot >= cDoc.nBlkBegin and nRandomSpot <= cDoc.nBlkEnd:
                TRC.tracef(5,"SHLF","proc mSelectVictimDoc shelf|%s| sector|%d| hits doc|%s| size|%d|outof|%d|" % (self.ID,nRandomSpot,sVictimID,cDoc.nSize,self.nCapacity))
                break
        else:
            iVictim = None
            sVictimID = None
            TRC.tracef(5,"SHLF","proc mSelectVictimDoc shelf|%s| sector|%d| hits empty space" % (self.ID,nRandomSpot))
        return sVictimID

# S h e l f . m D e s t r o y D o c u m e n t 
    @tracef("SHLF",level=3)
    def mDestroyDocument(self,mysDocID):
        self.lDocuments.remove(mysDocID)
        self.bContig = False
        self.nFreeSpace += G.dID2Document[mysDocID].nSize
        TRC.tracef(3,"SHLF","proc mDestroyDocument remove doc|%s| size|%d| from shelf|%s| remainingdocs|%d| free|%d|" % (mysDocID,G.dID2Document[mysDocID].nSize,self.ID,len(self.lDocuments),self.nFreeSpace))
        return self.ID + "-" + mysDocID

# S h e l f . m A g e _ s h e l f 
    @tracef("SHLF",level=3)
    def mAge_shelf(self,mynLifeParam):
        ''' An entire shelf fails.  Remove all the docs it contained.
            Eventually, this will trigger a repair event and make the 
            collection more vulnerable during the repair.  
        '''
        nShelfLife = makeexpo(mynLifeParam)
        TRC.tracef(3,"SHLF","proc mAge_shelf  time|%d| shelf|%s| next lifetime|%d|" % (G.env.now,self.ID,nShelfLife))
        yield G.env.timeout(nShelfLife)
        TRC.tracef(3,"SHLF","proc mAge_shelf  time|%d| shelf|%s| shelf_error" % (G.env.now,self.ID))
        # This whole shelf is a goner.  Kill it. 
        TRC.tracef(5,"SHLF","proc kill shelf contents ldocs|%s|" % (self.lDocuments)) 
        # Note that we have to copy the list before modifying it and 
        # iterate over the copy.  
        # Standard problem with updating an iterable inside the for loop.
        templDocuments = copy.deepcopy(self.lDocuments)
        for sDocID in templDocuments:
            self.mDestroyDocument(sDocID)
            G.dID2Library[self.sLibID].mDestroyDocument(sDocID,self.ID)
        self.bAlive = False
        # Rescind any pending sector error aging for this shelf.
        # (Only a performance improvement, I think, since the shelf
        # will be destroyed and never reused.)  
        # NYI
        # Tell the library to replace the dead shelf.
        # NYI

# S h e l f . m L i s t B o o k s 
    @tracef("COLL")
    def mListBooks(self):
        pass


# END
