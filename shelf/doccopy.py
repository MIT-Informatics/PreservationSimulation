#!/usr/bin/python
# doccopy.py
# NOTE: we have to call this file something other than copy.py because of the 
#  standard library "copy" module.  The classname, however, is okay.  

import  simpy
from    NewTraceFac     import  NTRC, ntrace, ntracef
import  itertools
from    globaldata      import  G
from    math            import  exp, log
import  util
import  copy
import  logoutput       as lg
from    catchex         import  catchex


#===========================================================
# Class C O P Y  ( of  D o c u m e n t )
#---------------------------------------

class CCopy(object):
    getID = itertools.count(1).next

    @ntracef("COPY")
    def __init__(self,mysDocID,mysClientID,mysServerID):
        self.ID = "X" + str(self.getID())
        G.dID2Copy[self.ID] = self
        G.nCopyLastID = self.ID

        # What document is this a copy of?
        self.sDocID = mysDocID
        self.sClientID = mysClientID
        # Where is this copy being stored?
        self.sServerID = mysServerID
        self.sShelfID = None
        self.nBlkBegin = None
        self.nBlkEnd = None
        
    @property
    def cDoc(self):
        return G.dID2Document[self.sDocID]

    @property
    def cClient(self):
        return G.dID2Document[self.sClientID]

    @property
    def cServer(self):
        return G.dID2Server[self.sServerID]

    @property
    def cServer(self):
        return G.dID2Shelf[self.sShelfID]

    @ntracef("COPY")
    def mShelveCopy(self,mysServerID,mysShelfID,mynBlkBegin,mynBlkEnd):
        self.sServerID = mysServerID
        self.sShelfID = mysShelfID
        self.nBlkBegin = mynBlkBegin
        self.nBlkEnd = mynBlkEnd
        return self.ID+"+"+mysServerID+"+"+mysShelfID+"+" + "["+str(mynBlkBegin)+","+str(mynBlkEnd)+"]"

    @ntracef("COPY")
    def mGetDocID(self):
        return self.sDocID


# Edit history:
# 20150812  RBL Move CCopy from server.py to its own file.  
# 20180516  RBL Update to use only ntrace, ntracef, NTRC.
# 

#END

