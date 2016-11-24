#!/usr/bin/python
# shock.py
#
# Timing routines for economic or environmental shocks to servers.  

from    NewTraceFac     import  NTRC,ntracef,ntrace
import  simpy
import  resettabletimer
from    globaldata      import  G
import  util
import  logoutput       as lg
from    catchex         import  catchex
import  server


#===========================================================
# C l a s s  C S h o c k 
#---------------------

class CShock(object):
    @ntracef("SHCK")
    def __init__(self,dunnoyet):
        pass

#
    @ntracef("SHCK")
    def foo(bar):
        pass





"""
Every server begins with lifetime generated from some overall halflife.
 This is not currently parameterized, hmmm.  It may be acceptable to have
 a param for it in the csv param-param file and not in the CLI.
After all servers instantiated, main or makethings allocates a Shock with 
 shockfreq param halflife.
When Shock fires, 
    - choose a subset of servers according to shockspan.
    - cancel their lifetimes and restart lifetimes of those servers using
       smaller halflife reduced by shock.

Details
- get shockfreq from globaldata; if zero, skip all this falderal.
- generate an expo using shockfreq as halflife.
- wait for that timeout; shock fires.
- get a subset of servers to schedule death for.
    -- server classmethod nominate subset: 
        CServer.fnlSelectServerVictims(nHowManyVictims)
- for each server in the list:
    - interrupt server's timer. 
        -- server instance method interrupt timer: cServer.mCorrFailHappensToMe()
    - generate new random short death time.
        - calculate new halflife using shockimpact.
        -- util something random.
    - change the server's timer deadline and restart the timer.
        -- instance method reschedule and start: cServer.mRescheduleMyLife(nNewLife)

When Server Lifetime expires, server loses all docs as usual.


"""




# Edit history:
# 20160411  RBL Begin.
# 20161121  RBL Describe plan in comments.  Real code to follow.
# 
# 

#END
