#!/usr/bin/python
# repair.py

import simpy
from NewTraceFac import TRC,trace,tracef
import itertools
from globaldata import *
from logoutput import logInfo


# C l a s s   C R e p a i r 
class CRepair(object):
    getID = itertools.count().next

    @tracef("SERV")
    def __init__(self):
        self.ID = "R" + str(self.getID())
        G.dID2Repair[self.ID] = self

    
    pass





# END
