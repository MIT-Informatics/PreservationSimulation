#!/usr/bin/python

import simpy
from NewTraceFac07 import TRC,trace,tracef
import itertools
from globaldata import *
from util import *

# L I B R A R Y 
#--------------

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
        G.dID2Library = self

    @tracef("LIB")
    def mAddCollection(self,cColl):
        for cDoc in cColl.lDocuments:
            self.mAddDocument(cDoc)
        return cColl.ID

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
        # Add the doc to this shelf and decrement the space available.
        self.lDocuments.append(doc)
        cs.mAddDocument(doc)
        TRC.tracef(3,"LIB","proc mAddDocument lib|%s| docid|%s| size|%s| assigned to shelf|%s| id|%s| remaining|%s|" % (self.sName,doc.ID,doc.nSize,cs,cs.ID,cs.nFreeSpace))
        return self.ID+"+"+cs.ID+"+"+doc.ID

    @tracef("LIB")
    def mCreateShelf(self):
        ''' mCreateShelf()
            Add a new shelf of the standard size for this library.
            Called as needed when a doc arrives too large for available space.  
        '''
        cShelf = CShelf(self,self.nQual,self.nShelfSize)
        return cShelf
    
    #@tracef("LIB")
    def mDestroyDocument(self,myiDoc,myiShelf):
        ''' mDestroyDocument()
            Oops, a doc died, maybe just one or maybe the whole shelf.
        '''
        TRC.tracef(3,"LIB","proc mDestroyDocument remove doc|%s| from shelf|%s|" % (myiDoc.ID,myiShelf.ID))
        self.lDocuments.remove(myiDoc)
        return self.ID + "-" + myiDoc.ID

@tracef("LIBS")
def makeLibraries(mydLibs):
    for sLibName in mydLibs:
        (nLibQual,nShelfSize) = mydLibs[sLibName][0]
        cLib = CLibrary(sLibName,nLibQual,nShelfSize)
        # Invert the library list so that clients can look up 
        # all the libraries that satisfy a quality criterion.  
        if nLibQual in G.dQual2Libs:
            G.dQual2Libs[nLibQual].append([sLibName,cLib])
        else:
            G.dQual2Libs[nLibQual] = [[sLibName,cLib]]
        TRC.tracef(5,"LIBS","proc makeLibraries dQual2Libs qual|%s| libs|%s|" % (nLibQual,G.dQual2Libs[nLibQual]))

# S H E L F 
#----------

class CShelf(object):
    getID = itertools.count().next

    @tracef("SHLF")
    def __init__(self,myiLib,mynQual,mynCapacity):
        self.lDocuments = list()
        self.nCapacity = int(mynCapacity)
        self.nFreeSpace = int(mynCapacity)
        self.iLib = myiLib          # Library instance we belong to
        self.nQual = mynQual
        self.ID = "H" + str(self.getID())
        G.nShelfLastID = self.ID
        G.dID2Shelf = self
        self.birthdate = G.env.now
        self.bAlive = True
        # Get error rate params and start aging processes
        (self.nSectorLife,self.nShelfLife) = P.dShelfParams[self.nQual][0]
        G.env.process(self.mAge_shelf(self.nShelfLife))
        G.env.process(self.mAge_sector(self.nSectorLife))

    @tracef("SHLF")
    def mAddDocument(self,myiDoc):
        self.lDocuments.append(myiDoc)
        self.nFreeSpace -= myiDoc.nSize
        TRC.tracef(5,"SHLF","proc mAddDocument add doc|%s| to shelf|%s| size|%d| remaining|%d|" % (myiDoc.ID,self.ID,myiDoc.nSize,self.nFreeSpace))
        return self.ID+"+"+myiDoc.ID

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
            TRC.tracef(3,"SHLF","proc mAge_sector time|%d| shelf|%s| Sector_error" % (G.env.now,self.ID))
            # Select a victim Document, probability proportional to size.
            # Small error, size=1.  What doc dies as a result?
            iDocVictim = self.mSelectVictimDoc(1)
            if iDocVictim:
                self.mDestroyDocument(iDocVictim)
                self.iLib.mDestroyDocument(iDocVictim,self)
            else:
                TRC.tracef(3,"SHLF","shelf|%s| sector error fell in empty space" % (self.ID))

    @tracef("SHLF",level=5)
    def mSelectVictimDoc(self,mynErrorSize):
        nRandomSpot = makeunif(1,self.nCapacity)
        nLoc = 0
        for idxDoc,iDoc in enumerate(self.lDocuments):
            nLoc += iDoc.nSize
            iVictim = iDoc
            if nLoc > nRandomSpot:
                TRC.tracef(5,"SHLF","proc mSelectVictimDoc shelf|%s| sector|%d| hits doc|%s|" % (self.ID,nRandomSpot,iVictim.ID))
                break
        else:
            iVictim = None
            TRC.tracef(5,"SHLF","proc mSelectVictimDoc shelf|%s| sector|%d| hits empty space" % (self.ID,nRandomSpot))
        return iVictim

    @tracef("SHLF",level=5)
    def mDestroyDocument(self,myiDoc):
        TRC.tracef(3,"SHLF","proc mDestroyDocument remove doc|%s| from shelf|%s|" % (myiDoc.ID,self.ID))
        self.lDocuments.remove(myiDoc)
        return self.ID + "-" + myiDoc.ID

    @tracef("SHLF",level=5)
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
        for iDoc in self.lDocuments:
            self.mDestroyDocument(iDoc)
            self.iLib.mDestroyDocument(iDoc,self)
        self.bAlive = False

    @tracef("COLL")
    def mListBooks(self):
        pass


# END
