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

    @catchex
    @ntracef("SHOK")
    def __init__(self, mynShockHalflife, mynShockSpan, mynShockImpact):
        self.nLife = mynShockHalflife
        self.nSpan = mynShockSpan
        self.nImpact = mynShockImpact
        self.ID = "Z99"
        self.lServersShocked = []
        
        # If there is to be any shockin' 'round here, start it.  
        #  Otherwise, nothing.
        if self.nLife:
            G.env.process(self.mWaitForShockToHappen(self.nLife))

    @catchex
    @ntracef("SHOK")
    def mWaitForShockToHappen(self, mynHalflife):
        ''' Generator that waits Wait for shock event. '''
        fNewLife = util.makeshocklife(mynHalflife)
        lg.logInfo("SHOCK", "waiting for shock at |%s|" 
            % (fNewLife))
        # Suspend action until shock happens.
        G.env.timeout(fNewLife)
        # Shock has happened.
        lg.logInfo("SHOCK", "t|%6.0f| shock happens" 
            % (G.env.now))
        self.mShockHappens()

    @catchex
    @ntracef("SHOK")
    def mShockHappens(self):
        ''' 
        Shock has happened.  Shorten server lives and schedule the 
        end of the shock cycle.
        '''
        self.mReduceSomeServerLifetimes()
        # TODO: schedule the expiration of the shick
        G.env.process(self.mWaitForShockToExpire(s))

    @catchex
    @ntracef("SHOK")
    def mReduceSomeServerLifetimes(self):
        ''' 
        Find a shockspan-wide subset of servers and reduce their
        expected lifetimes by the stated reduction percentage.
        '''
        lServersToShock = server.CServer.fnlSelectServerVictims(self.nSpan)
        fReduction = self.nImpact * 1.0 / 100.0 
        NTRC.ntracef(3, "SHOK", "proc reduce servers|%s| by pct|%s|" 
            % (lServersToShock, fReduction))
        for sServerID in lServersToShock:
            self.mReduceSingleServerLifetime(sServerID, fReduction)

    @catchex
    @ntracef("SHOK")
    def mReduceSingleServerLifetime(self, mysServerID, myfReduction):
        ''' Reduce the lifetime of a single server. '''
        cServer = G.dId2Server[mysServerID]
        fCurrentLife = cServer.mfGetMyLife()
        fNewLife = myfReduction * fCurrentLife
        NTRC.ntracef(3, "SHOK", "proc shock at t|%8.0f| server|%s| new life|%s|" 
            % (G.env.now, sServerID, fNewLife))
        cServer.mRescheduleMyLife(fNewLife)

    @catchex
    @ntracef("SHOK")
    def mWaitForShockToExpire(self):
        ''' Generator that waits Wait for when the shock cycle expires. '''
        if self.nSpan:
            lg.logInfo("SHOCK", "waiting for shock to expire after |%s|" 
                % (self.nSpan))
            G.env.timeout(self.nSpan)
            lg.logInfo("SHOCK", "t|%6.0f| shock expires" 
                % (G.env.now))
            self.mShockExpires()

    @catchex
    @ntracef("SHOK")
    def mShockExpires(self):
        ''' 
        The shock has expired.  Restore normal lifetimes for
        all the servers that were injured by the shock.
        '''
        pass

    @catchex
    @ntracef("SHOK")
    def mRestoreSomeServerLifetimes(self):
        ''' For all the servers injured by the shock, restore life. '''
        pass

    @catchex
    @ntracef("SHOK")
    def mRestoreSingleServerLifetime(self):
        ''' Restore normal lifetime to a single server. '''
        pass

    @catchex
    @ntracef("SHOK")
    def mBeforeAudit(self):
        '''
        Before each audit cycle, check to see if any servers
        have exceeded their lifetimes.
        '''
        pass

    @catchex
    @ntracef("SHOK")
    def mAtEndOfRun(self):
        '''
        At end of run, check to see if any servers have exceeded
        their lifetimes.  
        '''
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

=============================
BZZZT!  Major change of plan!
=============================

The death of a server does not really affect anything much UNTIL 
the next audit cycle.  Then the dead server is detected when a repair
is attempted and all the usual crap happens.  There is, admittedly, a
small waste of time processing sector errors in the server which should
be dead, but this is a very minor waste of CPU time.  

Soooo, the theory goes like this:
- Server is born with an expiration date.  Random, derived from some
distribution or other.  The boss wants to generalize from exponential
to maybe-something-else.  What?  Gamma?  Beta with a max (ha, ha, 
Beta-Max, get it?)?  Weibull?  
- If default server halflife is zero, then infinite, no expiration.  
This is important so that we don't disturb the random number stream.
- Server deaths are silent when they occur.  They will not be noticed 
until the next audit cycle.  
- At the beginning of each audit cycle, and at the end of the simulation, 
check all servers to see if the expiration date is less than the current 
time.
- If the server has expired, kill it and all its documents.  Standard
functions already available, or used to be.  
- When a shock occurs, immediately downgrade the life expectancies of 
a number of servers based on shockspan.  And set an event for the 
shock end date.
- When the shock expires, restore the life expectancies of all servers
to their original values.  Doesn't matter if the value is now less than 
the next audit time, because the death will be noticed then.  



"""




# Edit history:
# 20160411  RBL Begin.
# 20161121  RBL Describe plan in comments.  Real code to follow.
# 
# 

#END
