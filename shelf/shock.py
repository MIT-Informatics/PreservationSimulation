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
    def __init__(self, mynShockHalflife, mynShockSpan, mynShockImpact, mynShockMaxlife):
        self.nLife = mynShockHalflife
        self.nSpan = mynShockSpan
        self.nImpact = mynShockImpact
        self.nMaxlife = mynShockMaxlife
        self.ID = "Z99"
        self.lsServersShocked = []
        
        # If there is to be any shockin' 'round here, start it.  
        #  Otherwise, nothing.
        if self.nLife:
            G.env.process(self.mWaitForShockToHappen(self.nLife))

# m W a i t F o r S h o c k T o H a p p e n 
    @catchex
    @ntracef("SHOK")
    def mWaitForShockToHappen(self, mynHalflife):
        ''' Generator that waits Wait for shock event. '''
        while True:
            # Schocks happen every so often, not just once.  
            fNewLife = util.makeshocklife(mynHalflife)
            lg.logInfo("SHOCK", "t|%6.0f| waiting for shock in|%6.0f| from hl|%s|" 
                % (G.env.now, fNewLife, mynHalflife))
            # Suspend action until shock happens.
            yield G.env.timeout(fNewLife)
            # Shock has happened.
            lg.logInfo("SHOCK", "t|%6.0f| shock happens now, maxlife|%s|" 
                % (G.env.now, self.nMaxlife))
            self.mShockHappens()
            # If maxlife nonzero, then wait and expire shock;
            #  else, never expires, so wait forever and don't 
            #  start another shock cycle.
            if self.nMaxlife > 0:
                lg.logInfo("SHOCK", "t|%6.0f| waiting for shock to expire in|%6.0f|" 
                    % (G.env.now, self.nMaxlife))
                yield G.env.timeout(self.nMaxlife)
                self.mShockExpires()
            else:
                yield G.env.timeout(G.fInfinity)

# m S h o c k H a p p e n s 
    @catchex
    @ntracef("SHOK")
    def mShockHappens(self):
        ''' 
        Shock has happened.  Shorten server lives and schedule the 
        end of the shock cycle.
        '''
        G.nShocksTotal += 1
        lg.logInfo("SHOCK", "t|%6.0f| start to reduce life of |%s| servers by pct|%s|" 
            % (G.env.now, self.nSpan, self.nImpact))
        self.mReduceSomeServerLifetimes(self.nSpan, self.nImpact)
        return G.env.now

# m R e d u c e S o m e S e r v e r L i f e t i m e s 
    @catchex
    @ntracef("SHOK")
    def mReduceSomeServerLifetimes(self, mynSpan, mynImpact):
        ''' 
        Find a shockspan-wide subset of servers and reduce their
        expected lifetimes by the stated reduction percentage.
        '''
        lServersToShock = server.CServer.fnlSelectServerVictims(mynSpan)
        fReduction = mynImpact * 1.0 / 100.0 
        NTRC.ntracef(3, "SHOK", "proc reduce servers|%s| by|%s|" 
            % (lServersToShock, fReduction))
        for sServerID in lServersToShock:
            lg.logInfo("SHOCK", "t|%6.0f| reduce server|%s| life by pct|%s|" 
                % (G.env.now, sServerID, self.nImpact))
            self.mReduceSingleServerLifetime(sServerID, fReduction)
            self.lsServersShocked.append(sServerID)

# m R e d u c e S i n g l e S e r v e r L i f e t i m e 
    @catchex
    @ntracef("SHOK")
    def mReduceSingleServerLifetime(self, mysServerID, myfReduction):
        ''' Reduce the lifetime of a single server. '''
        cServer = G.dID2Server[mysServerID]
        fCurrentLife = cServer.mfGetMyCurrentLife()
        fNewLife = (1.0 - myfReduction) * fCurrentLife
        NTRC.ntracef(3, "SHOK", "proc shock at t|%8.0f| server|%s| new life|%s|" 
            % (G.env.now, mysServerID, fNewLife))
        lg.logInfo("SHOCK", "t|%6.0f| reducing server|%s| life by|%s| to |%s|" 
            % (G.env.now, mysServerID, myfReduction, fNewLife))
        cServer.mRescheduleMyLife(fNewLife)

# m S h o c k E x p i r e s 
    @catchex
    @ntracef("SHOK")
    def mShockExpires(self):
        ''' 
        The shock has expired.  Restore normal lifetimes for
        all the servers that were injured by the shock.
        '''
        self.mRestoreSomeServerLifetimes()

# m R e s t o r e S o m e S e r v e r L i f e t i m e s 
    @catchex
    @ntracef("SHOK")
    def mRestoreSomeServerLifetimes(self):
        ''' For all the servers injured by the shock, restore life. '''
        for sServerID in self.lsServersShocked:
            self.mRestoreSingleServerLifetime(sServerID)
        self.lsServersShocked = []

# m R e s t o r e S i n g l e S e r v e r L i f e t i m e 
    @catchex
    @ntracef("SHOK")
    def mRestoreSingleServerLifetime(self, mysServerID):
        ''' Restore normal lifetime to a single server. '''
        cServer = G.dID2Server[mysServerID]
        fOriginalLifespan = cServer.mfGetMyOriginalLife()
        lg.logInfo("SHOCK", "t|%6.0f| restoring server|%s| life to |%s|" 
            % (G.env.now, mysServerID, fOriginalLifespan))
        cServer.mRescheduleMyLife(fOriginalLifespan)

# m B e f o r e A u d i t 
    @catchex
    @ntracef("SHOK")
    def mBeforeAudit(self):
        '''
        Before each audit cycle, check to see if any servers
         have exceeded their lifetimes.
        '''
        pass

# m A t E n d O f R u n 
    @catchex
    @ntracef("SHOK")
    def mAtEndOfRun(self):
        '''
        At end of run, check to see if any servers have exceeded
         their lifetimes.  It is possible for servers to die from
         shocks even if there is no auditing, and that counts
         because we evaluate every doc at the end of run.
        '''
        pass


"""
Every server begins with lifetime generated from some overall halflife.
After all servers instantiated, main or makethings allocates a Shock with 
 shockfreq param halflife.
When Shock fires, 
    - choose a subset of servers according to shockspan.
    - reduce their lifetimes.

Details
- get shockfreq from globaldata; if zero, skip all this falderal.
- generate an expo using shockfreq as halflife.
- wait for that timeout; shock fires.
- get a subset of servers to schedule death for.
    -- server classmethod to nominate subset: 
        CServer.fnlSelectServerVictims(nHowManyVictims)
- for each server in the list:
    - XXXXXX all the stuff that was here has been superseded.  

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
# 20161205  RBL Insert stubs.
# 21061212  RBL Flesh out most of the stubs.
# 20161218  RBL Debug, and revise GUI.  Still need to fix CLI->G.
# 20161222  RBL Simplify (and correct) shock expiration.  
#                Limitation: cannot start shock2 while shock1 is
#                still in progress.  Not too serious, but maybe
#                noticeable to some.
#               Make sure that reducing and restoring lifetime works.
# 
# 

#END
